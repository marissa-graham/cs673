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

def scansion_score(w_ind, loc, neighbor, corp, template, forward, verbose):
	"""
	Return a score in [0,1] telling how well the meter of the given word
	matches the verse template.

	Zero points for crashing into an edge, neighbor, or breakpoint.
	
	Otherwise, full credit for every stress that matches, quarter credit for
	mismatched stress, normalize by number of syllables.
	"""
	word = corp.wordList[w_ind]
	
	# Check if you've crashed into the edge or your neighbor
	if forward and loc + word.length > neighbor:
		if verbose: 
			print("\t\t'"+word.stringRepr+"' crashes into right neighbor", neighbor)
		return 0.0

	elif forward == False:
		if neighbor in template.verse and loc <= neighbor:
			if verbose:
				print("\t\t'"+word.stringRepr+"' at loc", loc, 
					"crashes into left neighbor", neighbor)
			return 0.0

		elif loc < neighbor:
			if verbose:
				print("\t\t'"+word.stringRepr+"' crashes into edge neighbor")
			return 0.0

	# Check if you've crashed into a breakpoint
	loc_inds = np.array([loc, loc + word.length - 1])
	if np.unique(np.searchsorted(template.breakpoints, loc_inds)).size == 2:
		if verbose: print("\t\t'"+word.stringRepr+"' crashes into breakpoint")
		return 0.0

	# Score the syllable matches and return
	goods = template.stresses[loc:loc+word.length] == word.rhythm

	score = 0.25 + 0.75*np.sum(goods)/word.length
	if verbose: print("\t\t'"+word.stringRepr+"' has a score of "+str(score))
	return score

def check_choices(choices, fill_ind, neighbor, corp, template, forward, verbose):
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
	
	scansion_scores = np.zeros_like(choices, dtype=np.float)

	for i in range(len(choices)):
		if forward:
			scansion_scores[i] = scansion_score(choices[i], fill_ind, 
				neighbor, corp, template, forward, verbose=verbose)
		else:
			L = corp.wordList[choices[i]].length
			scansion_scores[i] = scansion_score(choices[i], fill_ind - L,
				neighbor, corp, template, forward, verbose=verbose)

	return scansion_scores

def get_choices(fill_index, prev_L, neighbor, corp, template, forward, random, verbose):

	# Get a pool of choices
	if random:
		choices = np.random.choice(corp.size, size=20, replace=False)
	else:
		word_index = corp.wordDict[template.verse[fill_index][0].stringRepr]
		choices = corp.sample_distribution(word_index, 20, forward, verbose)

	if forward:
		scansion_scores = check_choices(choices, fill_index + prev_L, 
			neighbor, corp, template, forward, verbose)
	else:
		scansion_scores = check_choices(choices, fill_index, neighbor, 
			corp, template, forward, verbose)

	return choices, scansion_scores

def filter_choices(choices, scansion_scores, corp, forward, verbose):

	# Take top 25% of scores
	cutoff = np.nanpercentile(scansion_scores, 75)
	scansion_scores[scansion_scores < cutoff] = 0
	
	# Scale by length and followability 
	for i in np.nonzero(scansion_scores)[0]:
		scansion_scores[i] *= corp.wordList[choices[i]].length
		scansion_scores[i] *= corp.followability(choices[i], forward)

	# Take the top 25% of those
	cutoff = np.nanpercentile(scansion_scores, 75)
	scansion_scores[scansion_scores < cutoff] = 0
	scansion_scores /= np.sum(scansion_scores)
	
	# Sample from the remaining probability distribution
	best_index = np.random.choice(choices,p=scansion_scores)
	best = corp.wordList[best_index]
	L = corp.wordList[best_index].length

	# Print feedback
	if verbose:# and np.nonzero(scansion_scores)[0].size > 1:
		goods = choices[np.nonzero(scansion_scores)[0]]
		print("\t\tChoose between: "+", ".join([corp.wordList[i].stringRepr for i in goods]))
		np.set_printoptions(2)
		print("\t\tFiltered scores:", scansion_scores)

		if forward:
			print("\t => Add '"+best.stringRepr+"' going forward")
		else:
			print("\t => Add '"+best.stringRepr+"' going backward")

	return best, L

def get_word(fill_index, neighbor, corp, template, forward, verbose):
	"""
	Generate a word based on the given corpus to fill the given template.

	Arguments:
		fill_index : Location of the current word in the template
		neighbor : Index of the left or right neighbor
		corp : WordCorpus to use
		template : VerseTemplate to use
		forward : if True, fill forward; if False, fill backward

	Returns:
		new_fill_index : Updated information about current word and indices
	"""

	# Check if there's actually a word at that index
	try:
		prev_word, prev_L = template.verse[fill_index]
	except KeyError:
		if verbose:
			print("\t\tNo word exists at fill_index, return current index")
		return fill_index

	choices, scansion_scores = get_choices(fill_index, prev_L, neighbor, corp, 
		template, forward, False, verbose)

	# If everything crashes, just pick random words from the corpus
	if np.amax(scansion_scores) == 0:

		if verbose:
			print("\tOH **** EVERYTHING CRASHED")
			print("\tShame fail choices:", 
				", ".join([corp.wordList[i].stringRepr for i in choices]))
			print("\tCurrent state of template:",template.join_template())

		choices, scansion_scores = get_choices(fill_index, prev_L, neighbor, 
			corp, template, forward, True, verbose)

		# Justify not having this be a while loop, because come on now
		if np.amax(scansion_scores) == 0:
			raise ValueError("You unlucky b******, you picked 20 unique words\
				from the entire corpus and ALL of them smash into something")
	
	best, L = filter_choices(choices, scansion_scores, corp, forward, verbose)

	# Update the template and return the new location index
	if forward:
		template.add_word(best, fill_index + prev_L, L)
		return fill_index + prev_L
	else:
		template.add_word(best, fill_index - L, L)
		return fill_index - L

