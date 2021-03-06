# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/remove_experiments.ipynb (unless otherwise specified).

__all__ = ['remove', 'parse_args', 'parse_arguments_and_remove', 'main']

# Cell
import warnings
warnings.filterwarnings('ignore')

import argparse
import sys
sys.path.append('.')
sys.path.append('src')
import pandas as pd
import pickle

from ..utils.organize_experiments import remove_experiments
from ..config.hpconfig import get_experiment_manager
import hpsearch.config.hp_defaults as dflt

# Cell
def remove (experiments=[], folder=None, manager_path=dflt.manager_path):
    remove_experiments (experiments=experiments, folder=folder, manager_path=manager_path)

# Cell
def parse_args(args):
    parser = argparse.ArgumentParser(description='show metrics about experiments')
    # Datasets
    parser.add_argument('-e', nargs='+', default=[-1, -2], type=int,
                        help="experiments")
    parser.add_argument('--folder', type=str, default=None)
    parser.add_argument('-p', '--path', default=dflt.manager_path, type=str)

    pars = parser.parse_args(args)

    return pars

def parse_arguments_and_remove (args):

    pars = parse_args(args)

    remove (pars.e, folder=pars.folder, manager_path=pars.path)

def main():

    parse_arguments_and_remove (sys.argv[1:])