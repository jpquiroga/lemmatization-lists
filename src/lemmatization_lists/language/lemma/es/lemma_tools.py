# coding=utf-8

import os.path
import configparser
import sqlite3
import logging
from nltk.stem import SnowballStemmer
import threading



_BASE_RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "verb_data")
_VERB_DB_DIR = os.path.join(os.path.dirname(__file__), "verb_db")
_SPANISH_VERB_DB_PATH = os.path.join(_VERB_DB_DIR, "spanish_verbs.db")
_DETAILED_INFO_MAPPING_PATH = os.path.join(_BASE_RESOURCES_DIR, "detailed_info_mapping.conf")
_VERB_LIST_PATH = os.path.join(_BASE_RESOURCES_DIR, "verbs_list_final")
_MODELS_PATH = os.path.join(_BASE_RESOURCES_DIR, "models")
_MODEL_REGULAR_AR = "regular_ar"
_MODEL_REGULAR_ER = "regular_er"
_MODEL_REGULAR_IR = "regular_ir"


class SpanishVerbFlexioner:
    """
    Spanish verbs flexioner.
    """

    def __init__(self):
        self.irregular_verbs_models = {}
        self.regular_model_ar = None
        self.regular_model_er = None
        self.regular_model_ir = None
        self._load_models()

    def _load_models(self):
        """
        Load models information from disk.
        """
        with open(_MODELS_PATH, "r") as f:
            for _s in f.readlines():
                _s = _s.strip()
                if len(_s) > 0:
                    _model = ConjugationModel.load(_s)
                    for _irregular_verb in _model.verbs:
                        self.irregular_verbs_models[_irregular_verb] = _model

        self.regular_model_ar = ConjugationModel.load(_MODEL_REGULAR_AR)
        self.regular_model_er = ConjugationModel.load(_MODEL_REGULAR_ER)
        self.regular_model_ir = ConjugationModel.load(_MODEL_REGULAR_IR)


    def get_all_simple_forms(self, infinitive):
        """
        Produce all the possible verbal flexions (forms) for a given infinitive.

        Args:
            - infinitive

        Returns:
            A list with all possible simple forms (stringS).
        """
        if infinitive in self.irregular_verbs_models:
            _model = self.irregular_verbs_models[infinitive]
            return _model.get_all_simple_forms(infinitive)
        elif infinitive.endswith("ar"):
            return self.regular_model_ar.get_all_simple_forms(infinitive)
        elif infinitive.endswith("er"):
            return self.regular_model_er.get_all_simple_forms(infinitive)
        elif infinitive.endswith("ir"):
            return self.regular_model_ir.get_all_simple_forms(infinitive)
        else:
            return None


class ConjugationModel:
    """
    Conjugation model.
    """

    def __init__(self, name):
        self.name = name
        self.suffix = None
        self.flexing_suffixes = []
        self.verbs = []

    def get_root(self, infinitive):
        """
        Get the root of an infinitive.

        Params:
            - infinitive:

        Returns:
             The root (string) of the infinitive.
        """
        if infinitive.endswith(self.suffix):
            return infinitive[0:len(infinitive) - len(self.suffix)]
        return None

    def get_all_simple_forms(self, infinitive):
        """
        Produce all the possible verbal flexions (forms) for a given infinitive.

        Args:
            - infinitive

        Returns:
            A list with all possible simple forms (stringS).
        """
        _res = []
        _root = self.get_root(infinitive)
        for _suffix in self.flexing_suffixes:
            _res.append(_root + _suffix)
        return _res


    @staticmethod
    def load(model_name):
        config = configparser.ConfigParser()
        config.read(os.path.join(_BASE_RESOURCES_DIR, model_name + ".props"))
        _conj_model = ConjugationModel(model_name)

        # Load model information
        _conj_model.suffix = config["DEF"]["suffix"]
        if "verbs" in config["DEF"]:
            _verbs = config["DEF"]["verbs"]
            _conj_model.verbs = [_s.strip() for _s in _verbs.split(",")]

        # Load suffixes
        with open(os.path.join(_BASE_RESOURCES_DIR, model_name + ".suffx"), "r") as f:
            for _l in f.readlines():
                _l = _l.strip()
#                _l = _l.strip()
                if len(_l) == 0:
                    continue
                if _l.startswith("#"):
                    continue
                if _l.startswith("@"):
                    _conj_model.flexing_suffixes.append("")
                else:
                    _conj_model.flexing_suffixes.append(_l)

        return _conj_model



