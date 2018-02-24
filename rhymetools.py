from nltk.corpus import cmudict

# revision
# test revision

class RhymeEvaluator:
    def __init__(self):
        pass

    @classmethod
    def evaluate(cls, a, b):
        """
        Evaluates how well two words rhyme
        Args:
            a: word 1
            b: word 2

        Returns:
        A number between 0-1 indicating how well the two words
        """
        """
        Naive implementation: 
        
        1. Take two words. For example:
            word 1: table
            word 2: stable
        
        2. Right align them so that their end syllables match:
                table |
               stable |
        
        3. Starting from the last syllable, traverse backwards until reaching 
            the first syllable of the shorter word. Count number of matches
                table |
               stable |
                ^^^^^
        4. Return the numbers of matched syllables/total number of syllables
        """
        dictionary = cmudict.dict()
        try:
            word1 = dictionary[a][0]
            word2 = dictionary[b][0]
        except KeyError as k:
            print("{} not found in dictionary".format(k))
        else:
            count = 0
            l_word1 = len(word1)
            l_word2 = len(word2)
            length =  l_word1 if l_word1 < l_word2 else l_word2
            for i in range(1, length + 1):
                if word1[-i] == word2[-i]:
                    count += 1
            return count * 2 / (l_word1 + l_word2)
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

