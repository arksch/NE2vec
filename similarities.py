from gensim.models import word2vec
import click

TEST_FILE = 'test_set'
MODEL_FILE = '/media/arkadi/arkadis_ext/NLP_data/guten.bin'

def check_word(model, word, tag):
    """ Checking whether a word with a person tag would be tagged correctly by the model

    :type model: gensim.model.word2vec.Word2Vec object
    :return: 4-tuple (per-distance, loc-distance, misc-distance, matching the given tag)
    :rtype: (float, float, float, bool)
    """
    per = model.similarity('nertagiper', word)
    loc = model.similarity('nertagiloc', word)
    misc = model.similarity('nertagimisc', word)
    if per == max([per, loc, misc]) and tag == 'per':
        match = 'TP'
    elif per != max([per, loc, misc]) and tag != 'per':
        match = 'TN'
    elif per == max([per, loc, misc]) and tag != 'per':
        match = 'FP'
    elif per != max([per, loc, misc]) and tag == 'per':
        match = 'FN'
    return per, loc, misc, match

@click.command()
@click.option('--model', default='/media/arkadi/arkadis_ext/NLP_data/guten.bin',
              type=click.Path(exists=True), help='A binary model of word2vec')
@click.option('--test', default='test_set',
              type=click.Path(exists=True), help='A file for testing')
def main(model, test):
    model_bin = word2vec.Word2Vec.load_word2vec_format(model, binary=True)

    with open(test, 'r') as f:
        test_word_tags = [(line.split()[0], line.split()[1]) for line in f.readlines()]

    tp = 0.0
    fp = 0.0
    tn = 0.0
    fn = 0.0

    print "Evaluation of the similarity model"
    print "=================================="
    print "word".ljust(15)+"\tperson   \tlocation \tmisc     \tmatch"  #15\t9\t9\t9\t
    for word, tag in test_word_tags:
        per, loc, misc, match = check_word(model_bin, word, tag)
        if match == 'TP':
            tp += 1
        elif match == 'TN':
            tn += 1
        elif match == 'FP':
            fp += 1
        elif match == 'FN':
            fn += 1
        print "%s\t%9.8f\t%9.8f\t%9.8f\t%s" % (word.ljust(15), per, loc, misc, match)

    recall = 100 * tp / (tp + fn)
    precision = 100 * tp / (tp + fp)
    fscore = 2 * recall * precision / (recall + precision)

    print "Recall:\t%6.3f" % recall
    print "Precision:\t%6.3f" % precision
    print "F-score:\t%6.3f" % fscore

if __name__ == '__main__':
    main()