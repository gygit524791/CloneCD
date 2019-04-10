import numpy as np
from sklearn.decomposition import PCA
from typing import List
np.set_printoptions(suppress=True)
class Word:
    def __init__(self, text, vector):
        self.text = text
        self.vector = vector

class Sentence:
    def __init__(self, word_list):
        self.word_list = word_list

    def len(self): #-> int:
        return len(self.word_list)

def cal_distance(vec1, vec2):
    dist = np.linalg.norm(vec1 - vec2)
    return dist

def sentence_to_vec(sentence_list: List[Sentence], embedding_size: int, fredict):
    sentence_set = []
    a = 0.1
    for sentence in sentence_list:
        vs = np.zeros(embedding_size)
        sentence_length = sentence.len()
        for word in sentence.word_list:
            if(len(fredict) == 0):
                a_value = a / (a + 1)
            else:
                a_value = a / (a + np.float(fredict.get(word.text)))
            vs = np.add(vs, np.multiply(a_value, word.vector))
        vs = np.divide(vs, sentence_length)
        sentence_set.append(vs)
    pca = PCA(n_components=embedding_size)
    pca.fit(np.array(sentence_set))
    u = pca.components_[0]  
    u = np.multiply(u, np.transpose(u)) 
    if len(u) < embedding_size:
        for i in range(embedding_size - len(u)):
            u = np.append(u, 0) 
    sentence_vecs = []
    for vs in sentence_set:
        sub = np.multiply(u,vs)
        sentence_vecs.append(np.subtract(vs, sub))
    return sentence_vecs
