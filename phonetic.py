import re


class Word:

    regex = re.compile("\d+")

    def __init__(self, word, syllables):
        self.word = word
        self.syllables = syllables
        self.rhythm = ""
        self.parse_rhythm()

    def word(self):
        return self.word

    def syllables(self):
        return self.syllables

    def parse_rhythm(self):
        """
        Extracts rhythm string from syllabic data 
        :return: 
        """
        for syllable in self.syllables:
            m = Word.regex.search(syllable)
            if m is not None:
                self.rhythm += m.group(0)
        return

    def rhymes_with(self, other):
        assert type(other) == type(self)
        return self.syllables[-1] == other.syllables[-1]

    def __str__(self):
        str = "Word: " + self.word + " "
        str += "Syllables: ["
        str += ", ".join(self.syllables) + "] "
        str += "Rhythm: [" + self.rhythm + "]"
        return str

class Sentence:
    def __init__(self):
        self.words = []

    def add(self, word):
        self.words.append(word)


class PhoneticDictionary:
    def __init__(self):
        self.filename = "None"
        self.pdict = {}

    def import_file(self, filename):
        self.filename = filename
        with open(filename, encoding="latin-1") as file:
            for line in file:
                if not line.startswith(";"):
                    key, value = self.parse_word(line)
                    self.pdict[key] = value

    def lookup(self, word: str):
        # assert(word.upper() in self.pdict)
        return self.pdict[word.upper()]

    def evaluate(self, s):
        sentence = Sentence()
        for word in s.split():
            sentence.add(self.lookup(word))
        return sentence

    @staticmethod
    def parse_word(line):
        tokens = line.split()
        return tokens[0], Word(tokens[0], tokens[1:])