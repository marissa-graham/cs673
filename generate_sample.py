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

# NEED TO DISCUSS (EASY IN {0,1}, NOT IN [0,1])
def scansion_score():
	"""
	Return a score in [0,1] telling how well the meter of the given word
	matches the verse template.
	"""
	pass

# PLANNNED OUT, EASY
def breakpoint_score():
	"""
	Return 1 if the word choice crosses a breakpoint in the template
	and 0 otherwise.
	"""
	pass

# FULLY PLANNED
def followability_score():
	"""
	Get a score for how comparatively followable each word is.
	"""

	# Calculate at time of read in, since it's cheap then, mostly just
	# look up here (aka avoid doing the division a bunch?)
	pass

# FULLY PLANNED
def get_choices(corpus, versetemplate):
	"""Get a pool of word choices from the corpus."""

	# Sample the distribution
	pass

# NEED TO DISCUSS
def fill_rhymes(corpus, versetemplate):
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

	# Return a list of the indices for the start of each filled word
	pass 

# FULLY PLANNED
def join_stubs(left_index, right_index, corpus, versetemplate):
	"""
	Join the words going forwards and backwards by maximizing
	the probability of a word or phrase following the left side 
	and being followed by the right side, while matching the 
	meter as best as possible.
	"""

	# Get ALL words from the corpus that follow Left and are followed
		# by Right, i.e. A[Left, i] > 0 AND A[i, Right] > 0

	# Also consider pairs of words?

	# Pick whatever fits best based on A[Left,i], A[i,Right], and scansion
		# fitness score

	pass

# NEED TO DISCUSS THE METRIC FOR COMBINING SCORES
# OTHERWISE FULLY PLANNED AND PRETTY STRAIGHTFORWARD
def generate_word(fill_index, neighbor_index, corpus, versetemplate, forward=True):
	"""
	Generate a word based on the given corpus to fill the given template.

	Arguments:
		fill_index : Location of the current word in the template
		neighbor_index : Index of the left or right neighbor
		corpus : WordCorpus to use
		versetemplate : VerseTemplate to use
		forward : if True, fill forward; if False, fill backward

	Returns:
		location : Updated information about current word and indices
	"""

	# Check for a beginning/end index that should be ignored
	if fill_index < 0 or fill_index >= versetemplate.num_syllables:
		return fill_index

	# Get a pool of choices


	# Get the fitness scores for each choice

		# How well do they fit the meter? (meter score should include
			# how many syllables it's supposed to take up)

		# Do they crash into the neighbor?

		# Do they cross a breakpoint?


	# Choose between them based on these scores, including minimum 
		# acceptability thresholds and compromise


	# Update the template and location accordingly)
	versetemplate.add_word(best, fill_index, L, scores, forward)

	# If we didn't add the word successfully, don't change fill_index

	if forward:
		return fill_index + L
	else:
		return fill_index - L

# FULLY PLANNED
def fill_template(corpus, versetemplate):
	"""
	Generate babble words to fill the given Verse template.

	We assume by this point that the Verse template has already had the rhyme
	matrix initialized.
	"""

	# Initialize stuff
	num_bones, bone_indices = fill_rhymes(corpus, versetemplate)

	# Now go through all the "holes" between bone words
	for i in xrange(num_bones):

		# Get the left and right indices
		if i == 0:
			left_index = -1
		else:
			left_index = bone_indices[i-1]

		if i+1 == num_bones:
			right_index = versetemplate.num_syllables
		else:
			right_index = bone_indices[i]

		# Fill the holes forwards and backwards 
		maxiters = 20
		iters = 0
		while abs(right_index - left_index) > 3 and iters < maxiters:

			# Paranoid
			iters += 1

			# Go forwards from left
			left_index = generate_word(left_index, right_index, corpus, 
				versetemplate, forward=True)

			# Go backwards from right if necessary
			if abs(right_index - left_index) > 2:
				right_index = generate_word(right_index, left_index, corpus, 
					versetemplate, forward=False)
		
		# Join up the middles
		join_stubs(left_index, right_index, corpus, versetemplate)

	# Return the joined-up string
	return versetemplate.join_template()