# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/tools/tst.rerun.ipynb (unless otherwise specified).

__all__ = ['test_parse_arguments_and_run_more_runs', 'test_parse_arguments_and_run_more_epochs',
           'test_parse_arguments_and_run_store']

# Cell
import pytest
import pandas as pd
import os
import joblib
from IPython.display import display
from dsblocks.utils.nbdev_utils import md

import hpsearch.config.hp_defaults as dflt
from hpsearch.tools.rerun import *
from hpsearch.examples.complex_dummy_experiment_manager import generate_data, init_em
import hpsearch.utils.experiment_utils as ut

# Comes from rerun.ipynb, cell
def test_parse_arguments_and_run_more_runs ():
    em = generate_data ('parse_arguments_and_run_more_runs',
                        folder='new_folder')

    df = em.get_experiment_data ()
    assert df.shape==(9,29)

    args = ['-e', '4', '3', '--verbose', '1', '-p', em.manager_path]
    parse_arguments_and_run (args)
    em.raise_error_if_run=True
    df = em.get_experiment_data ()
    assert df[dflt.scores_col, 'validation_accuracy'].columns.tolist() == list(range(5))
    assert df.shape==(9, 29)

    args = ['-e', '4', '3', '--runs', '10', '-p', em.manager_path]
    em.raise_error_if_run=False
    parse_arguments_and_run (args)
    df = em.get_experiment_data ()
    assert df.shape==(9,54)
    assert df[dflt.scores_col, 'validation_accuracy'].columns.tolist() == list(range(10))

    em.remove_previous_experiments (parent=True)

# Comes from rerun.ipynb, cell
def test_parse_arguments_and_run_more_epochs ():
    em = init_em ('parse_arguments_and_run_more_epochs')

    # get reference result
    _ = em.create_experiment_and_run (parameters={'offset':0.1, 'rate': 0.05, 'epochs': 7})
    df = em.get_experiment_data ()
    display (df)
    em.remove_previous_experiments (parent=True)

    # first 3 experiments
    _ = em.create_experiment_and_run (parameters={'offset':0.1, 'rate': 0.05, 'epochs': 5})
    _ = em.create_experiment_and_run (parameters={'offset':0.05, 'rate': 0.03, 'epochs': 6})
    _ = em.create_experiment_and_run (parameters={'offset':0.1, 'rate': 0.05, 'epochs': 9})
    _ = em.create_experiment_and_run (parameters={'offset':0.05, 'rate': 0.03, 'epochs': 10})
    _ = em.create_experiment_and_run (parameters={'offset':0.1, 'rate': 0.05, 'epochs': 11})
    df = em.get_experiment_data ()
    display (df)
    assert df.shape==(5,8)

    # more epochs
    #args = ['-e', '4', '3', '--epochs', '7', '-d']
    args = ['-e', '3', '--epochs', '7', '-d', '-p', em.manager_path]
    parse_arguments_and_run (
        args,
        em_attrs={'desired_path_results_previous_experiment':'test_parse_arguments_and_run_more_epochs/default/experiments/00001/0',
                 'desired_epochs': 1, 'desired_current_epoch': 7}
    )

    df = em.get_experiment_data ()
    print (df.shape)
    assert df.shape==(6,8)

    args = ['-e', '4', '--epochs', '7', '-d', '-p', em.manager_path]
    parse_arguments_and_run (
        args,
        em_attrs={'desired_path_results_previous_experiment':'test_parse_arguments_and_run_more_epochs/default/experiments/00000/0',
                 'desired_epochs': 2, 'desired_current_epoch': 7}
    )

    df = em.get_experiment_data ()
    print (df.shape)
    assert df.shape==(7,8)

    # *****************************************
    # *****************************************
    em.remove_previous_experiments (parent=True)
    em.desired_path_results_previous_experiment, em.desired_epochs, em.desired_current_epoch = None, None, None
    # first 3 experiments
    _ = em.create_experiment_and_run (parameters={'offset':0.1, 'rate': 0.05, 'epochs': 5})
    _ = em.create_experiment_and_run (parameters={'offset':0.05, 'rate': 0.03, 'epochs': 6})
    _ = em.create_experiment_and_run (parameters={'offset':0.1, 'rate': 0.05, 'epochs': 9})
    _ = em.create_experiment_and_run (parameters={'offset':0.05, 'rate': 0.03, 'epochs': 10})
    _ = em.create_experiment_and_run (parameters={'offset':0.1, 'rate': 0.05, 'epochs': 11})

    args = ['-e', '4', '3', '--epochs', '7', '-d', '-p', em.manager_path]
    parse_arguments_and_run (args)
    df = em.get_experiment_data ()
    print (df.shape)
    assert df.shape==(7,8)

    em.remove_previous_experiments (parent=True)

