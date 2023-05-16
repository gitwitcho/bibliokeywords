import os
import pandas as pd
import cmd
import inspect

from config import *
from typing import Union, List, Dict, Optional
from pathlib import Path
from IPython.core.display import HTML


def get_root_dir() -> Path:
    root_dir = Path(__file__).resolve().parents[1]
    return root_dir


def get_data_dir(project: str) -> Path:
    return Path(get_root_dir(), data_root_dir, project)


def get_model_dir(project: str) -> Path:
    return Path(get_root_dir(), model_root_dir, project)


def create_biblio_folders(project: str) -> Path:
    """
    Creates the data folder structure for a new project with the given name. This assumes
    that this python file is located in the root_dir/src folder.

    Args:
    project (str): The name of the project folder inside the data folder.

    Returns:
    root_dir (str): The root directory of the 
    """

    # Set the root directory of the project
    # root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    root_dir = get_root_dir()
    data_dir = get_data_dir(project)
    model_dir = get_model_dir(project)

    # Create the folder structure if the project directory doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        os.makedirs(os.path.join(data_dir, 'raw'))
        os.makedirs(os.path.join(data_dir, 'processed'))
        os.makedirs(os.path.join(data_dir, 'results'))

    # if not os.path.exists(os.path.join(root_dir, 'data/processed', project)):
    #     os.makedirs(os.path.join(root_dir, 'data/processed', project))

    # if not os.path.exists(os.path.join(root_dir, 'data/results', project)):
    #     os.makedirs(os.path.join(root_dir, 'data/results', project))

    if not os.path.exists(model_dir):
        os.makedirs(os.path.join(model_dir))

    logger.info(f"Working directory: {root_dir}")

    return root_dir


def check_output_file(root_dir: Path,
                      project: str, 
                      output_file: Optional[str] = None,
                      output_dir: Optional[str] = None
                      ) -> None:
    """
    Checks that an output file and directory exist with the correct file extension.

    If output_file is provided, check that it ends in .csv or .xlsx and that there is 
    an output_dir. If an output_dir is provided, check if it exists in the directory 
    path of root_dir/data_root_dir/project/output_dir.

    Raises: 
        ValueError: If any of the conditions described above are not met. 

    Parameters:
    
    root_dir (Path): 
        The root directory of the project.
    project (str): 
        The name of the project.
    output_file (Optional[str]): 
        The name of the output file (optional). 
    output_dir (Optional[str]): 
        The name of the output directory (optional).

    Returns:
        None
    """

    # If output_file is provided, check that it ends in .csv or .xlsx and that there is an output_dir
    if output_file:
        if output_dir:
            output_path = Path(root_dir, data_root_dir, project, output_dir)
            if not output_path.is_dir():
                raise ValueError(f"Output directory does not exist: {output_path}")
        else:
            raise ValueError(f"Since you have provided an output file name, you also need to provide an output directory name")
        if not Path(output_file).suffix in ['.csv', '.xlsx']:
            raise ValueError(f"The file name '{output_file}' needs to end in .csv or .xlsx")


def write_df(biblio_df: pd.DataFrame,
             project: str,
             output_dir: str,
             output_file: str
             ) -> None:

    """
    Write a pandas DataFrame to a file in the project's output directory.

    Parameters:

    biblio_df (pd.DataFrame): 
        The DataFrame to write to file.
    project (str): 
        The name of the project.
    output_file (str): 
        The name of the output file.
    output_dir (str): 
        The name of the output directory.

    Raises:
        ValueError: If the output_file parameter does not have the extension .csv or .xlsx.

    Returns:
        None
    
    TODO: Add timestamping
    """
    root_dir = get_root_dir()

    check_output_file(root_dir = root_dir,
                      project = project,
                      output_dir = output_dir,
                      output_file = output_file)

    logger.info(f"Writing biblio_df to file {output_file}")
    output_path = Path(root_dir, data_root_dir, project, output_dir, output_file)
    
    if Path(output_file).suffix == '.csv':
        biblio_df.to_csv(output_path, index = False)
    elif Path(output_file).suffix == '.xlsx':
        biblio_df.to_excel(output_path, index = False)
    else:
        raise ValueError("Currently only output files with the extension .csv or .xlsx are allowed")
    

def write_keyword_count_to_console(keywords_dict: Dict,
                                   max_n_rows: int,
                                   display_width: int = 120):
    
    cli = cmd.Cmd()

    for col, kw_count_df in keywords_dict.items():

        # Create the list of keyword-count pairs
        kw_count_str_list = kw_count_df.apply(lambda row: str(row['kw']) + ' (' + str(row['count']) + ')', axis=1).tolist()
        total_n_keywords = len(kw_count_str_list)

        # Adjust the list to the available display width and the given maximum number of rows
        cumulative_str_lengths = [sum(len(string) for string in kw_count_str_list[:i+1]) for i in range(len(kw_count_str_list))]
        max_characters = max_n_rows * display_width
        cutoff_idx = max((i for i, num in enumerate(cumulative_str_lengths) if num < max_characters), default = 0)
        kw_count_str_list = kw_count_str_list[:cutoff_idx]

        # Print the result
        print(f"\nKeywords for column '{col}")
        print(f"Displaying {len(kw_count_str_list)} keywords of a total of {total_n_keywords}")
        print("-------------------------------------------")
        cli.columnize(kw_count_str_list, displaywidth = display_width)  # neat function to print a list of values to a compact column
        print("-------------------------------------------")


