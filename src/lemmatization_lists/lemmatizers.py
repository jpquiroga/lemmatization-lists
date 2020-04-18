from typing import Dict, List, Set, Text
from pkg_resources import resource_stream
import unidecode
from spacy.language import Language
from spacy.tokens import Doc


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
        """
        :param lang: Language. Valid values are contained in SUPPORTED_LANGUAGES.
        """
        super().__init__(lang)
        if lang not in self.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageException("Language '{}' is not supported".format(lang))
        self.lemma_dict = self._build_dictionary(lang)
        self.lemma_dict_norm = self._build_dictionary_norm(self.lemma_dict)

    def _add_lemmatization_entry(self, lemma_dict: Dict[Text, List[Text]], word, lemma):
        """
        :param lemma_dict:
        :param word:
        :param lemma:
        """
        lemma_list = lemma_dict.get(word, [])
        if lemma not in lemma_list:
            lemma_list.append(lemma)
            lemma_dict[word] = lemma_list

    def _build_dictionary(self, lang: Text) -> Dict[Text, List[Text]]:
        """
        Build a dictionary of lemmas from the corresponding resources file.
        :param lang: Language. Valid values are contained in SUPPORTED_LANGUAGES.
        :return: The dictionary of lemmas.
        """
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

    def _build_dictionary_norm(self, lemma_dict:Dict[Text, List[Text]]) -> Dict[Text, List[Text]]:
        """
        Normalize a dictionary of lemmas.
        :param lemma_dict:
        :return: Normalized dictionary of lemmas.
        """
        res = {}
        for word, lemmas in lemma_dict.items():
            _normalized_lemmas = [_normalize_word(w) for w in lemmas]
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
    Spanish lemmatizer based on POS tagging, using Spacy.
    """

    VERB_POS_TAGS = {
        "VERB",
        "AUX"
    }

    def __init__(self):
        self.dict_lemmatizer = DictionaryLemmatizer("es")
        self.infinitives = self._read_verbs()

    def get_lemma(self, word: Text, is_verb: bool) -> List[Text]:
        """
        Lemmatize one word.
        :param word:
        :param is_verb:
        :return: List of possible lemmas.
        """
        lemmas = self.dict_lemmatizer.get_lemma(word)
        if is_verb:
            res = [l for l in lemmas if l in self.infinitives]
            if res == None or len(res) == 0:
                return [word]
            return res
        else:
            res = [l for l in lemmas if l not in self.infinitives]
            if res == None or len(res) == 0:
                return [word]
            return res

    def _get_pos(self, parsed_sentence: Doc) -> List[Text]:
        """
        :param parsed_sentence: Spacy parsed sentence.
        :return: List of POS tags corresponding to the parsed_sentence.
        """
        return [t.pos_ for t in parsed_sentence]

    def _get_pos_is_verb(self, parsed_sentence: Doc) -> List[bool]:
        """
        :param parsed_sentence: Spacy parsed sentence.
        :return: List of booleans telling whether the corresponding word is a verb.
        """
        return [t in self.VERB_POS_TAGS for t in self._get_pos(parsed_sentence)]

    def get_lemma_sentence(self, sentence: Text, nlp_model: Language) -> List[List[Text]]:
        """
        Lemmatize a sentence.

        :param sentence: Sentence a string.
        :param nlp_model: Spacy language model.
        :return: List of lists of lemmas (one list of lemmas per sentence word).
        """
        parsed_sentence = nlp_model(sentence, disable = ['parser', 'ner'])
        pos_bool_list = self._get_pos_is_verb(parsed_sentence)
        res = []
        for i, t in enumerate(parsed_sentence):
            res.append(self.get_lemma(str(t), pos_bool_list[i]))
        return res

    def _read_verbs(self) -> Set[Text]:
        """
        Read the list of verbs from resources.
        :return: Set of verb infinitives.
        """
        res = set()
#        with resource_stream(__name__, "language/lemma/es/verb_data/verbs_list") as f:
        with resource_stream(__name__, "language/lemma/es/verb_data/verbs_list_final") as f:
            for l in f.readlines():
                _l = l.decode("utf8").strip()
                if len(_l) > 0:
                    res.add(_l)
                    res.add(_normalize_word(_l))
        return res
