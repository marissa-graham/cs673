#!python3

def docstring_example(arg1, arg2, kwarg1=0):
    """
    Toy function to demonstrate the way I usually write docstrings.
    Usually the line lengths correspond to the ruler I put in my sublime
    text windows so they match the 72 character convention dictated by
    the pep8 style guide. Counting the four space indent, the longest 
    line in this paragraph is 72 characters exactly. 
    
    The description should not generally be long enough to require
    multiple paragraphs, so idk what the best way to handle that would
    be. Space break looks best, so that's probably the right way. 
    I like the hyphen line since it makes it more readable, but the :
    vs something like - doesn't matter, as long as it's surrounded
    by spaces.
    
    INPUT
    -----
    arg1 : Thing with datatype idk we should end with a period.
    arg2 : Other argument that we need with some other dtype.
    kwarg1 : Usually my keyword arguments are maxiters and tolerances.
    
    OUTPUT
    ------
    mystring : String that is the output that we return.
    """
    
    # We should include a line between the docstring and the start of the code. 
    # The comment above results in a line of exactly 79 characters, which is
    # the pep8 maximum for lines of actual code vs. docstrings/comments.
    mystring = "This is the thing we want to return."
    return mystring