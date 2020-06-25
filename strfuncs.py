def glfr(text):
    while "  " in text:
        text = text.replace("  ", " ")
    text = text.replace("\n", "").strip().split(" ")
    return text

def rmse(predictions, targets):
    return np.sqrt(((predictions - targets) ** 2).mean())

def find_nth(haystack, needle, n):
        start = haystack.find(needle)
        while start >= 0 and n > 1:
                start = haystack.find(needle, start + len(needle))
                n -= 1
        return int(start)

