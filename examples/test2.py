import sys

from pathlib import Path
from utilities import *
from transform import *
from config import *

project = 'mabs_repsol'
root_dir = Path(__file__).resolve().parents[1]

biblio_df = read_and_merge_csv_files(project = project, 
                                     input_dir = 'processed',
                                     is_dimensions = False)

biblio_df = reshape_cols_biblio_df(biblio_df = biblio_df,
                              reshape_filter = ['abstract'])

write_df(biblio_df = biblio_df,
         project = project,
         output_dir = 'results',
         output_file = 'scopus_mabs_energy_abstracts.csv')