def stack_keyword_count_dfs(keywords_dict: Dict) -> pd.DataFrame:

    # Get the maximum number of rows among the dataframes
    max_rows = max(df.shape[0] for df in keywords_dict.values())
        
    stacked_df = pd.DataFrame(index = range(max_rows))

    # Modify column names for each dataframe
    for key, df in keywords_dict.items():
        new_column_names = {df.columns[0]: key, df.columns[1]: key + '_count'}
        df.rename(columns = new_column_names, inplace = True)

    # Extract the keyword dataframes from the dictionary into a list
    kws_df_list = list(keywords_dict.values())

    # Concatenate the keyword dataframes horizontally
    stacked_df = pd.concat([df.reindex(range(max_rows)) for df in kws_df_list], axis = 1)

    return stacked_df


def create_keyword_count_html(keywords_dict: Dict,
                              n_cols: int,
                              max_n_rows: int) -> HTML:
    
    kws_html_str = ''

    for col, kw_count_df in keywords_dict:

        kw_count_str_list = kw_count_df.apply(lambda row: str(row['kw']) + ' (' + str(row['count']) + ')', axis=1).tolist()

        # Calculate the number of rows in the table
        n_rows = len(kw_count_str_list) // n_cols + (len(kw_count_str_list) % n_cols > 0)
        num_rows_all = n_rows

        # Row cutoff
        if n_rows > max_n_rows:
            n_rows = max_n_rows

        # Create an HTML string to display the list of strings in a table
        kws_html_str = "<h3>Keywords for column '{col}'"
        kws_html_str += f"Total number of '{col}' keywords: {len(kw_count_str_list)}"
        kws_html_str += f"Displaying {n_rows} rows of a total of {max_n_rows}"
        kws_html_str += '<table style="width:100%;">'
        for j in range(n_cols):
            kws_html_str += '<td style="vertical-align:top;">'
            for i in range(n_rows):
                idx = j * n_rows + i
                if idx < len(kw_count_str_list) and kw_count_str_list[idx]:
                    kws_html_str += f'{kw_count_str_list}<br>'
            kws_html_str += '</td>'
        kws_html_str += '</table>'
        kws_html_str += '<br><br>'
        
    return HTML(kws_html_str)



def read_and_merge_csv_files(project: str, 
                             input_dir: str, 
                             csv_files: Union[str, List[str]] = '',
                             biblio_type: BiblioType = BiblioType.UNDEFINED,
                             n_rows: Optional[int] = None,
                             ) -> pd.DataFrame:
    
    root_dir = get_root_dir()

    _input_dir = Path(root_dir, data_root_dir, project, input_dir)

    if not _input_dir.exists():
        raise ValueError(f"The folder {_input_dir} does not exist")
    
    if biblio_type == BiblioType.UNDEFINED:
        raise ValueError(f"The parameter biblio_type needs to be set to: SCOPUS, LENS, DIMS, OR BIBLIO")
    
    # check_output_file(root_dir, project, output_file, output_dir)
    
    # Skip the first row in a Dimensions CSV file, which contains details about the search
    skip_rows = 1 if biblio_type == BiblioType.DIMS else 0

    # Convert single file name to list
    if isinstance(csv_files, str):
        csv_files = [csv_files] if csv_files else []

    # Add .csv extension if missing
    csv_files = [f'{f}.csv' if not f.endswith('.csv') else f for f in csv_files]

    # Read all CSV files in the input directory if csv_files is empty
    if not csv_files:
        csv_files = [f.name for f in _input_dir.glob('*.csv')]

    all_df = []

    # Read all CSV files and store in a list
    logger.info(f'Reading {len(csv_files)} CSV files...')

    for csv_file in csv_files:
        csv_path = _input_dir / csv_file
        df = pd.read_csv(csv_path, nrows = n_rows, skiprows = skip_rows, on_bad_lines = 'skip')
        all_df.append(df)
        logger.info(f'File: {csv_file}, Size: {len(df)} rows')

    # Merge all dataframes into one
    biblio_df = pd.concat(all_df, ignore_index = True)

    # Apply cutoff again in case multiple files were read
    if isinstance(n_rows, int):
        biblio_df = biblio_df.head(n_rows)

    # Create the bib_src column and set to the biblio_type
    if biblio_type == BiblioType.SCOPUS:
        biblio_df['bib_src'] = 'scopus'
    elif biblio_type == BiblioType.LENS:
        biblio_df['bib_src'] = 'lens'
    elif biblio_type == BiblioType.DIMS:
        biblio_df['bib_src'] = 'dims'
    elif biblio_type == BiblioType.BIBLIO:
        biblio_df['bib_src'] = 'biblio'
    else:
        raise ValueError(f"The parameter biblio_type needs to be set to: SCOPUS, LENS, DIMS, OR BIBLIO")

    logger.info(f"Total number of publications in the dataframe: {len(biblio_df)}")

    return biblio_df


def get_functions_with_docstrings(module):
    """
    Get a list of functions in a module along with their docstrings.

    Args:
        module: The module object.

    Returns:
        A list of tuples containing function name and docstring.
    """
    functions = inspect.getmembers(module, inspect.isfunction)
    return [(name, func.__doc__) for name, func in functions if func.__doc__]


