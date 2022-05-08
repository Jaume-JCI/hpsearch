# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/tools/tst.print_info.ipynb (unless otherwise specified).

__all__ = ['test_print_info', 'test_parse_args']

# Cell
import pytest
import pandas as pd
import os
import joblib
from IPython.display import display
from dsblocks.utils.nbdev_utils import md

from hpsearch.tools.print_info import *
from hpsearch.examples.dummy_experiment_manager import generate_data

# Comes from print_info.ipynb, cell
def test_print_info ():
    em = generate_data ('print_info')

    print_info (manager_path=em.manager_path)

    em.remove_previous_experiments ()

# Comes from print_info.ipynb, cell
def test_parse_args ():
    em = generate_data ('parse_args')

    args = ['-e', '4', '3',
       '--compact', '3',
       '--round', '3',
       '-p', em.manager_path]
    parse_arguments_and_run (args)

    em.remove_previous_experiments ()