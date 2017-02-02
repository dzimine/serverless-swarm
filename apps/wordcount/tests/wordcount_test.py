import unittest
import io

from wordcount import wordcount

line1 = "Nory was a Catholic because her mother was a Catholic"
line2 = "and Nory\'s mother was a Catholic because her father was a Catholic,"
line3 = "and her father was a Catholic because his mother was a Catholic, or had been."


class WordCountTest(unittest.TestCase):
    def test_words_in_text(self):
        expected = [
            ('a', 2), ('catholic', 2),
            ('because', 1), ('her', 1), ('nory', 1), ('mother', 1), ('was', 2)
        ]

        result = wordcount.words_in_text(line1)
        self.assertItemsEqual(result, expected)

    def test_words_reduce(self):
        words = [('foo', 1), ('foo', 2), ('bar', 1), ('buz', 2)]
        expected = [('foo', 3), ('bar', 1), ('buz', 2)]
        result = wordcount.words_reduce(words)
        self.assertItemsEqual(result, expected)

    def test_words_reduce_stream(self):
        stream = io.StringIO(u"foo 1\nfoo 2\nbar 1\nbuz   2")
        expected = [('foo', 3), ('bar', 1), ('buz', 2)]
        result = wordcount.words_reduce_stream(stream)
        self.assertItemsEqual(result, expected)

    def test_map_reduce(self):
        counts = []
        for line in (line1, line2, line3):
            counts.extend(wordcount.words_in_text(line))
        result = wordcount.words_reduce(counts)
        expected = [
            ('a', 6), ('catholic', 6), ('was', 6), ('because', 3), ('her', 3),
            ('mother', 3), ('and', 2), ('father', 2), ('nory', 1), ('been', 1),
            ('his', 1), ('norys', 1), ('or', 1), ('had', 1)
        ]
        self.assertItemsEqual(result, expected)
