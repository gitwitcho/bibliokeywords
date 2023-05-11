
import sys

from pathlib import Path
from utilities import *
from config import *
from transform import *

project = 'systemic_risk'
root_dir = Path(__file__).resolve().parents[1]

# create_biblio_folders(project)

biblio_df = read_and_merge_csv_files(project = project, 
                                     input_dir = 'raw/scopus',
                                     is_dimensions = False,
                                     n_rows = 200)

biblio_df = reshape_cols_biblio_df(biblio_df = biblio_df, 
                                   reshape_base = Reshape.SCOPUS_FULL)

biblio_df = add_biblio_source(biblio_df = biblio_df,
                              biblio_source = BiblioType.SCOPUS)

biblio_df = normalise_biblio_entities(biblio_df = biblio_df,
                                      biblio_source = BiblioType.SCOPUS)

# biblio_df, dup_df = remove_title_duplicates(biblio_df = biblio_df)

biblio_df = clean_biblio_df(biblio_df = biblio_df,
                            biblio_type = BiblioType.SCOPUS)

write_df(biblio_df = biblio_df,
         project = project,
         output_dir = 'results',
         output_file = 'scopus_clean_200_df.csv')

# write_df(biblio_df = dup_df,
#          project = project,
#          output_dir = 'results',
#          output_file = 'scopus_dup_df.csv')
