#!/usr/bin/env python
import sys

#####################################################

if __name__ == '__main__':
    input = sys.stdin.readlines()

    sentences = list(set(input))

    for sent in sentences:
        sys.stdout.write(sent)
