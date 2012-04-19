#!/usr/bin/python
#-*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# This file is a plugin for anki flashcard application 
# ---------------------------------------------------------------------------
# File:        More Tolerant SpellCheck.py
# Description: Makes Spellchecking after type in answer more tolerant.
#              ignores:
#                 * upper-/lower case
#                 * white characters
#                 * punctuation (including unicode characters)

# Modified by:       Mike Bradley
# Original Author:   Bernhard Ibertsberger (Bernhard.Ibertsberger@gmx.net)
# Version:           0.02 (2011-04-20)
# License:           GPL
# ---------------------------------------------------------------------------
# Changelog:
# ---- 0.01 -- 2010-06-26 -- Bernhard Ibertsberger ----
#   initial release
# ---- 0.02 -- 2011-04-20 -- Mike Bradley ----
#   modified to make more tolerant
#   changed colors to work more like iOS version
#   changed name in case people still want Bernhard's version
# ---- 2.00 -- 2012-04-10 -- Mike Bradley ----
#   upgraded to work with Anki 2.0
# ---------------------------------------------------------------------------

'''
Created on May 26, 2011

@author: mmbradle
'''
import difflib, string, unittest
from aqt import mw
from aqt.reviewer import *

class TolerantSpellCheck():
    '''
    classdocs
    '''
    useWordBasedCheck = False
    okColor = "#00FF00"
    replaceColor = "#FF0000"
    deleteColor = "#FF0000"
    insertColor = "#FFFF00"

    AA = []
    BB = []
#    spellChecker = SpellCheck()
    
    def __init__(self):
        '''
        Constructor
        '''         
        
    def longestCommonSubstring(self, S1, S2):
        M = [[0]*(1+len(S2)) for i in xrange(1+len(S1))] #build matrix
        longest, x_longest = 0, 0
        for x in xrange(1,1+len(S1)):
            for y in xrange(1,1+len(S2)):
                if S1[x-1] == S2[y-1]:
                    M[x][y] = M[x-1][y-1] + 1
                    if M[x][y]>longest:
                        longest = M[x][y]
                        x_longest  = x
                else:
                    M[x][y] = 0
        return S1[x_longest-longest: x_longest]

    def findSubstr(self, substr, str):
        bPass = False    
        for i in range(len(str)):        
            for j in range(len(substr)):
                if str[0+i+j] == substr[j]:
                    bPass = True #passes so far, loop again to see if it continues to do so
                else:
                    bPass = False                 
                    break
            if bPass == True:
                break            
        if bPass:
            return i
        else:
            return -1
    def check(self, old, new):
        ret = ""; 
        if ((new == "") or (new==" ")):
            return ""
        self.AA=[]
        self.BB=[]
        try:
            sz = mw.bodyView.main.currentCard.cardModel.answerFontSize
            fn = mw.bodyView.main.currentCard.cardModel.answerFontFamily
        except:
            sz = 18
            fn = "Times New Roman"
        st = "background: %s; color: #000; font-size: %dpx; font-family: %s;"
        ok = st % (self.okColor, sz, fn)
        replace = st % (self.replaceColor, sz, fn)
        delete = st % (self.deleteColor, sz, fn)
        delete += "text-decoration: line-through;"
        insert = st % (self.insertColor, sz, fn)

        old = self.__stripPunct(old).lower()
        new = self.__stripPunct(new).lower()        
        
        old = old.split()
        new = new.split()
        if old == new:
            return ("<span style='%s'>%s</span>" % (ok, "Good!"))
                
#        selfspellChecker.trainMore(old)        
        #spell correct        
