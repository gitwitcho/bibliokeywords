import sys

from pathlib import Path
from utilities import *
from config import *
from transform import *

project = 'systemic_risk'
root_dir = Path(__file__).resolve().parents[1]

create_biblio_folders(project)

biblio_df = read_and_merge_csv_files(project = project, 
                                     input_dir = 'raw/scopus',
                                     is_dimensions = False)

biblio_df = reshape_cols_biblio_df(biblio_df = biblio_df, 
                              reshape_base = Reshape.SCOPUS_COMPACT,
                              reshape_filter = ['title', 'year', 'abstract'])



write_df(biblio_df = biblio_df,
                     project = project,
                     output_dir = 'processed',
                     output_file = 'scopus_mabs_energy_reshaped.csv')


print(biblio_df.columns)
print(biblio_df.head())