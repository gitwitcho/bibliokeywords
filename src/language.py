import random
import nltk
import spacy

from typing import Union, List, Dict
from textblob import TextBlob
from textblob import Word

nltk.download('wordnet')
nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")  # conda install -c conda-forge spacy-model-en_core_web_sm

# Download stopwords if they haven't been downloaded previously
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

nltk_stopwords = nltk.corpus.stopwords.words('english')


def synonymise_terms_dict(string_counts_dict: Dict) -> Dict:

    syn_dict = {}
    terms = list(string_counts_dict.keys())

    for term in terms:

        # Find the synonyms of the term
        synonyms = Word(term).synsets

        # Create a list of the synonyms and and include the term
        term_and_synonyms = list(set([term] + [syn.lemma_names()[0] for syn in synonyms]))      # type: ignore - Pylance: "cached_property" is not iterable

        # Find a/the string/synonym with the highest count in the dictionary
        max_value_term = max(term_and_synonyms, key = lambda string: string_counts_dict.get(string, 0))

        # Get the strings with the highest count in string_counts
        highest_value_terms = [string for string in term_and_synonyms if string_counts_dict.get(string, 0) == string_counts_dict[max_value_term]]

        # Choose one string at random from the highest value strings
        chosen_term = random.choice(highest_value_terms)

        # Add the key-value pairs 'synonym: chosen_string' to the synonym dictionary.
        # TODO: Currently, if the key exists, it will not add the alternative synonym 
        # to the dictionary. For instance if the words 'luck' and 'risk' are in string_counts_dicts,
        # then both might have 'hazard' among their synonyms. If 'luck' is processed
        # first, then syn_dict will have an entry 'hazard: luck'. When 'risk' is then
        # processed, the key-value pair 'hazard: risk' cannot be added to syn_dict since
        # the key 'hazard' already exists. What can be done? Check which of both terms
        # ('risk' and 'luck') has the highest count in string_counts_dict and use that 
        # term as the synonym in syn_dict. 
        syn_dict.update({new_key: chosen_term for new_key in term_and_synonyms if new_key != chosen_term and new_key not in syn_dict})


    # Replace synonym strings in strings_count with their 'root' synonym and
    # sum the corresponding counts
    # FIXME: If a word has different meanings (a bank for instance), then not all its 
    # synonyms are meaningful. If the word 'bank' refers to a financial institution, 
    # then the code below will add them nonetheless to the dictionary. 
    for key, value in syn_dict.items():     # key: synonyms, value: chosen 'root' synonym
        if key in string_counts_dict:
            if value in string_counts_dict:
                string_counts_dict[value] += string_counts_dict.get(key, 0)
            else:
                string_counts_dict[value] = string_counts_dict.get(key, 0)
            
            string_counts_dict.pop(key, None)

    return string_counts_dict


def singularise_terms(terms: Union[List[str], str]) -> List[str]:
    '''
        Only singularise the last word in a term like 'physics based'
    '''
    # TODO:
    #   - Run the profiler on this function since it is very slow
    
    singularised_terms = []
    endings = ['ics']

    if isinstance(terms, str):
        terms = [terms]

    for term in terms:
        term = term.strip()
        last_word = term.split(' ')[-1]

        # Check whether the word is singular even if it ends in 's'
        if term and nlp(last_word)[0].tag_ in {"NNS", "NNPS"} and not any(last_word.endswith(ending) for ending in endings):
            last_word = ''.join(list(TextBlob(last_word).words.singularize()))    # type: ignore - Pylance: Cannot access member "singularize" for type "cached_property"
            term_lst = term.split(' ')       
            term_lst[-1] = last_word
            term_str = ' '.join(term_lst)
            singularised_terms += [term_str]
        elif term:
            singularised_terms += [term]

    return singularised_terms


def stem_terms_dict(string_counts_dict: Dict) -> Dict:
    terms = list(string_counts_dict.keys())

    for key in terms:
        l = Word(key).stem()

        if l != key:
            if l in string_counts_dict:
                string_counts_dict[l] += string_counts_dict[key]
            else:
                string_counts_dict[l] = string_counts_dict[key]

            string_counts_dict.pop(key)

    return string_counts_dict


def stem_terms(terms: Union[List[str], str]) -> List[str]:

    if isinstance(terms, str):
        terms = [terms]

    terms_dict = {string: 0 for string in terms}
    stemmed_terms_list = list(set(stem_terms_dict(terms_dict).keys()))

    return stemmed_terms_list
