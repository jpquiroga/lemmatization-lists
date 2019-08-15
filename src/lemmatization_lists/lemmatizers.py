from typing import Dict, List, Text
from pkg_resources import resource_stream

class UnsupportedLanguageException(Exception):
    """
    Raised when a non supported language is requested.
    """
    pass


class Lemmatizer(object):
    """
    Abstract class for lemmatizers.
    """

    SUPPORTED_LANGUAGES = [
        "ast",
        "bg",
        "ca",
        "cs",
        "cy",
        "de",
        "en",
        "es",
        "et",
        "fa",
        "fr",
        "ga",
        "gd",
        "gl",
        "gv",
        "hu",
        "it",
        "pt",
        "ro",
        "sk",
        "sl",
        "sv",
        "uk"
    ]

    def __init__(self, lang: Text):
        """
        :param lang: Language code. Supported values are defined in SUPPORTED_LANGUAGES.
        """
        if lang not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageException("Language '{}' is not supported".format(lang))
        self.lang = lang
        pass

    def get_lemma(self, word: Text) -> List[Text]:
        """
        Get the lemma corresponding to a given word
        :param word:
        :return: A list with the identified lemmas. More than one lemma may be returned due to language
          ambiguity.
        """
        raise(NotImplementedError("{} is an abstract class and cannot be directly used.".format(self.__class__)))


class DictionaryLemmatizer(Lemmatizer):
    """
    Lemmatizer based on an in memory dictionary.
    """

    def __init__(self, lang: Text):
        super().__init__(lang)
        self.lemma_dict = self._build_dictionary(lang)

#    def _get_lemmatization_list_file(self, lang: Text) -> Text:
#        if lang not in self.SUPPORTED_LANGUAGES:
#            raise UnsupportedLanguageException("Language '{}' is not supported".format(lang))
#        # TODO

    def _add_lemmatization_entry(self, lemma_dict: Dict[Text, List[Text]], word, lemma):
        lemma_list = lemma_dict.get(word, [])
        if lemma not in lemma_list:
            lemma_list.append(lemma)
            lemma_dict[word] = lemma_list

    def _build_dictionary(self, lang: Text) -> Dict[Text, List[Text]]:
        lemma_dict = {}
        with resource_stream(__name__, "data/lemmatization-{}.txt".format(lang)) as f:
            for s in f.readlines():
                l = s.decode('utf-8-sig').strip().split()
                if l is None or len(l) < 2:
                    continue
                self._add_lemmatization_entry(lemma_dict, l[1], l[0])
                # Ensure that lemmas themselves are also included into the dictionary
                self._add_lemmatization_entry(lemma_dict, l[0], l[0])
        return lemma_dict

    def get_lemma(self, word) -> List[Text]:
        return self.lemma_dict.get(word.lower(), [word.lower()])

