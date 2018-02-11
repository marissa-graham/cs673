from phonetic import PhoneticDictionary

if __name__ == "__main__":
    filename = "data/cmudict/cmudict-0.7b"
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

    pass



