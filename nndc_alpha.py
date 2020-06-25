import urllib.request
import urllib.error
from lxml.html import parse
from urllib.request import urlopen
import pandas as pd
import sys
import time
import random
import numpy as np
import unicodedata
from unidecode import unidecode
from decimal import Decimal
import re

class nuc:
    def __init__(self, z, n, t):
        self.z = int(z)
        self.n = int(n)
        self.t = t
    def __repr__(self):
        return "{}".format(*[self.z, self.n, self.t])

def _unpack(row, kind='td'):
    elts = row.findall('.//{}'.format(kind))
    return [val.text_content().replace('\xa0', '') for val in elts]

def find_nth(haystack, needle, n): #sök efter char i text
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + len(needle))
        n -= 1
    return int(start)

def _preparse_data(table, bindingenergy = 0):
    rows = table.findall('.//tr')
    data = [_unpack(r) for r in rows[1:2]]
    #data[0].apply(lambda x: x.replace('?', '').replace('≈','').replace('X','').replace('+','').split(' '))
    newdata = [x.replace('?', '').replace('≈','').replace('<', '').replace('>','').replace('=','').replace('≥','') for x in data[0]]
    print(newdata)
    try:
        th = str(newdata[3]).strip()
        if th == '':
            th = str(newdata[2]).strip()
            if th == '':
                th = str(newdata[1]).strip()
        return th
    except IndexError:
        try:
            th = str(newdata[2]).strip()
            if th == '':
                th = str(newdata[1]).strip()
            return th
        except IndexError:
            try:
                th = str(newdata[1]).strip()
                return th
            except IndexError:
                #print(newdata)
                return False

def _parse_options_data(inplist):
    tabledate = pd.DataFrame(inplist)
    pd.options.display.max_rows = 40000
    tabledate['Jpar'] = tabledate[2].apply(lambda x: x.strip())
    tabledate['thalf'] = tabledate[3].apply(lambda x: x.strip())
    tabledate['Ecompare'] = tabledate[0].apply(
        lambda x: round(float('0'+x.replace('?', '').replace('≈','').replace('X','').replace('+','').split(' ')[0]) / 1000, 5))
    tabledate['Jnum'] = tabledate[['Ecompare', 'Jpar']].groupby(by=['Jpar'])[['Ecompare']].rank()
    tabledate['Jnum'] = tabledate['Jnum'].apply(lambda x: int(x))
    tabledate['Eall'] = tabledate['Ecompare'].apply(lambda x: round(x + bindingenergy, 5))
    result = tabledate[['Jpar', 'Jnum', 'Ecompare', 'Eall', 'thalf']]
    return result

def get_list_from_row(text):
    while "  " in text:
        text = text.replace("  ", " ")
    text = text.replace("\n", "").strip().split(" ")
    return text

def print_thalf(): #downloads the data from nudat and prints to thalf.dat
    t_file = open('thalf.dat', "w")
    with open('bind2016.dat') as file:
        explist = file.readlines()
    bindfile = open('bind2_stripped.dat', "w")
    for e in explist:
        nuc = get_list_from_row(e)
        if float(nuc[5])*float(nuc[2]) > 100 or int(nuc[1]) < 6 or int(nuc[2]) < 12:
            continue        
        bindfile.write("{: >5} {: >5} {: >5} {: >5} {: >5} {: >6}".format(*nuc) + "\n")
    bindfile.close()
    with open('bind2_stripped.dat') as file:
        nuclist = file.readlines()
    for n in nuclist:
        nl = get_list_from_row(n)
        mass = nl[2]
        if len(nl) > 6:
            ft = ''
            for i in range(5, len(nl)):
                ft += nl[i] + " "
            nl[5] = ft.strip()
            t_file.write("{: >5} {: >5} {: >5} {: >5} {: >5} {: >6} {: >15}".format(*nl) + "\n")
            continue
        dataname = nl[3]
        dataurl = 'https://www.nndc.bnl.gov/chart/getdataset.jsp?nucleus={}{}&unc=nds'.format(mass, dataname)
        req = urllib.request.Request(dataurl)
        try:
            html = urlopen(req).read()
        except urllib.error.URLError as e:
            print('error')
            continue
        if 'Empty dataset for' in str(html, 'utf-8'):
            print('error')
        if 'We are sorry' in str(html, 'utf-8'):
            print('error')
        time.sleep(np.random.randint(1,4)) 
        try:
            html = parse(urlopen(req))
        except urllib.error.URLError:
            continue

        doc = html.getroot()
        table = doc.findall('.//table')
        if len(table) == 0:
            continue
            print('error')
        table = table[0]
        rows = table.findall('.//tr')
        if len(rows) == 0:
            print('no table')
            print('error')
            continue
        if len(rows) == 1:
            print('no value')
            print('error')
            continue
        columns = _unpack(rows[0])
        if 'Elevel  (keV)' not in columns:
            print('no Ekev')
            print('error')
        if 'Jπ ' not in columns:
            print('no Jpar')
            print('error')
        if ' XREF ' not in columns:
            print('no XREF')
            print('error')

        bindingenergy = 0
        thalf = _preparse_data(table = table, bindingenergy = bindingenergy)
        print(thalf)
        if thalf is False:
            continue
        nl.append(str(thalf))
        t_file.write("{: >5} {: >5} {: >5} {: >5} {: >6} {: >10} {: >15}".format(*nl) + "\n")
    t_file.close()

