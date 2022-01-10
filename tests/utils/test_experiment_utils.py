# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/utils/tst.experiment_utils.ipynb (unless otherwise specified).

__all__ = ['generate_data_exp_utils', 'test_get_scores_names', 'test_get_monitored_training_metrics',
           'test_replace_with_default_values']

# Cell
import pytest
import pandas as pd
import numpy as np
import os
import joblib
from IPython.display import display
from block_types.utils.nbdev_utils import md

from hpsearch.utils.experiment_utils import *
from hpsearch.examples.dummy_experiment_manager import (DummyExperimentManager,
                                                        run_multiple_experiments)

# Comes from experiment_utils.ipynb, cell
def generate_data_exp_utils (name_folder):
    em = DummyExperimentManager (path_experiments=f'test_{name_folder}', verbose=0)
    em.remove_previous_experiments ()
    run_multiple_experiments(em=em, nruns=5, noise=0.1, verbose=False,
                             values_to_explore=dict(offset=[0.1, 0.3, 0.6], epochs=[5, 10, 100]))
    run_multiple_experiments(em=em, nruns=5, noise=0.1, verbose=False, rate=0.0001,
                             values_to_explore=dict(offset=[0.1, 0.3, 0.6], epochs=[5, 10, 100]))
    return em

# Comes from experiment_utils.ipynb, cell
def test_get_scores_names ():
    em = generate_data_exp_utils ('get_scores_names')

    df = em.get_experiment_data ()
    scores_names = get_scores_names (df)
    print (scores_names)
    assert scores_names == ['test_accuracy', 'validation_accuracy']

    scores_names=get_scores_names (df, run_number=3, experiment=7)
    print(scores_names)
    assert list(np.sort(scores_names))==['test_accuracy', 'validation_accuracy']

    # test when only some scores are valid
    df2 = df.copy()
    df2.loc[7, '3_test_accuracy']=np.nan
    scores_names=get_scores_names (df2, run_number=3, experiment=7)
    print (scores_names)
    assert scores_names==['validation_accuracy']

    em.remove_previous_experiments()

# Comes from experiment_utils.ipynb, cell
def test_get_monitored_training_metrics ():
    em = generate_data_exp_utils ('get_monitored_training_metrics')

    monitored_metrics = get_monitored_training_metrics (0)
    print (monitored_metrics)
    assert monitored_metrics==['validation_accuracy', 'test_accuracy', 'accuracy']

    em.remove_previous_experiments()

# Comes from experiment_utils.ipynb, cell
def test_replace_with_default_values ():
    em = generate_data_exp_utils ('replace_with_default_values')

    df = em.get_experiment_data ()
    df=replace_with_default_values(df)
    assert (df.epochs.values == ([5.]*3 + [10.]*3 + [100.]*3)*2).all()

    em.remove_previous_experiments()