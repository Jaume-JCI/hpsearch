# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/examples/tst.dummy_experiment_manager.ipynb (unless otherwise specified).

__all__ = ['test_dummy_experiment_manager']

# Cell
import pytest
import pandas as pd
import numpy as np
import os
import joblib
from IPython.display import display
from dsblocks.utils.nbdev_utils import md

import hpsearch.config.hp_defaults as dflt
from hpsearch.examples.dummy_experiment_manager import *
from hpsearch.examples.dummy_experiment_manager import generate_data

# Comes from dummy_experiment_manager.ipynb, cell
def test_dummy_experiment_manager ():
    em = generate_data ('dummy_experiment_manager')
    df = em.get_experiment_data ()
    display (df)

    # check that stored parameters are correct
    par = lambda parameter: (dflt.parameters_col, parameter, '')
    assert (df[par('epochs')].values == np.array([ 5.,  5.,  5., 15., 15., 15., 30., 30., 30.])).all()
    assert (df[par('offset')].values == np.array([0.1, 0.3, 0.6, 0.1, 0.3, 0.6, 0.1, 0.3, 0.6])).all()
    assert (df[par('rate')].values == 0.03).all()

    # check that the accuracy values are correct
    epochs_before_overfitting = 20
    epochs_test = 10
    for experiment_id in df.index:
        if df.loc[experiment_id, par('epochs')] < epochs_before_overfitting:
            accuracy = (df.loc[experiment_id, par('offset')] +
                        df.loc[experiment_id, par('rate')] * df.loc[experiment_id, par('epochs')])
        else:
            epochs_after_overfitting = df.loc[experiment_id, par('epochs')]-epochs_before_overfitting
            accuracy = (df.loc[experiment_id, par('offset')] +
                        df.loc[experiment_id, par('rate')] *
                        (epochs_before_overfitting  - epochs_after_overfitting))
        if df.loc[experiment_id, par('epochs')] < epochs_test:
            test_accuracy = accuracy + 0.1
        else:
            test_accuracy = accuracy - 0.1
        validation_accuracy = max(min(accuracy, 1.0), 0.0)
        test_accuracy = max(min(test_accuracy, 1.0), 0.0)

        #assert np.abs(df.loc[experiment_id, '0_validation_accuracy'] - validation_accuracy) <1.e-10, f"experiment {experiment_id}: {df.loc[experiment_id, '0_validation_accuracy']} == {validation_accuracy}"
        #assert np.abs(df.loc[experiment_id, '0_test_accuracy'] - test_accuracy) <1.e-10

        md ('check that model history is written correcly')
        path_experiment = em.get_path_results (3, 0)
    model = FakeModel()
    model.load_model_and_history(path_experiment)
    assert np.max(np.abs(model.history['accuracy']-np.arange(0.13, 0.55, 0.03))) < 1e-10

    em.experiment_visualization ([3,4,5], backend='matplotlib')

    em.remove_previous_experiments (parent=True)