class Verse:
    """
    A class that represents a verse or collection of lines. A Verse contains
    information about its metrical content in the form of a stress template
    for each of the component syllables and information about its semantic
    content in the form of a list of sentences with the actual words
    """
    def __init__(self):
        self.template = []
        self.lines = []
        pass