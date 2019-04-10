import Levenshtein

threshold = 0.80


def methodlist(method: str):
    st = method.split(';')
    st.remove(st[len(st) - 1])
    mlist = []
    for i in range(len(st)):
        s = st[i].split(',')
        mlist.append(s)
    return mlist


def getMethodOptSimilarity(s: list, t: list):
    i, j, pair = 0, 0, 0
    lens = len(s)
    lent = len(t)
    removedIndex = []
    while i < len(s):
        while j < len(t):
            if removedIndex.__contains__(j):
                j += 1
                continue
            lineSim = Levenshtein.seqratio(s[i], t[j])
            if lineSim >= threshold:
                removedIndex.append(j)
                pair += 1
                break
            elif j + 1 == len(t):
                break
            else:
                j += 1
        i += 1
        j = 0
        if i == len(s) or len(s) == 0:
            break
    return pair * 2 / (lens + lent)

def betaMain(sourceMethod: str, targetMethod: str):
    return getMethodOptSimilarity(methodlist(sourceMethod), methodlist(targetMethod))
