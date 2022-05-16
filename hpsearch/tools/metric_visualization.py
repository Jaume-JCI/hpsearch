# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/metric_visualization.ipynb (unless otherwise specified).

__all__ = ['include_best_and_last_experiment', 'metric_visualization', 'parse_args', 'parse_arguments_and_visualize',
           'main']

# Cell
import warnings
warnings.filterwarnings('ignore')

import argparse
import sys
sys.path.append('.')
sys.path.append('src')
import pandas as pd
import pickle

import hpsearch.visualization.experiment_visualization as ev
from ..config.hpconfig import get_experiment_manager, get_path_experiments
import hpsearch.config.hp_defaults as dflt

# Cell
def include_best_and_last_experiment (metrics, experiments=[-1, -2], run_number=0,
                                      op='max', manager_path=dflt.manager_path,):
    path_experiments = get_path_experiments (manager_path=manager_path)
    for i in range(len(experiments)):
        if experiments[i] == -1:
            experiment_number = pickle.load(open(path_experiments/'current_experiment_number.pkl','rb'))
            experiments[i] = experiment_number

        if experiments[i] == -2:
            first_metric = metrics[0]
            if len(metrics)>1:
                print (f'we use the first metric {first_metric} in given list {metrics} for obtaining the best experiment')
            df = pd.read_csv(path_experiments/'experiments_data.csv',index_col=0)
            score_column = f'{run_number}_{first_metric}'
            if score_column in df.columns:
                if op=='max':
                    experiments[i] = df[score_column].idxmax()
                else:
                    experiments[i] = df[score_column].idxmin()
            else:
                del experiments[i]

    return experiments

# Cell
def metric_visualization (experiments=[-1,-2], run_number=0, folder=None, metric=None, op = None,
                          parameters=None, name_file='model_history.pk', visualization_options = {},
                          backend='plotly', manager_path=dflt.manager_path, **kwargs):

    if folder is not None or metric is not None or op is not None:
        em = get_experiment_manager (manager_path=manager_path)
        if folder is not None: em.set_path_experiments (folder=folder)
        if metric is not None: em.key_score = metric
        if op is not None: em.op = op
    folder = em.folder
    metric = em.key_score
    op = em.op

    # metrics
    if type(metric) is str:
        metrics = [metric]
    else:
        metrics = metric

    experiments = include_best_and_last_experiment (metrics, experiments=experiments,
                                                    run_number=run_number, op=op,
                                                    manager_path=manager_path)

    visualization_options = visualization_options.copy()
    visualization_options.update(kwargs)
    if 'visualization' in visualization_options.keys():
        visualization = visualization_options.pop('visualization')
    else:
        visualization = 'history'

    ev.visualize_experiments(visualization=visualization,
                             experiments=experiments, run_number=run_number,
                             metrics=metrics, parameters=parameters, name_file=name_file,
                             **visualization_options, backend=backend)

# Cell
def parse_args(args):
    parser = argparse.ArgumentParser(description='show metrics about experiments')
    # Datasets
    parser.add_argument('-e', nargs='+', default=[-1, -2], type=int,
                        help="experiments")
    parser.add_argument('-m', '--metric', nargs='+', type=str, default=None, help="metrics")
    parser.add_argument('--folder', type=str, default=None)
    parser.add_argument('-l','--labels',nargs='+', default=None, type=str)
    parser.add_argument('--run', default=0, type=int)
    parser.add_argument('--op', default=None, type=str)
    parser.add_argument('-b', '--backend', default='visdom', type=str)
    parser.add_argument('-f', '--file', default='model_history.pk', type=str)
    parser.add_argument('-v', '--visualization', default='{}', type=str)
    parser.add_argument('-p', '--path', default=dflt.manager_path, type=str)

    pars = parser.parse_args(args)

    pars.visualization = eval(pars.visualization)

    return pars

def parse_arguments_and_visualize (args):

    pars = parse_args(args)

    metric_visualization (pars.e, run_number=pars.run, folder=pars.folder, metric=pars.metric,
                          parameters=pars.labels, name_file=pars.file, backend=pars.backend,
                          visualization_options=pars.visualization, manager_path=pars.path)

def main():

    parse_arguments_and_visualize (sys.argv[1:])