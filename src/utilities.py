import os
import pandas as pd

from config import *
from typing import Union, List, Dict, Optional
from pathlib import Path


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


def read_and_merge_csv_files(project: str, 
                             input_dir: str, 
                             csv_files: Union[str, List[str]] = '', 
                             n_rows: Optional[int] = None,
                             is_dimensions: bool = False
                             ) -> pd.DataFrame:
    
    root_dir = get_root_dir()

    _input_dir = Path(root_dir, data_root_dir, project, input_dir)

    if not _input_dir.exists():
        raise ValueError(f"The folder {_input_dir} does not exist")
    
    # check_output_file(root_dir, project, output_file, output_dir)
    
    # Skip the first row in a Dimensions CSV file, which contains details about the search
    skip_rows = 1 if is_dimensions else 0

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

    logger.info(f"Total number of publications in the dataframe: {len(biblio_df)}")

    # if output_file and output_dir:
    #     logger.info(f"Writing biblio_df to file {output_file}")
    #     output_path = Path(root_dir, 'data', project, output_dir, output_file)
        
    #     if Path(output_file).suffix == '.csv':
    #         biblio_df.to_csv(output_path, index = False)
    #     elif Path(output_file).suffix == '.xlsx':
    #         biblio_df.to_excel(output_path, index = False)

    return biblio_df




def read_biblio_files() -> None:
    pass


def clean_biblio_files() -> None:
    pass


# create_biblio_data_folders("ml_in_engineering")
