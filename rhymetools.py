from nltk.corpus import cmudict
import numpy as np


# revision
# test revision

class RhymeEvaluator:
    def __init__(self):
        """

        - Dictionary to lookup integers for arpabet symbols
        - Av: vowel pair score lookup table
        - Ac: consonant pair score lookup table
        """
        self.vowel_symbols = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", \
                              "IY", "OW", "OY", "UH", "UW"]
        self.consonant_symbols = ["B", "CH", "D", "DH", "F", "G", "HH", "JH", "K", "L", "M",
                                  "N", "NG", "P", "R", "S", "SH", "T", "TH", "V", "W", "Y",
                                  "Z", "ZH"]
        self.vowel_data = self.import_arpabet("data/arpabet_vowels_to_ipa.txt")
        self.consonant_data = self.import_arpabet("data/arpabet_consonants_to_ipa.txt")

        self.num_vowels = len(self.vowel_symbols)
        self.num_consonants = len(self.consonant_symbols)
        self.vowel_dict = {self.vowel_symbols[i]: i for i in range(self.num_vowels)}
        self.consonant_dict = {self.consonant_symbols[i]: i for i in range(self.num_consonants)}

        self.vowel_weights = np.array([0.355, 0.921, 0.979, 0.053, 0.398])
        self.consonant_weights = np.array([0.933, 0.0, 1.0])

        self.vowel_features = np.zeros((5, self.num_vowels))
        self.consonant_features = np.zeros((3, self.num_consonants))

        self.Mh = np.loadtxt("data/v_height.csv", delimiter=",")
        self.Mf = np.loadtxt("data/v_frontness.csv", delimiter=",")
        self.Mr = np.loadtxt("data/v_roundness.csv", delimiter=",")
        self.Mt = np.loadtxt("data/v_tensing.csv", delimiter=",")
        self.Ms = np.loadtxt("data/v_stress.csv", delimiter=",")

        self.vowel_feature_matrices = [self.Mh, self.Mf, self.Mr, self.Mt, self.Ms]

        self.Mm = np.loadtxt("data/c_manner.csv", delimiter=",")
        self.Mp = np.loadtxt("data/c_place.csv", delimiter=",")
        self.Mv = np.loadtxt("data/c_voicing.csv", delimiter=",")

        self.consonant_feature_matrices = [self.Mm, self.Mp, self.Mv]

        self.Av = np.zeros((self.num_vowels, self.num_vowels))
        self.Ac = np.zeros((self.num_consonants, self.num_consonants))
        self.initialize_tables()
        self.initialize_arpabet_data()

    def import_arpabet(self, filename):
        import re
        attribute_data = []
        phoneme_data = {}
        capture_data = False
        with open(filename, "r") as file:
            for line in file:
                if re.match("^@attribute", line):
                    line = re.sub("['\s\n]", "", line[10:])
                    match = re.match("(.*){(.*)}")
                    attr_name = match.group(1)
                    attr_values = match.group(2).split(",")
                    data.append((attr_name, attr_values))
                elif re.match("^@data", line):
                    capture_data = True
                if capture_data:
                    line = re.sub("['\s\n]", "", line)
                    match = re.match("(.*){(.*)}")
                    phoneme = match.group(1)
                    values = match.group(2).split(",")
                    phoneme_data[phoneme] = values
        return phoneme_data


    def initialize_tables(self):
        """
        Create Mv and Mc using the hardcoded property tables (made manually) and the 
        correlation matrices for phoneme properties (colorful ones from the paper)
        """
        for i in range(self.num_vowels):
            for j in range(self.num_vowels):
                self.Av[i, j] = self.vowel_pair_score(i, j)

        for i in range(self.num_consonants):
            for j in range(self.num_consonants):
                self.Ac[i, j] = self.consonant_pair_score(i, j)

    def diff(self, a, b):
        SUB_COST = 1
        MATCH_COST = -3
        if a == b:
            return MATCH_COST
        else:
            return SUB_COST

    def align(self, w1, w2):
        IN_DEL_COST = 5
        rows = len(w1) + 1
        cols = len(w2) + 1
        alignment = [[0] * cols for i in range(rows)]
        prev = [[0] * cols for i in range(rows)]
        alignment[0][0] = 0
        prev[0][0] = -1
        for i in range(1, rows):
            alignment[i][0] = alignment[i - 1][0] + IN_DEL_COST
            prev[i][0] = 1
        for i in range(1, cols):
            alignment[0][i] = alignment[0][i - 1] + IN_DEL_COST
            prev[0][i] = 2
        for i in range(1, rows):
            for j in range(1, cols):
                top = alignment[i - 1][j] + IN_DEL_COST
                left = alignment[i][j - 1] + IN_DEL_COST
                diag = alignment[i - 1][j - 1] + self.diff(w1[i - 1], w2[j - 1])
                choice = min(top, left, diag)
                alignment[i][j] = choice
                if choice == top:
                    prev[i][j] = 1
                elif choice == left:
                    prev[i][j] = 2
                else:
                    prev[i][j] = 3
        score = alignment[rows - 1][cols - 1]
        return alignment, prev, score

    def vowel_pair_score(self, i, j):
        score = 0
        for k in range(5):
            M = self.vowel_feature_matrices[k]
            score += self.vowel_weights[k] * M[self.vowel_features[k, i], self.vowel_features[k, j]]
        return score

    def consonant_pair_score(self, i, j):
        score = 0
        for k in range(3):
            M = self.consonant_feature_matrices[k]
            index1 = self.consonant_features[k, i]
            index2 = self.consonant_features[k, j]
            score += self.consonant_weights[k] * M[index1, index2]
        return score

    def consonant_sequence_score(self, onset):
        """
        Alignment function for consonant sequences with like edit distances and stuff
        """
        optimal_alignment_score = 0.5
        return optimal_alignment_score

    def rhyme_score(self, word1, word2, i, j, priority=np.array([0.013, 0.355, 0.014])):
        """
        Calculate the rhyme score for syllables i and j of words 1 and 2, respectively.
        Args:
            word1: the first word
            word2: the second word
            i: idx of nucleus of first word
            j: idx of nucleus of second word
            priority: a numpy array [x,x,x] containing weights for onset, nucleus, and coda

        Returns: 
            rhyme_score: A value in [0,1] indicating how well the syllables rhyme.
        """

        # TODO: Get the arpabet symbols for the vowels
        index1, index2 = "IH", "IH"

        # TODO: Get the list of arpabet symbols for onset and coda
        onset1, onset2 = [], []
        coda1, coda2 = [], []

        vowel_score = self.Av[self.vowel_dict[vowel1], self.vowel_dict[vowel2]]
        onset_score = self.consonant_sequence_score(onset1, onset2)
        coda_score = self.consonant_sequence_score(coda1, coda2)

        scores = np.array([vowel_score, onset_score, coda_score])

        return np.dot(scores, priority)
