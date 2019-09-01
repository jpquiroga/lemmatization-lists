from lemmatization_lists import SpanishPosLemmatizer
import time

import spacy

if __name__ == "__main__":
#    NLP_MODEL_NAME = "es_core_news_md"
    NLP_MODEL_NAME = "es"
    nlp = spacy.load(NLP_MODEL_NAME)
    lemmatizer = SpanishPosLemmatizer()

    texts = [
        "Me gustaría ver el segundo episodio de Star Trek",
        "El perro de San Roque no tiene rabo porque Ramón Rodríguez se lo ha robado.",
        "El camino al infierno está empedrado de buenas intenciones."
    ]

    start_time = time.time()
    num_words = 0
    num_phrases = 0
    lemma_results = []
    for text in texts:
        lemmas = lemmatizer.get_lemma_sentence(text, nlp)
        num_words += len(text.split())
        num_phrases += 1
        lemma_results.append(lemmas)
    end_time = time.time()
    for i, phrase in enumerate(texts):
        print("\n\n{} \n->{}".format(phrase, lemma_results[i]))

    print("\n\n\n")
    print("Time per phrase: {} ms".format((end_time - start_time)*1000/num_phrases))
    print("Time per word: {} ms".format((end_time - start_time)*1000/num_words))