import phonetic
import corpus
import string
import nltk
import numpy as np
from scipy import sparse
from matplotlib import pyplot as plt

def get_sample(i):
	s0 = "I know a song that gets on everybody's nerves, everybody's \
	nerves, everybody's nerves. Oh, I know a song that gets on everybody's nerves, \
	and this is how it goes, oh oh oh"

	s1 = "How does a bastard, orphan, son of a whore and a scotsman, dropped \
	in the middle of a forgotten spot in the caribbean in providence impoverished \
	in squalor, grow up to be a hero and a scholar?"

	s2 = "Alexander Hamilton, my name is Alexander Hamilton"

	s3 = "row, row, row your boat, gently down the stream, merrily, merrily, \
	merrily, merrily, life is but a dream"

	s4 = "buddy you're a boy make a big noise, playing in the street, gonna be \
	a big man some day, you got mud on your face, you big disgrace, kicking your can \
	all over the place, singing, we will, we will, rock you, we will, we will, rock you"

	samples = [s0, s1, s2, s3, s4]
	return samples[i]

class VerseTemplate:
	"""
	Arguments:
		- template_string: Text with the desired rhythm and rhyme pattern.
		- dictionary: Phonetic dictionary to use for lookup.
		- breakrules: Require no word breaking across original words ('word')
					  or no word breaking across phrases ('phrase')
	
	Attributes:
		- breakpoints: List of indices that a word can't cross
		- break
	"""

	def __init__(self, template_string, dictionary, breakrules="word"):

		self.template = template_string
		self.dictionary = dictionary
		self.breakrules = breakrules
		self.phraseBreakpoints = ('!', ')', ',', '--', '.', ':', ';', '?')
		self.nonos = string.punctuation + '0123456789'

		self.breakpoints = []
		self.stresses = []

	def get_rhythm(self):
		"""
		Extract the meter pattern and desired breaks from a given string.
		"""
		wordstrings = self.template.split()

		def add_word(wordstrings, i):
			wordstring = wordstrings[i].strip(self.nonos).lower()
			if len(wordstring) == 0:
				pass
			else:
				word = self.dictionary.lookup(wordstring)
				self.stresses.extend(word.rhythm)

		for i in range(len(wordstrings)):
			add_word(wordstrings, i)
			
			if self.breakrules == "word":
				self.breakpoints.append(len(self.stresses))

			elif self.breakrules == "phrase":
				if wordstrings[i].endswith(self.phraseBreakpoints):
					self.breakpoints.append(len(self.stresses))

		print('\n',self.template)
		print(self.stresses)
		print(self.breakpoints)

	def get_rhyme(self):
		"""
		Go through a local-ish window of the syllables and check where the
		rhyme patterns are.
		"""
		pass

	def fill(self, corpus):
		"""
		Should this go here, or in generate_sample?
		"""
		pass

