#!python3
import corpus
import phonetic
import numpy as np
#import rhymetools

def dada_filler():
	"""
	Generate a daDada filler word with the desired scansion.
	"""
	pass


def join_stubs(location, params, corpus, versetemplate):
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

def fill_rhyme(location, corpus, versetemplate):
	"""
	Get words which:
		1) match the meter and rhyme pattern at the given indices, and 
		2) are either in or synonymous to something in the corpus.
	"""
	pass 

def generate_word(location, corpus, versetemplate, forward=True):
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

		# Sample the distribution

		# Get synonyms as desired (w/ original index in transition matrix)


	# Get the fitness scores for each choice

		# How well do they fit the meter?

		# Do they cross a breakpoint?

		# How "followable" are they?

		# Do they result in plagiarism?


	# Choose between them based on these scores, including minimum 
		# acceptability thresholds and compromise

	# Update the template and location accordingly

		# Should we have a "ChoiceOption" class and such to keep track
			# of all this nonsense? What needs to be stored?

		# KEEP the fitness scores of the choice for potential
			# backtracking later

	pass

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