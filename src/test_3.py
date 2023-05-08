import sys

from pathlib import Path
from utilities import *
from transform import *
from topics import *
from config import *

from sklearn.feature_extraction.text import CountVectorizer


project = 'mabs_repsol'
root_dir = Path(__file__).resolve().parents[1]

biblio_df = read_and_merge_csv_files(project = project, 
                                     input_dir = 'processed',
                                     is_dimensions = False)

model, biblio_topics_df = generate_bert_topics(biblio_df = biblio_df,
                                               input_col = 'abstract',
                                               verbose = True)

reshape_filter = {'Document': 'title', 'Topic': 'tp_num', 'Name': 'tp_name', 'Top_n_words': 'top_n_words'}
topic_info_df = reshape_cols_biblio_df(biblio_df = biblio_topics_df,
                                reshape_filter = reshape_filter)

topic_summary_df = create_topic_summary_df(topic_info_df = topic_info_df)

reshape_filter = {'title': 'title', 'year': 'year', 'abstract': 'abstract', 
                  'Topic': 'tp_num', 'Name': 'tp_name', 'Top_n_words': 'top_n_words'}
biblio_topics_df = reshape_cols_biblio_df(biblio_df = biblio_topics_df,
                                    reshape_filter = reshape_filter)

write_df(biblio_df = topic_summary_df, 
         project = project,
         output_dir = 'results',
         output_file = 'bertopic_mabs_energy_topic_summary.csv')

write_df(biblio_df = biblio_topics_df, 
         project = project,
         output_dir = 'results',
         output_file = 'scopus_mabs_energy_abstract_topics.xlsx')

print(biblio_topics_df.head())