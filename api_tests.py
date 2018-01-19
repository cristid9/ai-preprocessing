import unittest
from api import get_phrases
from api import parse_phrase

class TestStringMethods(unittest.TestCase):

    file_path = "file.txt"
    file_path2 = "file2.txt"

    def test_get_phrase_file1(self):
        self.assertEquals(get_phrases(self.file_path), ['Foo bar'])

    def test_get_phrase_file2(self):
        self.assertEquals(get_phrases(self.file_path2), ['Foo', 'bar'])

    def test_parse_phrase(self):
        self.assertEquals(parse_phrase(parse_phrase('Foo bar')),
                          [[4, 'foo', 'foo', 'noun'], [5, 'bar', 'bar', 'noun']])

if __name__ == '__main__':
    unittest.main()