def join_stubs(left, right, corp, template, verbose):
	"""
	Join the words going forwards and backwards by maximizing
	the probability of a word or phrase following the left side 
	and being followed by the right side, while matching the 
	meter as best as possible.
	"""

	def get_to_fill(left, right, template):

		if left == right:
			return 0, 0
		else:
			try:
				left_length = template.verse[left][1]
			except KeyError:
				left_length = 0
			return right - left - left_length, left_length

	if verbose:
		print("\nJoin stub between", left, "and", right, ':',
		template.join_template(a=left,b=right+1))
		print("Fill", get_to_fill(left, right, template), "syllables")

	original_left = left
	original_right = right

	# Try to fill with length to_fill
	iters = 0
	to_fill, L = get_to_fill(left, right, template)

	while to_fill > 0:

		if verbose: print("\n\tLeft, right, to_fill:", left, ",", right, ",", to_fill)
		iters += 1
		if iters > 10: 
			raise ValueError("your stub joiner stop condition is fucked up")

		# Get words that follow left and are followed  by right, i.e. A[Left, i] > 0 AND A[i, Right] > 0
		followsleft = np.where(corp.A_forward[left,:] > 0)
		rightfollows = np.where(corp.A_forward[:,right] > 0)

		# See if you have anything that actually fits
		plausibles = np.intersect1d(followsleft, rightfollows)
		
		picked_something = False
		if plausibles.size > 0:

			if verbose: 
				print("\t\tWE HAVE PLAUSIBLES! they are:",
				", ".join([corp.wordList[i].stringRepr for i in plausibles]))

			for i in range(plausibles.size):
				if corp.wordList[plausibles[i]].length == to_fill:
					picked_something = True
					template.add_word(corp.wordList[plausibles[i]], left + L)
					left = left + to_fill

		# Otherwise, add a word and try again
		if picked_something == False:

			if verbose: print("\t\tNo plausibles that fit; just add a word")
			new_left = get_word(left, right, corp, template, True, verbose)
			if left == new_left:
				right = get_word(right, left, corp, template, False, verbose)
			else:
				left = new_left
			to_fill, L = get_to_fill(left, right, template)
			if verbose:
				print(template.join_template(a=original_left, b=original_right+1))

		to_fill, L = get_to_fill(left, right, template)
	
	if verbose: print("\n"+template.join_template())

def fill_rhymes(corp, template):

	print("not doing rhymes for now")

def fill_template(corp, template, verbose=False, get_rhymes=True):
	"""
	Generate babble words to fill the given Verse template.

	We assume by this point that the Verse template has already had the rhyme
	matrix initialized.
	"""

	# Initialize stuff
	if get_rhymes:
		fill_rhymes(corp, template)

	rhyme_inds = list(template.verse.keys())

	# Now go through all the "holes" between bone words
	for i in range(len(rhyme_inds)):

		if i == 0:
			if verbose: print("\nFILL BETWEEN 0 AND", rhyme_inds[0])
			join_stubs(0, rhyme_inds[0], corp, template, verbose)
		
		left = rhyme_inds[i]
		L = rhyme_inds[i]
		
		if i == len(rhyme_inds) - 1:
			right = template.num_syllables-1
			Right = template.num_syllables
		else:
			right = rhyme_inds[i+1]
			R = rhyme_inds[i+1] + 1
		
		# Fill the holes forwards and backwards 

		if verbose:
			print("\nFILL BETWEEN", left + template.verse[left][1], "AND", right-1)
		to_fill = abs(right - left - template.verse[left][1])
		
		while to_fill > 3:

			# Go forwards from left
			left = get_word(left, right, corp, template, True, verbose)
			to_fill = abs(right - left - template.verse[left][1])

			if verbose:
				print("\tLocal state of template:",template.join_template(a=L,b=R))
				print("    to_fill:", to_fill)

			# Go backwards from right if necessary
			if to_fill > 2:
				right = get_word(right, left, corp, template, False, verbose)
				to_fill = abs(right - left - template.verse[left][1])
				if verbose:
					print("\tLocal state of template:",template.join_template(a=L,b=R))
					print("    to_fill:", to_fill)

		# Join up the middles
		if verbose: print("\n"+template.join_template())
		join_stubs(left, right, corp, template, verbose)
		if verbose: print("\nLocal state of template:", template.join_template(a=L,b=R))

	# Return the joined-up string
	return template.join_template()