class SpanishVerbDatabaseBuilder:
    """
    Build a database with complete Spanish verbs information.
    """

    _CREATE_NON_PERSONAL_VERBS_TABLE = """CREATE TABLE `non_personal_verbs` (
  `ID` varchar NOT NULL,
  `normalized_verb` varchar NOT NULL,
  `verb` varchar DEFAULT NULL,
  `infinitive` varchar DEFAULT NULL,
  `type` int DEFAULT NULL,
  `simple` int DEFAULT NULL,
  PRIMARY KEY (`ID`)
);"""

    _CREATE_PERSONAL_VERBS_TABLE = """CREATE TABLE `personal_verbs` (
  `ID` varchar NOT NULL,
  `normalized_verb` varchar NOT NULL,
  `verb` varchar DEFAULT NULL,
  `infinitive` varchar DEFAULT NULL,
  `person` int DEFAULT NULL,
  `singular` int DEFAULT NULL,
  `time` int DEFAULT NULL,
  `mode` int DEFAULT NULL,
  `simple` int DEFAULT NULL,
  PRIMARY KEY (`ID`)
);"""

    def __init__(self, db_file_path=_SPANISH_VERB_DB_PATH):
        self.db_file_path = db_file_path
        _conn = sqlite3.connect(db_file_path)
        _cursor = _conn.cursor()
        # Create tables
        logging.info("Creating tables...")
        _cursor.execute(self._CREATE_PERSONAL_VERBS_TABLE)
        _cursor.execute(self._CREATE_NON_PERSONAL_VERBS_TABLE)
        # Create indexes
        logging.info("Creating indexes...")
        _cursor.execute("CREATE INDEX `index_normalized_verb_personal_verbs` on `personal_verbs` (normalized_verb)")
        _cursor.execute("CREATE INDEX `index_normalized_verb_non_personal_verbs` on `non_personal_verbs` (normalized_verb)")
        _conn.commit()
        _conn.close()


    def insert_data(self):
        _conn = sqlite3.connect(self.db_file_path)

        # Insert Spanish verbs data

        # Read mapping
        _mapping = []
        with open(_DETAILED_INFO_MAPPING_PATH, "r") as _f:
            for _l in _f.readlines():
                _l = _l.strip()
                if len(_l) > 0:
                    if _l.startswith("#"):
                        continue
                    _mapping.append([_s.strip() for _s in _l.split(",")])

        # Read list of verbs
        _verb_list = []
        with open(_VERB_LIST_PATH, "r") as _f:
            for _l in _f.readlines():
                _l = _l.strip()
                if len(_l) > 0:
                    if _l.startswith("#"):
                        continue
                    _verb_list.append(_l)

        # Generate verbal forms and insert into database
        _flexioner = SpanishVerbFlexioner()
        for _v in _verb_list:
            _vf_list = flexioner.get_all_simple_forms(_v)
            self._insert_into_db(_conn, _vf_list, _mapping, _v)

        _conn.commit()
        _conn.close()


    def _insert_into_db(self, conn, vf_list, mapping, infinitive):
        logging.info("Inserting " + infinitive)
        _cursor = conn.cursor()
        for i in range(len(vf_list)):
            if len(mapping[i]) == 5:
                # Personal form
                _id = infinitive + "_" + str(i)
                _verb = vf_list[i]
                _normalized_verb = vf_list[i]
                _s_person = mapping[i][0]
                _singular = 1 if mapping[i][1].lower() == "true" else 0
                _s_time = mapping[i][2]
                _s_mode = mapping[i][3]
                _simple = 1 if mapping[i][4].lower() == "true" else 0
                _sql_stat = "insert into personal_verbs values('" + _id + "', '" + _normalized_verb + "', '" + _verb + "', '" \
                            + infinitive + "', " + _s_person + ", " + str(_singular) + ", " + _s_time + ", " \
                            + _s_mode + ", " + str(_simple) + ")"
                logging.debug("Inserting personal form: " + _sql_stat)
                _cursor.execute(_sql_stat)
            elif len(mapping[i]) == 2:
                # Non personal form
                _id = infinitive + "_" + str(i)
                _verb = vf_list[i]
                _normalized_verb = vf_list[i]
                _s_type = mapping[i][0]
                _simple = 1 if mapping[i][1].lower() == "true" else 0
                _sql_stat = "insert into non_personal_verbs values('" + _id + "', '" + _normalized_verb + "', '" + _verb + "', '" \
                            + infinitive + "', " + _s_type + ", " + str(_simple) + ")"
                logging.debug("Inserting non personal form: " + _sql_stat)
                _cursor.execute(_sql_stat)
        conn.commit()



