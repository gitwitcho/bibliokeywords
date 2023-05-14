import pandas as pd
import numpy as np
import igraph as ig
import random
import sys

import nltk
nltk.download('wordnet')

from collections import Counter
from typing import Tuple, Dict, List
from textblob import TextBlob

from config import *

from collections import Counter
from textblob import TextBlob
from textblob import Word

from textblob.wordnet import NOUN, ADJ


def DEPREC_compress_synonyms(strings_lst: List,
                      string_counts_dict: Dict):

    if not all(string in string_counts_dict for string in strings_lst):
        raise ValueError(f"The strings in strings_lst need to correspond to a key in string_counts_dict")
    
    syn_dict = {}

    for string in strings_lst:
        # Find synonyms of string
        synonyms = Word(string).synsets

        # List of the synonyms and the string
        combined_set = list(set([string] + [syn.lemma_names()[0] for syn in synonyms]))      # type: ignore - Pylance: "cached_property" is not iterable

        # Find a/the string/synonym with the highest count in the dictionary
        max_value_string = max(combined_set, key = lambda string: string_counts_dict.get(string, 0))

        # Get the strings with the highest count in string_counts
        highest_value_strings = [string for string in combined_set if string_counts_dict.get(string, 0) == string_counts_dict[max_value_string]]

        # Choose one string at random from the highest value strings
        chosen_string = random.choice(highest_value_strings)

        # Add the key-value pairs 'synonym: chosen_string' to the synonym dictionary.
        # TODO: Currently, if the key exists, it will not add the alternative synonym 
        # to the dictionary. For instance if the words 'luck' and 'risk' are in string_counts_dicts,
        # then both might have 'hazard' among their synonyms. If 'luck' is processed
        # first, then syn_dict will have an entry 'hazard: luck'. When 'risk' is then
        # processed, the key-value pair 'hazard: risk' cannot be added to syn_dict since
        # the key 'hazard' already exists. What can be done? Check which of both terms
        # ('risk' and 'luck') has the highest count in string_counts_dict and use that 
        # term as the synonym in syn_dict. 
        syn_dict.update({new_key: chosen_string for new_key in combined_set if new_key != chosen_string and new_key not in syn_dict})


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

# # Example usage
# strings_lst = ['happy', 'content']
# string_dict = {'happy': 6,
#                'content': 10,
#                'joyful': 6,
#                'felicitous': 2}
# result = compress_synonyms(strings_lst, string_dict)
# print(result)


def synonymise_terms(string_counts_dict: Dict) -> Dict:

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


def singularize_term(terms: List):
    singularised_terms = []

    for term in terms:
        term = ' '.join(TextBlob(term).words.singularize()) # type: ignore - Pylance: Cannot access member "singularize" for type "cached_property"
        singularised_terms += [term]

    return singularised_terms


def stem_terms(string_counts_dict: Dict) -> Dict:
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


def create_co_term_df(term_se: pd.Series,
                      min_count: int = 0,
                      singularise: bool = True,
                      synonymise: bool = False,
                      stem: bool = False) -> Tuple[ig.Graph, Counter]:

    # Convert term_df items to lists of terms
    # term_se = term_se.str.split(';').apply(lambda x: [item.strip() for item in x])
    term_se = term_se.str.split(';').apply(lambda x: [item.strip() for item in x if item.strip()])
    term_se = term_se.apply(lambda lst: lst if len(lst) > 0 else np.nan).dropna()


    # Singularise the terms in term_df
    if singularise:
        term_se = term_se.apply(singularize_term)

    # Create a set of all unique strings in term_df
    unique_strings = term_se.explode().unique()
    unique_strings = [s.strip() for s in unique_strings if s.strip() != '']

    # Create a dictionary to keep track of the count of occurrences for each string
    string_counts_dict = {string: 0 for string in unique_strings}

    # Iterate over term_se to add the individual terms to the string_counts dictionary
    # and update their count (the frequency of overall occurrence of the term in term_df)
    for terms in term_se:
        terms_lst = [term.strip() for term in terms]
        string_counts_dict.update({string: string_counts_dict.get(string, 0) + 1 for string in terms_lst if string.strip()})

    # The dictionary is filtered if min_count > 0. If min_count < 0, filtering 
    # is done on the co-term pairs.
    if min_count > 1:   # there are no entries with count = 0 in the dictionary
        string_counts_dict = {key: value for key, value in string_counts_dict.items() if value >= min_count}

    if synonymise:
        string_counts_dict = synonymise_terms(string_counts_dict = string_counts_dict)

    if stem:
        string_counts_dict = stem_terms(string_counts_dict = string_counts_dict)

    # Include strings that occur with frequency min_count or more often, unless 
    # filtered_strings = [string for string, count in string_counts_dict.items() if count >= min_count or min_count < 0]
    terms = list(string_counts_dict.keys())

    # Create a new series containing only the terms that have at least one string from the filtered_strings list
    term_se = term_se[term_se.apply(lambda entry: any(string in entry for string in terms))]

    # Create an empty graph
    # graph = nx.Graph()
    g = ig.Graph()

    # Add nodes to the graph
    # graph.add_nodes_from(filtered_strings)
    # g.add_vertices(terms)

    # Create a counter to track the distinct pairs
    pair_counter = Counter()

    vs = [] # list of graph vertices

    # Iterate over the values of the filtered Series and add edges to the graph
    for se_terms in term_se:
        for string1 in se_terms:
            if string1 in terms:
                for string2 in se_terms:
                    if (string1 != string2) and  string2 in terms:
                        vs += [string1, string2]
                        pair_counter[frozenset([string1, string2])] += 1    # frozenset creates an immutble key

    g.add_vertices(list(set(vs)))

    for pair, _ in pair_counter.items():
        v_ed = list(set(pair))
        g.add_edge(v_ed[0], v_ed[1])

    # for key, value in pair_counter.items():
    #     print(key, value)

    # for vertex in g.vs['name']:
    #     print(vertex)

    # If min_count < 0, use |min_count| as a threshold for the number of occurrences 
    # of string pairs (string1, string2)
    if min_count < 0:
        pair_counter = Counter({pair: count for pair, count in pair_counter.items() if count >= np.abs(min_count)})

    # Remove multiple edges
    g.simplify()

    # for vertex in g.vs:
    #     print(vertex["name"])

    return g, pair_counter






