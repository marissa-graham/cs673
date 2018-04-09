#!python3
import itertools
import nltk
import re
import string
import numpy as np
from scipy import sparse

import phonetic
import corpus
import rhymetools
import verse
import generate_sample

"""
Just an outline for all the stuff you need to have, know, call, and do to run
a full test case.
"""

# Initialize phonetic dictionary

dictionary = phonetic.PhoneticDictionary()

# Instatiate the corpus object with that phonetic dictionary

verse_template = verse.VerseTemplate(verse.get_sample(5), dictionary, breakrules="phrase")
verse_template.add_unknowns("logios_output/g2p.txt")
verse_template.get_rhyme()

# Call the initialize() method of the corpus

# If there's stuff in the unknowns file, go to LOGIOS tool and get the phonetic information file

corp = corpus.WordCorpus(dictionary)
corp.initialize(verse.get_sample(5), is_filename=False)
print()
print(corp.wordList)
print(corp.wordSeq)
corp.add_unknowns("logios_output/g2p.txt")
print()
print(corp.wordList)
corp.initializeMatrix()

# Make a verse template
template = verse.VerseTemplate(verse.get_sample(4), dictionary, breakrules='phrase')
template.get_rhyme()