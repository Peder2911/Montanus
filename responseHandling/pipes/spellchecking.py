#!/usr/bin/env python
import enchant

import sys

englishDict = enchant.Dict('en_US')

def checkWord(word):
    if englishDict.check(word):
        check = True
    else:
        check = False
    return(check)

def spellCheck(sentence,tolerance):
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
    tolerance = int(sys.argv[1])
    input = sys.stdin.readlines()
    
    for line in input:
        if spellCheck(line,tolerance):
            sys.stdout.write(line)
        else:
            sys.stderr.write('Removed : %s'%(line))
