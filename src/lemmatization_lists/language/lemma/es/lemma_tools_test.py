# coding=utf-8
from .lemma_tools import SpanishVerbFlexioner, SpanishVerbAnalyzer, SpanishLemmatizer

import logging


if __name__ == "__main__":

    nltk_data_dir = "~/nltk_data"
    text_processor = TextPreprocessor.TextPreprocessor(nltk_data_dir, ["spanish"])

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    infinitives = ["ser", "abeldar", "cantar", "temer", "partir", u"abarañar"]
    flexioner = SpanishVerbFlexioner(text_processor)
    for v in infinitives:
        _vf = flexioner.get_all_simple_forms(v)
        print("v --> " + str(_vf))
        for _v in _vf:
            print(_v)
        print("\n\n\n")


#    _builder = SpanishVerbDatabaseBuilder(text_processor)
#    _builder.insert_data()

    _va = SpanishVerbAnalyzer()
    for _r in _va.get_verb_info("cante"):
        _s = _r.__str__()
        print(_r)

    for _w in "esto es una prueba".split():
        print("{} is verb: {}".format(_w, _va.is_verb(_w)))

    _spanish_lemmatizer = SpanishLemmatizer(text_processor)

    for _w in "esto es una prueba".split():
        print("{} --> lemas --> {}".format(_w, _spanish_lemmatizer.get_lemmas(_w)))

#    print _spanish_lemmatizer.lemmatize_text("esto es una prueba".split())
    print(_spanish_lemmatizer.lemmatize_text("Consiguen arranque en segundo intento al tener maquina con inercia".split()))
