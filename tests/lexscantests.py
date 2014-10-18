
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



import lexscan
import unittest
import time



class LexScanTests( unittest.TestCase ):
    '''Class contains unit tests.'''
    
    teststr = "this!!is !! a test!!!!!! yay"
    wordexp = lexscan.ScanExp( r'\w+' )
    bangexp = lexscan.ScanExp( r'!+' )
    spaceexp = lexscan.ScanExp( r'\s+', significant = False )
    expressions = ( wordexp, bangexp, spaceexp )
    
    def test_tokenize( self ):
        '''Make sure a simple string is tokenized correctly.'''
        
        # Get stuff ready
        expected = ( "this", "!!", "is", "!!", "a", "test", "!!!!!!", "yay" )
        
        # Beam it up
        tokens = lexscan.tokenize( LexScanTests.teststr, LexScanTests.expressions )
        
        # Check equivalency
        assert len(tokens) == len(expected)
        for i in range(0, len(tokens)):
            assert str(tokens[i]) == expected[i]
            
    def test_cacheclearing( self ):
        '''Make sure cache clearing works as expected, text the same string multiple times.'''
        
        # Get stuff ready
        teststr="one two three four"
        expected = ( "one", "two", "three", "four" )
        
        for i in range(0,3):
            print "Running cache clearing test round #",i
            # Beam it up
            tokens = lexscan.tokenize( teststr, LexScanTests.expressions )
            
            # Check equivalency
            assert len(tokens) == len(expected)
            for i in range(0, len(tokens)):
                assert str(tokens[i]) == expected[i]
            
    
    def test_unrecognizedchars( self ):
        '''Make sure unrecognized chars are parsed correctly.'''
        
        # Get stuff ready
        teststr = LexScanTests.teststr + "?? ?"
        expected = ( "this", "!!", "is", "!!", "a", "test", "!!!!!!", "yay", "?", "?", "?" )
        
        # Beam it up
        tokens = lexscan.tokenize( teststr, LexScanTests.expressions )
        
        # Check equivalency
        assert len(tokens) == len(expected)
        for i in range(0, len(tokens)):
            assert str(tokens[i]) == expected[i]
        
    def test_cachespeed( self ):
        '''Make sure match caching hasn't buggered up and that it's still faster than not caching.'''
        
        # Don't cache
        class ScanExpNoCache(lexscan.ScanExp):
            def search( self, start = 0 ):
                if not self.regex:
                    self.compile()
                return self.regex.search( self.cachestr, start )
                
        # Run a test N times
        def test( exp, count ):
            init = time.clock()
            for i in xrange(0, count):
                lexscan.tokenize( LexScanTests.teststr, exp )
            return time.clock()-init

        # Make test data
        expA = LexScanTests.expressions
        expB = ( ScanExpNoCache(r'\w+'), ScanExpNoCache(r'!+'), ScanExpNoCache(r'\s+', significant = False) )
        
        # Initialize time-tracking vars
        totalA, totalB = 0, 0
        minA, maxA, minB, maxB = 0, 0, 0, 0

        # How many times are we going to do these things?
        testcount = 4
        testtimes = 10000
        testrange = range(0,testcount)

        # I heard once that a sort of warmup was good for getting consistent results
        test( expA, 1000 )
        test( expB, 1000 )

        # Do the testing
        for i in testrange:
            print "Running cache vs no cache test, #",i
            timeA = test( expA, testtimes )
            timeB = test( expB, testtimes )
            minA = timeA if minA == 0 else min( minA, timeA )
            maxA = max( maxA, timeA )
            minB = timeB if minB == 0 else min( minB, timeB )
            maxB = max( maxB, timeB )
            totalA += timeA
            totalB += timeB

        meanA = totalA / testcount
        meanB = totalB / testcount
            
        # Output the results
        print "A:"
        print "\tTotal:",totalA
        print "\tMean:",meanA
        print "\tRange:",minA,",",maxA
        print "B:"
        print "\tTotal:",totalB
        print "\tMean:",meanB
        print "\tRange:",minB,",",maxB
        if minA > minB:
            print "B is",(minA/minB*100),"percent as fast as A."
        else:
            print "A is",(minB/minA*100),"percent as fast as B."
        
        # Make sure everything is on-track
        assert minA < minB



if __name__ == '__main__':
    print "lexscan version: " + lexscan.__version__
    unittest.main()