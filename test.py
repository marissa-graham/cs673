from phonetic import PhoneticDictionary
import nltk

if __name__ == "__main__":
    # nltk.download('punkt')
    # nltk.download('averaged_perceptron_tagger')
    filename = "data/cmudict/cmudict-0.7b"
    '''
    p = PhoneticDictionary()
    p.import_file(filename)
    table = p.lookup("table")
    fable = p.lookup("fable")
    dog = p.lookup("dog")
    sentence = p.evaluate("Hey all you people")
    print (table)
    print (fable)
    print (table.rhymes_with(fable))
    print (dog.rhymes_with(table) == False)
    '''

    '''
    sentence = "Hey all you people"
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    print(tokens)
    print(tagged)
    '''

    words = []
    # word_map = {}
    word_to_vec = {}

    import re
    strip_punct = re.compile("[,.!?:-]")

    with open("data/text/trump.txt") as file:
        for line in file:
            for word in line.split():
                stripped = strip_punct.sub("", word)
                if len(stripped) > 0:
                    words.append(stripped.lower())
                # print(stripped)
                # words.add(word)
    # print(word_map)
    '''
    cur = "" # initialize start state to empty string
    for i in words:
        word_map[cur] = i
        cur = i

    state = ""
    for i in range(100):
        print(word_map[state], " ")
        state = word_map[state]
    '''

    state = "" # initialize start state to empty string
    for i in words:
        if i in word_to_vec:
            word_to_vec[state].append(i)
        else:
            word_to_vec[state] = [i]

        state = i

    pass



