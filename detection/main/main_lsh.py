import os
import redis
import numpy as np
import csv
import time
from main.methodFilter import lineFilter
from dictfile.read_dict import get_rule_dict
from dictfile.read_dict import read_rule_file
from main.methodFilter import methodTotalLine
from main.quicksort import quick_sort
from main.transformCsv import getCloneTuple
from main.sent2vec import Word
from main.sent2vec import Sentence
from main.sent2vec import sentence_to_vec
# from main.beta_backup import betaMain
# from main.beta_lenv import betaMain
# from main.beta_lenv_simp import betaMain
from main.beta_lenv_simp import betaMain

from main.glove_test import lsh_for_ccd
from main.detectionThread import DetectionThread

import collections
import hashlib
import time


class Method:
    def __init__(self, id, key, line, statement, vector, tokens):
        self.id = id
        self.key = key
        self.line = line
        self.statement = statement
        self.vector = vector
        self.tokens = tokens


# jedis = redis.Redis()
jedis = redis.Redis(host='127.0.0.1', port=6379, db=0)
keys = jedis.keys()

data_size = len(keys)
word_list = []
embedding_size = 128

# cloneTheta = 0.02

dict_path = os.path.abspath(os.path.dirname(os.getcwd())) + '/dictfile/new/'
rule_index_path = dict_path + 'ruleindex.txt'
rule_vector_path = dict_path + 'rulevector.txt'
a_value_path = dict_path + 'fredict.txt'

rule_dict = get_rule_dict(rule_index_path, rule_vector_path)
time_start = time.time()
detect = []
print("data_size: ", data_size)


def cal_distance(vec1, vec2):
    dist = np.linalg.norm(vec1 - vec2)
    return dist


def getMethodWords(nodes):
    method_vec_list = []
    for rule_index in nodes:
        if rule_index in rule_dict.keys():
            word_list.append(rule_index)
            word = Word(rule_index, rule_dict[rule_index])
            method_vec_list.append(word)
    return method_vec_list


def getRedisMethods():
    methods = []
    for i in range(data_size):
        key = keys[i].decode()
        line = methodTotalLine(key)
        methodSeq = jedis.get(keys[i]).decode().split("ccdMethodSeparate")
        tokens = methodSeq[0]
        rulenodes = list(methodSeq[1].split(","))
        vector = []
        statement = getMethodWords(rulenodes)
        method = Method((i + 1), key, line, statement, vector, tokens)
        methods.append(method)
    return methods


def getSortedMethods():
    idindex = list()
    idDict = dict()
    sortedMethods = []
    methods = getRedisMethods()
    for i in range(len(methods)):
        idindex.append(i)
        idDict[i] = methods[i].line
    if len(methods) > 6:  
        quick_sort(idindex, idDict, 0, 6)  
    for i in range(len(methods)):
        sortedMethods.append(methods[idindex[i]])
    return sortedMethods


def get_word_counts(word_list):
    word_counts = collections.Counter(word_list)
    return word_counts


def get_word_frequency(word_text, word_counts, word_list_len):
    word_count = word_counts.get(word_text)
    if (word_count != None):
        return word_counts.get(word_text) / word_list_len
    else:
        return 1


def getWordFrequencyDict(word_list):
    word_counts = get_word_counts(word_list)
    word_list_len = len(word_list)
    rule_indexs = read_rule_file(rule_index_path)
    for word_text in rule_indexs:
        word_frequency = get_word_frequency(word_text, word_counts, word_list_len)
        # a_value = a / (a + word_frequency)
        with open(a_value_path, 'a+') as fw:
            s = str(word_text) + " " + str(word_frequency) + '\n'
            fw.write(s)


def getAvalueDict():
    # getWordFrequencyDict(word_list)
    avaluedict = {}
    for line in open(a_value_path):  
        kv = line.split(" ")
        avaluedict[kv[0]] = kv[1].replace("\n", "")
    return avaluedict


def getVectorMethods():
    methods = getSortedMethods()
    avaluedict = getAvalueDict()
    sentence_list = []
    for i in range(len(methods)):
        sentence_list.append(Sentence(methods[i].statement))
    sentence_vectors = sentence_to_vec(sentence_list, embedding_size, avaluedict)
    for i in range(len(methods)):
        methods[i].vector = sentence_vectors[i]
    return methods


def getOptDist(beta, dist):
    # if (minbeta < beta <= maxbeta):
    #     distOpt = dist / beta
    #     return distOpt
    if (beta >= maxbeta):
        distOpt = dist * (1 - beta)
        return distOpt
    else:
        return dist

def distribute_tasks(lsh_dataset:list, thread_count:int):
    data_size = len(lsh_dataset)
    min_task_count = data_size / thread_count
    remain_task_count = data_size % thread_count
    if min_task_count > 0:
        actual_thread_count = thread_count
    else:
        actual_thread_count = remain_task_count
    tasks_per_thread = list()
    partition = int(data_size / actual_thread_count)
    for i in range(actual_thread_count):
        index = int(partition * i)
        tasks_per_thread.append(lsh_dataset[index:index + partition])
    if remain_task_count > 0 and data_size >= thread_count:
        list(tasks_per_thread[len(tasks_per_thread) - 1]).extend(list(lsh_dataset[data_size-remain_task_count : data_size]))
    return tasks_per_thread

# txtfile = open(dict_path + '/vector.txt', 'a')
# txtfile.write(str(m_top.vector).replace("\n", " ").replace("]", "]\n"))
thread_count = 4
print(time.time())
def method_compare():
    methods = getVectorMethods()
    print("len method:", len(methods))
    print("start create Vector-File:")
    methodVectorDict = dict()
    methodVectorList = list()
    for i in range(len(methods)):
        mdKey = hashlib.md5(str(methods[i].vector.tolist()).encode()).hexdigest()
        if methodVectorDict.keys().__contains__(mdKey):
            methodVectorDict[mdKey] = methodVectorDict[mdKey] + "ccdFileKeySeparate" + methods[i].key
        else:
            methodVectorDict[mdKey] = str(methods[i].line) + "ccdCodeLineSeparate" + methods[i].tokens + "ccdTokenSeparate" + methods[i].key
            methodVectorList.append(methods[i].vector)

    print("len datatset:", len(methodVectorList))
    print("len dict:", len(methodVectorDict))

    lsh_dataset = np.array(methodVectorList)
    tasks_per_thread = distribute_tasks(lsh_dataset=lsh_dataset, thread_count=thread_count)

    lastIndexBefore=0
    for i in range(len(tasks_per_thread)):
        queries = tasks_per_thread[i]
        thread = DetectionThread((i+1), lsh_dataset, queries, methodVectorDict, lastIndexBefore)
        lastIndexBefore += len(queries)
        thread.start()

method_compare()
time_end = time.time()
print('time cost', time_end - time_start, 's')


