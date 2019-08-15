from .lemmatizers import DictionaryLemmatizer

import unittest


class TestDictionaryLemmatizer(unittest.TestCase):

    def test_dict(self):
        # Load the dictionary
        language = "es"
        lemmatizer = DictionaryLemmatizer(language)

        UNKNOWNWORD = "UNKNOWNWORD"

        self.assertEqual([UNKNOWNWORD.lower()], lemmatizer.get_lemma(UNKNOWNWORD))
        self.assertEqual([UNKNOWNWORD.lower()], lemmatizer.get_lemma(UNKNOWNWORD.lower()))

        self.assertEqual(["puerta"], lemmatizer.get_lemma("puertas"))

        self.assertEqual(["comprar"], lemmatizer.get_lemma("compramos"))

        self.assertEqual({"compra", "comprar"}, set(lemmatizer.get_lemma("compras")))

if __name__ == '__main__':
    unittest.main()
