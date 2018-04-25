#!python
import string
import nltk
import numpy as np
from scipy import sparse
import os

import phonetic
from phonetic import Word, PhoneticDictionary

from rhymetools import RhymeEvaluator

def get_sample(i):
	"""
	Return one of the pre-determined template strings, for convenience.
	"""
	s0 = "I know a song that gets on everybody's nerves, everybody's nerves, everybody's nerves. Oh, I know a song that gets on everybody's nerves, and this is how it goes, oh oh oh"

	s1 = "How does a bastard, orphan, son of a whore and a scotsman, dropped in the middle of a forgotten spot in the caribbean by providence, impoverished, in squalor, grow up to be a hero and a scholar?"

	s2 = "Alexander Hamilton, my name is Alexander Hamilton"

	s3 = "row, row, row your boat, gently down the stream, merrily, merrily, merrily, merrily, life is but a dream"

	s4 = "buddy you're a boy make a big noise, playing in the street, gonna be a big man some day, you got mud on your face, you big disgrace, kicking your can all over the place"

	s5 = "Alexander Hamilton, my dawg is Alexander Hamilton. He studies trigonometry, dawg"

	s6 = "My mistress eyes' are nothing like the sun.\nCoral is far more red than her lips red.\nIf snow be white, why then her breasts are dun.\nIf hair be wires, black wires grow on her head."

	s7 = "My anaconda don't, my anaconda don't, my anaconda don't want none unless you got buns hun"

	samples = [s0, s1, s2, s3, s4, s5, s6, s7]
	return samples[i]

