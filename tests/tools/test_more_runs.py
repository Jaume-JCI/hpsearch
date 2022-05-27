# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/tools/tst.more_runs.ipynb (unless otherwise specified).

__all__ = ['test_parse_arguments_and_run_more_runs']

# Cell
import pytest
import pandas as pd
import os
import joblib
from IPython.display import display
from dsblocks.utils.nbdev_utils import md

import hpsearch.config.hp_defaults as dflt
from hpsearch.tools.more_runs import *
from hpsearch.examples.complex_dummy_experiment_manager import generate_data

# Comes from more_runs.ipynb, cell
def test_parse_arguments_and_run_more_runs ():
    em = generate_data ('test_parse_arguments_and_run_more_runs')

    df = em.get_experiment_data ()
    assert df.shape==(9,29)

    args = ['-e', '4', '3', '-p', em.manager_path]
    parse_arguments_and_run (args)
    em.raise_error_if_run=True
    df = em.get_experiment_data ()
    assert df[dflt.scores_col, 'validation_accuracy'].columns.tolist() == list(range(5))
    assert df.shape==(9,29)

    args = ['-e', '4', '3', '--runs', '10', '-p', em.manager_path]
    em.raise_error_if_run=False
    parse_arguments_and_run (args)
    df = em.get_experiment_data ()
    assert df.shape==(9,54)
    assert df[dflt.scores_col, 'validation_accuracy'].columns.tolist() == list(range(10))

    em.remove_previous_experiments (parent=True)