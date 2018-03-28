#!python3
import numpy as np
import phonetic
import string
from scipy import sparse
from matplotlib import pyplot as plt

class WordCorpus:
    """
    Calculate the transition probabilities for a given corpus of text and 
    use the distribution to generate options for new text.

    Attributes:
        size (int): Number of unique words in the corpus.
        length (int): Total number of words in the corpus.

        wordSeq: NumPy array where the i-th element is the index of 
          the i-th word in the corpus text.
        wordList: List of unique Word objects in the corpus.
        wordDict: Dictionary with wordDict[Word.word] = index of Word.
          That is, we look up the index based on the text of an actual Word,
          so we can extend the corpus without duplicating Word objects.
          
        A : Transition matrix.
    """

    def __init__(self, dictionary):
        """
        Initialize an empty corpus. Dictionary is a PhoneticDictionary object.
        """
        self.dictionary = dictionary
        self.corpString = None
        self.size = 0
        self.wordSeq = []
        self.wordList = []
        self.wordDict = dict()
        self.A = None

    def _initializeCorpus(self):
        """
        Initialize wordSeq, wordList, and wordDict for a corpus given a
        list of word strings.
        """

        # Split the corpus string into words
        wordstrings = self.corpString.split()

        # Define the characters we want to strip away
        nonos = string.punctuation + '0123456789'

        # Go through all the words
        for i in range(len(wordstrings)):

            # Get punctuation free word text
            word = wordstrings[i].strip(nonos).lower()

            # Ignore an empty stripped word
            if len(word) == 0:
                pass
               
            # Add the normal words to the wordDict and wordSeq 
            else:

                # If the word is already in the corpus, only update wordSeq
                if word in self.wordDict:
                    self.wordSeq.append(self.wordDict[word])

                # Otherwise, create the word and update accordingly 
                else:
                    
                    # Look the word up in the dictionary
                    new_word = self.dictionary.lookup(word)

                    # Append to wordList 
                    self.wordList.append(new_word)

                    # Update the index and use to update wordDict and wordSeq
                    self.wordDict[word] = self.size
                    self.wordSeq.append(self.size)
                    self.size += 1

        self.wordSeq = np.array(self.wordSeq)
        print("Input text:", len(wordstrings), "words,", self.size, "unique")

    def _initializeMatrix(self):
        """
        Initialize the transition matrix as a scipy.sparse.csr_matrix.

        We use the convention that A[i,j] is the probability of word i
        being followed by word j.
        """

        # Initialize total number of each word transition compactly
        n = self.wordSeq.size
        A_raw = sparse.coo_matrix(
            (np.ones(n - 1), (self.wordSeq[:-1], self.wordSeq[1:])),
            shape=(self.size, self.size)
        ).tocsr()

        # Jot down followability stuff

        # Normalize A to get probabilities
        data = np.maximum(A_raw.sum(axis=1).T, np.ones(self.size))
        d = sparse.spdiags(1.0/data, 0, self.size, self.size)
        self.A = d * A_raw

        # TODO: better to keep it sparse?
        self.A = np.asarray(self.A.todense())

    def initialize(self, text, is_filename=True, keeplines=False):
        """
        Read in the corpus and calculate the transition matrix self.A

        Arguments:
            - text: String containing either a filename or the actual text.
            - is_filename: Bool telling us whether text is a filename.
            - keeplines: Bool telling us whether to keep line structure at 
                the cost of sometimes splitting words apart, or to keep words
                together at the cost of losing line structure.
        """

        # Assign the text to self.corpString
        if is_filename:
            with open(text) as filename:
                self.corpString = filename.read()
        else:
            self.corpString = text

        #print("Raw corpString:", self.corpString[:500])

        #self.corpString = self.corpString.replace("\'","")

        # Remove newline characters
        if keeplines == False:

            # Hyphens followed by a newline should be ignored
            self.corpString = self.corpString.replace('-\n', '')
            self.corpString = self.corpString.replace('\n', ' ')

        # Remove hyphens so hyphenated words can be treated as two words
        self.corpString = self.corpString.replace('-', ' ')

        #print("\nTidied corpString:", self.corpString[:500])

        self._initializeCorpus()
        self._initializeMatrix()

    def add_constraints(self):

        # Can we add a MaxOrder constraint here without too much trouble?
        pass

    def sample_distribution(self, current, n):
        """
        Sample the probability distribution for word 'current' n times.
        """
        #row = self.A.getrow(current)
        try:
            samples = np.random.choice(self.size, size=n, p=self.A[current,:])
        except ValueError:
            print("Probabilities do not sum to 1. Generally means a row of zeros,\
                so we simply choose randomly.")
            samples = np.random.randint(self.size, size=n)
        return np.unique(samples)