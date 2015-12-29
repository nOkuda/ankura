"""Runs a demo of the anchor words algorithm

This is really a proof of concept and is ugly as sin.
"""

import os
import numpy

import ankura

@ankura.util.memoize
@ankura.util.pickle_cache('newsgroups.pickle')
def get_newsgroups():
    """Retrieves the 20 newsgroups dataset"""
    news_glob = '/local/jlund3/data/newsgroups/*/*'
    engl_stop = '/local/jlund3/data/stopwords/english.txt'
    news_stop = '/local/jlund3/data/stopwords/newsgroups.txt'
    pipeline = [(ankura.read_glob, news_glob, ankura.tokenize.news),
                (ankura.filter_stopwords, engl_stop),
                (ankura.filter_stopwords, news_stop),
                (ankura.filter_rarewords, 100),
                (ankura.filter_commonwords, 1500)]
    dataset = ankura.run_pipeline(pipeline)
    return dataset


@ankura.util.memoize
@ankura.util.pickle_cache('anchors.pickle')
def default_anchors():
    """Retrieves default anchors for newsgroups using Gram-Schmidt"""
    return ankura.gramschmidt_anchors(get_newsgroups(), 20, 500)


@ankura.util.memoize
def get_topics(dataset, anchors):
    """Gets the topics for 20 newsgroups given a set of anchors"""
    return ankura.recover_topics(dataset, anchors)


def main():
    """Runs the example code"""
    dataset = get_newsgroups()

    anchors = default_anchors()
    # anchors = open('/local/jlund3/data/constraints/newsgroups.txt').readlines()
    # anchors = [line.strip().split() for line in anchors]
    # anchors = [[w for w in a if w in dataset.vocab] for a in anchors]
    # anchors = [[dataset.vocab.index(w) for w in a] for a in anchors]
    # anchors = ankura.util.tuplize(anchors)

    topics = get_topics(dataset, anchors)

    for k in xrange(topics.shape[1]):
        print k,
        for word in numpy.argsort(topics[:, k])[-20:][::-1]:
            print dataset.vocab[word],
        print

    tdataset = ankura.topic_transform(topics, dataset)

    titles = [os.path.dirname(t) for t in tdataset.titles]
    naive = ankura.measure.NaiveBayes(tdataset, titles)
    print naive.validate(tdataset, titles)

if __name__ == '__main__':
    main()
