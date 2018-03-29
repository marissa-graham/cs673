#!python3
import itertools
import nltk
import re
import string
import numpy as np
from scipy import sparse

import phonetic
import corpus
import rhymetools
import verse

def dada_filler():
	"""
	Generate a daDada filler word with the desired scansion.
	"""
	pass

def scansion_score():
	"""
	Return a score in [0,1] telling how well the meter of the given word
	matches the verse template.
	"""
	pass

def breakpoint_score():
	"""
	Return 1 if the word choice crosses a breakpoint in the template
	and 0 otherwise.
	"""
	pass

def followability_score():
	"""
	Get a score for how comparatively followable each word is.
	"""

	# Calculate at time of read in, since it's cheap then, mostly just
	# look up here (aka avoid doing the division a bunch?)
	pass

def get_choices(corpus, versetemplate):
	"""
	Get a pool of word choices from the corpus.
	"""

	# Sample the distribution

	# Get synonyms as desired (w/ original index in transition matrix)
	pass


def fill_rhymes(location, corpus, versetemplate):
	"""
	Get words which:
		1) match the meter and rhyme pattern at the given indices, and 
		2) are either in or synonymous to something in the corpus.
	"""

	# Stage 1: Match the words that are supposed to be repeated

	# Stage 2: Match the rhymes. 
		# Get the matrix with all the rhymes for everything
		# Go through and match a pair at a time
			# If you have a cutesy little diagonal, and you pick a word
			# with more than one syllable, they both gotta match. Idk how
			# exactly that's gonna work
	pass 


def join_stubs(left_index, right_index, corpus, versetemplate):
	"""
	Join the words going forwards and backwards by maximizing
	the probability of a word or phrase following the left side 
	and being followed by the right side, while matching the 
	meter as best as possible.
	"""

	# Get ALL words from the corpus that follow Left and are followed
		# by Right, i.e. A[Left, i] > 0 AND A[i, Right] > 0

	# Get some synonyms maybe

	# Pick whatever fits best based on A[Left,i], A[i,Right], and scansion
		# fitness score

	pass


def generate_word(fill_index, corpus, versetemplate, forward=True):
	"""
	Generate a word based on the given corpus to fill the 
	given template.

	Arguments:
		- location: Tuple with the information about the current
					word and indices in the template.
		- corpus: WordCorpus to use.
		- versetemplate: VerseTemplate to use.
		- forward: if True, fill forward; if False, fill backward.

	Returns:
		- location: Updated information about current word
					and indices.
	"""

	# Get a pool of choices


	# Get the fitness scores for each choice

		# How well do they fit the meter?

		# Do they cross a breakpoint?

		# How "followable" are they? vs. unique

		# Do they result in plagiarism?


	# Choose between them based on these scores, including minimum 
		# acceptability thresholds and compromise


	# Update the template and location accordingly (keep track of index,
		# and whether you're going backwards or forwards)
	versetemplate.add_word(best, fill_index, L, scores, forward)

	if forward:
		return fill_index + L
	else:
		return fill_index - L

def fill_template(corpus, versetemplate):
	"""
	Generate babble words to fill the given Verse template.
	"""

	# Pure initialization steps

	# Go through the rhymes in the template and get bone words that 
		# match the desired scansion

	# Now go through all the "holes" between bone words
		
		# If you are at the first rhyme word, go backwards to start

		# If you are at the last rhyme word, go forward to the end

		# If you are between two pairs of rhyme words, work forwards
			# and backwards simultaneously until the desired choices
			# overlap each other, backtrack one step, then call join_stubs

	pass