def make_seconds(num, time): #converts days to seconds etc.
    if time == "s":
        mult = 1
    elif time == "m":
        mult = 60
    elif time == "h":
        mult = 3600
    elif time == "d":
        mult = 3600*24
    elif time == "y":
        mult = 3600*24*365
    elif time == "ky":
        mult = 1e+3*3600*24*365
    elif time == "My":
        mult = 1e+6*3600*24*365
    elif time == "Gy":
        mult = 1e+9*3600*24*365
    elif time == "Ty":
        mult = 1e+12*3600*24*365
    elif time == "Py":
        mult = 1e+15*3600*24*365
    elif time == "Ey":
        mult = 1e+18*3600*24*365
    elif time == "Zy":
        mult = 1e+21*3600*24*365
    elif time == "Yy":
        mult = 1e+24*3600*24*365
    elif time == "ms":
        mult = 1e-3 #0.001
    elif time == "µS" or time == "us":
        mult = 1e-6 #0.000001
    elif time == "ns":
        mult = 1e-9 #0.000000001
    elif time == "ps":
        mult = 1e-12 #0.000000000001
    elif time == "as":
        mult = 1e-18 #0.000000000000000001
    elif time == "zs":
        mult = 1e-21 #0.000000000000000000001
    elif time == "ys":
        mult = 1e-24 #0.000000000000000000000001
    else:
        print(time)
        return 0
    return '%.3E' % Decimal(float(num)*float(mult))

def convert_to_sec(datafile): #converts the thalf.dat file to thalf_s.dat in seconds.
    with open(datafile) as file:
        text = file.readlines()
    text_file = open('thalf_s.dat', "w")
    for n in text:
        nl = get_list_from_row(n)
        if "(" in n:
            continue
        elif "STABLE" in n:
            text_file.write("{: >5} {: >5} {: >5} {: >5} {: >10} {: >8} {: >10}".format(*nl) + "\n")
            continue
        elif len(nl) < 7:
            continue
        if "eV" in n:
            search = nl[2] + nl[3]
            with open('nubase.mas12.txt') as file:
                nubase = file.readlines()
            for nb in nubase:
                if " " + search + " " in nb:
                    nbl = get_list_from_row(nb)
                    newnbl = [x.replace('?', '').replace('≈','').replace('<', '').replace('>','').replace('=','').replace('≥','') for x in nbl]
                    ind1 = 0
                    ind2 = 0
                    for pos in range(len(newnbl)):
                        if "s" in newnbl[pos]:
                            ind1 = pos - 1
                            ind2 = pos
                            break
                            if pos == len(newnbl) - 1:
                                ind1 = False
                    if ind2 == False:
                        continue
                    try:
                        s = make_seconds(newnbl[ind1], newnbl[ind2]) 
                        if s == "0":
                            print(n)
                        nl = nl[:6]
                        nl.append(str(s))
                        text_file.write("{: >5} {: >5} {: >5} {: >5} {: >10} {: >8} {: >10}".format(*nl) + "\n")
                    except ValueError:
                        print(newnbl)
                        print("NOPE first")
        else:
            try:
                s = make_seconds(float(nl[6]), nl[7])
            except (ValueError, IndexError):
                try:
                   s = make_seconds(float(nl[7]), nl[8])
                except (ValueError, IndexError):
                   print(nl)
                   print("NOPE second")
                   continue
            if s == 0:
                print(n)
                continue
            else:
                nl = nl[:6]
                nl.append(str(s))
                text_file.write("{: >5} {: >5} {: >5} {: >5} {: >10} {: >8} {: >10}".format(*nl) + "\n")
    text_file.close() 

