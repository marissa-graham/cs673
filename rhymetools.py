import nltk
import re
import itertools
import numpy as np

class RhymeEvaluator:
    """
    Necessary data structures and trappings to calculate rhyme scores
    for pairs of syllables.
    
    Hard-coded attributes:

        self.priority : Priority weights for onset, nucleus, and coda
        self.vowel_priorities: Weights for height, frontness, rounding, and tensing
        self.consonant_priorities: Weights for manner and voicing

        self.num_vowels: Number of vowel phonemes possible
        self.num_consonants: Number of consonant phonemes possible
        self.v_list: List of vowel phoneme symbols
        self.c_list: List of consonant phoneme symbols

        self.vowels: Dictionary lookup for vowel phoneme index by symbol
        self.consonants: Dict lookup for consonant phoneme index by symbol
    
    Attributes loaded from file:

        self.v_features: Phoneme features for the vowels
        self.c_features: Phoneme features for the consonants
        self.M* : Similarity matrix for a specific phoneme feature
            (Vowels: Mh, Mf, Mr, Mt; Consonants: Mm, Mv)

    Calculated attributes:

        self.Av : Pairwise rhyme scores between vowel phonemes
        self.Ac : Pairwise rhyme scores between consonant phonemes
    """

    def __init__(self):
        """
        Initialize hard-coded and read-in things, calculate phoneme
        score matrices accordingly.
        """

        # Initialize the priority weights
        self.priority = np.array([0.013, 0.355, 0.014])
        self.priority /= np.sum(self.priority)
        self.vowel_priorities = np.array([0.355, 0.921, 0.979, 0.53])
        self.consonant_priorities = np.array([0.933, 1.0])

        # Hard code the vowel and consonant phonemes 
        self.v_list = ["AA", "AE", "AH", "AO", "AW", "AY", "EH", "ER",\
                              "EY", "IH", "IY", "OW", "OY", "UH", "UW"]
        self.c_list = ["B", "CH", "D", "DH", "F", "G", "HH", "JH",\
                                  "K", "L", "M", "N", "NG", "P", "R", "S", \
                                  "SH", "T", "TH", "V", "W", "Y", "Z", "ZH"]

        # Set up the vowel and consonant lookup dictionaries
        self.num_vowels = len(self.v_list)
        self.num_consonants = len(self.c_list)
        self.vowels = {self.v_list[i]: i for i in range(self.num_vowels)}
        self.consonants = {self.c_list[i]: i for i in range(self.num_consonants)}

        # Load the features for the vowel and consonant phonemes
        self.v_features = self._loadFeatures("data/arpabet_vowels_to_ipa.txt")
        self.c_features = self._loadFeatures("data/arpabet_consonants_to_ipa.txt")

        # Load the results from the paper for each phoneme feature used
        self.Mh = np.loadtxt("data/v_height.csv", delimiter=",")
        self.Mf = np.loadtxt("data/v_frontness.csv", delimiter=",")
        self.Mr = np.loadtxt("data/v_rounding.csv", delimiter=",")
        self.Mt = np.loadtxt("data/v_tensing.csv", delimiter=",")

        self.Mm = np.loadtxt("data/c_manner.csv", delimiter=",")
        self.Mv = np.loadtxt("data/c_voicing.csv", delimiter=",")

        # Initialize and fill the pairwise vowel and consonant scores
        self.Av = np.zeros((self.num_vowels, self.num_vowels))
        self.Ac = np.zeros((self.num_consonants, self.num_consonants))
        self._computeAv()
        self._computeAc()

    def _loadFeatures(self, filename):
        """
        Get the indices for looking up vowel or consonant features in the 
        feature matrices from the paper based on the index of a certain phoneme.
        """
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

    def _computeAv(self):
        """ Initialize the pairwise vowel phoneme scores. """

        # Iterate through all pairs of vowel phonemes
        for vowel1 in self.vowel_symbols:

            # Get the index of the first vowel phoneme
            v1 = self.vowels[vowel1]

            for vowel2 in self.vowel_symbols:

                # Get the index of the second vowel phoneme
                v2 = self.vowels[vowel2]

                # Look up the feature scores in the corresponding matrices
                height = self.Mh[self.v_features[v1][0], self.v_features[v2][0]]
                frontness = self.Mf[self.v_features[v1][1], self.v_features[v2][1]]
                rounding = self.Mr[self.v_features[v1][2], self.v_features[v2][2]]
                tensing = self.Mt[self.v_features[v1][3], self.v_features[v2][3]]

                # Calculate the overall similarity score from weights in the paper
                feature_scores = np.array([height, frontness, rounding, tensing])
                self.Av[v1, v2] = np.dot(self.vowel_priorities, feature_scores)

        # Shift and normalize values to lie in [0,1]
        self.Av = (self.Av - np.min(self.Av)) / (np.max(self.Av) - np.min(self.Av))
        
        # Cheat to make sure exact matches give you a score of 1
        np.fill_diagonal(self.Av, 1.0)

    def _computeAc(self):
        """ Initialize the pairwise consonant phoneme scores. """
        
        # Iterate through all pairs of consonant phonemes
        for consonant1 in self.c_list:

            # Get the index of the first consonant phoneme
            c1 = self.consonants[c1]

            for consonant2 in self.c_list:

                # Get the index of the second consonant phoneme
                c2 = self.consonants[c2]

                # Look up the feature scores for manner and voicing
                manner = self.Mm[self.c_features[c1][0], self.c_features[c2][0]]
                voicing = self.Mv[self.c_features[c1][2], self.c_features[c2][2]]

                # Calculate the overall similarity score from weights in the paper
                feature_scores = np.array([manner, voicing])
                self.Ac[c1, c2] = np.dot(self.consonant_priorities, feature_scores)
        
        # Shift and normalize values to lie in [0,1]     
        self.Ac = (self.Ac - np.min(self.Ac)) / (np.max(self.Ac) - np.min(self.Ac))
        
        # Cheat to make sure exact matches give you a score of 1
        np.fill_diagonal(self.Ac,1.0)
        
    def _sequenceAlignmentScore(self, alignment):
        """
        Get a rhyme score for multi-phoneme consonant sequences by taking the 
        average of the rhyme scores on the diagonal.

        If the matrix is not square, we find the alignment (that is, a choice
        of columns that gives a square matrix) which gives the best result.
        """

        # Freak out if there are more rows than columns
        m, n = np.shape(alignment)
        diff = n - m
        if diff < 0:
            raise ValueError("Should have more columns than rows")

        # If they're the same shape, the alignment is just the diagonal
        if diff == 0:
            return np.diag(alignment) / np.max(np.diag(alignment))

        # If it's one-dimensional, the alignment is just the max score
        if m == 1:
            return np.max(alignment) / n
        elif n == 1:
            return np.max(alignment) / m

        best = 0
        tot = 0

        # Iterate through all feasible alignment possibilities
        for c in itertools.combinations(range(n), n - diff):

            # See how good the score is for this particular possibility
            mydiag = np.diag(alignment[:,c])
            tot = np.sum(mydiag)/np.max(mydiag)

            # Keep it if it's the best one we've seen
            if tot > best:
                best = tot

        # Normalize by the maximum dimension
        return tot / n

    def _consonantSequenceScore(self, onset1, onset2):
        """
        Alignment function for consonant sequences with like edit distances and stuff
        """

        # Return 1 if the sequences are identical
        if onset1 == onset2:
            return 1.0

        # Get the similarity score for each phoneme pair
        rows = len(onset1)
        cols = len(onset2)
        alignment = np.zeros((rows, cols))
        for i in range(rows):
            for j in range(cols):
                phoneme1 = self.consonants[onset1[i]]
                phoneme2 = self.consonants[onset2[j]]
                alignment[i,j] = self.Ac[phoneme1, phoneme2]
        
        # Call the sequence aligner on a matrix with more columns than rows
        if rows > cols:
            score = self._sequenceAlignmentScore(alignment.T)
        else:
            score = self._sequenceAlignmentScore(alignment)

        return score

    def _getOnset(self, word, nucleus, i):
        """
        Get the onset consonant phonemes for the given word.
        """

        # Start from the beginning if it's the very first vowel
        if i == 0:
            return word.phonemes[0:nucleus]

        # Otherwise, start immediately after the previous vowel and stop
        # just before the current vowel.
        else:
            return word.phonemes[word.vowelIndices[i-1]+1:nucleus]

    def _getCoda(self, word, nucleus, i):
        """
        Get the coda consonant phonemes for the given word.
        """

        # If it's the last vowel, go to the end
        if i == word.vowelIndices.size - 1:

            # If there's anything after the vowel, slice to the end
            if len(word.phonemes) > nucleus + 1:
                coda = word.phonemes[nucleus+1:]

            # Otherwise, it's just empty
            else:
                coda = []

        # Otherwise, start immediately after the current vowel and stop 
        # just before the next vowel.
        else:
            coda = word.phonemes[nucleus+1:word.vowelIndices[i+1]]

    def rhyme_score(self, word1, word2, i, j):
        """
        Calculate the rhyme score between the i-th syllable of word1 and the
        j-th syllable of word2.

        Arguments:
            word1 : the first Word object
            word2 : the second Word
            i : relevant syllable index in first word
            j : relevant syllable index in second word

        Returns: 
            rhyme_score : A value in [0,1] indicating the rhyme quality.
        """

        # Get the nucleus for each word (i.e. if i is 0, get the 1st vowel)
        nucleus1 = word1.vowelIndices[i]
        nucleus2 = word2.vowelIndices[j]

        # Get the onset consonant phonemes for each word
        onset1 = self._getOnset(word1, nucleus1, i)
        onset2 = self._getOnset(word2, nucleus2, j)

        # Get the coda consonant phonemes for each word
        coda1 = self._getCoda(word1, nucleus1, i)
        coda2 = self._getCoda(word2, nucleus2, j)

        # Get the vowel phoneme symbols with stress marker stripped
        syl1 = word1.phonemes[nucleus1][:-1]
        syl2 = word2.phonemes[nucleus2][:-1]

        # Get the matching scores for the nucleus, onset, and coda
        vowel_score = self.Av[self.vowels[syl1], self.vowels[syl2]]
        onset_score = self._consonantSequenceScore(onset1, onset2)
        coda_score = self._consonantSequenceScore(coda1, coda2)
        scores = np.array([vowel_score, onset_score, coda_score])

        # Weight the scores by priority and return the result
        return np.dot(self.priority, scores)