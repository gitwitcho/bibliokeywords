
import sys

from pathlib import Path
from utilities import *
from config import *
from transform import *

project = 'systemic_risk'
root_dir = Path(__file__).resolve().parents[1]

# create_biblio_folders(project)

biblio_df = read_and_merge_csv_files(project = project, 
                                     input_dir = 'raw/lens',
                                     is_dimensions = False,
                                     n_rows = 100)

biblio_df = reshape_cols_biblio_df(biblio_df = biblio_df, 
                                   reshape_base = Reshape.LENS_FULL)

biblio_df = add_biblio_source(biblio_df = biblio_df,
                              biblio_source = BiblioType.LENS)

biblio_df = remove_title_duplicates(biblio_df = biblio_df)

print(biblio_df)