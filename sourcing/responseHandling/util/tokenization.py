
import re
import nltk
import enchant

import sys

PStemmer = nltk.PorterStemmer()
englishDict = enchant.Dict('en_US')

#####################################################

def prepSentence(sentence):
    sentence = re.sub(r'[^a-zA-Z ]',' ',sentence)
    sentence = re.sub(r' +',' ',sentence)
    sentence = PStemmer.stem(sentence)

    if validateSentence(sentence):
        pass
    else:
        sentence = ''

    return(sentence)

def validateSentence(sentence,tolerance=4):

    valid = len(sentence) != 0
    valid &= spellcheckSentence(sentence,tolerance)
    valid &= len(sentence.split(' ')) > 4

    return(valid)

#####################################################

def checkWord(word):
    if englishDict.check(word):
        check = True
    else:
        check = False
    return(check)

def spellcheckSentence(sentence,tolerance):
    words = [word for word in sentence.split(' ') if len(word) > 1]
    faults = [not checkWord(word) for word in words if len(word) != 0]

    if sum(faults) > tolerance:
        valid = False
    else:
        valid = True

    return(valid)

#####################################
# Very strict sentence cleaning
# currently removes ALL sentences will spelling errors(!)
# Filter script, feed it text, recieve standard text.

if __name__ == '__main__':
    input = sys.stdin.readlines()
    sentences = [sent.rstrip() for sent in input]

    sentences = [prepSentence(sent) for sent in sentences]

    [sys.stdout.write(sentence+'\n') for sentence in sentences]
