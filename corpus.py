#!python3
import string
import numpy as np
from scipy import sparse
import os

import phonetic
from phonetic import Word

class WordCorpus:
    """
    Calculate the transition probabilities for a given corpus of text and 
    use the distribution to generate options for new text.

    Attributes:

        dictionary : PhoneticDictionary to use for lookup
        corpString : Source text in string format
        size : Number of unique words in the corpus

        frequency : Number of times each word occurs
        unique_precedent_counts : # of unique words each word follows
        unique_antecedent_counts : # of unique follow words for each word

        wordSeq : Indices for each word in the corpus text
        wordList : List of unique Word objects in the corpus
        wordDict : Dictionary with wordDict[Word.stringRepr] = index of Word
          That is, we look up the index based on the text of an actual Word,
          so we can extend the corpus without duplicating Word objects
        
        sylDict : Dictionary with sylDict[syl] = a list of tuples that represent
          the (word, syl_index) coordinates of where the syllable appears in the 
          corpus

        A : Transition matrix used to sample the probability distribution
    """

    def __init__(self, dictionary):
        """ Initialize an empty corpus. """
        self.dictionary = dictionary
        self.corpString = None
        
        self.size = 0
        self.frequency = None
        self.unique_precedent_counts = None
        self.unique_antecedent_counts = None
        self.A = None

        self.wordSeq = []
        self.wordList = []
        self.wordDict = dict()
        self.sylDict = dict()
        self.unknowns = ""
        self.unknowns_indices = []

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

                    # If the word isn't in the phonetic dictionary
                    if new_word == None:

                        # Add to file of unknown words
                        with open(self.unknowns, "a") as unknowns:
                            unknowns.write(word + "\n")
                            self.unknowns_indices.append(self.size)

                    self.wordSeq.append(self.size)
                    self.wordDict[word] = self.size
                    self.wordList.append(new_word)
                    self.size += 1

        self.wordSeq = np.array(self.wordSeq)
        print("Corpus text:", len(wordstrings), "words,", self.size, "unique")

    def add_unknowns(self, logios_file):
        """
        Function to add the unknown words after using the LOGIOS tool, either
        manually or via API.

        You just have to go through and fix wordList, since it has null 
        values at the indices at the end of the line. wordDict and wordList
        are fine. It should be pretty easy, just replace the value at that
        index.

        The wordList isn't used until generate_sample, so it can just throw 
        a warning at the end of the normal initialization steps.
        """

        new_words = []
        with open(logios_file, "r") as logios_output:
            for line in logios_output:
                items = line.split()
                word_string = items[0]
                phonemes = items[1:]
                for i in range(len(phonemes)):
                    if phonetic.is_vowel(phonemes[i]):
                        phonemes[i] += "0" # default stress to 0
                new_words.append(Word(word_string.lower(), phonemes))

        for i in range(len(self.unknowns_indices)):
            self.wordList[self.unknowns_indices[i]] = new_words[i]

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
        self.frequency = A_raw.sum(axis=1).T
        self.unique_precedent_counts = np.count_nonzero(A_raw.toarray(), axis=0)
        self.unique_antecedent_counts = np.count_nonzero(A_raw.toarray(), axis=1)

        # Normalize A to get probabilities
        data = np.maximum(self.frequency, np.ones(self.size))
        d = sparse.spdiags(1.0/data, 0, self.size, self.size)
        self.A = d * A_raw

        # TODO: better to keep it sparse?
        self.A = np.asarray(self.A.todense())

    def initialize(self, text, is_filename=True, keeplines=False):
        """
        Read in the corpus and calculate the transition matrix.

        Arguments:
            text : String containing either a filename or the actual text
            is_filename : Bool telling us whether text is a filename
            keeplines : Bool telling us whether to keep line structure at 
                the cost of sometimes splitting words apart, or to keep words
                together at the cost of losing line structure
        """

        # Assign the text to self.corpString
        if is_filename:
            with open(text) as filename:
                self.corpString = filename.read()
            self.unknowns = text + "_unknowns.txt"
        else:
            self.corpString = text
            self.unknowns = "corpus_unknowns.txt"

        # Remove unknowns file if it already exists
        if os.path.exists(self.unknowns):
            os.remove(self.unknowns)

        #self.corpString = self.corpString.replace("\'","")

        # Remove newline characters
        if keeplines == False:

            # Hyphens followed by a newline should be ignored
            self.corpString = self.corpString.replace('-\n', '')
            self.corpString = self.corpString.replace('\n', ' ')

        # Remove hyphens so hyphenated words can be treated as two words
        self.corpString = self.corpString.replace('-', ' ')

        self._initializeCorpus()
        # self._initializeMatrix()

    def initializeMatrix(self):
        self._initializeMatrix()
        
    def initializeSylDict(self):
        # Can only be called after unknown words have been added
        
        # propbably not the most efficient implementation but...
        for word in self.wordList:
            for i in range(len(word.phonemes)):
                syl = word.phonemes[i]
                if syl[-1].isdigit(): # only care about vowels
                    key = syl[:-1] # strip stress indicator
                    val = (self.wordDict[word.stringRepr], i)
                    if key not in self.sylDict.keys():
                        self.sylDict[key] = [val]
                    else:
                        self.sylDict[key].append(val)
                        
    def sample_distribution(self, current, n, forward):
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

    def followability(self, word_index, forward):
        """
        Get the followability score for the given index.
        """
        if forward:
            num_options = self.unique_antecedent_counts[word_index]
        else:
            num_options = self.unique_precedent_counts[word_index]

        return num_options/(1.0 + self.frequency[word_index])
