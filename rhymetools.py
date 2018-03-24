from nltk.corpus import cmudict
import numpy as np
import re
import itertools


class RhymeEvaluator:
    def __init__(self):
        """

        - Dictionary to lookup integers for arpabet symbols
        - Av: vowel pair score lookup table
        - Ac: consonant pair score lookup table
        """
        self.priority = np.array([0.013, 0.355, 0.014])
        self.priority /= np.sum(self.priority)

        self.vowel_symbols = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER", "EY", "IH", \
                              "IY", "OW", "OY", "UH", "UW"]
        self.consonant_symbols = ["B", "CH", "D", "DH", "F", "G", "HH", "JH", "K", "L", "M",
                                  "N", "NG", "P", "R", "S", "SH", "T", "TH", "V", "W", "Y",
                                  "Z", "ZH"]

        self.num_vowels = len(self.vowel_symbols)
        self.num_consonants = len(self.consonant_symbols)
        self.vowel_dict = {self.vowel_symbols[i]: i for i in range(self.num_vowels)}
        self.consonant_dict = {self.consonant_symbols[i]: i for i in range(self.num_consonants)}

        self.vowel_weights = np.loadtxt("data/vowel_weights.csv", delimiter=",")
        self.consonant_weights = np.loadtxt("data/consonant_weights.csv", delimiter=",")

        self.vowel_features = self.get_features_from_file("data/arpabet_vowels_to_ipa.txt")
        self.consonant_features = self.get_features_from_file("data/arpabet_consonants_to_ipa.txt")

        self.Mh = np.loadtxt("data/v_height.csv", delimiter=",")
        self.Mf = np.loadtxt("data/v_frontness.csv", delimiter=",")
        self.Mr = np.loadtxt("data/v_rounding.csv", delimiter=",")
        self.Mt = np.loadtxt("data/v_tensing.csv", delimiter=",")
        self.Ms = np.loadtxt("data/v_stress.csv", delimiter=",")

        #self.vowel_feature_matrices = [self.Mh, self.Mf, self.Mr, self.Mt, self.Ms]

        self.Mm = np.loadtxt("data/c_manner.csv", delimiter=",")
        self.Mp = np.loadtxt("data/c_place.csv", delimiter=",")
        self.Mv = np.loadtxt("data/c_voicing.csv", delimiter=",")

        self.consonant_feature_matrices = [self.Mm, self.Mp, self.Mv]

        self.compute_Av_values()
        self.compute_Ac_values()

    def compute_Av_values(self):
        self.Av = np.zeros((self.num_vowels, self.num_vowels))

        for vowel1 in self.vowel_symbols:
            v1_idx = self.vowel_dict[vowel1]
            for vowel2 in self.vowel_symbols:
                v2_idx = self.vowel_dict[vowel2]
                height_score = self.Mh[self.vowel_features[v1_idx][0], self.vowel_features[v2_idx][0]]
                frontness_score = self.Mf[self.vowel_features[v1_idx][1], self.vowel_features[v2_idx][1]]
                rounding_score = self.Mr[self.vowel_features[v1_idx][2], self.vowel_features[v2_idx][2]]
                tensing_score = self.Mt[self.vowel_features[v1_idx][3], self.vowel_features[v2_idx][3]]
                # stress_score = self.Ms[self.vowel_features[v1_idx], self.vowel_features[v2_idx]]
                # self.Av[v1_idx, v2_idx] = sum((height_score, frontness_score, rounding_score, tensing_score))

                self.Av[v1_idx, v2_idx] = .355 * frontness_score + \
                                            .921 * height_score + \
                                            .979 * rounding_score + \
                                            .053 * tensing_score

        self.Av = (self.Av - np.min(self.Av)) / (np.max(self.Av) - np.min(self.Av))
        np.fill_diagonal(self.Av, 1.0)
        # self.Av /= (.355 + .921 + .979 + .053)
        print(np.diag(self.Av))

    def compute_Ac_values(self):
        self.Ac = np.zeros((self.num_consonants, self.num_consonants))

        for c1 in self.consonant_symbols:

            c1_idx = self.consonant_dict[c1]

            for c2 in self.consonant_symbols:

                c2_idx = self.consonant_dict[c2]
                manner_score = self.Mm[self.consonant_features[c1_idx][0], self.consonant_features[c2_idx][0]]
                # place_score = self.Mp[self.consonant_features[c1_idx][1], self.consonant_features[c2_idx][1]]
                voicing_score = self.Mm[self.consonant_features[c1_idx][2], self.consonant_features[c2_idx][2]]

                self.Ac[c1_idx, c2_idx] = 0.933 * manner_score + voicing_score
                # self.Ac[c1_idx, c2_idx] = sum((manner_score, place_score, voicing_score))
        self.Ac = (self.Ac - np.min(self.Ac)) / (np.max(self.Ac) - np.min(self.Ac))
        np.fill_diagonal(self.Ac,1.0)
        # self.Ac /= 1.933
        print(np.diag(self.Ac))

    def get_features_from_file(self, filename):
        attribute_data = []
        phoneme_data = []
        capture_data = False
        enumerated_features = []
        with open(filename, "r") as file:
            for line in file:
                if re.match("^@attribute", line):
                    line = re.sub("['\s\n]", "", line[10:])
                    match = re.match("(.*){(.*)}", line)
                    attr_name = match.group(1)
                    attr_values = match.group(2).split(",")
                    attribute_data.append((attr_name, attr_values))
                elif re.match("^@data", line):
                    enumerated_features = [{k: v for v, k in enumerate(attr[1])} for attr in attribute_data]
                    capture_data = True
                    continue
                if capture_data:
                    line = re.sub("['\s\n]", "", line)
                    match = re.match("(.*){(.*)}", line)
                    phoneme = match.group(1)
                    values = match.group(2).split(",")

                    for i in range(len(values)):
                        try:
                            assert values[i] in attribute_data[i][1]
                        except AssertionError:
                            print("Error parsing '{}'".format(values[i]))
                            print("\tPossible options: {}".format(attribute_data[i][1]))

                    enumerated_values = [enumerated_features[i][values[i]] for i in range(len(values))]
                    phoneme_data.append(enumerated_values)
        return np.array(phoneme_data)

    def similarity_score(self, phoneme_1, phoneme_2):
        phoneme_1_idx = self.consonant_dict[phoneme_1]
        phoneme_2_idx = self.consonant_dict[phoneme_2]
        return self.Ac[phoneme_1_idx, phoneme_2_idx]

    def seq_align(self, alignment):

        m, n = np.shape(alignment)
        diff = n - m
        if diff < 0:
            raise ValueError("Should have more columns than rows")

        if diff == 0:
            return np.diag(alignment) / np.max(np.diag(alignment))
        if m == 1:
            return np.max(alignment) / n
        elif n == 1:
            return np.max(alignment) / m

        best = 0
        tot = 0
        for c in itertools.combinations(range(n), n - diff):
            mydiag = np.diag(alignment[:,c])
            tot = np.sum(mydiag)/np.max(mydiag)
            if tot > best:
                best = tot
        return tot / n

    def consonant_sequence_score(self, onset1, onset2):
        """
        Alignment function for consonant sequences with like edit distances and stuff
        """
        # create matrix out of onset1 and onset2
        # get the similarity score for every cell
        # get the largest cell in each row or column (whichever dimension is shorter)
        # sum those together and normalize by the bigger direction

        if onset1 == onset2:
            return 1.0
        rows = len(onset1)
        cols = len(onset2)
        alignment = np.zeros((rows, cols))
        for i in range(rows):
            for j in range(cols):
                alignment[i,j] = self.similarity_score(onset1[i],onset2[j])
        if rows > cols:
            score = self.seq_align(alignment.T)
        else:
            score = self.seq_align(alignment)
        return score

    def rhyme_score(self, word1, word2, i, j):
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

        # get the ith and jth nuclei from both words
        # aka if i is 0, that means get the first vowel
        nucleus1, nucleus2 = word1.stress_indices[i], word2.stress_indices[j]

        if i == 0:
            onset1 = word1.syllables[0:nucleus1]
        else:
            onset1 = word1.syllables[word1.stress_indices[i-1]+1:nucleus1]

        if i == word1.stress_indices.size - 1:
            if len(word1.syllables) > nucleus1 + 1:
                coda1 = word1.syllables[nucleus1+1:]
            else:
                coda1 = []
        else:
            coda1 = word1.syllables[nucleus1+1:word1.stress_indices[i+1]]

        # word 2
        if j == 0:
            onset2 = word2.syllables[0:nucleus2]
        else:
            onset2 = word2.syllables[word2.stress_indices[j - 1] + 1:nucleus2]

        if j == word2.stress_indices.size - 1:
            if len(word2.syllables) > nucleus2 + 1:
                coda2 = word2.syllables[nucleus2 + 1:]
            else:
                coda2 = []
        else:
            coda2 = word2.syllables[nucleus2 + 1:word2.stress_indices[j + 1]]

        syl1 = word1.syllables[nucleus1][:-1] # strip stress marker
        syl2 = word2.syllables[nucleus2][:-1]

        vowel_score = self.Av[self.vowel_dict[syl1], self.vowel_dict[syl2]]
        onset_score = self.consonant_sequence_score(onset1, onset2)
        coda_score = self.consonant_sequence_score(coda1, coda2)

        scores = np.array([vowel_score, onset_score, coda_score])
        print(np.sum(self.priority))
        return np.dot(scores, self.priority)