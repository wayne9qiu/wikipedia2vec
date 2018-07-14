#from cupy_utils import *
from wikipedia2vec.dictionary import Entity, Word

import numpy as np


def read(file, threshold=0, vocabulary=None, dtype='float'):
    header = file.readline().split(' ')
    count = int(header[0]) if threshold <= 0 else min(threshold, int(header[0]))
    dim = int(header[1])
    words = []
    matrix = np.empty((count, dim), dtype=dtype) if vocabulary is None else []
    for i in range(count):
        word, vec = file.readline().split(' ', 1)
        if vocabulary is None:
            words.append(word)
            matrix[i] = np.fromstring(vec, sep=' ', dtype=dtype)
        elif word in vocabulary:
            words.append(word)
            matrix.append(np.fromstring(vec, sep=' ', dtype=dtype))
    return (words, matrix) if vocabulary is None else (words, np.array(matrix, dtype=dtype))


def write(words, matrix, file):
    m = asnumpy(matrix)
    print('%d %d' % m.shape, file=file)
    for i in range(len(words)):
        print(words[i] + ' ' + ' '.join(['%.6g' % x for x in m[i]]), file=file)


def length_normalize(matrix):
    norms = np.sqrt(np.sum(matrix**2, axis=1))
    norms[norms == 0] = 1
    matrix /= norms[:, np.newaxis]


def mean_center(matrix):
    avg = np.mean(matrix, axis=0)
    matrix -= avg


def length_normalize_dimensionwise(matrix):
    norms = np.sqrt(np.sum(matrix**2, axis=0))
    norms[norms == 0] = 1
    matrix /= norms


def mean_center_embeddingwise(matrix):
    avg = np.mean(matrix, axis=1)
    matrix -= avg[:, np.newaxis]


def normalize(matrix, actions):
    for action in actions:
        if action == 'unit':
            length_normalize(matrix)
        elif action == 'center':
            mean_center(matrix)
        elif action == 'unitdim':
            length_normalize_dimensionwise(matrix)
        elif action == 'centeremb':
            mean_center_embeddingwise(matrix)

def get_emb_old(wiki2vec, n_vocab):
    items = list(wiki2vec.dictionary.words()) + list(wiki2vec.dictionary.entities())
    items = sorted(items, key=lambda item: item.count, reverse=True)
    items = items[:n_vocab]
    matrix = np.zeros(shape=(n_vocab, wiki2vec.syn0.shape[1]), dtype='float32')
    for i, item in enumerate(items):
        matrix[i] = wiki2vec.get_vector(item)

    return [item.text if isinstance(item, Word) else item.title for item in items], matrix


def get_emb(dictionary, matrix, n_vocab):
    items = list(dictionary.words()) + list(dictionary.entities())
    items = sorted(items, key=lambda item: item.count, reverse=True)
    items = items[:n_vocab]
    limited_matrix = np.zeros(shape=(n_vocab, matrix.shape[1]), dtype='float32')
    ind2ind = {}
    for i, item in enumerate(items):
        limited_matrix[i] = matrix[item.index]
        ind2ind[item.index] = i

    
    return ind2ind, limited_matrix