import pandas as pd
import numpy as np
import igraph as ig

from collections import Counter
from typing import Tuple, Dict, List, Union, Optional
from collections import Counter
from tqdm import tqdm

from config import *
from utilities import *

# FIXME: When `sampling = True`, some runs lead to an error (see Co-Words notebook).


def create_co_term_graph(term_se: pd.Series,
                      min_count: int = 0,
                      singularise: bool = True,
                      synonymise: bool = False,
                      stem: bool = False,
                      exclude_terms: Optional[List] = None) -> Tuple[ig.Graph, List[str], Counter]:

    # TODO: Implement negative min_count for keyword pair frequency threshold
    # TODO: Remove the graph.simplify() in create_co_term_graph, remove the
    # paur_counter, and instead add the edge count to a new attribute 'count'
    # to the edges, removing the code below that does that.
    # TODO: Raise an error if there are less then two terms in the dictionary after applying min_count

    # Convert term_df items to lists of terms
    # term_se = term_se.str.split(';').apply(lambda x: [item.strip() for item in x])
    term_se = term_se.str.split(';').apply(lambda x: [item.strip() for item in x if item.strip()])
    term_se = term_se.apply(lambda lst: lst if len(lst) > 0 else np.nan).dropna()


    # Singularise the terms in term_df
    if singularise:
        tqdm.pandas(desc = f"Singularising the keywords")   # lots of cool paramiters you can pass here. 
        term_se = term_se.progress_apply(singularise_terms)

    # Create a set of all unique strings in term_df
    unique_strings = np.sort(term_se.explode().unique())
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
        string_counts_dict = synonymise_terms_dict(string_counts_dict = string_counts_dict)

    if stem:
        string_counts_dict = stem_terms_dict(string_counts_dict = string_counts_dict)

    # Create a list of all the terms
    terms = list(string_counts_dict.keys())

    # Remove terms in exclude_terms
    if exclude_terms:
        terms = [term for term in terms if term not in exclude_terms]

    # Create a new series containing only the terms that have at least one string from the filtered_strings list
    term_se = term_se[term_se.apply(lambda entry: any(string in entry for string in terms))]

    # Remove duplicate keywords in the keyword lists in_se (singularisation and stemming creates duplicates)
    term_se = term_se.apply(lambda lst: sorted(list(set(lst))))

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
                    if (string1 < string2) and  string2 in terms:   # the '<' prevents couble counting of string pairs
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
    # g.simplify()

    return g, vs, pair_counter






