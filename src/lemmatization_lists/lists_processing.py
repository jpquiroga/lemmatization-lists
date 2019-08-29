import os
import typing
from lemmatization_lists.lemmatizers import DictionaryLemmatizer
from tqdm import tqdm

def es_list_process(dest_file:str):
    """
    This function generates an improved version of the Spanish lemmatization list:
    - Remove accents.
    - Add primitive lemma forms.

    :param list_file:
    :param dest_file:
    """
    lemmatizer = DictionaryLemmatizer("es")
    with open(dest_file, "w") as f:
        _tmp_dict = {}
        for word, lemmas in tqdm(lemmatizer.lemma_dict_norm.items()):
            for l in lemmas:
                f.write("{}\t{}\n".format(l, word))

if __name__ == "__main__":
    dest_file = "src/lemmatization_lists/data/lemmatization-norm-es.txt"
    es_list_process(dest_file)

