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
        - size (int): Number of unique words in the corpus.
        - length (int): Total number of words in the corpus.
        - wordSeq: NumPy array where the i-th element is the index of 
          the i-th word in the corpus text.
        - wordList: List of unique Word objects in the corpus.
        - wordDict: Dictionary with wordDict[Word.word] = index of Word.
          That is, we look up the index based on the text of an actual Word,
          so we can extend the corpus without duplicating Word objects.
        - A (csr_matrix): Transition matrix.
    """

    def __init__(self, dictionary):
        """
        Initialize an empty corpus. Dictionary is a PhoneticDictionary object.
        """
        self.dictionary = dictionary
        self.corpString = None
        self.size = 0
        self.wordSeq = None
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

        # Initialize variables before iterating through the words
        self.wordSeq = np.zeros(len(wordstrings))
        nonos = string.punctuation+'0123456789'
        
        for i in range(len(wordstrings)):

            # Get punctuation free word text
            word = wordstrings[i].strip(nonos).lower()

            # If the word is already in the corpus, only update wordSeq
            try:
                self.wordSeq[i] = self.wordDict[word]

            # Otherwise, create the word and update accordingly 
            except KeyError:

                # Look the word up in the dictionary
                new_word = self.dictionary.lookup(word)

                # Append to wordList 
                self.wordList.append(new_word)

                # Update the index and use to update wordDict and wordSeq
                self.wordDict[word] = self.size
                self.wordSeq[i] = self.size
                self.size += 1

        print("Input text:", len(wordstrings), "words,", self.size, "unique")
        #print("\nWord indices:\n", self.wordDict)
        #print("\nTransition sequence:\n", self.wordSeq)
        #print("\nTransition matrix:\n")

    def _initializeMatrix(self):
        """
        Initialize the transition matrix as a scipy.sparse.csr_matrix.

        We use the convention that A[i,j] is the probability of word i
        being followed by word j.
        """
        n = len(self.wordSeq)
        A_raw = sparse.coo_matrix(
            (np.ones(n-1),(self.wordSeq[:-1], self.wordSeq[1:])),
            shape=(self.size, self.size)
            ).tocsr()

        # TODO: NORMALIZE WITHOUT DENSIFYING THE DAMN THING
        # Normalize rows to get probabilities
        #self.A = A_raw.copy()
        #rowsums = A_raw.sum(axis=1)
        #self.A.data /= rowsums.repeat(np.diff(self.A.indptr))
        self.A = A_raw / np.maximum(A_raw.sum(axis=1),np.ones(self.size))
        #plt.imshow(self.A, cmap="Greys")
        #plt.show()

    def _extendCorpus(self, text):
        pass

    def _extendMatrix(self):
        pass

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

        #print("Raw corpString:", self.corpString)

        # Remove newline characters
        if keeplines == False:

            # Hyphens followed by a newline should be ignored
            self.corpString = self.corpString.replace('-\n','')
            self.corpString = self.corpString.replace('\n',' ')

        # Remove hyphens so hyphenated words can be treated as two words
        self.corpString = self.corpString.replace('-',' ')

        #print("\nTidied corpString:", self.corpString)

        self._initializeCorpus()
        self._initializeMatrix()

    def extend(self, text, is_filename=True):
        pass

    def add_constraints(self):
        pass

    def sample_distribution(self, current, n):
        """
        Sample the probability distribution for word 'current' n times.
        """
        self.A = np.asarray(self.A)

        samples = np.random.choice(self.size, size=n, p=self.A[current,:])
        return np.unique(samples)

    def generate_babble(self, n):
        """
        Generate n word/s of babble.
        """
        current = np.random.randint(self.size)
        #current = 0
        babble_words = [self.wordList[current].word.lower()]
        self.A = np.asarray(self.A)

        for i in range(1,n):
            current = np.random.choice(self.size, p=self.A[current,:])
            babble_words.append(self.wordList[current].word.lower())

        print("\n", " ".join(babble_words))

class StructureCorpus:
    """
    Calculate the transition probabilities for rhyme and meter in order to
    use the distribution to generate new structures.

    1) Brute force: Go through all of the words/chunks of syllables and 
       ask "does it rhyme with anything we've seen yet"
       - By the word? By the syllable? By chunks of syllables?
    2) Learning of what patterns to pay attention to
    3) Simplify to a small number of patterns
    4) Generate new patterns accordingly
    """
    pass