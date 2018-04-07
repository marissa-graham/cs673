#!python3
import string
import nltk
import numpy as np
from scipy import sparse

import phonetic

from rhymetools import RhymeEvaluator

def get_sample(i):
	"""
	Return one of the pre-determined template strings, for convenience.
	"""
	s0 = "I know a song that gets on everybody's nerves, everybody's \
	nerves, everybody's nerves. Oh, I know a song that gets on everybody's \
	nerves, and this is how it goes, oh oh oh"

	s1 = "How does a bastard, orphan, son of a whore and a scotsman, dropped \
	in the middle of a forgotten spot in the caribbean in providence \
	impoverished in squalor, grow up to be a hero and a scholar?"

	s2 = "Alexander Hamilton, my name is Alexander Hamilton"

	s3 = "row, row, row your boat, gently down the stream, merrily, merrily, \
	merrily, merrily, life is but a dream"

	s4 = "buddy you're a boy make a big noise, playing in the street, \
	gonna be a big man some day, you got mud on your face, you big disgrace, \
	kicking your can all over the place, singing, we will, we will, rock you, \
	we will, we will, rock you"

	samples = [s0, s1, s2, s3, s4]
	return samples[i]

class VerseTemplate:
	"""
	Generate a template for scansion and rhyme requirements mimicking the 
	given input text.	
	
	Attributes:

		template_string : Text with the desired rhythm and rhyme pattern
		dictionary : Phonetic dictionary to use for lookup
		breakrules : Require no word breaking across original words ('word')
					  or no word breaking across phrases ('phrase')

		wordList : List of Words in the source text.
		breakpoints : List of indices that a word can't cross
		stresses : List of stresses for each syllable
		verse : Dictionary to store the filled template
		rhymes : Matrix with rhyme patterns to be mimicked
	"""

	def __init__(self, template_string, dictionary, breakrules="word"):
		""" 
		Initialize all the data structures and variables. 
		"""

		self.template = template_string
		self.dictionary = dictionary
		self.breakrules = breakrules

		self.phraseBreakpoints = ('!', ')', ',', '--', '.', ':', ';', '?')
		self.nonos = string.punctuation + '0123456789'

		self.wordList = []
		self.breakpoints = []
		self.stresses = []
		self.syllable_indices = []
		self.matrix_indices = []
		self.verse = dict()

		self._getRhythm()

		self.unknowns = template_string[:10].replace(" ", "_") + "_unknowns.txt"

	def _getRhythm(self):
		"""
		Extract the meter pattern and desired breaks from a given string.
		"""

		# Go through all the words in the template text
		wordstrings = self.template.split()

		num_words = 0
		for i in range(len(wordstrings)):

			# Add the word's rhythm to the template
			wordstring = wordstrings[i].strip(self.nonos).lower()

			if len(wordstring) == 0:
				pass

			else:
				word = self.dictionary.lookup(wordstring)

				if word == None:
					with open(self.unknowns, "a") as unknowns:
						line = word + " " + num_words + " " + len(self.stresses)
						unknowns.write(line)

				else:
					self.stresses.extend(word.rhythm)

				self.wordList.append(word)
				num_words += 1

			# Add any breakpoints associated with the word 
			if self.breakrules == "word":
				self.breakpoints.append(len(self.stresses))

			elif self.breakrules == "phrase":
				if wordstrings[i].endswith(self.phraseBreakpoints):
					self.breakpoints.append(len(self.stresses))

	def get_rhyme(self):
		"""
		Go through a local-ish window of the syllables and check where the
		rhyme patterns are.

		It's not an internal function because you have to have the unknowns
		fixed and we might need to do that manually. If we can get that to
		be automatic, it can be internal again and we can call add_unknowns
		in here.

		Here is how syllable_indices and matrix_indices are going to work:
			- If you've got word i and syllable j and you want to know what
			  index in the matrix that is, you get syllable_indices[i] + j
			- If you've got index k in the matrix and you want to know what
			  word/syllable that is, you get the k-th row of matrix_indices.
			  So matrix_indices[k,:] = (i,j) (that's a numpy array, not a 
			  tuple, it's just nicer-looking as a tuple).

		So if you've got the string "Mary had a little lamb", we have 5 words
		and 7 syllables, with
			syllable_indices = [0,2,3,4,6]
			matrix_indices = [(0,0),(0,1),(1,0),(2,0),(3,0),(3,1),(4,0)]*
				*but it's a 2d array with the columns, this is just prettier
		"""


		"""
		from nltk.tag import pos_tag

		sentence = "Michael Jackson likes to eat at McDonalds"
		tagged_sent = pos_tag(sentence.split())
		# [('Michael', 'NNP'), ('Jackson', 'NNP'), ('likes', 'VBZ'), ('to', 'TO'), ('eat', 'VB'), ('at', 'IN'), ('McDonalds', 'NNP')]

		propernouns = [word for word, pos in tagged_sent if pos == 'NNP']
		# ['Michael','Jackson', 'McDonalds']
		"""

		# MAKE SURE YOU'VE ALREADY ADDED THE UNKNOWNS

		# Fill out syllable_indices and matrix_indices
		# TEST THIS PLEASE
		num_syllables = 0
		syllables = []
		for i in range(len(self.wordList)):

			self.syllable_indices.append(num_syllables)
			num_syllables += self.wordList[i].length

			for j in range(self.wordList[i].length):
				self.matrix_indices.append(np.array([i,j]))
				syllables.append(self.wordList[i][j])

		self.syllable_indices = np.array(self.syllable_indices)
		self.matrix_indices = np.array(self.matrix_indices).T

		rhyme_matrix = np.zeros((num_syllables, num_syllables))

		bandwidth = 30
		rm = RhymeEvaluator()
		for i in range(num_syllables):
			for j in range(i, min(i + bandwidth, num_syllables)):
				word1 = self.wordList[self.matrix_indices[i][0]]
				syl1_index = self.matrix_indices[i][1]
				word2 = self.wordList[self.matrix_indices[j][0]]
				syl2_index = self.matrix_indices[j][1]
				rhyme_matrix[i,j] = rm.rhyme_score(word1, word2, syl1_index, syl2_index)

		rhyme_matrix[np.where(rhyme_matrix == 1)] = 0
		rhyme_matrix[np.where(rhyme_matrix < .65)] = 0




		# Fill the matrix within like a 30-syllable window

		# Ignore the 1s (ignore = zero out)

		# Ignore the 1-syllable prepositions, articles, and pronouns

		# Zero out everything except the top x% of values

		""" Look at real data to see about what percent of syllables fit a 
		noticeable rhyme pattern, then decide what x is accordingly. Probably
		somewhere between 1% and 5%, I think."""
		pass

	def add_unknowns(self, logios_file):
		"""
		Function to add the unknown words after using the LOGIOS tool, either
        manually or via API.
        
        It'll be harder here than in corpus.py because you've got the stress 
        pattern thing. This is what you need to update for each word:
        	(1) self.wordList : This one will be exactly the same as in 
        			corpus.py. Just replace the null values at the indices
        			of the unknown words, which are in the file so it's easy.
        	(2) self.stresses : The value of self.stresses at which you need
        			to insert the rhythm pattern is in the file (test this). 
        			This stackexchange question should be useful:
        			https://stackoverflow.com/questions/39541370/how-to-insert-multiple-elements-into-a-list
        			but play with baby test cases in a jupyter notebook or
        			something to make sure it's working as expected.

		"""
		new_words = []
		with open(self.unknowns, "r") as unknowns:
			for line in unknowns:
				items = line.split()
				word = items[0]
				syllables = items[1:]
				new_words.append(Word(word, syllables))

		counter = 0
		for i in range(len(self.wordList)):
			if self.wordList[i] == None:
				self.wordList[i] = new_words[counter]
				counter += 1
			self.stresses[i:i] = self.wordList[i].stresses

		# Pitch a fit if you haven't got the file you want?
		pass

	def add_word(self, word, fill_index, L, scores, forward):
		"""
		Put the given word into the verse template at location start_ind, and
		have it take up L syllables of the stress pattern. Keep track of the
		fitness score profile so we can potentially backtrack later.
		"""

		# Check for overlap and freak out accordingly

		# Separate cases for going forwards and backwards

		self.verse[start_ind] = (word, L, scores)

	def remove_word(self, word, start_ind):
		"""
		Delete the word at start_ind, if it exists.
		"""
		pass

	def join_template(self):
		"""
		Join the filled template into a single result string.
		"""
		pass