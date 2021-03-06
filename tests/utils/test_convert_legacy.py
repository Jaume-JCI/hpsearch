# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/utils/tst.convert_legacy.ipynb (unless otherwise specified).

__all__ = ['generate_data', 'test_update_data_format', 'test_convert_run_numbers',
           'test_update_and_replace_experiment_data']

# Cell
import pytest
import pandas as pd
import numpy as np
import os
import joblib
from IPython.display import display
import datetime

from dsblocks.utils.nbdev_utils import md
from dsblocks.utils.utils import remove_previous_results

from hpsearch.utils.convert_legacy import *
from hpsearch.utils.experiment_utils import read_df, write_df
from hpsearch.examples.dummy_experiment_manager import (DummyExperimentManager,
                                                        run_multiple_experiments)
from hpsearch.examples.complex_dummy_experiment_manager import generate_data, init_em
from hpsearch.config import hp_defaults as dflt

# Comes from convert_legacy.ipynb, cell
def generate_data ():
    df = pd.DataFrame ([[0.1, 0.05, 0.6, 0.5, 0.0034384727478027344,
            datetime.time(10, 42, 26, 630428), True, 0.61, 0.51,
            0.002204418182373047, True, 0.62, 0.52, 0.002073526382446289, True],
           [0.2, 0.05, 0.7000000000000001, 0.6000000000000001,
            0.0020360946655273438, datetime.time(10, 42, 26, 669600), True,
            None, None, None, None, None, None, None, None]])
    df.columns = ['offset', 'rate', '0_validation_accuracy', '0_test_accuracy', 'time_0',
                                   'date', '0_finished', '1_validation_accuracy', '1_test_accuracy',
                                   'time_1', '1_finished', '2_validation_accuracy', '2_test_accuracy',
                                   'time_2', '2_finished']
    return df

def test_update_data_format ():
    # get data
    df = generate_data ()
    display (df)

    # run function
    df = update_data_format (df)

    # check results
    np.testing.assert_array_equal (df[('scores','validation_accuracy')].values,
                               np.array([[0.6, 0.61, 0.62], [0.7000000000000001, np.nan, np.nan]]))
    np.testing.assert_array_equal (df[('scores','test_accuracy')].values,
                               np.array([[0.5, 0.51, 0.52], [0.6000000000000001, np.nan, np.nan]]))

# Comes from convert_legacy.ipynb, cell
def test_convert_run_numbers ():
    # get data
    df = generate_data ()
    df = update_data_format (df)

    # run function
    df = convert_run_numbers (df)

    # check results
    rn = df[dflt.scores_col].columns.get_level_values(1)
    assert type(rn[0]) is int

# Comes from convert_legacy.ipynb, cell
def test_update_and_replace_experiment_data ():
    path_experiments = 'test_update_and_replace_experiment_data'
    os.makedirs (path_experiments, exist_ok=True)

    # get and write data
    df = generate_data ()
    write_df (df, path_experiments)
    display (df)

    # run function
    update_and_replace_experiment_data (path_experiments)
    print ('\nfiles written: ', os.listdir (path_experiments))

    # check results
    df = read_df (path_experiments)
    np.testing.assert_array_equal (df[('scores','validation_accuracy')].values,
                               np.array([[0.6, 0.61, 0.62], [0.7000000000000001, np.nan, np.nan]]))
    np.testing.assert_array_equal (df[('scores','test_accuracy')].values,
                               np.array([[0.5, 0.51, 0.52], [0.6000000000000001, np.nan, np.nan]]))

    remove_previous_results (path_experiments)