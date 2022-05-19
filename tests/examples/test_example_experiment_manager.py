# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/examples/tst.example_experiment_manager.ipynb (unless otherwise specified).

__all__ = ['test_example_experiment_manager']

# Cell
import pytest
import pandas as pd
import os
import joblib
from IPython.display import display
from dsblocks.utils.nbdev_utils import md

from hpsearch.examples.example_experiment_manager import *
from hpsearch.examples.dummy_experiment_manager import generate_data

# Comes from example_experiment_manager.ipynb, cell
def test_example_experiment_manager ():
    em = ExampleExperimentManager (path_experiments='test_example_experiment_manager',
                                   verbose=0)
    parameters = dict(my_third=3.0)
    other_parameters = dict()
    em.grid_search (log_message='single input, learning rate and regularization grid search, 500 epochs',
            parameters_multiple_values=dict(my_first=[0.6, 0.3], my_second=[1.2, 2.3, 4.0]),
            parameters_single_value = parameters,
            other_parameters=other_parameters,
            nruns=1)

    em.remove_previous_experiments ()