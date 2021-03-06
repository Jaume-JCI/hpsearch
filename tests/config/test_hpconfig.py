# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/config/tst.hpconfig.ipynb (unless otherwise specified).

__all__ = ['test_get_experiment_manager', 'test_get_em_args', 'test_modify_experiment_manager', 'test_add_em_args',
           'test_register_manager']

# Cell
import pytest
import pandas as pd
import numpy as np
import os
import joblib
from IPython.display import display
from dsblocks.utils.nbdev_utils import md
import pickle
import shutil

from sklearn.utils import Bunch

from dsblocks.utils.utils import check_last_part, remove_previous_results

from hpsearch.config.hpconfig import *
from hpsearch.examples.dummy_experiment_manager import DummyExperimentManager, generate_data

# Comes from hpconfig.ipynb, cell
def test_get_experiment_manager ():
    em = generate_data ('get_experiment_manager')
    path_experiments = str(em.path_experiments.parent)
    manager_path = em.manager_path
    em_orig = em
    del em

    em = get_experiment_manager (manager_path)
    check_last_part (em.path_experiments, 'test_get_experiment_manager/default')
    assert em.key_score == 'validation_accuracy' and em.op == 'max'

    em = get_experiment_manager (manager_path, path_experiments='my_new_parent_path/my_new_folder',
                               metric='new_metric', op='min')
    check_last_part (em.path_experiments, 'my_new_parent_path/my_new_folder')
    assert em.key_score == 'new_metric' and em.op == 'min'

    em = get_experiment_manager (manager_path, folder='other_folder')
    check_last_part (em.path_experiments, 'my_new_parent_path/other_folder')
    assert em.key_score == 'new_metric' and em.op == 'min'
    remove_previous_results (path_experiments)

# Comes from hpconfig.ipynb, cell
def test_get_em_args ():
    em_args = get_em_args ({'hello': 1, 'path_experiments': 'mypath', 'folder': None})
    assert (em_args=={'path_experiments': 'mypath'})

# Comes from hpconfig.ipynb, cell
def test_modify_experiment_manager ():
    em = DummyExperimentManager ()
    check_last_part (em.path_experiments, 'results')
    assert em.key_score == 'validation_accuracy' and em.op == 'max'

    modify_experiment_manager (em, path_experiments='my_new_parent_path/my_new_folder',
                               metric='new_metric', op='min')
    check_last_part (em.path_experiments, 'my_new_parent_path/my_new_folder')
    assert em.key_score == 'new_metric' and em.op == 'min'

    modify_experiment_manager (em, folder='other_folder')
    check_last_part (em.path_experiments, 'my_new_parent_path/other_folder')
    assert em.key_score == 'new_metric' and em.op == 'min'

# Comes from hpconfig.ipynb, cell
def test_add_em_args ():
    import argparse

    # by default, add multiple string parameters
    parser = argparse.ArgumentParser(description='test')
    add_em_args (parser)
    pars = parser.parse_args([])
    assert hasattr(pars, 'metric') and hasattr(pars, 'manager_path')

    # we can skip some of those using `but`:
    parser = argparse.ArgumentParser(description='test')
    add_em_args (parser, but=['metric'])
    pars = parser.parse_args([])
    assert not hasattr(pars, 'metric') and hasattr(pars, 'manager_path')

# Comes from hpconfig.ipynb, cell
def test_register_manager ():
    em = generate_data ('register_manager')
    manager_path = em.manager_path
    em_orig = em
    del em
    em = get_experiment_manager (manager_path)
    assert em is not None

    register_manager (None)
    import hpsearch.config.hpconfig as hpcfg
    assert hpcfg.mf.experiment_manager is None

    em_orig.remove_previous_experiments (parent=True)