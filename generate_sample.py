#!python3
import corpus
import phonetic
import numpy as np
#import rhymetools

def similarity_metric(A, B):
	"""
	Return a float between 0 and 1 representing the similarity score between
	texts A and B, where 0 is complete dissimilarity and 1 is plagiarism.

	Arguments:
		A, B: Are they WordCorpus? Are they Sentence? Who knows?

	Returns:
		s (float) : Similarity score.
	"""
	pass

def get_synonyms():
	"""
	Placeholder to eventually get WordNet synonyms.
	"""
	pass

def check_meter():
	"""
	Check for a meter match to the template, accounting for the fact that 
	we can have binary or ternary stress pattern symbols.
	"""
	pass

def check_rhyme():
	"""
	Wrap around the rhymetools module to allow for multi-syllable rhymings.
	"""
	pass

def check_line_breaks():
	"""
	Check whether the potential word crosses a line break.
	"""
	pass

def check_grammar():
	"""
	Get a grammar score for the desired word.
	"""
	pass

def check_quality():
	"""
	Check the quality of the writing.
	"""
	pass

def choose_next(corpus, index, template):
	"""
	Choose next word to use.
	"""
	pass

def generate_verse(corp, template):
	"""
	Generate babble words to fill the given Verse template.
	"""
	current_word = np.random.randint(corp.size)
	index = 0

	# TODO: FIX THIS
	corp.A = np.asarray(corp.A)
	rhyme_patterns = [("",-1)]
	words = []

	while index < template.size:
		probs = corp.A[current_word,:]
		
		choices = corp.sample_distribution(current_word, 10)
		for choice in choices:
			
		#current_word = np.random.choice(corp.size, p=probs)
		words.append(corp.wordList[current_word].word.lower())

		# CHANGE TO SIZE INSTEAD OF LEN WHEN IT'S A NUMPY ARRAY
		index += len(corp.wordList[current_word].rhythm)
	
	print(" ".join(words))