def print_ratios(full, secs): #prints a new list with all the different decays and branching ratios and partial halflives. Not perfect yet.
    with open(full) as file:
        fulldata = file.readlines()
    with open(secs) as file:
        secdata = file.readlines()
    ratios_file = open('thalf_ratios.dat', "w")
    names = ["N", "Z", "A", "name", "E", "uncert", "half-life", "ε","β-","β+","α","p"]
    ratios_file.write("{: >3} {: >3} {: >3} {: >5} {: >8} {: >6} {: >10} {: >22} {: >22} {: >22} {: >22} {: >22}".format(*names) + "\n")
    for i in fulldata:
        if "STABLE" in i:
                continue
        il = get_list_from_row(i)
        decays = ["-" ,"-" ,"-" ,"-" ,"-" ]
        dcount = 0
        for k in range(len(il)):
            if "β-" == il[k]:
                try:
                    decays[1] = il[k + 1]
                    dcount += 1
                except IndexError:
                    dcount -= 1
                    continue
            elif "β+" == il[k]:
                try:
                    decays[2] = il[k + 1]	
                    dcount += 1
                except IndexError:
                    dcount -= 1
                    continue
            elif "α" == il[k]:
                try:
                    decays[3] = il[k + 1]	
                    dcount += 1
                except IndexError:
                    dcount -= 1
                    continue
            elif "p" == il[k]:
                try:
                    decays[4] = il[k + 1]
                    dcount += 1
                except IndexError:
                    dcount -= 1
                    continue
            elif "ε" == il[k]:
                try:
                    decays[0] = il[k + 1]
                    dcount += 1
                except IndexError:
                    dcount -= 1
                    continue
            nuc = il[2] + il[3]
        for sc in secdata:
            scl = get_list_from_row(sc)
        if scl[2] + scl[3] == nuc:
            s = scl[6]
            if dcount > 1:
                for d in decays:
                    try:
                        scl.append('%.8E' % Decimal(str(np.log(2)*float(s)/(float(d)/100))))
                    except ValueError:
                        scl.append(str(d))
            ratios_file.write("{: >3} {: >3} {: >3} {: >3} {: >8} {: >6} {: >10} {: >22} {: >22} {: >22} {: >22} {: >22}".format(*scl) + "\n")
        else:
            for d in decays:
                if d == "-":
                    scl.append(str(d))
                else:
                    scl.append(s)
            ratios_file.write("{: >3} {: >3} {: >3} {: >3} {: >8} {: >6} {: >10} {: >22} {: >22} {: >22} {: >22} {: >22}".format(*scl) + "\n")
            break
    ratios_file.close()

def make_comparelist(inp): #only used this to get z from names.
    with open(inp) as file:
        text = file.readlines()
    checked = ''
    compare_file = open('nametoz.dat', "w")
    for t in text:
        tl = get_list_from_row(t)
        name = tl[3]
        if name + " " in checked:
            continue
        else:
            z = tl[1]
            compare_file.write("{: >5} {: >5}".format(*[name, z]) + "\n")
            checked += name + " "
    compare_file.close()

def get_z_from_name(name): #same
    with open('nametoz.dat') as file:
        names = file.readlines()
    for n in names:
        nl = get_list_from_row(n)
        if name == nl[0]:
            return(nl[1])
    return 0

