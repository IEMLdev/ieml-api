from ieml.dictionary import Dictionary
import numpy as np


def dword(u0, u1):
    return int(np.einsum('i,j,ij->', u0.words_vector(), u1.words_vector(),
               Dictionary(u0.dictionary_version).relations_graph.matrix))