#        for i in range(len(new)):
#            new[i] = self.spellChecker.correct(new[i])
        #for i in range(len(old)):
        #    old[i] = correct(old[i])                        
        
        self.parseDiff(old, new)        
     
        for i in range(len(self.AA)):
            if self.AA[i][1] == 0:
                ret += ("<span style='%s'>%s</span>" % (ok, self.AA[i][0]))
            elif self.AA[i][1] == 3:
                ret += ("<span style='%s'>%s</span>"
                        % (insert, '[' ))
                ret += ("<span style='%s'>%s</span>"
                        % (replace, self.BB[i][0] ))
                ret += ("<span style='%s'>%s</span>"
                        % (insert, '/' + self.AA[i][0] + ']' ))
            elif self.AA[i][1] == 1:
                ret += ("<span style='%s'>%s</span>" % (delete, self.BB[i][0]))
            elif self.AA[i][1] == 2:
                ret += ("<span style='%s'>%s</span>" % (insert, self.AA[i][0]))
        return ret    
        
    def parseDiff(self, A, B):    
        #function
        aTemp = A
        bTemp = B
        lcsArray = []
        lcsLocA, lcsLocB = 0, 0
        lcsTemp = self.longestCommonSubstring(aTemp, bTemp)
        lcsLocA = self.findSubstr(lcsTemp, aTemp)
        lcsLocB = self.findSubstr(lcsTemp, bTemp)
        while (lcsTemp):
            lcsArray.append((lcsTemp, lcsLocA))
            aTemp=aTemp[:lcsLocA] + aTemp[lcsLocA+len(lcsTemp):]
            bTemp=bTemp[:lcsLocB] + bTemp[lcsLocB+len(lcsTemp):]
            lcsTemp = self.longestCommonSubstring(aTemp, bTemp)
            lcsLocA = self.findSubstr(lcsTemp, aTemp)
            lcsLocB = self.findSubstr(lcsTemp, bTemp)
        lcsArray = sorted(lcsArray, key=lambda student: student[1])
        
        aSubstrLoc, bSubstrLoc = 0, 0
        for lcs in lcsArray:                 
            aSubstrLoc = self.findSubstr(lcs[0], A)
            bSubstrLoc = self.findSubstr(lcs[0], B)
            aCode = 1
            if aSubstrLoc > 0:            
                aCode = 2            
            bCode = 1
            if bSubstrLoc > 0:
                bCode = 2
            if aCode == bCode:
                aCode = 3
                bCode = 3        
            assert(aSubstrLoc >= 0)
            assert(bSubstrLoc >= 0)
            if ((aSubstrLoc > 0)or(bSubstrLoc > 0)):
                self.AA.append((" ".join(A[0:aSubstrLoc]),aCode))
                self.BB.append((" ".join(B[0:bSubstrLoc]),bCode))
                A = A[aSubstrLoc:]
                B = B[bSubstrLoc:]
            self.AA.append((" "+" ".join(A[:len(lcs[0])])+" ",0)) 
            self.BB.append((" "+" ".join(B[:len(lcs[0])])+" ",0))            
            A = A[len(lcs[0]):]
            B = B[len(lcs[0]):]            
        aCode = 1
        if len(A) > 0:
            aCode = 2
        bCode = 1
        if len(B) > 0:
            bCode = 2
        if aCode == bCode:
            aCode = 3
            bCode = 3
        if A or B:
            self.AA.append((" ".join(A),aCode))
            self.BB.append((" ".join(B),bCode))
   
    def __strip_accents(self, string):
        import unicodedata
        return unicodedata.normalize('NFKD', string).encode('ASCII', errors='ignore')
    def __stripPunct(self, input):
        input = self.__strip_accents(input)
        input = input.translate(None, string.punctuation)
        return input
    def spellCheck(self, a, b):
        if b == "" or b==" ":
            return "";
        ret = ""
        
        a = a.split()
        b = b.split()
        aa=list(a)
        bb=list(b)
        for i in range(len(a)):
            a[i] = self.__stripPunct(a[i])
            a[i] = a[i].upper()
        for i in range(len(b)):
            b[i] = self.__stripPunct(b[i])
            b[i] = b[i].upper()
        
        s = difflib.SequenceMatcher(None, b, a)
 
        try:
            sz = mw.bodyView.main.currentCard.cardModel.answerFontSize
            fn = mw.bodyView.main.currentCard.cardModel.answerFontFamily
        except:
            sz = 18
            fn = "Times New Roman"        
        st = "background: %s; color: #000; font-size: %dpx; font-family: %s;"
        ok = st % (self.okColor, sz, fn)
        replace = st % (self.replaceColor, sz, fn)
        delete = st % (self.deleteColor, sz, fn)
        delete += "text-decoration: line-through;"
        insert = st % (self.insertColor, sz, fn)
     
        for tag, i1, i2, j1, j2 in s.get_opcodes():
            if tag == "equal":
                ret += ("<span style='%s'>%s</span>" % (ok, " ".join(aa[j1:j2])))                
            elif tag == "replace":
                ret += ("<span style='%s'>%s</span>"
                        % (insert, '[' ))
                ret += ("<span style='%s'>%s</span>"
                        % (replace, " ".join(bb[i1:i2]) ))
                ret += ("<span style='%s'>%s</span>"
                        % (insert, '/' + " ".join(aa[j1:j2]) + ']' ))
            elif tag == "delete":
                ret += ("<span style='%s'>%s</span>" % (delete, " ".join(bb[i1:i2])))
            elif tag == "insert":
                ret += ("<span style='%s'>%s</span>" % (insert, " ".join(aa[j1:j2])))
            if j2 < len(aa):
                ret += ("<span style='%s'>%s</span>" % (ok, " "))     
        return ret    
    
def tolerantCorrect(a, b):
    tolSpell = TolerantSpellCheck()    
    if tolSpell.useWordBasedCheck:
        return tolSpell.check(a, b)
    else:
        return tolSpell.spellCheck(a, b)

mw.reviewer.correct = tolerantCorrect

class SpellCheckTest(unittest.TestCase):                            
#    def test1Spell(self):                
#        verse  = u"and to put on the new self, created in"
#        input  = u"put on the new sllf created in the"                          
#        tolerantCorrect(input, verse)
    def test2Spell(self):                
        verse  = u"to put off your old self, which belongs to your former manner of life and is corrupt through deceitful desires,"
        input  = u"to off put your old sllf which belongs to your former manner of life and is corrupt through decietful desires"                          
        verse = u"1 2 3"
        input = u"2 3"
        tolerantCorrect(verse, input)

if __name__ == "__main__":    
    unittest.main() 

