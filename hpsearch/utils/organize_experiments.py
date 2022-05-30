# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/utils/organize_experiments.ipynb (unless otherwise specified).

__all__ = ['remove_defaults_from_experiment_data', 'remove_experiments']

# Cell
import pandas as pd
import numpy as np
import shutil
import joblib

from . import experiment_utils
import hpsearch.config.hp_defaults as dflt
from .experiment_utils import read_df, write_df

# Cell
def remove_defaults_from_experiment_data (experiment_data):
    from ..config.hpconfig import get_default_parameters

    experiment_data_original = experiment_data.copy()
    parameters_names = experiment_utils.get_parameters_columns (experiment_data)
    parameters_data = experiment_data_original[parameters_names]
    changed_df = False
    for experiment_number in range(experiment_data.shape[0]):
        good_params = ~(experiment_data.loc[experiment_number, parameters_names].isna()).values
        parameters_names_i = np.array(parameters_names)[good_params]
        parameters_names_i = parameters_names_i.tolist()
        parameters = experiment_data.loc[experiment_number, parameters_names_i].to_dict()

        defaults = get_default_parameters(parameters)
        default_names = [default_name for default_name in defaults.keys() if default_name in parameters_names_i]

        for default_name in default_names:
            has_default = experiment_data.loc[experiment_number, default_name] == defaults[default_name]
            if has_default:
                print ('found experiment with default in experiment_number {}, parameter {}, values: {}'.format(experiment_number, default_name, experiment_data.loc[experiment_number, default_name]))
                changed_df = True
                experiment_data.loc[experiment_number, default_name] = None

    # check if there are repeated experiments
    if changed_df:
        if experiment_data[parameters_names].duplicated().any():
            print ('duplicated experiments: {}'.format(experiment_data[parameters_names].duplicated()))
            experiment_data = experiment_data_original
            changed_df = False

    return experiment_data, changed_df

# Cell
def remove_experiments (experiments=[], folder=None, manager_path=dflt.manager_path):
    from ..config.hpconfig import get_experiment_manager
    em = get_experiment_manager (manager_path=dflt.manager_path)
    if folder is not None: em.set_path_experiments (folder=folder)
    if type(experiments) is not list:
        experiments = [experiments]
    path_experiments = em.path_experiments

    # 1. remove experiments from csv file
    experiment_data = read_df (path_experiments)
    experiment_data = experiment_data.drop (index=experiments)

    # 2. remove experiments folders
    for experiment in experiments:
        path_experiment = em.get_path_experiment (experiment)
        shutil.rmtree(path_experiment)

    # 3. move experiment folders
    for new_number, original_number in enumerate(experiment_data.index):
        path_new_experiment = em.get_path_experiment (new_number)
        path_original_experiment = em.get_path_experiment (original_number)
        if path_new_experiment != path_original_experiment:
            shutil.move (path_original_experiment, path_new_experiment)

    # 4. move experiment indexes
    experiment_data.index = range(len(experiment_data.index))

    # 5. save experiment data
    write_df (experiment_data, path_experiments)