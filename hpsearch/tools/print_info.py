# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/print_info.ipynb (unless otherwise specified).

__all__ = ['print_info', 'parse_args', 'parse_arguments_and_run', 'main']

# Cell
import warnings
warnings.filterwarnings('ignore')

import pandas as pd
from IPython.display import display
import argparse

import sys
sys.path.append('.')
sys.path.append('src')

from ..config.hpconfig import get_path_experiments, get_path_results, get_experiment_manager
import hpsearch.utils.experiment_utils as ut
from .metric_visualization import include_best_and_last_experiment
import hpsearch.config.hp_defaults as dflt
from ..utils.experiment_utils import read_df, write_df

# Cell
def print_info (experiments=[-1], path_experiments=None, folder=None, display_all=False, include_best=False,
                op=None, metric=None, round_digits=2, compare=True, compact=0, run_number=0,
                manager_path=dflt.manager_path):

    em = get_experiment_manager (manager_path=manager_path)
    if path_experiments is not None or folder is not None:
        em.set_path_experiments (path_experiments=path_experiments, folder=folder)
    if metric is not None:
        em.key_score = metric
    if op is not None:
        em.op = op

    path_experiments = em.path_experiments

    df = read_df (path_experiments)

    metric_column = (dflt.scores_col, em.key_score, run_number)
    metric_column_str = (dflt.scores_col, em.key_score, str(run_number))

    experiments = include_best_and_last_experiment ([em.key_score], experiments=experiments,
                                                    run_number=run_number, op=em.op)


    df_scores = None
    print ('\n*****************************')
    for experiment in experiments:
        parameters = ut.get_parameters_columns(df.loc[[experiment]], True)
        print (f'\nparameters for {experiment}:')
        try:
            display (df.loc[experiment, parameters + [metric_column]])
        except KeyError:
            display (df.loc[experiment, parameters + [metric_column_str]])
            run_number = str(run_number)
        print ('scores for all experiments:')
        df_scores = ut.get_experiment_scores(df.loc[[experiment]], score_name=metric, remove_score_name=True)
        display(df_scores.round(round_digits))

        path_results = em.get_path_results (experiment, run_number)
        print (f'path to results: {path_results}')
        scores_names = ut.get_scores_names (df, experiment=experiment, run_number=run_number)
        print (f'scores names: {sorted(scores_names)}')
        monitored_metrics = ut.get_monitored_training_metrics (experiment, run_number, path_results=path_results)
        print (f'\nmonitored metrics: {sorted(monitored_metrics)}')
        print ('\n*****************************')

# Cell
def parse_args(args):
    parser = argparse.ArgumentParser(description='print table')
    # Datasets
    parser.add_argument('--folder', type=str, default=None, help='name of experiments folder')
    parser.add_argument('--path_experiments', type=str, default=None, help='full experiments path')
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

    print_info (experiments=pars.e, path_experiments = pars.path_experiments, folder=pars.folder,
                display_all=pars.a, include_best=pars.best, op=pars.op, metric=pars.metric,
                round_digits=pars.round, compare=not pars.no_comp, compact=pars.compact,
                run_number=pars.run, manager_path=pars.path)

def main():
    parse_arguments_and_run (sys.argv[1:])