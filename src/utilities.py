import os
import pandas as pd
import cmd
import inspect

from config import *
from typing import Union, List, Dict, Optional
from pathlib import Path
from IPython.core.display import HTML


def get_root_dir() -> Path:
    """
    Returns the absolute path to the root folder of the Python project.
    Assumes the presence of a list of marker files or directories indicating the root.

    Globals:
        project_root_markers (List[str]): A list of file and directory names to be checked as markers. 
        Defined in config.py.

    Returns:
        A string representing the absolute path to the root folder.
        None is returned if the root folder cannot be determined.
    """

    current_dir = Path(__file__).resolve().parent

    # Traverse up the directory hierarchy until any marker is found or the root is reached
    while not any((current_dir / marker).exists() for marker in project_root_markers):
        parent_dir = current_dir.parent

        # If the current directory is the actual root, exit the loop as no marker was found
        if current_dir == parent_dir:
            raise ValueError(f"Could not find any of the markers in [{','.join(project_root_markers)}]")
        
        current_dir = parent_dir

    return current_dir


def get_data_dir(biblio_project_dir_name: str) -> Path:
    """
    Returns the path to the data directory of a bibliometric project.

    Args:
        biblio_project_dir: The name of the bibliometric project directory.

    Returns:
        A Path object representing the path to the bibliometric project's data directory.

    Raises:
        ValueError: If the data directory does not exist.
    """

    # Get the root directory of the project
    root_dir = get_root_dir()

    # Construct the path to the data directory
    data_dir = Path(root_dir, data_root_dir, biblio_project_dir_name)

    # Check if the path exists
    if not data_dir.exists():
        raise ValueError(f"The path '{data_dir}' does not exist.")

    return data_dir


def get_model_dir(biblio_project_dir_name: str) -> Path:
    """
    Returns the path to the model directory of a bibliometric project.

    Args:
        biblio_project_dir: The name of the bibliometric project directory.

    Returns:
        A Path object representing the path to the bibliometric project's model directory.

    Raises:
        ValueError: If the data directory does not exist.
    """

    # Get the root directory of the project
    root_dir = get_root_dir()

    # Construct the path to the data directory
    model_dir = Path(root_dir, model_root_dir, biblio_project_dir_name)

    # Check if the path exists
    if not model_dir.exists():
        raise ValueError(f"The path '{model_dir}' does not exist.")

    return model_dir


def create_biblio_project_folders(biblio_project_dir_name: str) -> None:
    """
    Creates the directory structure for a new bibliometric project. 
    
    A bibliometric project has bibliographic data and models that are stored in
    the data and models directories respectively. The CSV files and topic models
    for a literature review could for instance be stored in its own bibliometric
    project direcrtory 'biblio_project_dir_name', in the 'data' and 'model'
    subdirectories.

    The following folder structure is created by this function:

    - root_dir/
        - data/
            - biblio_project_dir_name/
                - raw/
                - processed/
                - results/
        - models/
            - biblio_project_dir_name/

    Args:
        biblio_project_dir_name (str): The name of the biblio project directory.

    Returns:
        None
    """

    # Set the root directory of the project
    root_dir = get_root_dir()
    data_dir = get_data_dir(biblio_project_dir_name)
    model_dir = get_model_dir(biblio_project_dir_name)

    # Create the folder structure if the project directory doesn't exist
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        (data_dir / 'raw').mkdir()
        (data_dir / 'processed').mkdir()
        (data_dir / 'results').mkdir()

    if not model_dir.exists():
        model_dir.mkdir(parents=True)

    logger.info(f"Working directory: {root_dir}")

    return


def check_output_dir_and_ext(biblio_project_dir_name: str, 
                      output_file: Optional[str] = None,
                      output_dir: Optional[str] = None,
                      file_extensions: Optional[List[str]] = None
                      ) -> None:
    """
    Checks that the target directory exists and that output_file has a valid extension.

    If output_file is provided, check that it ends in .csv or .xlsx and that there is 
    an output_dir. If an output_dir is provided, check if it exists in the directory 
    path of root_dir/data_root_dir/project/output_dir.

    Args:
        biblio_project_dir_name: The name of the bibliometric project directory.
        output_file: The name of the output file (optional). 
        output_dir (optional): The name of the output directory (optional).
        file_extensions: List of valid file extensions (optional).

    Raises: 
        ValueError: If any of the conditions described above are not met.

    Returns:
        None
    """

    root_dir = get_root_dir()

    # If output_file is provided, check that output_dir is also provided
    if output_file:
        if output_dir:
            output_path = Path(root_dir, data_root_dir, biblio_project_dir_name, output_dir)
            if not output_path.is_dir():
                raise ValueError(f"Output directory does not exist: {output_path}")
        else:
            raise ValueError(f"Since you have provided an output file name, you also need to provide an output directory name")
        
        # Check if the output_file has a valid extension
        if file_extensions and not Path(output_file).suffix in file_extensions:
            ext_str = ', '.join(file_extensions[:-1]) + f" or {file_extensions[-1]}"
            raise ValueError(f"The file name '{output_file}' needs to end in {ext_str}")


