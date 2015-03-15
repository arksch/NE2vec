# Named Entities and Word Representations

This code was created for an experiment to try recognizing German nouns that can refer to persons by their proximity to a class of named entities in a word representation. This is giving a small tutorial how to reproduce this experiment. You find the theoretical insights in the uploaded pdf file.
I am assuming a basic understanding of Python and the command line. This experiment was done on Ubuntu 14.04, and I do not know how reproducable it is on other OS. You do need at least 2GB of RAM to run this experiment, even though it is much more convenient with a a lot more.

## Required Software

You will have to install some software, unless you already have it. 

### Clone this Repository

Since you are using github I'm assuming you have git installed. Open your terminal and go to the folder where you want to install the repository.
    
    git clone this_sites_url

### Stanford's Named Entity Recognition

This is the weak point. Stanford's NER takes an aweful lot of memory (about 1000 times the input files size).
Download from the following site the Named Entity Recognizer and also the German classifiers from further below.
    
    http://nlp.stanford.edu/software/CRF-NER.shtml
    http://nlp.stanford.edu/software/stanford-ner-2012-05-22-german.tgz
Follow the instructions there, which is basically unpacking it to some folder where you find it later on.

### Google's word2vec

This is a nice piece of software, but read the whole paragraph before you start installing. You find everything you need here
    
    https://code.google.com/p/word2vec/
To follow their instructions you would need Apache's Subversion (svn). If you do not have it you might just try to download the files by hand.
You do not have to run the demo scripts, but it is nice.

### gensim (Python API for word2vec)

I hope you have pip, then you can just type
    
    $ pip install --upgrade gensim    
Otherwise I suggest you install pip or you check out this page
    
    http://radimrehurek.com/gensim/install.html

## Downloading the Data

The experiment worked with the Gutenberg Corpus. To download all German books (about 500MB) type
    
    $ wget -t inf -o log -w 2 -m -H "http://www.gutenberg.org/robot/harvest?filetypes[]=txt&langs[]=de"
    
This is actually not too much data. If you feel like writing another preprocessing script, you can also download the newest German Wikipedia dump from
    
    http://dumps.wikimedia.org/dewiki/

## Running the Experiment

### Cleaning the Data

With this repository you downloaded some scripts.
Run the script to strip the headers and footers of Project Gutenberg and concatenate all zip files into one text file. The output will be saved in a file gutenberg_corpus.txt in the same folder where the Gutenberg corpus is located (if you did not rename it its called www.gutenberg.lib.md.us/)

    $ ./gutenberg.py www.gutenberg.lib.md.us/

### Creating the Input for word2vec

The repository also contains a script that is running the Stanford NER with the German classifier. You might want to open it and give it more memory. Note that you will probably have to split the Gutenberg Corpus into chunks of about 1/1000 the size of your memory to run this script and concatenate the outcome together. This is a nice practice in Python for you.
On each chunk you can run

    $ ./path/to/stanfordNER/ner-ger.sh www.gutenberg.lib.md.us/gutenberg_corpus_chunk1.txt > output_file1

Once you are done concatenating everything back together, you can use the following script to convert this text to be read by word2vec (converting umlauts, stripping of unknown characters, lowercasing)

    $ ./NER-to-w2v.py input_file > output_file
 
### Running word2vec with Parameters
   
Now you can create your own binary word representation with word2vec (for an explanation of the variables see their homepage). Here are two different parameter settings to play with:

    $ time ./word2vec -train /media/arkadi/arkadis_ext/NLP_data/Rammis_gutenberg/gutenberg_corpus_ner_real_clean.txt -output guten.bin -skipgram 10 -size 300 -window 5 -negative 0 -hs 1 -sample 1e-4 -threads 2 -binary 1 -save-vocab defull-vocab.txt > guten.bin
    Vocab size: 262369
    Words in train file: 71619017
    Alpha: 0.000005  Progress: 100.00%  Words/thread/sec: 52.51k  
    real	70m43.637s
    user	113m49.045s
    sys	0m26.959s

    $ time ./word2vec -train /media/arkadi/arkadis_ext/NLP_data/Rammis_gutenberg/gutenberg_corpus_ner_real_clean.txt -output guten_neg10.bin -skipgram 10 -size 300 -window 10 -negative 10 -hs 1 -sample 1e-3 -threads 2 -binary 1 -save-vocab defull-vocab.txt > guten_neg10.bin
    Vocab size: 262369
    Words in train file: 71619017
    Alpha: 0.000005  Progress: 100.00%  Words/thread/sec: 20.70k  
    real	168m32.287s
    user	288m13.476s
    sys	0m44.350s

