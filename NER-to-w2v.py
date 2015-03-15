#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
The goal of this script is to transform the output of the Stanford NER tagger of a German text to be suitable for
Google's word2vec program.
Words that have been tagged as NEs are replaced completely by that single tag,
Also the script strips of all punctuation and lowercases each character.
e.g. "Tom/I-Per Sawyer/I-Per sah/O Huck/I-Per ./O" -> "nertagipers sah nertagipers"
"""
__author__ = 'arkadi'

import re
import sys
import os.path

#FILEPATH_IN = '/home/arkadi/Programme/NLPtools/Stanford NER/stanford-ner-2015-01-30/texts/gutenberg_ner_test_tagged.txt'
FILEPATH_IN = sys.argv[1]
GERMAN_NER_TAGS = ['I-MIS', 'B-LOC', 'I-PER', 'I-LOC', 'B-MISC', 'I-ORG', 'B-ORG']

def strip_text(text):
    # Add a white space in the beginning, s. t. all words start with a white space for better parsing
    text = ' ' + text
    # Stripping the non NER tag /O
    text_stripped = re.sub('/O', '', text)
    for tag in GERMAN_NER_TAGS:
        tag_name = ' NERTAG'+tag
        text_stripped = re.sub(' [^ ]*/'+tag, tag_name, text_stripped)
        # Multiple word NERs are concentrated to one tag
        # This might shrink different NERs that occur immediately after another, but they are unseparable anyways
        # text_stripped = re.sub('('+tag_name+')+', tag_name, text_stripped)
    # Lowercasing everything (seems to be buggy for umlauts)
    text_stripped = text_stripped.lower()
    # Dealing with the German umlauts (might still be capitalized) and sharp s
    text_stripped = text_stripped.replace('ä', 'ae').replace('ö', 'oe').replace('ü', 'ue').replace('ß', 'ss')
    text_stripped = text_stripped.replace('Ä', 'ae').replace('Ö', 'oe').replace('Ü', 'ue')
    # Strip the most frequent accents from foreign words
    text_stripped = text_stripped.replace('é', 'e').replace('è', 'e').replace('á', 'a').replace('à', 'a')
    text_stripped = text_stripped.replace('É', 'e').replace('È', 'e').replace('Á', 'a').replace('À', 'a')
    text_stripped = text_stripped.replace('í', 'i').replace('ì', 'i').replace('Í', 'i').replace('Ì', 'i')
    text_stripped = text_stripped.replace('ó', 'o').replace('ò', 'o').replace('Ó', 'o').replace('Ò', 'o')
    text_stripped = text_stripped.replace('œ', 'oe').replace('Œ', 'oe').replace('â', 'a').replace('Â', 'a')
    text_stripped = text_stripped.replace('ñ', 'n').replace('ç', 'c').replace('ø', 'o').replace('å', 'a')
    # Stripping all non alphabetical or numerical tokens that are left (mainly punctuation)
    text_stripped = re.sub('[^a-z1-9 ]', '', text_stripped)
    # Possibly multiple whitespace
    text_stripped = re.sub(' +', ' ', text_stripped)
    return text_stripped

step_size = 10000000 # 10MB chunks 
margin = 500 # Actually have to think about the margin, but it should work fine for gluing
counter = 0

filesize = os.path.getsize(FILEPATH_IN)
sys.stderr.write('%i bytes in file' % filesize)
with open(FILEPATH_IN, 'r') as f_in:
    while counter*step_size < filesize:
        sys.stderr.write('Processing the %i-th step' % (counter + 1))
        f_in.seek(counter*step_size)
        if filesize - counter*step_size < step_size + margin:
            part_length = filesize - counter*step_size
        else:
            part_length = step_size + margin
        text_part = f_in.read(part_length)
        text_stripped = strip_text(text_part)
        sys.stdout.write(text_stripped[:-margin])
        del text_stripped
        counter += 1
    





