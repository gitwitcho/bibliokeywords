import sys

import matplotlib.pyplot as plt
import igraph as ig

from pathlib import Path
from openpyxl import Workbook
from utilities import *
from config import *
from transform import *
from co_term_occurrence import *

model_project_dir = 'systemic_risk'

exclude_terms = ['human', 'male', 'female']

root_dir = Path(__file__).resolve().parents[1]

biblio_df = read_and_merge_csv_files(project = model_project_dir, 
                                    input_dir = 'raw/scopus',
                                    biblio_type = BiblioSource.SCOPUS,
                                    n_rows = 1000)

biblio_df = modify_cols_biblio_df(biblio_df = biblio_df, reshape_base = Reshape.SCOPUS_COMPACT)
biblio_df = normalise_biblio_entities(biblio_df = biblio_df)
biblio_df = clean_biblio_df(biblio_df = biblio_df)

# TODO: Implement negative min_count for keyword pair frequency threshold
# TODO: Remove the graph.simplify() in create_co_term_graph, remove the
# paur_counter, and instead add the edge count to a new attribute 'count'
# to the edges, removing the code below that does that.
graph, pair_counter = create_co_term_graph(biblio_df['kws'], 
                                           min_count = 18,
                                           singularise = True,
                                           synonymise = True,
                                           stem = True)

# Convert pair_counter to a DataFrame
pairs_df = pd.DataFrame.from_dict(pair_counter, orient='index', columns=['Count'])

# Reset the index and rename the column
pairs_df = pairs_df.reset_index().rename(columns={'index': 'Pair'})

# Print the pairs
print(pairs_df.sort_values(by = 'Count', ascending = False).reset_index(drop = True))

# Add the edge labels to the graph based on the count of distinct pairs
for (string1, string2), count in pair_counter.items():
    graph.es[graph.get_eid(string1, string2)]['label'] = count

fig, ax = plt.subplots()

ig.plot(graph, 
        target = ax,
        vertex_size = 0.1,
        vertex_label = graph.vs["name"],
        edge_label=graph.es["label"]
        )

plt.show()

graph.write(root_dir / 'data' / model_project_dir / 'results' / 'test_graph.graphml', format = 'graphml')