class SpanishVerbAnalyzer():
    """
    This class gets the lemma (infinitive form) of any Spanish simple verbal form.
    """

    def __init__(self, db_file_path=_SPANISH_VERB_DB_PATH):
        self.db_file_path = db_file_path
        self.connections = {}
#        self.conn = sqlite3.connect(db_file_path)
#        self.lock = threading.Lock()

    def _get_connection(self):
        _thread_id = threading.currentThread()
        if not _thread_id in self.connections:
            self.connections[_thread_id] = sqlite3.connect(self.db_file_path)
        return self.connections[_thread_id]


    def is_verb(self, word):
        """
        :param word:
        :return:
        """
        _v_info = self.get_verb_info(word)
        return _v_info != None and len(_v_info) > 0

    def get_verb_info(self, word):
#        self.lock.acquire()

        _conn = self._get_connection()
        _cur = _conn.cursor()
        _cur.execute("SELECT * FROM personal_verbs where normalized_verb='" + word + "'")
        _res = []
        for _r in _cur.fetchall():
            _verb = _r[2]
            _person = int(_r[4])
            _is_singular = int(_r[5]) == 1
            _time = int(_r[6])
            _verbal_mode = int(_r[7])
            _is_simple = int(_r[8]) == 1
            _is_personal = True
            _is_perfect = None
            _is_continuous = None
            _is_participle = False
            _is_geround = False
            _infinitive = _r[3]
            _res.append(SpanishVerbalForm(_verb, _time, _is_perfect, _is_continuous, _verbal_mode,
                                          _is_personal, _person, _is_singular, _is_participle, _is_geround, _infinitive,
                                          _is_simple))
        if len(_res) == 0:
            # Not found in personal verbs. Look into non personal verbs table.
            _cur.execute("SELECT * FROM non_personal_verbs where normalized_verb='" + word + "'")
            for _r in _cur.fetchall():
                _verb = _r[2]
                _person = None
                _is_singular = None
                _time = None
                _verbal_mode = None
                _is_simple = int(_r[5]) == 1
                _is_personal = False
                _is_perfect = None
                _is_continuous = None
                _is_participle = _r[4] == 3
                _is_geround = _r[4] == 2
                _infinitive = _r[3]
                _res.append(SpanishVerbalForm(_verb, _time, _is_perfect, _is_continuous, _verbal_mode,
                                              _is_personal, _person, _is_singular, _is_participle, _is_geround, _infinitive,
                                              _is_simple))
#        self.lock.release()
        return _res

    def close(self):
#        self.conn.close()
        _thread_id = threading.currentThread()
        if _thread_id in self.connections:
            self.connections[_thread_id].close()



class SpanishVerbalForm():

    def __init__(self, verb, time, is_perfect, is_continuous, verbal_mode, is_personal, person, is_singular,
                 is_participle, is_geround, infinitive, is_simple):
        self.verb = verb
        self.time = time
        self.is_perfect = is_perfect
        self.is_contiuous = is_continuous
        self.verbal_mode = verbal_mode
        self.is_personal = is_personal
        self.person = person
        self.is_singular = is_singular
        self.is_participle = is_participle
        self.is_geround = is_geround
        self.infinitive = infinitive
        self.is_simple = is_simple
        self.language = "spanish"

    def __str__(self):
        _res = "SpanishVerbalForm:[verb:"
        _res += self.verb
        _res += ", time: {}".format(self.time)
        _res += ", is_perfect: {}".format(self.is_perfect)
        _res += ", is_continuous: {}".format(self.is_contiuous)
        _res += ", verbal_mode: {}".format(self.verbal_mode)
        _res += ", os_personal: {}".format(self.is_personal)
        _res += ", person: {}".format(self.person)
        _res += ", is_singular: {}".format(self.is_singular)
        _res += ", is_participle: {}".format(self.is_participle)
        _res += ", is_geround: {}".format(self.is_geround)
        _res += ", infinitive: {}".format(self.infinitive)
        _res += ", is_simple: {}".format(self.is_simple)
        _res += ", language: {}".format(self.language)
        _res += "]"
        return _res

    def __unicode__(self):
        _res = "SpanishVerbalForm:[verb:"
        _res += self.verb
        _res += ", time: {}".format(self.time)
        _res += ", is_perfect: {}".format(self.is_perfect)
        _res += ", is_continuous: {}".format(self.is_contiuous)
        _res += ", verbal_mode: {}".format(self.verbal_mode)
        _res += ", os_personal: {}".format(self.is_personal)
        _res += ", person: {}".format(self.person)
        _res += ", is_singular: {}".format(self.is_singular)
        _res += ", is_participle: {}".format(self.is_participle)
        _res += ", is_geround: {}".format(self.is_geround)
        _res += ", infinitive: {}".format(self.infinitive)
        _res += ", is_simple: {}".format(self.is_simple)
        _res += ", language: {}".format(self.language)
        _res += "]"
        return _res


