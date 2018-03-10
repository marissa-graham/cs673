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
        self.vowel_symbols = ["AA","AE","AH","AO","AW","AY","EH","ER","EY","IH",\
        "IY","OW","OY","UH","UW"] 
        self.consonant_symbols = ["B"] 

        self.num_vowels = len(vowel_symbols)
        self.num_consonants = len(consonant_symbols)
        self.vowel_dict = {self.vowel_symbols[i]:i for i in range(self.num_vowels)}
        self.consonant_dict = {self.consonant_symbols[i]:i for i in range(self.num_consonants)}

        self.vowel_weights = np.array([0.355,0.921,0.979,0.053,0.398])
        self.consonant_weights = np.array([0.933,0.0,1.0])

        self.vowel_features = np.zeros((5,self.num_vowels))
        self.consonant_features = np.zeros((3,self.num_consonants))

        self.Mh = np.array([[],[]])
        self.Mf = []
        self.Mr = []
        self.Mt = []
        self.Ms = []
        self.vowel_feature_matrices = [self.Mh, self.Mf, self.Mr, self.Mt, self.Ms]

        self.Mm = []
        self.Mp = []
        self.Mv = []
        self.consonant_feature_matrices = [self.Mm, self.Mf, self.Mr]

        self.Av = np.zeros((num_vowels,num_vowel))
        self.Ac = np.zeros((num_consonants,num_consonants))
        self.initialize_tables()

    def initialize_tables(self):
        """
        Create Mv and Mc using the hardcoded property tables (made manually) and the 
        correlation matrices for phoneme properties (colorful ones from the paper)
        """
        for i in range(self.num_vowels):
            for j in range(self.num_vowels):
                self.Av[i,j] = vowel_pair_score(i,j)

        for i in range(self.num_consonants):
            for j in range(self.num_consonants):
                self.Ac[i,j] = consonant_pair_score(i,j)

    def vowel_pair_score(i,j):
        score = 0
        for k in range(5):
            M = self.vowel_feature_matrices[k]
            score += vowel_weights[k]*M[self.vowel_features[k,i], self.vowel_features[k,j]]
        return score

    def consonant_pair_score(i,j):
        score = 0
        for k in range(3):
            M = self.consonant_feature_matrices[k]
            index1 = self.consonant_features[k,i]
            index2 = self.consonant_features[k,j]
            score += self.consonant_weights[k]*M[index1, index2]
        return score

    def consonant_sequence_score(self, onset):
        """
        Alignment function for consonant sequences with like edit distances and stuff
        """
        optimal_alignment_score = 0.5
        return optimal_alignment_score

    def rhyme_score(self, word1, word2, i, j, priority=np.array([0.013,0.355,0.014])):
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
