from rhymetools import RhymeEvaluator as rm
from phonetic import PhoneticDictionary

if __name__ == "__main__":
    # print(rm.evaluate("enable", "fable"))
    from phonetic import PhoneticDictionary
    pd = PhoneticDictionary("data/cmudict/cmudict.0.7a")
    word1 = pd.lookup("table")
    word2 = pd.lookup("relabel")
    print(word1)
    print(word2)
    pass


