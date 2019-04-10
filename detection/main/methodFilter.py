import re

multiplier = 3

def methodTotalLine(m_str):
    strIndex = m_str[int(re.search('\(', m_str).span()[0]):]
    si = re.search('\-', strIndex).span() #(3, 4)
    startLine = strIndex[1:int(si[0])]
    endLine = strIndex[int(si[0])+1:len(strIndex)-1]
    totalLine = int(endLine) - int(startLine)
    return totalLine

def lineFilter(line1, line2):
    lineList = [line1, line2]
    lineList = sorted(lineList)
    line1 = lineList[0]
    line2 = lineList[1]
    if((line1 * multiplier) <= line2):
        return True
    else:
        return False


def methodCompareFilter(m_str1, m_str2):
    m1Line = methodTotalLine(m_str1)
    m2Line = methodTotalLine(m_str2)
    lineList = [m1Line, m2Line]
    lineList = sorted(lineList)
    line1 = lineList[0]
    line2 = lineList[1]
    if((line1 * multiplier) <= line2):
        return True
    else:
        return False