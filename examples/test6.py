import sys

from pathlib import Path
from openpyxl import Workbook
from utilities import *
from config import *
from transform import *

data_project = 'systemic_risk'
root_dir = Path(__file__).resolve().parents[1]

highlight_params = [
    {
        'strings': ['probabilit', 'financ'],
        'targets': ['abstract'],
        'colour': 'red'
    },
    {
        'strings': ['risk', 'exterme', 'probab'],
        'targets': ['title'],
        'colour': 'magenta'
    },
    {
        'strings': ['risk'],
        'targets': ['title'],
        'colour': 'blue'
    },
    {
        'strings': ['risk', 'systemic'],
        'targets': ['title'],
        'colour': 'red'
    },
    {
        'strings': ['risk', 'real'],
        'targets': ['title', 'abstract'],
        'colour': 'lime'
    }
]

excel_params = {
    'cols': [           # this also determines the order of the columns in the Excel sheet
        {'col': 'title', 'heading': 'Title', 'width': 40, 'wrap': True},
        {'col': 'abstract', 'heading': 'Abstract', 'width': 80, 'wrap': True},
        {'col': 'year', 'heading': 'Year', 'width': 6, 'wrap': False}
    ],
    'sheet_name': 'Highlights',
    'zoom': 140,
    'freeze_panes': 'A2'
}

# Note: the tilde character is not allowed inside squarte brackets
# filter_query = "(risk in* title) & (year == 2014)"
# filter_query = "systemic in* title"
# filter_query = "public in* title | extreme in* abstract"
# filter_query = "013 in* lens_id"
# filter_query = "'exists' in* abstract"
# filter_query = "['modules', extreme] in* title"
# filter_query = "extreme in* [title, abstract]"
# filter_query = "[[systemic, 'equity']] in* title"
# filter_query = "[[procyc, 'module']] in* [title, abstract]"
# filter_query = "['modules', extreme] in* [title, abstract]"
# filter_query = "~systemic in* title"
# filter_query = "~(~public in* title | extreme in* abstract)"
# filter_query = "~'exists' in* abstract"
# filter_query = "~['modules', extreme] in* title"
filter_query = "~[[systemic risk, 'equity']] in* title"

# filter_pandas_query = generate_pandas_query_string(filter_query)

biblio_df = read_and_merge_csv_files(project = data_project, 
                                    input_dir = 'raw/lens',
                                    biblio_type = BiblioType.LENS,
                                    n_rows = 3)

biblio_df = rename_and_retain_cols_biblio_df(biblio_df = biblio_df, reshape_base = Reshape.LENS_COMPACT)
biblio_df = normalise_biblio_entities(biblio_df = biblio_df)
biblio_df = clean_biblio_df(biblio_df = biblio_df)

biblio_df = filter_biblio_df(biblio_df = biblio_df,
                             query_str = filter_query)

_, excel_wb = highlight_keywords(biblio_df = biblio_df,
                                highlight_params = highlight_params,
                                # xlsx_cols = ['title', 'abstract', 'year'],
                                excel_params= excel_params)

if excel_wb:
    excel_wb.save(root_dir / 'data' / data_project / 'results' / 'highlights.xlsx')

