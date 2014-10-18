# lexscan

## Introduction

lexscan is a simple Python 2.7 module for tokenizing an input string based on a set of regular expressions.

## Example

    >>> import lexscan
    >>> from pprint import pprint
    >>> teststr = "this!!is !! a test!!!!!! yay"
    >>> wordexp = lexscan.ScanExp( r'\w+' )
    >>> bangexp = lexscan.ScanExp( r'!+' )
    >>> spaceexp = lexscan.ScanExp( r'\s+', significant = False )
    >>> tokens = lexscan.tokenize( teststr, ( wordexp, bangexp, spaceexp ) )
    >>> pprint(tokens)
    [1:0: 'this' \w+,
     1:4: '!!' !+,
     1:6: 'is' \w+,
     1:9: '!!' !+,
     1:12: 'a' \w+,
     1:14: 'test' \w+,
     1:18: '!!!!!!' !+,
     1:25: 'yay' \w+]
 
