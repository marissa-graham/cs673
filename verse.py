import phonetic
import corpus
import nltk
import numpy as np
from scipy import sparse
from matplotlib import pyplot as plt

def get_sample(i):
	s0 = "I know a song that gets on everybody's nerves, everybody's \
	nerves, everybody's nerves. Oh, I know a song that gets on everybody's nerves \
	and this is how it goes oh oh oh"

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