# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/modify_manager.ipynb (unless otherwise specified).

__all__ = ['modify_manager', 'parse_args', 'run_modify_manager', 'parse_arguments_and_run', 'main']

# Cell
import sys
import argparse
from importlib import reload
import warnings
warnings.filterwarnings('ignore')

import hpsearch.config.hp_defaults as dflt
from ..config.hpconfig import get_experiment_manager

# Cell
def modify_manager (path_experiments=None, parent_path=None, folder=None, metric=None, op=None,
                    manager_path=dflt.manager_path):
    em = get_experiment_manager (manager_path=manager_path)
    print ('current properties:')
    print (f'class={em.__class__.__name__}')
    print (f'path_experiments={em.path_experiments}')
    print (f'metric={em.key_score}')
    print (f'op={em.op}')

    modified = False
    if path_experiments is not None or folder is not None or parent_path is not None:
        em.set_path_experiments (path_experiments, parent_path=parent_path, folder=folder)
        modified = True
    if metric is not None:
        em.key_score = metric
        modified = True
    if op is not None:
        em.op = op
        modified = True

    if modified:
        em.register_and_store_subclassed_manager ()
        print ('new properties:')
        print (f'path_experiments={em.path_experiments}')
        print (f'metric={em.key_score}')
        print (f'op={em.op}')

# Cell
def parse_args (args):
    parser = argparse.ArgumentParser(description='change experiment manager')
    parser.add_argument('--path_experiments', type=str, default=None, help="new experiment manager to use")
    parser.add_argument('--parent_path', type=str, default=None, help="new experiment manager to use")
    parser.add_argument('--folder', type=str, default=None, help="new experiment manager to use")
    parser.add_argument('-m','--metric', type=str, default=None, help="new experiment manager to use")
    parser.add_argument('-o','--op', type=str, default=None, help="new experiment manager to use")
    parser.add_argument('--manager_path', type=str, default=None,
                        help=f"path where experiment managers are stored, default={dflt.manager_path}")
    pars = parser.parse_args(args)
    return pars

# Cell
def run_modify_manager (pars):
    pars.manager_path = dflt.manager_path if pars.manager_path is None else pars.manager_path
    modify_manager (**vars(pars))

# Cell
def parse_arguments_and_run (args):
    pars = parse_args (args)
    run_modify_manager (pars)

# Cell
def main():
    parse_arguments_and_run (sys.argv[1:])