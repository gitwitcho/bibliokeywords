import sys

from pathlib import Path
from utilities import *
from config import *
from transform import *
from keyword_stats import *

project = 'PINNs'

keyword_cols = ['kws']
assoc_filter = "[learning, carbon] in* {}"

root_dir = Path(__file__).resolve().parents[1]

biblio_df = read_and_merge_csv_files(project = project, 
                                    input_dir = 'raw/scopus',
                                    biblio_type = BiblioType.SCOPUS,
                                    n_rows = 10)

biblio_df = reshape_cols_biblio_df(biblio_df = biblio_df, reshape_base = Reshape.SCOPUS_COMPACT)
biblio_df = normalise_biblio_entities(biblio_df = biblio_df)
biblio_df = clean_biblio_df(biblio_df = biblio_df)

keywords_dict = generate_keyword_stats(biblio_df_ = biblio_df,
                                       cols = keyword_cols,
                                       assoc_filter = assoc_filter,
                                       singularise = False,
                                       stem = False)

# TODO: Write the keywords dict to HTML
