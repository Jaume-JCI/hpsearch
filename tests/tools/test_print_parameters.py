# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/tools/tst.print_parameters.ipynb (unless otherwise specified).

__all__ = ['test_print_parameters']

# Cell
import pytest
import pandas as pd
import os
import joblib
from IPython.display import display
from block_types.utils.nbdev_utils import md

from hpsearch.tools.print_parameters import *
from hpsearch.examples.dummy_experiment_manager import generate_data

# Comes from print_parameters.ipynb, cell
def test_print_parameters ():
    em = generate_data ('print_parameters')

    print_parameters (3)

    em.remove_previous_experiments ()