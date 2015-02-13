
# Copyright (c) 2014, Sophie Kirschner. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.



'''Lexical scanner module by Sophie Kirschner. (sophiek@pineapplemachine.com)
Define lexemes by creating ScanExp objects, which are used to map an input
string to a sequence of tokens. Tokenize an input string by calling tokenize()
'''



# re doesn't support start pos for search so we're using regex instead.
import regex



__version__ = '1.0.0'



# Tokenize a string using a set of ScanExp objects
def tokenize( strinput, expressions, source = None, newline = '\n' ):
    '''Tokenize an input string using a set of ScanExp objects.
    Starting at the beginning of the string: The longest ScanExp
    match starting at the current position is found. (In case of
    a tie, lowest-index is used. If none is found, a single-
    character token associated with no ScanExp object is created.
    Repeat from the end of the token.
    Returns a list of ScanToken objects.
    
    :param strinput: The string to be tokenized.
    :param expressions: A set of ScanExp objects.
    :param source: (optional) The source to associate with
        generated tokens. For example, you might use a file path
        for this argument so that if something goes wrong when
        parsing tokenized code, the user can be given a source
        file as well as a line number and/or char position.
        Defaults to None.
    :param newline: (optional) Increment the line counter every
        time this character is encountered. Defaults to '\n'.
    '''
    for exp in expressions:
        exp.setsearchstring( strinput )
    tokens = []
    strlen = len(strinput)
    strpos = 0
    strline = 1
    while strpos < strlen:
        # Get the best (longest) match
        bestexp = None
        bestmatch = None
        bestlen = 0
        for exp in expressions:
            match = exp.search( strpos )
            if match and (match.start() == strpos):
                matchlen = (match.end() - strpos) if match else 0
                if matchlen > bestlen:
                    bestexp = exp
                    bestmatch = match
                    bestlen = matchlen
        # Add the token to the list
        if bestexp:
            matchstr = bestmatch.group()
            if bestexp.significant:
                tokens.append( ScanToken( matchstr, bestexp, bestmatch, strpos, strline, source ) )
            strline += matchstr.count( newline )
            strpos += bestlen
        else:
            tokens.append( ScanToken( strinput[ strpos ], None, None, strpos, strline, source ) )
            strline += ( strinput[ strpos ] == newline )
            strpos += 1
    return tokens
        


class ScanExp(object):
    '''ScanExp objects contain a regular expression and some extra info for telling the tokenizer how to treat tokens of this kind.'''
    
    # Constructor
    def __init__( self, expression, settings = regex.IGNORECASE, significant = True, name = '', precompile = True ):
        '''Construct a ScanExp object.
        Returns a ScanExp object.
        
        :param expression: A regular expression, like r'\w'.
        :param settings: (optional) The settings with which to compile
            the regex. Defaults to regex.IGNORECASE.
        :param significant: (optional) Significant tokens are added to
            the return data, nonsignificant tokens are not. (Whitespace
            and comments would be good candidates for nonsignificance.)
            Defaults to True.
        :param name: (optional) Can be useful for debugging purposes,
            gives the object a name. For example, you might name a
            ScanExp object with the expression r'\w' "word". Defaults
            to a blank string.
        :param precompile: (optional) If True, the expression is
            compiled immediately. If False, it isn't compiled until
            the first time the search method is called. Defaults to
            true.
        '''
        self.expression = expression
        self.settings = settings
        self.significant = significant
        self.name = name
        
        self.regex = self.compile() if precompile else None
        '''The compiled regular expression.'''
        
        self.cachematch = None
        '''Cached match.'''
        self.cachepos = -1
        '''Cached match position.'''
        self.cachestr = ''
        '''Cached match came from this string.'''
       
    def setsearchstring( self, string ):
        '''Set string to be used for search method.'''
        self.clearcache()
        self.cachestr = string
       
    # Caching results gives tokenization a substantial speed increase
    def search( self, start = 0 ):
        '''Search the string for a regex match and return the first encountered.'''
        if not self.regex:
            self.compile()
        if (self.cachepos >= start):
            return self.cachematch
        else:
            match = self.regex.search( self.cachestr, start )
            self.cachepos = match.start() if match else -1
            self.cachematch = match
            return match
            
    def clearcache( self ):
        '''Get rid of cache info.'''
        self.cachematch = None
        self.cachepos = -1
        self.cachestr = ''
            
    def compile( self ):
        '''Compile and return the regular expression.'''
        return regex.compile( self.expression, self.settings ) 
            
    # Simple string methods
    def __str__( self ):
        return self.name if self.name else self.expression
    def __repr__( self ):
        return ( self.name+": " if self.name else "" ) + self.expression + " ("+( "sig" if self.significant else "non" )+")"
        
        
        
class ScanToken(object):
    '''ScanToken objects contain a string as well as some contextual information about the token.'''
    
    # Constructor
    def __init__( self, text = '', expression = None, match = None, strpos = 0, linepos = 0, source = None ):
        '''Construct a ScanToken object. (You shouldn't need to use this.)
        Returns a ScanToken object.
        '''
        self.text = text
        '''The token text.'''
        self.match = match
        '''The regex match which resulted in this token being created.'''
        self.expression = expression
        '''The ScanExp object with which this token is associated.'''
        self.strpos = strpos
        '''The string character position where this token starts.'''
        self.linepos = linepos
        '''The string line position where this token starts.'''
        self.source = source
        '''If specified in ScanExp.tokenize, a way to identify which string this token was in.'''
        
    # Simple string methods
    def __str__( self ):
        return self.text
    def __repr__( self ):
        return (str(self.source)+":" if self.source else "") + str(self.linepos)+":" + str(self.strpos)+": '" + self.text + "' " + str(self.expression)
    

