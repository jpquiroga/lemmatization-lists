from typing import Dict, List, Text
from pkg_resources import resource_stream
import unidecode


def _normalize_word(word: Text) -> Text:
    """
    Normalize a wor:
    - to lower case
    - remove accents
    :param word:
    :return: The normalized word
    """
    return unidecode.unidecode(word.lower())


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

    def get_lemma(self, word: Text, *args) -> List[Text]:
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
        self.lemma_dict_norm = self._build_dictionary_norm(self.lemma_dict)

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

    def _build_dictionary_norm(self, lemma_dict:Dict[Text, List[Text]]):
        res = {}
        for word, lemmas in lemma_dict.items():
            _normalized_lemmas =[_normalize_word(w) for w in lemmas]
            res[word] = _normalized_lemmas
            res[_normalize_word(word)] = _normalized_lemmas
        return res

    def get_lemma(self, word) -> List[Text]:
        """
        Get the lemmas corresponding to a word.
        :param word:
        :return: List of possible lemmas.
        """
        return self.lemma_dict.get(word.lower(), [word.lower()])

    def get_lema_norm(self, word) -> List[Text]:
        """
        Get the normalized lemmas corresponding to a word.
        :param word:
        :return: List of possible lemmas.
        """
        return self.lemma_dict_norm.get(word.lower(), [word.lower()])


class SpanishPosLemmatizer(Lemmatizer):
    """

    """

    def __init__(self):
        self.dict_lemmatizer = DictionaryLemmatizer("es")
        self.infinitives = self._read_verbs()

    def get_lemma(self, word: Text, is_verb: bool) -> List[Text]:
        lemmas = self.dict_lemmatizer.get_lemma(word)
        if is_verb:
            return [l for l in lemmas if l in self.infinitives]
        else:
            return [l for l in lemmas if l not in self.infinitives]

    def _read_verbs(self):
        res = set()
        with resource_stream(__name__, "language/lemma/es/verb_data/verbs_list") as f:
#        with open("src/lemmatization_lists/language/lemma/es/verb_data/verbs_list") as f:
            for l in f.readlines():
                _l = l.decode("utf8").strip()
                if len(_l) > 0:
                    res.add(_l)
                    res.add(_normalize_word(_l))
        return res
