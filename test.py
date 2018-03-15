from rhymetools import RhymeEvaluator
from phonetic import Word
from phonetic import PhoneticDictionary

if __name__ == "__main__":
    # print(rm.evaluate("enable", "fable"))
    from phonetic import PhoneticDictionary
    pd = PhoneticDictionary()
    word1 = pd.lookup("refrain")
    word2 = pd.lookup("frame")
    print(word1)
    print(word2)
    rm = RhymeEvaluator()
    score = rm.rhyme_score(word1, word2, 0, 0)
    print()
    pass
