import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# from config import data_root_dir
from pathlib import Path
from utilities import get_data_dir, get_root_dir




# test_get_data_dir_with_existing_directory(Path(get_root_dir()))