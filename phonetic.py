import re
import numpy as np


class Word:
    """
    Represents a word like "table" or "dog" but with metric/syllabic information from the
    CMU phonetic dictionary
    Attributes:
        word        The string representation of the word
        syllables   A list of phonetic syllables with their stress information.
                    For example, the syllables for the word table are:
                    [T, EY1, B, AH0, L]
        rhythm      The string representation of the stress pattern of the word (gleaned
                    from its syllabic information). The rhythm for the word "table" is 
                    [10]
    """
    regex = re.compile("\d+")  # a regular expression used to search for stress pattern info

    def __init__(self, word, syllables):
        """
        Parameterized constructor
        :param word: a string that represents a word
        :param syllables: a list of syllabic information
        """
        self.word = word
        self.syllables = syllables
        self.rhythm = []
        self.parse_rhythm()

    def word(self):
        """
        :return: the internally word
        """
        return self.word

    def syllables(self):
        """
        :return: the internal syllable list  
        """
        return self.syllables

    def parse_rhythm(self):
        """
        Extracts rhythm string from syllabic data 

        TODO: store the indices where the vowels
        :return: None
        """
        for syllable in self.syllables:
            m = Word.regex.search(syllable)
            if m is not None:
                self.rhythm.append(int(m.group(0)))
        return

    def rhymes_with(self, other):
        """
        Determines if this word rhymes with another by checking to see if their
        last syllables are equal
        :param other: another word to compare to this one
        :return: True if they rhyme, otherwise False
        """
        assert type(other) == type(self)
        return self.syllables[-1] == other.syllables[-1]

    def __str__(self):
        """
        :return: a string representation of the Word object 
        """
        out = "Word: " + self.word + " "
        out += "Syllables: ["
        out += ", ".join(self.syllables) + "] "
        out += "Rhythm: "
        out += str(self.rhythm)
        return out


class Sentence:
    """
    Represents a group of Words
    Attributes:
        words       The words in the Sentence
    """

    def __init__(self):
        self.words = []

    def add(self, word):
        self.words.append(word)


class PhoneticDictionary:
    """
    A phonetic dictionary stored in memory. Phonetic dictionaries provide syllabic stress 
    information for a given word
    Attributes:
        filename    The name of the file containing the CMU phonetic dictionary
        pdict       A dictionary of words (as uppercase strings) to their corresponding Word
                    objects
    """

    def __init__(self, file=None):
        self.filename = file
        self.pdict = {}
        if file is not None:
            self.import_file(file)

    def import_file(self, filename):
        """
        Reads and parses a file into memory
        :param filename: the phonetic dictionary file
        :return: None
        """
        self.filename = filename
        with open(filename, encoding="latin-1") as file:
            for line in file:
                if not line.startswith(";"):
                    key, value = self.parse_word(line)
                    self.pdict[key] = value
        return

    def lookup(self, word: str):
        self.checkDictLoaded()
        """
        Look up a word in the dictionary and return a corresponding Word object

        TODO:
        If you run across a word you don't know, look it up using the LOGIOS tool
            
        :param word: a word to look up in the dictionary
        :return: a Word object
        """
        # assert(word.upper() in self.pdict)
        return self.pdict[word.upper()]

    def evaluate(self, s):
        self.checkDictLoaded()
        """
        Transforms a string into a Sentence of Words
        :param s: a string to parse
        :return: a Sentence containing the Words in s
        """
        sentence = Sentence()
        for word in s.split():
            sentence.add(self.lookup(word))
        return sentence

    @staticmethod
    def parse_word(line):
        """
        Parses a CMU dictionary entry (in the form of <word> <syllable list>) 
        into a Word object

        :param line: a line in the CMU phonetic dictionary
        :return: a tuple containing a word (represented by a string) and
                the Word object representing that entry
        """
        tokens = line.split()
        return tokens[0], Word(tokens[0], tokens[1:])

    def checkDictLoaded(self):
        if self.filename is None:
            raise Exception("no dictionary has been loaded")
