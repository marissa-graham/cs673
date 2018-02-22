#!python3
import numpy as np
import phonetic
from scipy import sparse

class WordCorpus:
	"""
	Calculate the transition probabilities for a given corpus of text and 
	use the distribution to generate options for new text.

	Attributes:
		- size (int): Number of unique words in the corpus.
		- wordSequence: NumPy array where the i-th element is the index of 
		  the i-th word in the corpus text.
		- wordList: List of unique Word objects in the corpus.
		- wordDict: Dictionary with wordDict[Word.word] = index of Word.
		  That is, we look up the index based on the text of an actual Word,
		  so we can extend the corpus without duplicating Word objects.
		- A (csr_matrix): Transition matrix.
	"""

	def __init__(self):
		"""
		Initialize an empty corpus.
		"""
		pass

	def _readStringCorpus(self, text):
		"""
		Read in a corpus from a plaintext string.

		Arguments:
			text (str): A plaintext string.

		Returns:
			words: A list of strings with the corpus words.
		"""
		pass

	def _readFileCorpus(self, filename):
		"""
		Read in a corpus from a given filename, either .csv or standard text
		delimiters, depending on how easy it is to accomodate both.

		Arguments:
			filename (str): The name of the file containing the corpus.

		Returns:
			words: A list of strings with the corpus words.
		"""
		pass

	def _initializeCorpus(self, words):
		"""
		Initialize wordSequence, wordList, and wordDict for a corpus given a
		list of word strings. Updates class attributes in place.

		Arguments:
			words: A list of strings with the corpus words.
		"""
		pass

	def _initializeMatrix(self):
		"""
		Initialize the transition matrix as a scipy.sparse.csr_matrix.

		Arguments
		"""
		pass

	def _extendCorpus(self, text):

		pass

	def _extendMatrix(self):
		pass

	def initialize(self, text):
		"""
		Read in the corpus and initialize the transition matrix.
		"""
		pass

	def extend(self, text):
		"""
		If the 
		"""
		pass

	def add_constraints(self):
		"""
		"""
		pass

class Syllable:
	"""
	Does this need to go here or in phonetic? Yes
	
	Four pieces (all ARPABET symbols)
	- Beginning consonant list
	- Vowel sound
	- Ending consonant list
	- Stress

	rhyme ending
		a syllable has to have a vowel sound in the middle, and can optionally
		begin or end in 
	"""
	pass

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