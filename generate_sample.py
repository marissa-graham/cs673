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

def scansion_score(word_index, loc, neighbor, corp, template, forward):
	"""
	Return a score in [0,1] telling how well the meter of the given word
	matches the verse template.

	Zero points for crashing into an edge, neighbor, or breakpoint.
	
	Otherwise, full credit for every stress that matches, quarter credit for
	mismatched stress, normalize by number of syllables.
	"""
	word = corp.wordList[word_index]

	# Check if you've crashed into the edge or your neighbor
	if forward and loc + word.length > neighbor:
		return 0.0
	elif forward == False and loc <= neighbor:
		return 0.0

	# Check if you've crashed into a breakpoint
	loc_inds = np.array([loc, loc + word.length - 1])
	if np.unique(np.searchsorted(template.breakpoints, loc_inds)).size == 2:
		return 0.0

	# Score the syllable matches and return
	goods = template.stresses[loc:loc+word.length] == word.rhythm
	return 0.25 + 0.75*np.sum(goods)/word.length

def check_choices(choices, fill_ind, neighbor_ind, corp, template, forward):
	"""
	Get the scansion scores for all the choices.
	
	Arguments:
		choices : List of indices of the words you want to check
		fill_index : Syllable index to start the word at
		neighbor_ind : Nearest word you might be able to crash into
		corp : Main corp, only used for looking up the word indices
		template : As usual
		forward : Whether to check the scores going forwards or backward

	Returns:
		scansion_scores : Array of rhythm scores for all the choices.
	"""
	
	scansion_scores = np.zeros_like(choices)

	for i in range(len(choices)):
		if forward:
			scansion_scores[i] = scansion_score(choices[i], fill_index, 
				neighbor_index, corp, template, forward)
		else:
			L = corp.wordList[choices[i]].length
			scansion_scores[i] = scansion_score(choices[i], fill_index - L,
				neighbor_index, corp, template, forward)

	return scansion_scores

def get_word(fill_index, neighbor_index, corp, template, forward=True):
	"""
	Generate a word based on the given corpus to fill the given template.

	Arguments:
		fill_index : Location of the current word in the template
		neighbor_index : Index of the left or right neighbor
		corp : WordCorpus to use
		template : VerseTemplate to use
		forward : if True, fill forward; if False, fill backward

	Returns:
		new_fill_index : Updated information about current word and indices
	"""

	# Check if there's actually a word at that index
	try:
		prev_word, prev_L, prev_scores = template.verse[fill_index]
	except KeyError:
		print("No word exists at fill_index, return current index")
		return fill_index

	# Get a pool of choices
	choices = corp.sample_distribution(prev_word, 20, forward)

	if forward:
		scansion_scores = check_choices(choices, fill_index + prev_L, 
			neighbor_index, corp, template, forward)
	else:
		scansion_scores = check_choices(choices, fill_index, neighbor_index, 
			corp, template, forward)

	# If everything crashes, just pick random words from the corpus
	if np.amax(scansion_scores) == 0:

		choices = np.random.choice(corp.size, size=20, replace=False)
		scansion_scores = check_choices(choices)

		# Justify not having this be a while loop, because come on now
		if np.amax(scansion_scores) == 0:
			raise ValueError("You unlucky bastard, you picked 20 unique words\
				from the entire corpus and ALL of them smash into something")

	# Zero out scores < 75th percentile & scale the rest by length + followability
	cutoff = np.nanpercentile(scores, 75)
	scansion_scores[scansion_scores < cutoff] = 0

	for i in np.nonzero(scansion_scores)[0]:
		scansion_scores[i] *= corp.wordList[choices[i]].length
		scansion_scores[i] *= corp.followability(choices[i], forward)

	# Choose the highest scaled score
	best_index = choices[np.amax(scansion_scores)]
	best = corp.wordList[best_index].stringRepr
	L = corp.wordList[best_index].length

	# Update the template and return the new location index
	if forward:
		template.add_word(best, fill_index + prev_L, L)
		return fill_index + prev_L
	else:
		template.add_word(best, fill_index - L, L)
		return fill_index - L

def join_stubs(left, right, corp, template):
	"""
	Join the words going forwards and backwards by maximizing
	the probability of a word or phrase following the left side 
	and being followed by the right side, while matching the 
	meter as best as possible.
	"""

	to_fill = abs(right - left)
	iters = 0
	maxiters = 10

	print("fill between index", left, "and", right)

	# Try to fill with length to_fill
	while to_fill > 0 and iters < maxiters:

		iters += 1

		break

		# Get ALL words from the corpus that follow Left and are followed
			# by Right, i.e. A[Left, i] > 0 AND A[i, Right] > 0

		# Pick out the ones that are the right length

		# If none of them are long enough, call get_word on left and then
			# try again

		# Pick whatever fits best based on A[Left,i], A[i,Right], and scansion
			# fitness score
	
def fill_rhymes(corp, template):
	"""
	Get words which:
		1) match the meter and rhyme pattern at the given indices, and 
		2) are either in or synonymous to something in the corp.
	"""

	# Go through all the nonzero indices in the rhyme matrix
	nonzero_rows, nonzero_cols = np.nonzero(template.rhyme_matrix)
	print("rows: ", nonzero_rows)
	print("cols: ", nonzero_cols)

	# STAGE ONE: PICK THE FIRST WORD IN THE PAIR
	for syl_pair in list(zip(nonzero_rows, nonzero_cols)):
		print(syl_pair)

	# Check if you've already got a word overlapping either one in the
		# pair, if so, skip to stage two

	# Sample from the probability distribution of the vowels, and then
		# pick words with that vowel in them until you get one that 
		# doesn't cross a breakpoint

	# STAGE TWO: PICK THE SECOND WORD

	# Just go through the ones with the same vowel and see what has the
		# best match
	pass 

def fill_template(corp, template):
	"""
	Generate babble words to fill the given Verse template.

	We assume by this point that the Verse template has already had the rhyme
	matrix initialized.
	"""

	# Initialize stuff
	fill_rhymes(corp, template)

	rhyme_inds = list(template.verse.keys())

	# Now go through all the "holes" between bone words
	for i in range(len(rhyme_inds)):

		if i == 0:
			join_stubs(0,rhyme_inds[0], corp, template)
		
		left = rhyme_inds[i]
		
		if i == len(rhyme_inds) - 1:
			right = template.num_syllables-1
		else:
			right = rhyme_inds[i+1]
		
		# Fill the holes forwards and backwards 
		maxiters = 20
		iters = 0

		to_fill = abs(right - left + template.verse[left][1])
		while to_fill > 4 and iters < maxiters:

			# Paranoid
			iters += 1

			# Go forwards from left
			left = get_word(left, right, corp, template)
			to_fill = abs(right - left + template.verse[left][1])

			# Go backwards from right if necessary
			if to_fill > 3:
				right = get_word(right, left, corp, template, forward=False)
		
		# Join up the middles
		join_stubs(left, right, corp, template)

	# Return the joined-up string
	return template.join_template()
