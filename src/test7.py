import sys
# import networkx as nx
import matplotlib.pyplot as plt
import igraph as ig

from pathlib import Path
from openpyxl import Workbook
from utilities import *
from config import *
from transform import *
from co_term_occurrence import *

project = 'systemic_risk'



exclude_terms = ['human', 'male', 'female']

root_dir = Path(__file__).resolve().parents[1]

biblio_df = read_and_merge_csv_files(project = project, 
                                    input_dir = 'raw/scopus',
                                    biblio_type = BiblioType.SCOPUS,
                                    n_rows = 1000)

biblio_df = reshape_cols_biblio_df(biblio_df = biblio_df, reshape_base = Reshape.SCOPUS_COMPACT)
biblio_df = normalise_biblio_entities(biblio_df = biblio_df)
biblio_df = clean_biblio_df(biblio_df = biblio_df)

# TODO: Implement negative min_count for number of keywords to include
# TODO: Stemming, plurals
graph, pair_counter = create_co_term_df(biblio_df['kws'], 
                                        min_count = 18,
                                        singularise = True,
                                        synonymise = True,
                                        stem = True)    # TODO: check whether this couldn't be applied to the number of pairs

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


# # Draw the graph
# fig, ax = plt.subplots(figsize=(5,5))
# ig.plot(graph, target = ax)
# # nx.draw_networkx(graph, with_labels = True, font_weight = 'bold')

# # Show the plot
# plt.show()

graph.save(root_dir / 'data' / project / 'results' / 'test_graph.gml')
# nx.write_gexf(graph, root_dir / 'data' / project / 'results' / 'test_graph.gexf')