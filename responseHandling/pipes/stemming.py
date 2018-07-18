#!/usr/bin/env python
import nltk

import sys

PStemmer = nltk.PorterStemmer()

#####################################################

if __name__ == '__main__':
    input = sys.stdin.readlines()

    for line in input:
        words = [word.strip() for word in line.split(' ')]
        words = [PStemmer.stem(word) for word in words]
        
        outLine = ' '.join(words) + '\n'
        sys.stdout.write(outLine)

    sys.stdout.write('\n')
