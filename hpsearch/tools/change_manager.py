# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/change_manager.ipynb (unless otherwise specified).

__all__ = ['change_manager', 'main']

# Cell
import argparse
from importlib import reload
import warnings
import pdb
warnings.filterwarnings('ignore')

def change_manager (subclass=None):
    import hpsearch.config.manager_factory as mf
    reload(mf)

    manager_factory = mf.ManagerFactory(verbose=2)

    if subclass is None:
        manager_factory.list_subclasses()
    else:
        manager_factory.change_manager(subclass)
        manager_factory.import_written_manager ()
        change_manager (None)

def main():
    parser = argparse.ArgumentParser(description='change experiment manager')
    parser.add_argument('-m','--manager', type=str, default=None, help="new experiment manager to use")
    parser.add_argument('-l', '--list', action= "store_true", help="list experiment managers registered so far")
    pars = parser.parse_args()

    #pdb.set_trace()
    if pars.list:
        change_manager (None)
    else:
        assert pars.manager is not None
        change_manager (pars.manager)