import string
from operator import itemgetter


def words_in_text(text):
    words = {}
    for word in text.translate(None, string.punctuation).lower().split():
        count = words.setdefault(word, 0)
        words[word] = count + 1
    return words.items()


def words_reduce(words):
    """
    Word count reduce function.

    words: list of tuples [(word,count),...] where words arent unique
    """
    result = {}
    for word, count in words:
        result.update({word: result.get(word, 0) + count})
    # return sorted(result.iteritems(), key=lambda (k, v): (v, k), reverse=True)
    return sorted(result.items(), key=itemgetter(1), reverse=True)


def words_reduce_stream(stream):
    """
    Word count reduce function with iterator interface.

    stream: an iterator object, like file e.g ``io.TextIOWrapper``.
    """
    result = {}
    for line in stream:
        (word, count) = line.split()
        count = int(count)
        result.update({word: result.get(word, 0) + count})
    return sorted(result.items(), key=itemgetter(1), reverse=True)
