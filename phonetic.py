#!python3
from nltk.corpus import cmudict
import numpy as np

vowels = frozenset(["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", "IY", "OW", "OY", "UH", "UW"])

def is_vowel(word):
    return word in vowels

class Word:
    """
    Store convenient phonetic and metric information for a word.

    Attributes:
        word : The string representation of the word
        length : The number of syllables in the word
        phonemes : Phoneme list for the word, e.g. table =  [T, EY1, B, AH0, L]
        rhythm : Stressed/unstressed information for the syllables
        vowelIndices : The indices in the phoneme list corresponding to the vowels
    """
    
    def __init__(self, word, phonemes):
        """
        Initialize and parse a given word with phoneme list already parsed.
        """
        self.stringRepr = word
        self.length = 0
        self.phonemes = phonemes
        self.rhythm = []
        self.vowelIndices = []

        # Go through all the phonemes
        for i in range(len(self.phonemes)):

            # If it's a vowel, store the stress and vowel index
            if self.phonemes[i].endswith(('0','1','2','3')):
                self.rhythm.append(int(self.phonemes[i][-1]))
                self.vowelIndices.append(i)

        # Make things arrays instead of lists.
        self.length = len(self.rhythm)
        self.rhythm = np.array(self.rhythm)
        self.vowelIndices = np.array(self.vowelIndices)

    def __getitem__(self, idx):
        return self.phonemes[idx]

    def __str__(self):
        """
        Get a string representation of the Word object.
        """
        out = "phonetic.Word("
        out += "\"" + self.stringRepr + "\" "
        out += " ".join(self.phonemes) + " " 
        # out += "".join(str(r) for r in self.rhythm)
        out += ")"
        return out

    def __repr__(self):
        """
        Get the internal representation of the Word object.
        """
        return self.__str__()

    def vowel_at(self, idx):
        return self.phonemes[self.vowelIndices[idx]]


class PhoneticDictionary:
    """
    Wrap around the CMU phonetic dictionary (by default, but with the option 
    to use an alternative file) to conveniently and robustly look up 
    phonetic information for English words as strings. 

    Attributes:
        filename : The filename for the CMU phonetic dictionary
        pdict : A dictionary assigning Word objects to their uppercase string
    """

    def __init__(self, file=None):

        self.filename = file
        self.pdict = None
        if file is not None:
            self.import_file(file)
        else:
            self.pdict = cmudict.dict()

    def import_file(self, filename):
        """
        Add the words in the phonetic dictionary to our dictionary.
        """
        self.filename = filename
        with open(filename, encoding="latin-1") as file:
            for line in file:
                if not line.startswith(";"):
                    tokens = line.split()
                    self.pdict[tokens[0]] = Word(tokens[0], tokens[1:])

    def lookup(self, word):
        """
        Look up a word in the dictionary and return a Word object. If you 
        run across a word you don't know, look it up using the LOGIOS tool.
        """
        word = word.lower()

        # Check if it's already in the CMU dictionary
        if word in self.pdict:
            return Word(word, self.pdict[word][0])

        # Otherwise, get a reasonable approximation for the phonetic info
        else:

            # TODO: ACTUALLY RETURN SOMETHING IF IT'S NOT IN CMU DICT
            print("\"{}\" not in dictionary".format(word))
            return None