class SpanishLemmatizer():

    def __init__(self):
        self.snowball_stemmer = SnowballStemmer("spanish")
        self.spanish_verb_analyzer = SpanishVerbAnalyzer()

    def get_lemmas(self, word, strategy="ALL"):
        """
        Get the possible lemmas for a given wordm, without using any disambiguation procedure.

        Params:
            - word: word to be lemmatized.
            - strategy:
                Possible strategies: "ALL"|"VERB"|"POS"
                "ALL": Return all possible lemmas. The first of them comes from Spanish Snowball stemmer.
                    The second, if present, is the result of verbal analysis (infinitive of the corresponding
                    verbal form).
                "VERB": Return only one lemma, with preference for verbs (infinitive).
                "POS": Return only one lemma, by means of POS disambiguation. NOT YET IMPLEMENTED

        Returns:
            A list with possible lemmas.
        """
        _res = []
        if strategy == "ALL" or strategy == "VERB":
            _snowball_lemma = self.snowball_stemmer.stem(word)
            _verb_lemma = None
            _verbal_form_list = self.spanish_verb_analyzer.get_verb_info(word)
            if _verbal_form_list != None and len(_verbal_form_list) > 0:
                _verb_lemma = _verbal_form_list[0].infinitive
            if strategy == "ALL":
                if _snowball_lemma != None:
                    _res.append(_snowball_lemma)
                if _verb_lemma != None:
                    _res.append(_verb_lemma)
                return _res
            else:
                if _verb_lemma != None:
                    return [_verb_lemma]
                return [_snowball_lemma]
        elif strategy == "POS":
            raise Exception("POS lemmatizing strategy is not yet implemented!")
        else:
            raise Exception("Not valid lemmatizing strategy")
        return word


    def lemmatize_text(self, text, strategy="ALL"):
        """
        Replace words by lemmas

        Args:
            - text: Text to be lemmatized in the form of an array of words.
            - strategy:
                Possible strategies: "ALL"|"VERB"|"POS"
                "ALL": Return all possible lemmas. The first of them comes from Spanish Snowball stemmer.
                    The second, if present, is the result of verbal analysis (infinitive of the corresponding
                    verbal form).
                "VERB": Return only one lemma, with preference for verbs (infinitive).
                "POS": Return only one lemma, by means of POS disambiguation. NOT YET IMPLEMENTED

        Returns:
            A list of strings, containing the lemmas.
        """
        _res = []
        for _w in text:
            for _l in self.get_lemmas(_w, strategy=strategy):
                _res.append(_l)
        return _res


# Debug
# TODO This is a debug program. Delete me when code is stable!!
if __name__ == "__main__":

    nltk_data_dir = "~/nltk_data"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    infinitives = ["ser", "abeldar", "cantar", "temer", "partir", u"abarañar"]
    flexioner = SpanishVerbFlexioner()
    for v in infinitives:
        _vf = flexioner.get_all_simple_forms(v)
        print("v --> " + str(_vf))
        for _v in _vf:
            print(_v)
        print("\n\n\n")

    _va = SpanishVerbAnalyzer()
    for _r in _va.get_verb_info("cante"):
        print("{}".format(_r))

    for _w in "esto es una prueba".split():
        print("{} is verb: {}".format(_w, _va.is_verb(_w)))

    _spanish_lemmatizer = SpanishLemmatizer()

    for _w in "esto es una prueba".split():
        print("{} --> lemas --> {}".format(_w, _spanish_lemmatizer.get_lemmas(_w)))

#    print _spanish_lemmatizer.lemmatize_text("esto es una prueba".split())
    print(_spanish_lemmatizer.lemmatize_text("consiguen arranque en segundo intento al tener maquina con inercia".split()))
