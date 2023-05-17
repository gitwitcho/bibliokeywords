import sys

from pathlib import Path
from utilities import *
from config import *
from transform import *
from keyword_stats import *

model_project_dir = 'PINNs'

keyword_cols = ['kws']
assoc_filter = "[learning, carbon] in* {}"

root_dir = Path(__file__).resolve().parents[1]

biblio_df = read_and_merge_csv_files(project = model_project_dir, 
                                    input_dir = 'raw/scopus',
                                    biblio_type = BiblioSource.SCOPUS,
                                    n_rows = 10)

biblio_df = modify_cols_biblio_df(biblio_df = biblio_df, reshape_base = Reshape.SCOPUS_COMPACT)
biblio_df = normalise_biblio_entities(biblio_df = biblio_df)
biblio_df = clean_biblio_df(biblio_df = biblio_df)

keywords_dict = generate_keyword_stats(biblio_df_ = biblio_df,
                                       cols = keyword_cols,
                                       assoc_filter = assoc_filter,
                                       singularise = False,
                                       stem = False)

# TODO: Write keywords dict to console
write_keyword_count_to_console(keywords_dict = keywords_dict,
                               max_n_rows = 10,
                               display_width = 180)

keywords_stacked_df = stack_keyword_count_dfs(keywords_dict = keywords_dict)

write_df(biblio_df = keywords_stacked_df,
         project = model_project_dir,
         output_dir = 'results',
         output_file = 'keywords_stacked.xlsx')