def read_nubase(inp): #this one reads the nubase2016.txt and parses it
    timeunits = "ys zs as fs ps ns us ms s m h d y ky My Gy Ty Py Ey Zy Yy" 
    with open(inp) as file:
        text = file.readlines()
    text = [x.replace('?', '').replace('≈','').replace('<', '').replace('>','').replace('=','').replace('≥','').replace('~','').replace(';', ' ') for x in text]
    #with open('thalf_ratios.dat') as file:
    #    basedata = file.readlines()
    newfile = open('nubase2016_alpha.dat', "w")
    newprint = ['N', 'A', 'Q', 'dQ', 't1/2', 'dt1/2', 'br(%)', 'dbr','S_p', 'S_d', 'Decay']
    newfile.write("{: >5} {: >5} {: >10} {: >10} {: >10} {: >11} {: >10} {: >10} {: >10} {: >10} {: >8}".format(*newprint) + "\n")
    count_decays = 0
    for t in text[1:]:
        #if '189Bi' not in t:
        #    continue
        if 'stbl' in t:
            continue
        try:
            if 'A' not in t[105:]: #"".join(tl[11:]):
                continue
        except IndexError:
            continue
        tl = get_list_from_row(t)
        if '#' in tl[3]:
            continue
        thalf = '-'
        uncert = '-'
        spin = '?'
        spin_d = '?'
        dbr = '?'
        nuc = tl[2]
        nuc = re.findall('\d+|\D+',nuc)
        A = nuc[0]
        name = nuc[1]
        Z = tl[1][:3]
        N = str(int(A) - int(Z))
        spin = get_spin(tl)
        decays = []
        several = ''
        for i in range(0, len(tl)):
            if " - " in tl[i]:
                continue
            if " " + tl[i] + " " in timeunits:
                time = tl[i - 1]
                unit = tl[i]
                try:
                    uncert = '%.3E' % Decimal(float(tl[i + 1]))
                except ValueError:
                    uncert = 0
                try:
                    thalf = make_seconds(time, unit)
                except ValueError:
                    continue
            if 'A' in tl[i]:
                if 'AD' in tl[i]:
                    continue
                test = re.split('(\d+)',tl[i])
                if 'A' != test[0] or len(test) == 1:
                    continue
                count_decays += 1
                try:
                    dbr = float(tl[i + 1])
                except IndexError:
                    dbr = '?'
                except ValueError:
                    dbr = '?'
                if len(test) > 1:
                    branch = "".join(test[1:]).replace("e-","E-0")
                    decays.append([test[0], branch, dbr])
                break 
        if thalf == '-':
            continue
        loops = get_loops(Z, A, text)
        for l in range(1, loops + 1):
            (Q, Qunc, spin_d) = get_Q_value(Z, A, tl[3], tl[4], text, l)
            if float(Q) <= 0:
                continue
            for d in decays:
                try:
                    dbr = d[2]
                except IndexError:
                    dbr = '?'
                newprint = [N, A, Q, Qunc, thalf, uncert, d[1], dbr, spin, spin_d, d[0]]
                newfile.write("{: >5} {: >5} {: >10} {: >10} {: >10} {: >11} {: >10} {: >10} {: >10} {: >10} {: >8}".format(*newprint) + "\n")
    print(count_decays)
    newfile.close()

def get_Q_value(z, a, dM, dMunc, nubase, l):
    dMHE4 = 2424.9156
    dMHE4unc = 0.0001 
    dMf = 0
    dMfunc = 0
    dMi = dM
    dMiunc = dMunc
    count = 0
    Q = 0
    spin = '?'
    uncert = '?'
    for t in nubase[1:]:
        tl = get_list_from_row(t)
        A = tl[0]
        Z = tl[1][:3]
        if int(Z) == int(z) - 2 and int(A) == int(a) - 4:
            if '#' in tl[3] or 'non-exist' in t:
                continue
            count += 1
            if count < l:
                continue
            spin = get_spin(tl)
            dMf = tl[3]
            dMfunc = tl[4]
            nucline = tl
            try:
                Q = str(round((float(dMi) - float(dMf) - float(dMHE4))/1000, 8))
            except ValueError:
                print('VALUE ERROR')
                print(tl)
            if float(Q) > 15:
                print('Q > 15')
                print(z + " " + a)
                print(t)
            uncert = str(round((float(dMHE4unc) + float(dMiunc) + float(dMfunc))/1000, 5)).replace('e', 'E')
            break
    return Q, uncert, spin

def get_loops(z, a, nubase):
    count = 0
    for t in nubase[1:]:
        tl = get_list_from_row(t)
        A = int(tl[0])
        Z = int(tl[1][:3])
        if int(z) == Z + 2 and int(a) == A + 4:
            count += 1
    return count

