# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/change_manager.ipynb (unless otherwise specified).

__all__ = ['change_manager', 'parse_args', 'run_change_manager', 'parse_arguments_and_run', 'main']

# Cell
import sys
import argparse
from importlib import reload
import warnings
warnings.filterwarnings('ignore')

import pdb

import hpsearch.config.hp_defaults as dflt

# Cell
def change_manager (subclass=None, manager_path=dflt.manager_path):
    # TODO: check if it is really necessary to import inside the function and reload
    import hpsearch.config.manager_factory as mf
    reload (mf)

    manager_factory = mf.ManagerFactory (manager_path=manager_path, verbose=2)

    if subclass is None:
        manager_factory.list_subclasses ()
    else:
        manager_factory.change_manager (subclass)
        change_manager (subclass=None, manager_path=manager_path)

# Cell
def parse_args (args):
    parser = argparse.ArgumentParser(description='change experiment manager')
    parser.add_argument('-m','--manager', type=str, default=None, help="new experiment manager to use")
    parser.add_argument('-l', '--list', action= "store_true", help="list experiment managers registered so far")
    parser.add_argument('-p','--path', type=str, default=None,
                        help=f"path where experiment managers are stored, default={dflt.manager_path}")
    pars = parser.parse_args(args)
    return pars

# Cell
def run_change_manager (pars):
    manager_path = dflt.manager_path if pars.path is None else pars.path
    #pdb.set_trace()
    if pars.list:
        change_manager (subclass=None, manager_path=manager_path)
    else:
        if pars.manager is None:
            print ('you did not indicate any manager to change to, listing the managers available')
        change_manager (subclass=pars.manager, manager_path=manager_path)

# Cell
def parse_arguments_and_run (args):
    pars = parse_args(args)
    run_change_manager (pars)

# Cell
def main():
    parse_arguments_and_run (sys.argv[1:])