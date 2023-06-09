import pandas as pd
import numpy as np
# import nltk
# import spacy

from pathlib import Path
from io import BytesIO

from config import *
from typing import Union, List, Dict, Optional, Any

# nltk.download('wordnet')
# nltk.download('punkt')
# nlp = spacy.load("en_core_web_sm")  # conda install -c conda-forge spacy-model-en_core_web_sm

def get_root_dir() -> Path:
    """
    Returns the absolute path to the root folder of the Python project.
    Assumes the presence of a list of marker files or directories indicating the root.

    Globals:
        project_root_markers (List[str]): A list of file and directory names to be checked as markers. 
        Defined in `config.py`.

    Returns:
        A string representing the absolute path to the root folder.

    Raises:
        ValueError: If none of the marker files could be found.
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
        biblio_project_dir: 
            The name of the bibliometric project directory.

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
        biblio_project_dir: 
            The name of the bibliometric project directory.

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
    project directory `biblio_project_dir_name`, in the `data` and `models`
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
        biblio_project_dir_name: 
            The name of the biblio project directory.

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


def validate_output_dir_and_ext(biblio_project_dir_name: str, 
                                output_file: str,
                                output_dir: str,
                                file_extensions: List[str]
                                ) -> None:
    """
    Checks that the target directory exists and that output_file has a valid extension.

    If output_file is provided, check that it ends in `.csv` or `.xlsx` and that the directory 
    `output_dir` exists on the path `root_dir/data_root_dir/biblio_project_dir_name/output_dir`.
    
    Args:
        biblio_project_dir_name: 
            The name of the bibliometric project directory.
        output_file: 
            The name of the output file. 
        output_dir: 
            The name of the output directory.
        file_extensions: 
            List of valid file extensions.

    Raises: 
        ValueError: If any of the conditions described above are not met.

    Returns:
        None
    """

    root_dir = get_root_dir()

    # Check that the output_dir exists
    output_path = Path(root_dir, data_root_dir, biblio_project_dir_name, output_dir)
    if not output_path.is_dir():
        raise ValueError(f"Output directory does not exist: {output_path}")
    
    # Check if the output_file has a valid extension
    if file_extensions and not Path(output_file).suffix in file_extensions:
        ext_str = ', '.join(file_extensions[:-1]) + f" or {file_extensions[-1]}"
        raise ValueError(f"The file name '{output_file}' needs to end in {ext_str}")


def is_none_nan_empty(value: Any) -> bool:
    if pd.isna(value) or value is None or not str(value).strip():
        return True
    return False


def is_not_none_nan_empty(value: Any) -> bool:
    return not is_none_nan_empty(value)


def empty_strings_to_nan(value: Any) -> Union[float, Any]:

    if pd.isna(value) or value is None or not str(value).strip():
        return np.nan
    return value


def merge_biblio_dfs(*biblio_dfs_: pd.DataFrame) -> pd.DataFrame:
    '''
    Merge multiple bibliogrpahic datasets from different sources (Scopus, Lens, 
    Dimensions, Biblio). 
    
    The datasets are stacked vertically so that dataset columns with the same name are 
    in the same column in the resulting dataset. Columns that are specific to a particular 
    bibliographic database are either merged as part of the `clean`function or they can 
    be droped using `modify_cols_biblio_df` function.

    Args:
        *biblio_df_:
            One or several bibliographic datasets `df1, df2, ...`
    
    Returns:
        A dataframe with the merged bibbliographic dataset
    '''

    biblio_dfs = []

    # Make copies of the dataframes and add them to a list
    for df in biblio_dfs_:
        biblio_dfs.append(df.copy().reset_index(drop = True))

    # Stack the different dataframes on top of each other
    merged_df = pd.concat(biblio_dfs, ignore_index = True)

    return merged_df


def write_df(biblio_df: pd.DataFrame,
             biblio_project_dir: str,
             output_dir: str,
             output_file: str
             ) -> None:
    """
    Write a bibliographic dataset to a file in `output_dir` in the bibliometric project.

    Args:
        biblio_df: 
            The bibliographic dataset (e.g. Scopus, Lens, Dimensions, Biblio,...).
        biblio_project_dir_name: 
            The name of the bibliometric project directory.
        output_dir:  
            The name of the output directory.
        output_file: 
            The name of the output file.

    Raises:
        ValueError: If the `output_file` parameter does not have the extension .csv or .xlsx.

    Returns:
        None
    """
    
    # TODO:
    #   - Add timestamping
    
    allowed_file_extensions = ['.csv', '.xlsx']
    root_dir = get_root_dir()

    # Check if the output_file parameter has a valid extension and if the output directory exists
    validate_output_dir_and_ext(biblio_project_dir_name = biblio_project_dir,
                             output_dir = output_dir,
                             output_file = output_file,
                             file_extensions = allowed_file_extensions)

    output_path = Path(root_dir, data_root_dir, biblio_project_dir, output_dir, output_file)
    
    logger.info(f"Writing biblio_df ({len(biblio_df)} records) to file '{output_file}'...")

    # Write the bibliographic dataset to output_file based on the file extension
    if Path(output_file).suffix == '.csv':
        biblio_df.to_csv(output_path, index = False)
    elif Path(output_file).suffix == '.xlsx':
        biblio_df.to_excel(output_path, index = False)

    return


def missing_strings_to_empty(biblio_df_: pd.DataFrame) -> pd.DataFrame:

    if biblio_df_.empty:
        return biblio_df_
    
    biblio_df = biblio_df_.copy()

    string_columns = [col for col in biblio_df.columns if type(biblio_df[col].iloc[0]).__name__ == 'str']
    biblio_df[string_columns] = biblio_df[string_columns].fillna('')

    return biblio_df


def string_to_biblio_source(bstr: str) -> BiblioSource:

    if bstr == 'scopus':
        biblio_source = BiblioSource.SCOPUS
    elif bstr == 'lens':
        biblio_source = BiblioSource.LENS
    elif bstr == 'dims':
        biblio_source = BiblioSource.DIMS
    elif bstr == 'biblio':
        biblio_source = BiblioSource.BIBLIO
    else:
        biblio_source = BiblioSource.UNDEFINED

    return biblio_source


def biblio_source_to_string(biblio_source: BiblioSource) -> str:

    if biblio_source == BiblioSource.SCOPUS:
        bstr = 'scopus'
    elif biblio_source == BiblioSource.LENS:
        bstr = 'lens'
    elif biblio_source == BiblioSource.DIMS:
        bstr = 'dims'
    elif biblio_source == BiblioSource.BIBLIO:
        bstr = 'biblio'
    else:
        bstr = ''

    return bstr


def read_biblio_csv_files_to_df(biblio_project_dir: str, 
                                input_dir: str, 
                                input_files: Union[str, List[str]] = '',
                                biblio_source: BiblioSource = BiblioSource.UNDEFINED,
                                n_rows: Optional[int] = None,
                                missing_str_to_empty = True,
                                sample = False
                                ) -> pd.DataFrame:
    """
    Read bibliographic datasets from CSV files and store in a `DataFrame`.

    The function can read single files, multiple files, and all files in a directory:

    - Single file: provide a file name with the extension `.csv` for `csv_file_names`.
    - Multiple files, method 1: provide a list with file names.
    - Multiple files method 2: don't specify `csv_file_names`. I this case, it will
                               read all the files in the `input_dir`.
    
    If the files are in different directories, this can be specified as a path in 
    the `csv_file_names` string(s).

    Args:
        biblio_project_dir_name: 
            The name of the bibliometric project directory.
        input_dir: 
            The name of the directory that contains the files.
        csv_file_names: 
            The name(s) of the CSV file(s) to read. If empty, all CSV files 
            in the input directory are read.
        biblio_source: 
            The type of bibliographic data being read (`SCOPUS`, `LENS`, `DIMS`, or `BIBLIO`).
            `BIBLIO` refers to the normalised bibliographic dataset format used
            in BiblioKeywords.
        n_rows:
            The maximum number of rows to read from each CSV file. Reads all rows if omitted.
        missing_str_to_empty:
            All missiing string values are set to empty string "".

    Returns:
        The merged DataFrame containing the bibliographic data.

    Raises:
        ValueError:
            - If the input directory does not exist.
            - If the `biblio_type` parameter is set to `BiblioType.UNDEFINED`.
            - If the `biblio_type` parameter is not one of the supported types: `SCOPUS`, `LENS`, `DIMS`, or `BIBLIO`.
    """
    
    root_dir = get_root_dir()

    input_dir_path = Path(root_dir, data_root_dir, biblio_project_dir, input_dir)

    if not input_dir_path.exists():
        raise ValueError(f"The folder {input_dir_path} does not exist")
    
    if biblio_source == BiblioSource.UNDEFINED:
        raise ValueError(f"The parameter biblio_source needs to be set to: SCOPUS, LENS, DIMS, OR BIBLIO")
        
    # Skip the first row in a Dimensions CSV file, which contains details about the search
    skip_rows = 1 if biblio_source == BiblioSource.DIMS else 0

    # Convert single file name to list
    if isinstance(input_files, str):
        input_files = [input_files] if input_files else []

    # Add .csv extension if missing
    input_files = [f'{f}.csv' if not f.endswith('.csv') else f for f in input_files]

    # Read all CSV files in the input directory if csv_files is empty
    if not input_files:
        input_files = [f.name for f in input_dir_path.glob('*.csv')]

    # If n_rows = 0, keep all the rows in the dataframe
    if isinstance(n_rows, int) and (n_rows < 1):
        n_rows = None

    all_dfs = []

    # Read all CSV files and store in a list
    logger.info(f'Reading {len(input_files)} CSV files...')

    for csv_file_name in input_files:
        csv_path = input_dir_path / csv_file_name
        if sample:
            df = pd.read_csv(csv_path, skiprows = skip_rows, on_bad_lines = 'skip')
        else:
            df = pd.read_csv(csv_path, nrows = n_rows, skiprows = skip_rows, on_bad_lines = 'skip')
        all_dfs.append(df)
        logger.info(f'File: {csv_file_name}, Size: {len(df)} rows')

    # Merge all dataframes into one
    biblio_df = pd.concat(all_dfs, ignore_index = True)

    # Sample or if not sampling, apply the cutoff again in case multiple files were read
    if sample:
        if isinstance(n_rows, int) and (n_rows > 0):
            biblio_df = biblio_df.sample(n = n_rows).reset_index(drop = True)
        else:
            raise ValueError(f"Because sample = True, the argument n_rows needs to be set to a positive integer")
    else:
        if isinstance(n_rows, int) and (n_rows > 0):
            biblio_df = biblio_df.head(n_rows)

    # Set all missing string values to empty string (if missing_str_to_empty = True, which is the default)
    if missing_str_to_empty:
        biblio_df = missing_strings_to_empty(biblio_df)

    # Create the bib_src column and set to the biblio_type
    if biblio_source == BiblioSource.SCOPUS:
        biblio_df['bib_src'] = 'scopus'
    elif biblio_source == BiblioSource.LENS:
        biblio_df['bib_src'] = 'lens'
    elif biblio_source == BiblioSource.DIMS:
        biblio_df['bib_src'] = 'dims'
    elif biblio_source == BiblioSource.BIBLIO:
        biblio_df['bib_src'] = 'biblio'
    else:
        raise ValueError(f"The parameter biblio_type needs to be set to: SCOPUS, LENS, DIMS, OR BIBLIO")

    logger.info(f"Total number of publications in the dataframe: {len(biblio_df)}")

    return biblio_df