def get_spin(tl):
    spin = '?'
    for i in range(0, len(tl)):
        if ('+' in tl[i] or '-' in tl[i]) and i > 3 and 'e' not in tl[i] and not re.search('[A-Z]', tl[i]):
            if "/" in tl[i]:
                spin = tl[i].replace("(", "").replace(")","").replace('*','')
            else:
                if "+" in tl[i]:
                    try:
                        spin = tl[i].replace('(','').replace(')','')
                    except ValueError:
                        spin = '?'
                elif "-" in tl[i]:
                    try:
                        spin = tl[i].replace('(','').replace(')','')
                    except ValueError:
                        spin = '?'
    return spin

def compare_Q_values():
    dMHE4 = 2424.9156
    text_file = open('nubase2016_alpha_compared.dat', "w")
    with open('rct1-16.txt') as file:
        atmass = file.readlines()
    with open('nubase2016_alpha.dat') as file:
        nubase = file.readlines()
    with open('nubase2016.txt') as file:
        nubasefull = file.readlines()
    filewrite = [nubase[0].replace("\n",""), "AMA2017_Q", "DIFF", "AMA2017_dQ", "DIFF_dQ", "A nubase"]
    text_file.write("{: >109} {: >10} {: >10} {: >10} {: >10} {: >10}".format(*filewrite) + "\n")
    missingfile = open('missing_from_rct.dat', "w")
    missingfile.write(atmass[38])
    for n in atmass[40:]:
        atmQ = 0
        atmdQ = 0
        nl = get_list_from_row(n)
        found = 0
        if nl[0] == "0":
            del nl[0]    
        if nl[6] == '*' and nl[7] == '*':
            continue
        try:
            atmn = int(nl[0]) - int(nl[2])
            atma = int(nl[0])
        except ValueError:
            print(n)
            print('Exiting')
            sys.exit()
        checkpos = n.split(" " + nl[6] + " ")
        if len(checkpos) == 2:
            checkpos = checkpos[0]
            if len(checkpos) > 45:
                if '#' in nl[6] or '*' in nl[6]:
                    continue
                try:
                    atmQ = round(float(nl[6])/1000, 8)
                    atmdQ = round(float(nl[7])/1000, 8)
                except ValueError:
                    print(6)
                    print(n)
                    continue
            else:
                if '#' in nl[7] or '*' in nl[7]:
                    continue
                try:
                    atmQ = round(float(nl[7])/1000, 8)
                    atmdQ = round(float(nl[8])/1000, 8)
                except ValueError:
                    print(7)
                    print(n)
                    continue
        else:
            if '#' in nl[7] or '*' in nl[7]:
                continue
            try:
                atmQ = round(float(nl[7])/1000, 8)
                atmdQ = round(float(nl[8])/1000, 8)
            except ValueError:
                print(n)
                sys.exit()
        if nl[5] and nl[6] in '*':
            continue
        for m in nubase[1:]:
            ml = get_list_from_row(m)
            nn = int(ml[0])
            a = int(ml[1])
            Q = float(ml[2])
            dQ = float(ml[3])
            if atmn == nn and atma == a:
                diff = round(Q - atmQ,8)
                diffdQ = round(dQ - atmdQ, 8)
                filewrite = [m.replace("\n",""), str(atmQ), str(diff).replace('e','E'), str(atmdQ).replace('e','E'), str(diffdQ).replace('e','E'), 'yes']
                text_file.write("{: >109} {: >10} {: >10} {: >10} {: >10} {: >10}".format(*filewrite) + "\n")
                found = 1
                break
        if atmQ > 0 and found == 0:
            daughterspin = []
            daughtermass = []
            for nb in nubasefull[1:]:
                nbl = get_list_from_row(nb)
                nba = int(nbl[0])
                nbz = nbl[1][:3]
                nbn = int(nba) - int(nbz)
                if nbn == atmn - 2 and nba == atma - 4:
                    #daughtermass.append(nbl[3])
                    daughterspin = get_spin(nbl)
                elif nbn == atmn and nba == atma:
                    dMi = nbl[3]
                    (thlf, unc) = get_thalf(nbl)
                    parentspin = get_spin(nbl)
                    break
            #for d in range(0, len(daughterspin)):
            #    if d > 0:
            #        if  '#' in daughtermass[d] or 'non-exist' in daughtermass[d] or 'non-exist' in dMi or '#' in dMi: 
            #            continue
            #        if '#' in dMi:
            #            continue
            #        try:
            #            atmQ = str(round((float(dMi) - float(daughtermass[d]) + dMHE4)/1000, 8)) #otestat!
            #        except ValueError:
            #            print(dMi)
            #            print(daughtermass)
            #            print(d)
            #            sys.exit()
            if float(atmQ) < 0:
                continue
            filewrite = [nbn, nba, '?', '?', thlf, unc, '?', '?', parentspin, daughterspin, 'A', str(atmQ), '?', str(atmdQ).replace('e','E'), '?', 'no']
            #if filewrite == []:
            #    continue
            text_file.write("{: >5} {: >5} {: >10} {: >10} {: >10} {: >11} {: >10} {: >10} {: >10} {: >10} {: >8} {: >10} {: >10} {: >10} {: >10} {: >10}".format(*filewrite) + "\n")
            #print(atmQ)
            missingfile.write(n)
    missingfile.close()
    text_file.close()

