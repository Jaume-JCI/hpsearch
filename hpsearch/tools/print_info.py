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
from ..config.hpconfig import get_path_experiments, get_path_results, get_default_operations
import hpsearch.utils.experiment_utils as ut
from .metric_visualization import include_best_and_last_experiment


def print_info (experiments=[-1], base=None, root_folder=None, display_all=False, include_best=False, op=None,
                metric=None, round_digits=2, compare=True, compact=0, run_number=0):

    default_operations = get_default_operations ()
    if root_folder is None:
        root_folder = default_operations.get('root', 'results')
    if metric is None:
        metric = default_operations.get('metric', 'accuracy')
    if op is None:
        op = default_operations.get('op', 'min')

    if base is not None:
        root_path = base
    else:
        root_path = get_path_experiments (folder = root_folder)

    df = pd.read_csv('%s/experiments_data.csv' %root_path,index_col=0)

    metric_column = f'{run_number}_{metric}'

    experiments = include_best_and_last_experiment ([metric], experiments=experiments, root_folder=root_folder,
                                                         run_number=run_number, op=op)


    df_scores = None
    print ('\n*****************************')
    for experiment in experiments:
        parameters = ut.get_parameters_columns(df.loc[[experiment]], True)
        print (f'\nparameters for {experiment}:')
        df2 = df.copy()
        df2[metric] = df.loc[experiment, metric_column]
        display (df2.loc[experiment, parameters + [metric]])
        print ('scores for all experiments:')
        df_scores = ut.get_experiment_scores(df.loc[[experiment]], suffix_results='_%s' %metric, remove_suffix=True)
        display(df_scores.round(round_digits))

        path_results = get_path_results (experiment, run_number, root_path=root_path)
        print (f'path to results: {path_results}')
        scores_names = ut.get_scores_names (df, experiment=experiment, run_number=run_number)
        print (f'scores names: {scores_names}')
        monitored_metrics = ut.get_monitored_training_metrics (experiment, run_number, path_results=path_results)
        print (f'monitored metrics: {monitored_metrics}')
        print ('\n*****************************')

# Cell
def parse_args(args):
    parser = argparse.ArgumentParser(description='print table')
    # Datasets
    parser.add_argument('--root', type=str, default=None, help='name of root folder')
    parser.add_argument('--base', type=str, default=None, help='full root path')
    parser.add_argument('-m', '--metric', type=str, default=None, help='metric score')
    parser.add_argument('-e', type=int, nargs='+', default=[-1, -2], help='experiment numbers')
    parser.add_argument('-a', type=bool, default=False)
    parser.add_argument ('-b', '--best', action= "store_true", help='include experiment with best performance (on given run id!!)')
    parser.add_argument ('-r', '--run', type=int, default=0, help='run id')
    parser.add_argument('-n', '--no_comp', action= "store_true", help='do not perform comparison')
    parser.add_argument('--compact', type=int, default=0, help='compact parameters to this number of characters')
    parser.add_argument('--op', default=None, type=str)
    parser.add_argument('--round', default=2, type=int, help='round scores to this number of digits')
    pars = parser.parse_args(args)

    return pars

def parse_arguments_and_run (args):

    pars = parse_args(args)

    print_info (experiments=pars.e, base = pars.base, root_folder=pars.root, display_all=pars.a,
                                         include_best=pars.best, op=pars.op, metric=pars.metric, round_digits=pars.round,
                                         compare=not pars.no_comp, compact=pars.compact, run_number=pars.run)

def main():
    parse_arguments_and_run (sys.argv[1:])