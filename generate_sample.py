#!python3
import corpus
import phonetic
import numpy as np


# import rhymetools

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


def check_rhyme():
    """
	Check for a meter match to the template, accounting for the fact that 
	we can have binary or ternary stress pattern symbols.
	"""
    pass


def check_rhythm(w, template, index):
    """
	Wrap around the rhymetools module to allow for multi-syllable rhymings.
	"""
    # print("Compare ", w.word, "(", w.rhythm, ") to ", template[index:index+len(w.rhythm)])

    # Single-syllable words match meter with everything
    if len(w.rhythm) == 1:
        # print("\tSingle-syllable words always match")
        return 1

    # Reject words that are too long
    elif (index + len(w.rhythm) >= len(template)):
        # print("\tWord is too long to match rhythm")
        return 0

    else:
        rhythm_score = 0

        # TODO: convert to rhythm being a numpy array
        for i in range(len(w.rhythm)):
            if w.rhythm[i] == template[index + i]:
                rhythm_score += 1

        if rhythm_score == len(w.rhythm):
            # print("\tMatches perfectly")
            return rhythm_score
        else:
            # print("\tNot a match")
            return 0


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
    rhyme_patterns = [("", -1)]
    words = []

    # print(template)
    while index < template.size:
        # probs = corp.A[current_word,:]

        choices = corp.sample_distribution(current_word, 10)
        # print("\n", choices)
        rhythm_scores = np.zeros_like(choices)
        for i in range(len(choices)):
            w = corp.wordList[choices[i]]
            rhythm_scores[i] = check_rhythm(w, template, index)
        # print("\tBest match: ", np.argmax(rhythm_scores), corp.wordList[choices[np.argmax(rhythm_scores)]].word)

        current_word = choices[np.argmax(rhythm_scores)]
        w = corp.wordList[current_word]
        if np.max(rhythm_scores) < len(w.rhythm):
            # print("Couldn't get a perfect match")
            # print("  We only had", len(choices), "choices:",[corp.wordList[choice].word for choice in choices])
            # print("  ", w.word, "has stress pattern", w.rhythm, "but we needed stress pattern", template[index:index+len(w.rhythm)])
            words.append(" ".join(["da" for i in range(len(w.rhythm))]))
        else:
            words.append(corp.wordList[current_word].word.lower())

        # CHANGE TO SIZE INSTEAD OF LEN WHEN IT'S A NUMPY ARRAY
        index += len(corp.wordList[current_word].rhythm)

    # print("\nResults:\n", " ".join(words))
    return " ".join(words)