def write_df(biblio_df: pd.DataFrame,
             biblio_project_dir_name: str,
             output_dir: str,
             output_file: str
             ) -> None:
    """
    Write a bibliographic dataset to a file in output_dir in the bibliometric project.

    Args:
        biblio_df: The bibliographic dataset (e.g. Scopus, Lens, Dimensions, Biblio,...).
        biblio_project_dir_name: The name of the bibliometric project directory.
        output_dir:  The name of the output directory.
        output_file: The name of the output file.

    Raises:
        ValueError: If the output_file parameter does not have the extension .csv or .xlsx.

    Returns:
        None

    TODO: Add timestamping
    """

    allowed_file_extensions = ['.csv', '.xlsx']
    root_dir = get_root_dir()

    # Check if the output_file parameter has a valid extension and if the output directory exists
    check_output_dir_and_ext(biblio_project_dir_name = biblio_project_dir_name,
                             output_dir = output_dir,
                             output_file = output_file,
                             file_extensions = allowed_file_extensions)

    output_path = Path(root_dir, data_root_dir, biblio_project_dir_name, output_dir, output_file)
    
    logger.info(f"Writing biblio_df to file {output_file}...")

    # Write the bibliographic dataset to output_file based on the file extension
    if Path(output_file).suffix == '.csv':
        biblio_df.to_csv(output_path, index = False)
    elif Path(output_file).suffix == '.xlsx':
        biblio_df.to_excel(output_path, index = False)

    return


def read_biblio_csv_files_to_df(biblio_project_dir_name: str, 
                                input_dir: str, 
                                csv_file_names: Union[str, List[str]] = '',
                                biblio_source: BiblioType = BiblioType.UNDEFINED,
                                n_rows: Optional[int] = None,
                                ) -> pd.DataFrame:
    """
    Read bibliographic datasets from CSV files and store in a DataFrame.

    The function can read single files, multiple files, and all files in a directory:

    - Single file: provide a file name with the extension .csv for csv_file_names.
    - Multiple files, method 1: provide a list with file names.
    - Multiple files method 2: don't specify csv_file_names. I this case, it will
                               read all the files in the input_dir.
    
    If the files are in different directories, this can be specified as a path in 
    the csv_file_names string(s).

    Args:
        biblio_project_dir_name: 
            The name of the bibliometric project directory.
        input_dir: 
            The name of the directory that contains the files.
        csv_file_names: 
            The name(s) of the CSV file(s) to read. If empty, all CSV files 
            in the input directory are read.
        biblio_source: 
            The type of bibliographic data being read (SCOPUS, LENS, DIMS, or BIBLIO).
            BIBLIO refers to the normalised bibliographic dataset format used
            in BiblioKeywords.
        n_rows:
            The maximum number of rows to read from each CSV file. Reads all rows if omitted.

    Returns:
        pd.DataFrame:
            The merged DataFrame containing the bibliographic data.

    Raises:
        ValueError:
            - If the input directory does not exist.
            - If the biblio_type parameter is set to BiblioType.UNDEFINED.
            - If the biblio_type parameter is not one of the supported types: SCOPUS, LENS, DIMS, or BIBLIO.
    """
    
    root_dir = get_root_dir()

    input_dir_path = Path(root_dir, data_root_dir, biblio_project_dir_name, input_dir)

    if not input_dir_path.exists():
        raise ValueError(f"The folder {input_dir_path} does not exist")
    
    if biblio_source == BiblioType.UNDEFINED:
        raise ValueError(f"The parameter biblio_source needs to be set to: SCOPUS, LENS, DIMS, OR BIBLIO")
        
    # Skip the first row in a Dimensions CSV file, which contains details about the search
    skip_rows = 1 if biblio_source == BiblioType.DIMS else 0

    # Convert single file name to list
    if isinstance(csv_file_names, str):
        csv_file_names = [csv_file_names] if csv_file_names else []

    # Add .csv extension if missing
    csv_file_names = [f'{f}.csv' if not f.endswith('.csv') else f for f in csv_file_names]

    # Read all CSV files in the input directory if csv_files is empty
    if not csv_file_names:
        csv_file_names = [f.name for f in input_dir_path.glob('*.csv')]

    all_dfs = []

    # Read all CSV files and store in a list
    logger.info(f'Reading {len(csv_file_names)} CSV files...')

    for csv_file_name in csv_file_names:
        csv_path = input_dir_path / csv_file_name
        df = pd.read_csv(csv_path, nrows = n_rows, skiprows = skip_rows, on_bad_lines = 'skip')
        all_dfs.append(df)
        logger.info(f'File: {csv_file_name}, Size: {len(df)} rows')

    # Merge all dataframes into one
    biblio_df = pd.concat(all_dfs, ignore_index = True)

    # Apply cutoff again in case multiple files were read
    if isinstance(n_rows, int):
        biblio_df = biblio_df.head(n_rows)

    # Create the bib_src column and set to the biblio_type
    if biblio_source == BiblioType.SCOPUS:
        biblio_df['bib_src'] = 'scopus'
    elif biblio_source == BiblioType.LENS:
        biblio_df['bib_src'] = 'lens'
    elif biblio_source == BiblioType.DIMS:
        biblio_df['bib_src'] = 'dims'
    elif biblio_source == BiblioType.BIBLIO:
        biblio_df['bib_src'] = 'biblio'
    else:
        raise ValueError(f"The parameter biblio_type needs to be set to: SCOPUS, LENS, DIMS, OR BIBLIO")

    logger.info(f"Total number of publications in the dataframe: {len(biblio_df)}")

    return biblio_df


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