### Playing around!

You are finally done with creating your binary word representations?! Start python, or ipython and play!
    
    from gensim.models import word2vec
    model = word2vec.Word2Vec.load_word2vec_format('path/to/your/binary_word_repr', binary=True)
    model.most_similar(positive=['koenig', 'frau'], negative=['mann'])
    model.most_similar(positive=['nertagiper'], negative=[])
    model.doesnt_match(['nertagiper', 'nertagiloc', 'nertagimisc'])
    model.similarity('nertagiper', 'student')
    model.similarity('nertagiloc', 'haus')
    model.similarity('nertagimisc', 'nation')

To play around you might as well alter the text file test_set by adding new lines with a word and a tag. Then run
    
    python similarities.py --model /path/to/your/binary_word_repr --test /path/to/your/test_file

What does this actually mean? It means you can compare nouns for their similarity to the person, location and miscellanious tags to to which the might refer.

### A first evaluation with the given test set
|word           	|person   	|location 	|misc     	|match |
| ----------------- | --------- | --------- | --------- | ---- |
|polizist       	|0.10749246	|0.01489580	|0.03354150	|TP |
|student        	|0.20737271	|0.02934145	|0.04367834	|TP |
|lehrer         	|0.12964790	|-0.12548146	|-0.01557306	|TP|
|lehrerin       	|0.08681190	|-0.08561248	|-0.04076674	|TP|
|gott           	|0.15922870	|-0.01843374	|-0.08631332	|FP|
|baum           	|-0.06563630	|-0.05539430	|-0.05834422	|TN|
|haus           	|0.06055429	|0.16598518	|-0.07558561	|TN|
|gross          	|-0.08251506	|-0.05296010	|-0.01279388	|TN|
|klein          	|0.01614168	|-0.02968299	|-0.06549737	|FP|
|nation         	|-0.12702281	|0.02772727	|0.22280701	|TN|
|staat          	|-0.02131612	|-0.00057563	|0.07930892	|TN|
|land           	|-0.01411605	|0.30458365	|0.06202623	|TN|
|erde           	|-0.00483644	|0.07872798	|-0.01798863	|TN|
|kind           	|0.07643456	|0.00363171	|-0.07258882	|TP|
|mensch         	|0.00071798	|-0.12818525	|-0.07854126	|TP|
|mann           	|0.22271588	|0.03623078	|0.02678832	|TP|
|frau           	|0.37619667	|0.05319752	|0.02605344	|TP|
|hund           	|0.10778271	|-0.08325005	|-0.08226270	|FP|
|katze          	|0.02991319	|-0.04702012	|-0.04696872	|FP|
|maus           	|0.01681365	|0.00533434	|0.01775033	|TN|
|schnell        	|0.10562476	|0.03038920	|-0.03581870	|FP|
|langsam        	|0.02893238	|-0.06661929	|-0.02774489	|FP|
|leicht         	|-0.02133644	|-0.09002297	|-0.05527122	|FP|
|er             	|0.39979196	|0.12971292	|-0.02913975	|TP|
|sie            	|0.30369458	|0.07522399	|0.01552288	|TP|
|es             	|0.15317690	|0.04054807	|-0.01511156	|FP|
|kreativ        	|-0.08148986	|-0.09344466	|0.03209482	|TN|
|sehr           	|0.08762989	|-0.02305989	|0.02555214	|FP|
|morgen         	|0.14761052	|0.11134531	|-0.06228537	|FP|
|Recall	|100.000| | | |
|Precision |50.000| | | |
|F-score|	66.667| | | |