class VerseTemplate:
	"""
	Generate a template for scansion and rhyme requirements mimicking the 
	given input text.	
	
	Attributes:

		template : Text with the desired rhythm and rhyme pattern
		dictionary : Phonetic dictionary to use for lookup
		breakrules : Require no word breaking across original words ('word')
					  or no word breaking across phrases ('phrase')
		
		num_syllables : Number of syllables in the template
		wordList : List of Words in the source text.
		breakpoints : List of indices that a word can't cross
		stresses : List of stresses for each syllable
		
		unknowns : File to store unknown words
		unknowns_info : List of tuples containing information about unknown words
	
		occupied_syllables : boolean array of filled syllables in the template
		verse : Dictionary to store the filled template
		rhyme_matrix : Matrix with rhyme patterns to be mimicked
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

		self.unknowns_info = []
		self.unknowns = "verse_unknowns.txt"
		if os.path.exists(self.unknowns):
			os.remove(self.unknowns)

		self._getRhythm()
		if len(self.unknowns_info) > 0:
			print("Need to add", len(self.unknowns_info), "words to template word list using LOGIOS tool")
			
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
		"""

		# Pitch a fit if you haven't got the file you want?

		new_words = []
		with open(logios_file, "r") as logios_output:
			for line in logios_output:
				items = line.split()
				word = items[0]
				syllables = items[1:]
				for i in range(len(syllables)):
					if phonetic.is_vowel(syllables[i]):
						syllables[i] += "0" # default stress of zero
				new_words.append(Word(word.lower(), syllables))

		counter = 0
		for i in range(len(self.wordList)):
			if self.wordList[i] == None:
				self.wordList[i] = new_words[counter]
				stress_idx = self.unknowns_info[counter][2]
				self.stresses[stress_idx:stress_idx] = self.wordList[i].rhythm
				counter += 1

		print("Unknown words successfully added")
	
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
					info = [wordstring, num_words, len(self.stresses)]
					self.unknowns_info.append(info)
					with open(self.unknowns, "a") as unknowns:
						unknowns.write(wordstring + "\n")

				else:
					self.stresses.extend(word.rhythm)

				self.wordList.append(word)
				num_words += 1

			# Add any breakpoints associated with the word 

			if self.breakrules == "word":
				self.breakpoints.append(len(self.stresses)-1)

			elif self.breakrules == "phrase":
				if wordstrings[i].endswith(self.phraseBreakpoints):
					self.breakpoints.append(len(self.stresses)-1)

	def get_rhyme(self, verbose=False):
		"""
		Go through a local-ish window of the syllables and check where the
		rhyme patterns are.

		It's not an internal function because you have to have the unknowns
		fixed and we might need to do that manually. If we can get that to
		be automatic, it can be internal again and we can call add_unknowns
		in here.

		Here is how syllable_indices and matrix_indices work:
			- If you've got word i and syllable j and you want to know what
			  index in the matrix that is, you get syllable_indices[i] + j
			- If you've got index k in the matrix and you want to know what
			  word/syllable that is, you get the k-th row of matrix_indices.
			  So matrix_indices[k,:] = (i,j) 

		Ex) "Mary had a little lamb" has 5 words and 7 syllables, with
			syllable_indices = [0,2,3,4,6]
			matrix_indices = [(0,0),(0,1),(1,0),(2,0),(3,0),(3,1),(4,0)]
		"""

		# Set up data structures to convert between syllable and word indices

		self.stresses = np.array(self.stresses)
		self.occupied_syllables = np.zeros_like(self.stresses)

		syllables = []
		self.num_syllables = 0
		for i in range(len(self.wordList)):

			self.syllable_indices.append(self.num_syllables)
			self.num_syllables += self.wordList[i].length
			
			for j in range(self.wordList[i].length):
				self.matrix_indices.append(np.array([i,j]))
				syllables.append(self.wordList[i][j])

		self.syllable_indices = np.array(self.syllable_indices)
		self.matrix_indices = np.array(self.matrix_indices)
		self.rhyme_matrix = np.zeros((self.num_syllables, self.num_syllables))

		# Fill the matrix within like a 30-syllable window

		bandwidth = 30
		rm = RhymeEvaluator()

		for i in range(self.num_syllables):

			word1 = self.wordList[self.matrix_indices[i][0]]
			syl1_index = self.matrix_indices[i][1]

			for j in range(i, min(i + bandwidth, self.num_syllables)):
				
				word2 = self.wordList[self.matrix_indices[j][0]]
				syl2_index = self.matrix_indices[j][1]

				self.rhyme_matrix[i,j] = rm.rhyme_score(word1, word2, syl1_index, syl2_index)

		# Discard all but the highest rhyme matches, such that approximately 
		# 10% of the syllables in the template are part of a matched rhyme 

		curr_nonzeros = np.nonzero(self.rhyme_matrix)[0]
		percentile = 100*(1 - 0.1*self.num_syllables/curr_nonzeros.size)
		cutoff = np.nanpercentile(self.rhyme_matrix[self.rhyme_matrix>0], percentile)
		
		self.rhyme_matrix[np.where(self.rhyme_matrix < cutoff)] = 0
		nonzeros = np.nonzero(self.rhyme_matrix)

		# Print results, if desired
		if verbose:

			print("\nTemplate length: ", self.num_syllables, "syllables,", 
				len(self.wordList), "words")

			print("\nTemplate:\n"+self.template)
			print("\nStress pattern:\n"+self.join_template())
			print("\nDesired number of match pairs:", np.around(0.1*self.num_syllables))
			print("\nNumber of nonzero indices:", curr_nonzeros.size)
			print("\nPercentile for cutoff:", np.around(percentile))
			print("Cutoff score: ", cutoff)
			print("\nPairs to match ("+str(nonzeros[0].size)+"):")

			for k in range(nonzeros[0].size):

				i, j = nonzeros[0][k], nonzeros[1][k]
				word1, i1 = self.matrix_indices[i,:]
				word2, j1 = self.matrix_indices[j,:]
				match = np.around(100*self.rhyme_matrix[i,j],1)

				print(" ", match, "% match: syllable", i1+1, "of", 
					self.wordList[word1].stringRepr, "+ syllable", j1+1, "of", 
					self.wordList[word2].stringRepr, "\n\t", i, ",", j)
		
	def add_word(self, word, fill_index, L=None):
		"""
		Put the given word into the verse template at location start_ind, and
		have it take up L syllables of the stress pattern. Keep track of the
		fitness score profile so we can potentially backtrack later.
		"""
		if L is None:
			L = word.length

		self.occupied_syllables[fill_index:fill_index+L] = 1
		self.verse[fill_index] = (word, L)

	def join_template(self, verbose=False, a=0, b='end'):
		"""
		Join the filled template into a single result string. Use
		"""
		if b == 'end':
			b = self.num_syllables

		result = ""
		for i in range(a,b):

			if self.occupied_syllables[i]:
				try:
					result += self.verse[i][0].stringRepr
					if i + self.verse[i][0].length - 1 in set(self.breakpoints):
						result += ", "
					else:
						result += " "
				except KeyError:
					pass
			else:
				if self.stresses[i] > 0:
					result += " #"
				else:
					result += " /"

				if i in set(self.breakpoints):
					result += ", "
				else:
					result += " "

		if verbose:
			print(self.result)

		return result