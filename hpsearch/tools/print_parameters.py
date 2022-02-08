# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/print_parameters.ipynb (unless otherwise specified).

__all__ = ['print_parameters', 'parse_args', 'parse_arguments_and_print', 'main']

# Cell
import warnings
warnings.filterwarnings('ignore')

import argparse
import sys
sys.path.append('.')
from IPython.display import display

import hpsearch.config.hp_defaults as dflt

# Cell
def print_parameters (experiment, root=None, manager_path=dflt.manager_path):

    from ..config.hpconfig import get_default_operations, get_path_experiment
    if root is None:

        default_operations = get_default_operations (manager_path=manager_path)
        root = default_operations.get('root', 'results')

    path_experiment = get_path_experiment (experiment, root_folder=root, manager_path=manager_path)
    parameters_text_file = open(f'{path_experiment}/parameters.txt', 'rt')
    print (parameters_text_file.read())
    parameters_text_file.close()

# Cell
def parse_args(args):
    parser = argparse.ArgumentParser(description='display dictionary of parameters used by this experiment')
    parser.add_argument('-e', '--experiment', type=int, required=True,  help="experiment number")
    parser.add_argument('-r','--root', type=str, default=None)
    parser.add_argument('-p', '--path', default=dflt.manager_path, type=str)
    pars = parser.parse_args(args)

    return pars

def parse_arguments_and_print (args):

    pars = parse_args(args)

    print_parameters (pars.experiment, pars.root, manager_path=pars.path)

def main():
    parse_arguments_and_print (sys.argv[1:])