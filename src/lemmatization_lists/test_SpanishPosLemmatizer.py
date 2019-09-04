import spacy

from lemmatization_lists.lemmatizers import SpanishPosLemmatizer

if __name__=="__main__":
    nlp_es = spacy.load("es")

    lemmatizer = SpanishPosLemmatizer()

    texts = [
        "Llama a Pepe",
        "Quiero ver la última llamada",
        "Llamadas perdidas",
        "llamada mamá",
        "ponme la última llamada",
        "pon juego de tronos",
        "que estoy viendo",
        "real madrid contra el betis",
        "ponme el partido del madrid",
        "me gustaría ver el partido del betis"
        ]

    for t in texts:
        print("{}: ->\n{}\n\n\n".format(t, lemmatizer.get_lemma_sentence(t, nlp_es)))

