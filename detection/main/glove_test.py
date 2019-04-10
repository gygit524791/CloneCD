from __future__ import print_function
import numpy as np
import falconn
import timeit
import hashlib
import csv
import time
from main.transformCsv import getCloneTuple
from main.methodFilter import lineFilter
from main.beta_lenv_simp import betaMain

# threshold = 0.001

# cloneTheta = 0.025
# endTheta = 0.03
# optTheta = 0.02

cloneTheta = 0.000625
endTheta = 0.0009
optTheta = 0.00018225
minbeta = 0.60
maxbeta = 0.70

clones = list()
csvFile = open('result.csv', 'a')
writer = csv.writer(csvFile)


def getOptDist(beta, dist):
    if (beta > maxbeta):
        distOpt = dist * (1 - beta)
        return distOpt
    else:
        return dist


def lsh_for_ccd(dataset: np.array, queries:list, methoddict: dict, lastIndexBefore:int):
    number_of_tables = 10
    # queries = dataset

    params_cp = falconn.LSHConstructionParameters()
    params_cp.dimension = len(dataset[0])
    params_cp.lsh_family = falconn.LSHFamily.CrossPolytope
    params_cp.distance_function = falconn.DistanceFunction.EuclideanSquared
    params_cp.l = number_of_tables
    params_cp.num_rotations = 1
    params_cp.seed = 5721840
    params_cp.num_setup_threads = 0
    params_cp.storage_hash_table = falconn.StorageHashTable.BitPackedFlatHashTable
    falconn.compute_number_of_hash_functions(18, params_cp)

    print('Constructing the LSH table')
    t1 = timeit.default_timer()
    table = falconn.LSHIndex(params_cp)
    table.setup(dataset)
    t2 = timeit.default_timer()
    print('Done')
    print('Construction time: {}'.format(t2 - t1))

    query_object = table.construct_query_object()
    methodfilterset = set()

    currentIter = lastIndexBefore
    totalIter = len(dataset)

    for query in queries:
        neighbors = query_object.find_near_neighbors(query, threshold=endTheta)
        for neighbor in neighbors:
            queryMdKey = hashlib.md5(str(query.tolist()).encode()).hexdigest()
            neighborMdKey = hashlib.md5(str(dataset[neighbor].tolist()).encode()).hexdigest()
            # 13ccdCodeLineSeparate112443321234ccdTokenSeparate/home/xxx/xx.java,3,15ccdFileKeySeparate/home/xxx/xx.java,31,45
            left = str(methoddict[queryMdKey])
            right = str(methoddict[neighborMdKey])
            ccdLeft = left.split("ccdCodeLineSeparate")
            ccdRight = right.split("ccdCodeLineSeparate")
            methodsLeftLine = ccdLeft[0]
            methodsRightLine = ccdRight[0]
            ccdTokenLeft = ccdLeft[1].split('ccdTokenSeparate')
            ccdTokenRight = ccdRight[1].split('ccdTokenSeparate')
            methodsLeft = ccdTokenLeft[1]
            methodsRight = ccdTokenRight[1]
            methodsLeftToken = ccdTokenLeft[0]
            methodsRightToken = ccdTokenRight[0]

            if queryMdKey == neighborMdKey:
                tmpStr = methodsLeft
                if "ccdFileKeySeparate" in tmpStr:
                    tmpArr = tmpStr.split("ccdFileKeySeparate")
                    if len(tmpArr) == 2:
                        result = getCloneTuple(tmpArr[0] + "," + tmpArr[1])
                        writer.writerow(result)
                    else:
                        for i in range(0, len(tmpArr)):
                            for j in range(i + 1, len(tmpArr)):
                                result = getCloneTuple(tmpArr[i] + "," + tmpArr[j])
                                writer.writerow(result)
                continue

            if neighbor > currentIter:
                if not lineFilter(int(methodsLeftLine), int(methodsRightLine)):
                    dist = np.linalg.norm(query - dataset[neighbor])
                    dist *= dist
                    if dist <= optTheta:
                        getCloneResult(methodsLeft, methodsRight)
                    else:
                        beta = betaMain(methodsLeftToken, methodsRightToken)
                        if beta <= minbeta:
                            continue
                        dist = getOptDist(beta, dist)
                        if dist < cloneTheta:
                            getCloneResult(methodsLeft, methodsRight)
        currentIter = currentIter + 1
        # print("%d / %d \r" % (currentIter, totalIter))
    print(time.time())

def getCloneResult(methodsLeft: str, methodsRight: str):
    # Split into arrays
    methodArrLeft = []
    methodArrRight = []
    if "ccdFileKeySeparate" in methodsLeft:
        methodArrLeft = methodsLeft.split("ccdFileKeySeparate")
    else:
        methodArrLeft.append(methodsLeft)

    if "ccdFileKeySeparate" in methodsRight:
        methodArrRight = methodsRight.split("ccdFileKeySeparate")
    else:
        methodArrRight.append(methodsRight)

    for methodLeft in methodArrLeft:
        for methodRight in methodArrRight:
            result = getCloneTuple(methodLeft + "," + methodRight)
            writer.writerow(result)
