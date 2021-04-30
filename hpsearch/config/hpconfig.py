# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/config/hpconfig.ipynb (unless otherwise specified).

__all__ = ['get_default_parameters', 'get_default_operations', 'get_path_experiments', 'get_path_alternative',
           'get_path_data', 'get_path_experiment', 'get_path_results', 'manager_factory', 'experiment_manager']

# Cell
import os
import hpsearch
from .manager_factory import ManagerFactory
from . import manager_factory as mf

manager_factory = ManagerFactory()
experiment_manager = manager_factory.get_experiment_manager()
mf.experiment_manager = experiment_manager

def get_default_parameters (parameters):
    return mf.experiment_manager.get_default_parameters (parameters)

def get_default_operations ():
    return mf.experiment_manager.get_default_operations ()

def get_path_experiments (path_experiments = None, folder = None):
    return mf.experiment_manager.get_path_experiments (path_experiments, folder)

def get_path_alternative (path_results):
    return mf.experiment_manager.get_path_alternative (path_results)

def get_path_data (run_number, root_path=None, parameters={}):
    return mf.experiment_manager.get_path_data (run_number, root_path, parameters)

def get_path_experiment (experiment_id, root_path=None, root_folder=None):
    return mf.experiment_manager.get_path_experiment (experiment_id, root_path, root_folder)

def get_path_results (experiment_id, run_number, root_path=None, root_folder=None):
    return mf.experiment_manager.get_path_results (experiment_id, run_number, root_path, root_folder)