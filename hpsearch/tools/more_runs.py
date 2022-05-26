# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/more_runs.ipynb (unless otherwise specified).

__all__ = ['parse_args', 'parse_arguments_and_run', 'main']

# Cell
import sys
import argparse
import warnings

from ..config.hpconfig import get_experiment_manager
import hpsearch.config.hp_defaults as dflt

# Cell
def parse_args (args):
    parser = argparse.ArgumentParser(description='run experiment')
    parser.add_argument('-d', '--debug', action= "store_true")
    parser.add_argument('-e', '--experiments', type=int, nargs='+', default=None,  help="experiment numbers")
    parser.add_argument('--runs', type=int, default=None,  help="number of runs")
    parser.add_argument('--folder', type=str, default=None, help='name of experiments folder')
    parser.add_argument('-p', '--path', default=dflt.manager_path, type=str)
    pars = parser.parse_args(args)

    return pars

def parse_arguments_and_run (args):

    print (f'\n{"*"*100}')
    print (f'{"*"*100}')
    print (f'{"*"*100}')
    print ('WARNING: should use rerun instead')
    print (f'{"*"*100}')
    print (f'{"*"*100}\n')
    warnings.warn ('WARNING: should use rerun instead')

    pars = parse_args(args)

    em_args = dict(use_process=not pars.debug)

    em = get_experiment_manager (manager_path=pars.path)

    em.rerun_experiment (experiments= pars.experiments, nruns = pars.runs,
                         **em_args)

def main():
    parse_arguments_and_run (sys.argv[1:])