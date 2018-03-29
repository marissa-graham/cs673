#!python3
import string
import numpy as np
from scipy import sparse

import phonetic

class WordCorpus:
    """
    Calculate the transition probabilities for a given corpus of text and 
    use the distribution to generate options for new text.

    Attributes:

        dictionary : PhoneticDictionary to use for lookup. 
        corpString : Source text in string format.
        size : Number of unique words in the corpus.

        frequencies : Number of times each word occurs.
        unique_precedent_counts : # of unique words each word follows.
        unique_antecedent_counts : # of unique follow words for each word.

        wordSeq : Indices for each word in the corpus text.
        wordList : List of unique Word objects in the corpus.
        wordDict : Dictionary with wordDict[Word.stringRepr] = index of Word.
          That is, we look up the index based on the text of an actual Word,
          so we can extend the corpus without duplicating Word objects.

        A : Transition matrix used to sample the probability distribution.
    """

    def __init__(self, dictionary):
        """ Initialize an empty corpus. """
        self.dictionary = dictionary
        self.corpString = None
        
        self.size = 0
        self.frequencies = None
        self.unique_precedent_counts = None
        self.unique_antecedent_counts = None
        self.A = None

        self.wordSeq = []
        self.wordList = []
        self.wordDict = dict()

    def _initializeCorpus(self):
        """
        Initialize wordSeq, wordList, and wordDict for a corpus given a
        normal string of punctuation and space separated text.
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

        # Initialize total number of each word pair transition
        n = self.wordSeq.size
        A_raw = sparse.coo_matrix( 
            (np.ones(n-1), (self.wordSeq[:-1], self.wordSeq[1:])),
            shape=(self.size, self.size)).tocsr()

        # Keep track of followability stuff
        self.frequencies = A_raw.sum(axis=1).T
        self.unique_precedent_counts = np.count_nonzero(A_raw, axis=0)
        self.unique_antecedent_counts = np.count_nonzero(A_raw, axis=1)

        # Normalize A to get probabilities
        data = np.maximum(self.frequencies, np.ones(self.size))
        d = sparse.spdiags(1.0/data, 0, self.size, self.size)
        self.A = d * A_raw

        # TODO: better to keep it sparse?
        self.A = np.asarray(self.A.todense())

    def initialize(self, text, is_filename=True, keeplines=False):
        """
        Read in the corpus and calculate the transition matrix.

        Arguments:
            text : String containing either a filename or the actual text.
            is_filename : Bool telling us whether text is a filename.
            keeplines : Bool telling us whether to keep line structure at 
                the cost of sometimes splitting words apart, or to keep words
                together at the cost of losing line structure.
        """

        # Assign the text to self.corpString
        if is_filename:
            with open(text) as filename:
                self.corpString = filename.read()
        else:
            self.corpString = text

        #self.corpString = self.corpString.replace("\'","")

        # Remove newline characters
        if keeplines == False:

            # Hyphens followed by a newline should be ignored
            self.corpString = self.corpString.replace('-\n', '')
            self.corpString = self.corpString.replace('\n', ' ')

        # Remove hyphens so hyphenated words can be treated as two words
        self.corpString = self.corpString.replace('-', ' ')

        self._initializeCorpus()
        self._initializeMatrix()

    def sample_distribution(self, current, n, forward=True):
        """
        Sample the probability distribution for word 'current' n times.
        """

        # Try to grab some samples
        try:

            # If we are sampling forward, we sample from the rows
            if forward:
                samples = np.random.choice(self.size, size=n, p=self.A[current,:])
            
            # If we are going backwards, we sample from the columns
            else:
                samples = np.random.choice(self.size, size=n, p=self.A[current,:])

        # If it doesn't work, there are no options, so just pick random words.
        except ValueError:
            samples = np.random.randint(self.size, size=n)

        return np.unique(samples)