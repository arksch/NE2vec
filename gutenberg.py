#!/usr/bin/python
# This script uses utf-8 encoding
"""
Written by Arkadi Schelling
2015-02-13
The Project Gutenberg provides a good source for NLP. Still, it does not have standard headers and tails to their texts.
This is very annoying for most NLP tasks, since the data has to be cleaned. This script is made to work for German,
but it should work for any other language than English as well.
You can write a different list of keywords, to improve the performance.
This script takes all files from the Gutenberg folder structure, strips of the headers and tails and concatenates
the rest into one single text file. A log file is written, that stores Gutenberg key words, to see whether everything
worked fine.
Downloaded all German txt files from Project Gutenberg
$ wget -t inf -o log -w 2 -m -H "http://www.gutenberg.org/robot/harvest?filetypes[]=txt&langs[]=de"

Run this script by typing:
./gutenberg.py gutenberg_path [output_file]
gutenberg_path is the path of the Gutenberg files
output_file is the name of the output file to write to the folder, where the script is called.
If not specified the output will be saved in the Gutenberg root folder.
"""
import logging
import os
import zipfile
import sys

### Parsing the arguments ###
GUTENBERG_ROOT = sys.argv[1] # "/media/arkadi/Arkadis Externe/NLP_data/Gutenberg/2015-02-08_de_dump/www.gutenberg.lib.md.us/"
try:
    OUTPUT_PATH = os.path.join(sys.argv[0], sys.argv[2])
except:
    OUTPUT_PATH = os.path.join(GUTENBERG_ROOT, 'gutenberg_corpus.txt')
LOG_PATH = os.path.join(os.path.split(OUTPUT_PATH)[0], 'gutenberg_log.txt')

GUTENBERG_KEY_WORDS = ['Gutenberg', 'gutenberg', 'GUTENBERG', 'http://', 'ETEXT', 'Etext', 'etext', 'Produced']
MIN_TEXT_LENGTH = 1000
MAX_HEADER_LENGTH = 150
MAX_TAIL_LENGTH = 850
MAX_ETEXT_HEADER = 650
MAX_ETEXT_TAIL = 250

logging.basicConfig(filename=LOG_PATH, level=logging.INFO)

def folders_to_text():
    with open(OUTPUT_PATH, 'a') as f_out:
        for root, subFolders, file_list in os.walk(GUTENBERG_ROOT):
            for zip_file in file_list:
                if zip_file.endswith('.zip'):
                    try:
                        zip_in = zipfile.ZipFile(os.path.join(root, zip_file), 'r')
                        for member in zip_in.namelist():
                            # namelist() finds all files, also if they are in subfolders of the zip archive
                            if member.endswith('.txt'):
                                f_in = zip_in.open(member, 'r')
                                text = f_in.readlines()
                                try:
                                    # This assertion actually loses some texts, but only very short ones.
                                    assert len(text) > MIN_TEXT_LENGTH,\
                                        'Text not long enough to be stripped safely of Gutenberg header and footer.'
                                    # Strip header and footer and concatenate to one text
                                    text = strip_Gutenberg_meta(text, root)
                                    # This text is usually decoded in latin1 = iso-8859-1
                                    try:
                                        text = text.decode("iso-8859-1").encode("utf-8")
                                    except UnicodeError, e:
                                        logging.warning(
                                            'Unicode error in file %s' % (os.path.join(root, zip_file), str(e)))

                                    f_out.write(text)
                                    # See whether key words are still left and log them
                                    find_Gutenberg_key_words(text,
                                                             text_path=os.path.join(root, zip_file),
                                                             logging_bool=True)
                                except Exception, e:
                                    logging.warning('Exception in file %s\n%s' % (os.path.join(root, zip_file), str(e)))
                    except Exception, e:
                        logging.warning('Exception while opening zipfile %s\n%s' % (os.path.join(root, zip_file), str(e)))

def strip_Gutenberg_meta(text, root):
    # Checking the first and last lines whether we find keywords
    # The texts in the etext folder seem to have a longer preamble
    if 'etext' in root:
        end_header = max([i for i in range(0, MAX_ETEXT_HEADER) if find_Gutenberg_key_words(text[i]) != []])
        start_tail = max([i for i in range(0, MAX_ETEXT_TAIL) if find_Gutenberg_key_words(text[-i]) != []])
    else:
        end_header = max([i for i in range(0, MAX_HEADER_LENGTH) if find_Gutenberg_key_words(text[i]) != []])
        start_tail = max([i for i in range(0, MAX_TAIL_LENGTH) if find_Gutenberg_key_words(text[-i]) != []])
    return ''.join(text[end_header + 1 : - (start_tail + 1)])

def find_Gutenberg_key_words(text, text_path=None, logging_bool=False):
    indices = []
    for word in GUTENBERG_KEY_WORDS:
        word_index = text.find(word)
        # returns -1 if word is not found
        if word_index != -1:
            indices.append(word_index)
            if logging_bool:
                logging.info('File: %s\nIndex: %s' % (text_path, word_index))
                logging.info(text[word_index - 100 : word_index + 100])
    return indices


if __name__ == '__main__':
    folders_to_text()
