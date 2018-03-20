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


def check_rhyme():
    """
    Check for a meter match to the template, accounting for the fact that 
    we can have binary or ternary stress pattern symbols.
    """
    pass


def check_rhythm(w, wordlengths, rhythmtemplate, wordindex, rhythmindex):
    """
    Wrap around the rhymetools module to allow for multi-syllable rhymings.
    """
    
    # Check if the word length is right
    if len(w.rhythm) != wordlengths[wordindex]:
        #print("\tWord doesn't have the right number of syllables")
        return 0

    # Single-syllable words match meter with everything
    if len(w.rhythm) == 1:
        #print("\tSingle-syllable words always match stress")
        return 1

    else:
        rhythm_score = 0

        # TODO: convert to rhythm being a numpy array
        for i in range(len(w.rhythm)):
            if w.rhythm[i] == rhythmtemplate[rhythmindex + i]:
                rhythm_score += 1

        #print("rhythm score: ", rhythm_score)
        if rhythm_score == len(w.rhythm):
            #print("\tMATCHES PERFECTLY")
            return rhythm_score
        else:
            #print("\tRIGHT NUMBER OF SYLLABLES BUT WRONG RHYTHM")
            return 0.5


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



def generate_verse(corp, wordlengths, rhythmtemplate):
    """
    Generate babble words to fill the given Verse template.
    """
    current_word = np.random.randint(corp.size)
    rhythmindex = 0
    wordindex = 0
    words = []

    while rhythmindex < rhythmtemplate.size:

        choices = corp.sample_distribution(current_word, 25)
        rhythm_scores = np.zeros_like(choices)

        for i in range(len(choices)):
            w = corp.wordList[choices[i]]
            rhythm_scores[i] = check_rhythm(w, wordlengths, rhythmtemplate, \
                wordindex, rhythmindex)
        
        current_word = choices[np.argmax(rhythm_scores)]
        w = corp.wordList[current_word]

        if np.max(rhythm_scores) < wordlengths[wordindex]:
            filler_word = ""
            for i in range(wordlengths[wordindex]):
                if rhythmtemplate[rhythmindex+i] == 0:
                    filler_word += "da"
                else:
                    filler_word += "DA"
            words.append(filler_word)
            rhythmindex += wordlengths[wordindex]
            wordindex += 1

        elif np.max(rhythm_scores) == 0.5:

            print("Match word length only")
            print(rhythmtemplate[rhythmindex:rhythmindex+wordlengths[wordindex]])
            print(current_word.rhythm)
            words.append(corp.wordList[current_word].word.lower())
            rhythmindex += wordlengths[wordindex]
            wordindex += 1

        else:
            words.append(corp.wordList[current_word].word.lower())
            rhythmindex += wordlengths[wordindex]
            wordindex += 1

    # print("\nResults:\n", " ".join(words))
    return " ".join(words)
