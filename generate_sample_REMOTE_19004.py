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
		#print("\t\t'"+word.stringRepr+"' crashes into neighbor")
		return 0.0
	elif forward == False and loc <= neighbor:
		#print("\t\t'"+word.stringRepr+"' crashes into neighbor")
		return 0.0

	# Check if you've crashed into a breakpoint
	loc_inds = np.array([loc, loc + word.length - 1])
	if np.unique(np.searchsorted(template.breakpoints, loc_inds)).size == 2:
		#print("\t\t'"+word.stringRepr+"' crashes into breakpoint")
		return 0.0

	# Score the syllable matches and return
	goods = template.stresses[loc:loc+word.length] == word.rhythm

	score = 0.25 + 0.75*np.sum(goods)/word.length
	#print("\t\t'"+word.stringRepr+"' has a score of "+str(score))
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
	if verbose and np.nonzero(scansion_scores)[0].size > 1:
		goods = choices[np.nonzero(scansion_scores)[0]]
		print("\tChoose between: "+", ".join([corp.wordList[i].stringRepr for i in goods]))
		np.set_printoptions(2)
		print("\t", scansion_scores)

		if forward:
			print("\t => Add '"+best.stringRepr+"' going backward")
		else:
			print("\t => Add '"+best.stringRepr+"' going forward")

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
		print("No word exists at fill_index, return current index")
		return fill_index

	choices, scansion_scores = get_choices(fill_index, prev_L, neighbor, corp, 
		template, forward, False, verbose)

	# If everything crashes, just pick random words from the corpus
	if np.amax(scansion_scores) == 0:

		if verbose:
			print("\tOH FUCK EVERYTHING CRASHED")
			print("\tCurrent state of template:",template.join_template())

		choices, scansion_scores = get_choices(fill_index, prev_L, neighbor, 
			corp, template, forward, True, verbose)

		# Justify not having this be a while loop, because come on now
		if np.amax(scansion_scores) == 0:
			raise ValueError("You unlucky bastard, you picked 20 unique words\
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

	to_fill = abs(right - left)

	if verbose:
		print("\n\tTODO: join stub between", left, "and", right, '\n')

	# Try to fill with length to_fill
	while to_fill > 0:

		# Get ALL words from the corpus that follow Left and are followed
			# by Right, i.e. A[Left, i] > 0 AND A[i, Right] > 0
		followsleft = np.where(corp.A_forward[20,:]>0)
		rightfollows = np.where(corp.A_forward[:,16]>0)

		# Pick out the ones that are the right length
		plausibles = np.intersect1d(followsleft, rightfollows)
		scores = np.zeros_like(plausibles)
		"""
	    for i in range(plausibles.size):
		 	scores[i] = 
		"""

		# If none of them are long enough, call get_word on left and then
			# try again

		# Pick whatever fits best based on A[Left,i], A[i,Right], and scansion
			# fitness score
	
def get_rhyme_word(ind, phoneme, corp, template):

	# print("phoneme in get_rhyme_word ", phoneme)
	candidates = corp.sylDict[phoneme]
	#2 Choose a bunch of (word, syllable) pairs for that phoneme
	choices = np.random.choice(len(candidates), size=20)
	# print("choices ", choices)
	
	#3 Get their scansion scores
	scansion_scores = np.zeros_like(choices, dtype=np.float)

	for i in range(len(candidates)):
		# print("word ", candidates[choices[i]][0])
		scansion_scores[i] = scansion_score(candidates[choices[i]][0], 
			template.syllable_indices[candidates[choices[i]][0]] - candidates[choices[i]][1], 
			template.num_syllables, corp, template, True, verbose=False)

	#4 Zero out all the ones below the 75th percentile
	cutoff = np.nanpercentile(scansion_scores, 75)
	scansion_scores[scansion_scores < cutoff] = 0
	
	#5 Out of the ones that are left, multiply by the followability score
	for i in np.nonzero(scansion_scores)[0]:
		scansion_scores[i] *= corp.followability(candidates[choices[i]][0], True)

	#6 Take the top 25% of those, and then sample from THAT distribution
	cutoff = np.nanpercentile(scansion_scores, 75)
	scansion_scores[scansion_scores < cutoff] = 0
	scansion_scores /= np.sum(scansion_scores)

	# Sample from the remaining probability distribution
	best = np.random.choice(len(choices), p=scansion_scores)
	
	#7 Call add_word to add that to the template 
	# print("choices[best]: ", choices[best])
	template.add_word(corp.wordList[candidates[choices[best]][0]], ind - candidates[choices[best]][1]	)

def fill_rhymes(corp, template):
	"""
	Get words which:
		1) match the meter and rhyme pattern at the given indices, and 
		2) are either in or synonymous to something in the corp.
	"""

	# row, col = indices of the location in the matrix
	rows, cols = np.nonzero(template.rhyme_matrix)

	vowel_list = list(corp.sylDict.keys())
	vowel_counts = [len(v) for v in corp.sylDict.values()]
	vowel_probs = vowel_counts / np.sum(vowel_counts)

	for row, col in list(zip(rows, cols)):
		
		if template.occupied_syllables[row] + template.occupied_syllables[col] == 2:
			print("All full")
			pass
		
		else:

			# If both of them are empty, we have to pick the first word
			if template.occupied_syllables[row] + template.occupied_syllables[col] == 0:

				#1 Sample from vowel probability distribution to get a phoneme
				phoneme_ind = np.random.choice(len(vowel_list), p=vowel_probs)
				phoneme = vowel_list[phoneme_ind]
				get_rhyme_word(row, phoneme, corp, template)
				get_rhyme_word(col, phoneme, corp, template)

			elif template.occupied_syllables[row] == 1:
				mtx_ind = template.matrix_indices[row]
				phoneme = template.wordList[mtx_ind[0]].vowel_at(mtx_ind[1])[:-1]			
				# print("phoneme ", phoneme)
				get_rhyme_word(col, phoneme, corp, template)

			else:
				mtx_ind = template.matrix_indices[col]
				phoneme = template.wordList[mtx_ind[0]].vowel_at(mtx_ind[1])[:-1]	
				# print("phoneme ", phoneme)
				get_rhyme_word(row, phoneme, corp, template)
			print("Filling phoneme: ", phoneme)


	print(template.join_template())

def fill_template(corp, template, verbose=False):
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
		
		while to_fill > 1:

			# Go forwards from left
			left = get_word(left, right, corp, template, True, verbose)
			to_fill = abs(right - left - template.verse[left][1])

			if verbose:
				print("\tLocal state of template:",template.join_template(a=L,b=R))
				print("    to_fill:", to_fill)

			# Go backwards from right if necessary
			if to_fill > 0:
				right = get_word(right, left, corp, template, False, verbose)
				to_fill = abs(right - left - template.verse[left][1])
				if verbose:
					print("\tLocal state of template:",template.join_template(a=L,b=R))
					print("    to_fill:", to_fill)

		# Join up the middles
		join_stubs(left, right, corp, template, verbose)
		if verbose: print("\nLocal state of template:", template.join_template(a=L,b=R))

	# Return the joined-up string
	return template.join_template()