def get_thalf(tl):
    timeunits = "ys zs as fs ps ns us ms s m h d y ky My Gy Ty Py Ey Zy Yy" 
    thalf = '?'
    uncert = '?'
    for i in range(0, len(tl)):
        if " - " in tl[i]:
            continue
        if " " + tl[i] + " " in timeunits:
            time = tl[i - 1]
            unit = tl[i]
            try:
                uncert = '%.3E' % Decimal(float(tl[i + 1]))
            except ValueError:
                uncert = 0
            try:
                thalf = make_seconds(time, unit)
                break
            except ValueError:
                continue
    return thalf, uncert

def check_missing():
    with open('missing_from_rct.dat') as file:
        missing = file.readlines()
    with open('nubase2016.txt') as file:
        nubase = file.readlines()
    with open('rct1-16.txt') as file:
        rct = file.readlines()
    with open('nubase2016_alpha.dat') as file:
        nubase_alpha = file.readlines()
    with open('nubase2016_alpha_compared.dat') as file:
        compared = file.readlines()
    misscomp = open('missing_compare.dat', "w")
    for m in missing[1:]:
        misscomp.write("PARENT\n")
        misscomp.write(m)
        daughter = ''
        ml = get_list_from_row(m)
        if ml[0] == "0":
            del ml[0]    
        try:
            mn = int(ml[0]) - int(ml[2])
            ma = int(ml[0])
        except ValueError:
            print(m)
            sys.exit()
        for n in nubase[1:]:
            nl = get_list_from_row(n)
            na = int(nl[0])
            nz = nl[1][:3]
            nn = int(na) - int(nz)
            if nn == mn - 2 and na == ma - 4:
                daughter += n
            if nn == mn and na == ma:
                misscomp.write(n)
        misscomp.write("\n")
        misscomp.write("DAUGHTER\n" + daughter + "\n")
    misscomp.close()

#print_thalf()
read_nubase('nubase2016.txt')
#convert_to_sec('thalf.dat')
#print_ratios('thalf.dat', 'thalf_s.dat')
#make_comparelist('thalf.dat')
#compare_Q_values()
#check_missing()
sys.exit()

energy_pd = _parse_options_data(energy_pre_pd)
part_file = open('Edata_state.dat', "w")
part_file.write('{}'.format(energy_pd[energy_pd['Jpar'] =='0+']))
part_file.close()
text_file = open('Edata.dat', "w")
jstates = energy_pd[energy_pd['Jpar'].str.contains("\(") == False]
text_file.write('{}'.format(jstates))
text_file.close()
full_file = open('Edata_full.dat', "w")
full_file.write('{}'.format(energy_pd))
full_file.close()
statelist = jstates.ix[: ,'Jpar'].unique()
statelist = [var for var in statelist if var]
print(statelist)
state_file = open('Edata_lowest_states.dat', "w")
for j in statelist:
	state = energy_pd[energy_pd['Jpar'] == j].iloc[0]
	state_file.write('{: >4} {: >10}'.format(*[str(state['Jpar']), str(state['Eall'])]) + "\n")
#state_file.write('{}'.format(*states))#Eall, Jpar]))
state_file.close()
