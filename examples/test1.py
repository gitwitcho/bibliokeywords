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
                              reshape_base = Reshape.LENS_COMPACT,
                              reshape_filter = ['title', 'year', 'abstract'])

biblio_df = clean_biblio_df(biblio_df = biblio_df,
                            biblio_type = BiblioType.LENS)

sys.exit()

write_df(biblio_df = biblio_df,
                     project = project,
                     output_dir = 'processed',
                     output_file = 'scopus_mabs_energy_reshaped.csv')


print(biblio_df.columns)
print(biblio_df.head())