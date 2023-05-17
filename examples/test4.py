
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from pathlib import Path
from utilities import *
from config import *
from transform import *

model_project_dir = 'systemic_risk'
root_dir = Path(__file__).resolve().parents[1]

# create_biblio_folders(project)

biblio_df = read_biblio_csv_files_to_df(biblio_project_dir_name = model_project_dir, 
                                        input_dir = 'raw/dimensions',
                                        biblio_source = BiblioSource.DIMS,
                                        n_rows = 10)

biblio_df = modify_cols_biblio_df(biblio_df_ = biblio_df, 
                                   reshape_base = Reshape.DIMS_COMPACT)

biblio_df = add_biblio_source(biblio_df_ = biblio_df,
                              biblio_source = BiblioSource.DIMS)

biblio_df = normalise_biblio_entities(biblio_df_ = biblio_df,
                                      biblio_source = BiblioSource.DIMS)

biblio_df = clean_biblio_df(biblio_df = biblio_df)

write_df(biblio_df = biblio_df,
         biblio_project_dir_name = model_project_dir,
         output_dir = 'results',
         output_file = 'dims_clean_10_df.csv')

# write_df(biblio_df = dup_df,
#          project = project,
#          output_dir = 'results',
#          output_file = 'scopus_dup_df.csv')
