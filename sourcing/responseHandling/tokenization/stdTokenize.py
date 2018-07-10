import re

import tokenization as tz
import sys

#####################################
# Very strict sentence cleaning
# currently removes ALL sentences will spelling errors(!)
# Filter script, feed it text, recieve standard text.

input = sys.stdin.readlines()
sentences = [sent.rstrip() for sent in input]

sentences = [tz.prepSentence(sent) for sent in sentences]

[sys.stdout.write(sentence+'\n') for sentence in sentences]

#####################################
