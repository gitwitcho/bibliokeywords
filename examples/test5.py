import sys

from pathlib import Path
from utilities import *
from config import *
from transform import *

model_project_dir = 'systemic_risk'
root_dir = Path(__file__).resolve().parents[1]

scopus_df = read_and_merge_csv_files(project = model_project_dir, 
                                     input_dir = 'raw/scopus',
                                     biblio_type = BiblioType.SCOPUS,
                                     n_rows = 3)

lens_df = read_and_merge_csv_files(project = model_project_dir, 
                                   input_dir = 'raw/lens',
                                   biblio_type = BiblioType.LENS,
                                   n_rows = 3)

dims_df = read_and_merge_csv_files(project = model_project_dir, 
                                   input_dir = 'raw/dimensions',
                                   biblio_type = BiblioType.DIMS,
                                   n_rows = 3)

scopus_df = rename_and_retain_cols_biblio_df(biblio_df = scopus_df, reshape_base = Reshape.SCOPUS_COMPACT)
lens_df = rename_and_retain_cols_biblio_df(biblio_df = lens_df, reshape_base = Reshape.LENS_COMPACT)
dims_df = rename_and_retain_cols_biblio_df(biblio_df = dims_df, reshape_base = Reshape.DIMS_COMPACT)

scopus_df = normalise_biblio_entities(biblio_df = scopus_df)
lens_df = normalise_biblio_entities(biblio_df = lens_df)
dims_df = normalise_biblio_entities(biblio_df = dims_df)

# Stack the different dataframes on top of each other
biblio_df = pd.concat([scopus_df, lens_df, dims_df])

# biblio_df, dup_df = remove_title_duplicates(biblio_df = biblio_df)

biblio_df = clean_biblio_df(biblio_df = biblio_df)

write_df(biblio_df = biblio_df,
         project = model_project_dir,
         output_dir = 'results',
         output_file = 'merged_clean_200_df.csv')

# write_df(biblio_df = dup_df,
#          project = project,
#          output_dir = 'results',
#          output_file = 'scopus_dup_df.csv')
