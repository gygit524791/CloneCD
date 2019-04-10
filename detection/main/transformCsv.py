#methodKeys = "F:\\java_ws\\ccd\\ex\\bcb\\mt3\\6\\2591329.java(22-35),F:\\java_ws\\ccd\\ex\\bcb\\mt3\\6\\123456.java(2-10)"
def getCloneTuple(result:str):
    methodKeys = result.split(",")

    sourceKey = methodKeys[0]
    # sourceTuple = getCloneMethod(methodKeys[0])

    sourceSplit1 = sourceKey.split("-")
    sourceEndLine = sourceSplit1[1].replace(")", "")
    sourceMethod = sourceSplit1[0].split("(")[0]
    sourceSplit2 = sourceMethod.split("\\")
    sourceFile = sourceSplit2[len(sourceSplit2) - 1]
    sourcePath = sourceMethod.split(sourceFile)[0]
    sourceStartLine = sourceSplit1[0].split("(")[1]

    targetKey = methodKeys[1]
    # targetTuple = getCloneMethod(methodKeys[1])

    targetSplit1 = targetKey.split("-")
    targetEndLine = targetSplit1[1].replace(")", "")
    targetMethod = targetSplit1[0].split("(")[0]
    targetSplit2 = targetMethod.split("\\")
    targetFile = targetSplit2[len(targetSplit2) - 1]
    targetPath = targetMethod.split(targetFile)[0]
    targetStartLine = targetSplit1[0].split("(")[1]

    cloneTuple = (sourcePath, sourceFile, sourceStartLine, sourceEndLine, targetPath, targetFile, targetStartLine, targetEndLine)
    return cloneTuple

def getCloneMethod(key:str):
    Key = key[0]
    Split1 = Key.split("-")
    EndLine = Split1[1].replace(")", "")
    Method = Split1[0].split("(")[0]
    Split2 = Method.split("\\")
    File = Split2[len(Split2) - 1]
    Path = Method.split(File)[0]
    StartLine = Split1[0].split("(")[1]
    return (Path, File, StartLine, EndLine)





