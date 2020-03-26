from config import base_dir
import os.path as path
import numpy as np
import json

def getDict():
    with open(path.join(base_dir, 'words_dataset.json')) as reader:
        return json.load(reader)


def buildRow(body_text):
    cDict = getDict()
    dictSize = len(cDict.keys())
    one_ex_vector = np.zeros(dictSize + 2)
    cwords = body_text.split()
    for word in cwords:
        if(word in cDict.keys()):
            one_ex_vector[cDict[word] - 1] = 1

    return(one_ex_vector)
