# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/print_table.ipynb (unless otherwise specified).

__all__ = ['print_table', 'parse_args', 'parse_arguments_and_run', 'main']

# Cell
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
from IPython.display import display
import argparse

import sys
sys.path.append('.')
sys.path.append('src')

from ..config.hpconfig import get_experiment_manager, get_path_experiments
import hpsearch.utils.experiment_utils as ut
from .metric_visualization import include_best_and_last_experiment
import hpsearch.config.hp_defaults as dflt
from ..utils.experiment_utils import read_df, write_df

# Cell
def print_table (experiments=[-1, -2], path_experiments=None, folder=None, display_all=False,
                 include_best=False, op=None, metric=None, round_digits=2, compare=True,
                 compact=0, run_number=0, manager_path=dflt.manager_path):

    em = get_experiment_manager (manager_path=manager_path)
    if path_experiments is not None or folder is not None:
        em.set_path_experiments (path_experiments=path_experiments, folder=folder)
    if metric is not None:
        em.key_score = metric
    if op is not None:
        em.op = op

    path_experiments = em.path_experiments

    df = read_df(path_experiments)

    if display_all:
        display (df[em.key_score])

    experiments = include_best_and_last_experiment ([metric], experiments=experiments,
                                                    run_number=run_number, op=em.op)
    metric_column = (dflt.scores_col, em.key_score, run_number)
    df_scores = None
    print ('\n*****************************')
    for e in experiments:
        parameters = ut.get_parameters_columns(df.loc[e:e+1], True)
        print ('\nparameters for %d:' %e)
        display (df.loc[e,parameters])
        print ('scores for all experiments:')
        df_scores = ut.get_experiment_scores(df.loc[[e]], score_name='%s' %em.key_score, remove_score_name=True)
        display(df_scores.round(round_digits))
        print ('score:')
        display (df.loc[e, metric_column])

    df2 = None
    if len(experiments) > 0 and compare:
        parameters = ut.get_parameters_columns(df.loc[experiments], True)
        print ('\ncomparison')
        display (df.loc[experiments, parameters])
        print ('score')
        display (df.loc[experiments, metric_column])

        print ('with unique parameters:')
        _, df2 = ut.get_parameters_unique(df.loc[experiments])
        if compact > 0:
            prev_cols = df2.columns.copy()
            df2, dict_rename = ut.compact_parameters (df2, compact)
            for k, kor in zip(df2.columns, prev_cols):
                print ('{} => {}'.format(k, kor))
        display(df2)

    return df, df2, df_scores

# Cell
def parse_args(args):
    parser = argparse.ArgumentParser(description='print table')
    # Datasets
    parser.add_argument('--folder', type=str, default=None, help='name of experiments folder')
    parser.add_argument('--path_experiments', type=str, default=None, help='full path')
    parser.add_argument('-m', '--metric', type=str, default=None, help='metric score')
    parser.add_argument('-e', type=int, nargs='+', default=[-1, -2], help='experiment numbers')
    parser.add_argument('-a', type=bool, default=False)
    parser.add_argument ('-b', '--best', action= "store_true", help='include experiment with best performance (on given run id!!)')
    parser.add_argument ('-r', '--run', type=int, default=0, help='run id')
    parser.add_argument('-n', '--no_comp', action= "store_true", help='do not perform comparison')
    parser.add_argument('--compact', type=int, default=0, help='compact parameters to this number of characters')
    parser.add_argument('--op', default=None, type=str)
    parser.add_argument('--round', default=2, type=int, help='round scores to this number of digits')
    parser.add_argument('-p', '--path', default=dflt.manager_path, type=str)
    pars = parser.parse_args(args)

    return pars

def parse_arguments_and_run (args):

    pars = parse_args(args)

    df, df2, df_scores=print_table (experiments=pars.e, path_experiments = pars.path_experiments,
                                    folder=pars.folder,
                                    display_all=pars.a, include_best=pars.best, op=pars.op,
                                    metric=pars.metric, round_digits=pars.round,
                                    compare=not pars.no_comp, compact=pars.compact,
                                    run_number=pars.run, manager_path=pars.path)

def main():
    parse_arguments_and_run (sys.argv[1:])