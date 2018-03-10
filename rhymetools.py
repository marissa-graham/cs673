from nltk.corpus import cmudict

# revision
# test revision

class RhymeEvaluator:
    def __init__(self):
        pass

    @classmethod
    def evaluate(cls, word1, word2, i, j, priority):
        """
        Returns the rhyme score by evaluating the onset, nucleus, and code of two words
        Args:
            word1: the first word
            word2: the second word
            i: idx of nucleus of first word
            j: idx of nucleus of second word
            priotity: a tuple (x,x,x) containing weights for onset, nucleus, and coda

        Returns: A value between 0-1 indicating how closly aligned the stress tails of both words are
        """
        return 0.5

    """
    def _rhyme(w, level):
        entries = cmudict.entries()
        syllables = [(word, syl) for word, syl in entries if word == w]
        rhymes = []
        for (word, syl) in syllables:
            rhymes += [word for word, pron in entries if pron[-level:] ==
                       syl[-level:]]
        a = set(rhymes)
        return set(rhymes)
    """