# Comes from rerun.ipynb, cell
def test_parse_arguments_and_run_store ():
    path_experiments = 'test_parse_arguments_and_run_store'
    em = generate_data (path_experiments,
                        folder='new_folder')

    df = em.get_experiment_data ()
    assert df.shape==(9,29)
    columns = ut.get_scores_columns (df, run_number=range(5), score_name='validation_accuracy')
    columns += ut.get_scores_columns (df, run_number=range(5), score_name='test_accuracy')

    # *************************************************
    # The following simulates the case where
    # many experiments were not saved probably
    # because they were interrupted with Ctrl-C
    # *************************************************
    df_orig = df.copy()
    columns = ut.get_scores_columns (df_orig)
    df[columns] = None
    path = em.path_experiments
    df.to_csv (path/'experiments_data.csv')
    df.to_pickle (path/'experiments_data.pk')
    df_overwritten = em.get_experiment_data ()
    assert (df_orig[columns]!=df_overwritten[columns]).all().all()

    parse_arguments_and_run ('--range-exp 0 9 --store --from-dict --runs 5 '
                             f'--min-iterations 1 -p {em.manager_path}'.split())

    df_new = em.get_experiment_data ()
    # TODO: see why finished is False after storing
    #assert (df_orig[columns]==df_new[columns]).all().all()
    x, y = df_orig[columns].astype('float'), df_new[columns].astype('float')
    #y[[f'{x}_finished' for x in range(5)]]=1.0
    pd.testing.assert_frame_equal(x,y)

    df = df_orig.copy()
    df.loc[1,columns] = None
    df.loc[3:,columns] = None
    df.to_csv (f'{path}/experiments_data.csv')
    df.to_pickle (f'{path}/experiments_data.pk')
    df_overwritten = em.get_experiment_data ()
    #assert (df_orig[columns]==df_overwritten[columns]).sum().sum() == 20
    # TODO: see why is the following true, instead of the previous:
    #assert (df_orig[columns]==df_overwritten[columns]).sum().sum() == 30

    parse_arguments_and_run ('--range-exp 0 9 --store --from-dict --runs 5 '
                             f'--min-iterations 1 -p {em.manager_path}'.split())

    df_new = em.get_experiment_data ()
    #assert (df_orig[columns]==df_new[columns]).all().all()
    x, y = df_orig[columns].astype('float'), df_new[columns].astype('float')
    #y[[f'{x}_finished' for x in range(5)]]=1.0
    pd.testing.assert_frame_equal(x,y)

    # *************************************************
    # The following simulates the case where
    # many experiments were not saved because
    # experiments_data.csv and experiments_data.pk
    # were overwritten by accident with an old file
    # *************************************************
    df = df_orig.copy()
    df.loc[1,columns] = None
    df = df.drop (index=range(3,9))
    df.to_csv (f'{path}/experiments_data.csv')
    df.to_pickle (f'{path}/experiments_data.pk')
    df_overwritten = em.get_experiment_data ()
    assert df_overwritten.shape==(3, 29)

    assert df_overwritten.isna().sum().sum()==10

    parse_arguments_and_run ('--range-exp 0 9 --store --from-dict --runs 5 '
                             f'--min-iterations 1 -p {em.manager_path}'.split())

    df_new = em.get_experiment_data ()
    #assert (df_orig[columns]==df_new[columns]).all().all()
    x, y = df_orig[columns].astype('float'), df_new[columns].astype('float')
    #y[[f'{x}_finished' for x in range(5)]]=1.0
    pd.testing.assert_frame_equal(x,y)

    # *************************************************
    # The following unrealistic scenario produces an error
    # For each row of an existing csv, we need to either have
    # the parameters of that row, or not have the row at all.
    # *************************************************
    df_orig = df.copy()
    df.iloc[1,:] = None
    df.iloc[3:,:] = None

    path = em.path_experiments

    df.to_csv (path/'experiments_data.csv')
    df.to_pickle (path/'experiments_data.pk')

    with pytest.raises (ValueError):
        parse_arguments_and_run (
            f'--range-exp 0 9 --store --from-dict --runs 5 -p {em.manager_path}'.split()
        )

    em.remove_previous_experiments (parent=True)