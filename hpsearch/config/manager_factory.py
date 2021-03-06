# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/config/manager_factory.ipynb (unless otherwise specified).

__all__ = ['experiment_manager', 'get_pickable_fields', 'ManagerFactory']

# Cell
import inspect
import shutil
import os
import logging
import joblib
import pickle
import dill
from pathlib import Path
import glob
import cloudpickle
import importlib.util
import pandas as pd
import numpy as np

from dsblocks.utils.utils import set_logger

import hpsearch
import hpsearch.config.hp_defaults as dflt

experiment_manager = None

# Cell
def get_pickable_fields (obj):
    dict_fields = vars(obj)
    # dill seems to have issues with DataFrame and possibly np.array
    dict_fields = {k:dict_fields[k] for k in dict_fields
                   if not isinstance(dict_fields[k], pd.DataFrame) and not isinstance(dict_fields[k], np.ndarray)}
    try:
        result = {k:dict_fields[k] for k in dict_fields if dill.pickles (dict_fields[k])}
    except:
        result = dict_fields
    return result

# Cell
class ManagerFactory (object):
    def __init__ (self, allow_base_class=True, manager_path=dflt.manager_path,
                  import_manager=False, verbose=dflt.verbose, logger=None,
                  name_logger_factory=dflt.name_logger_factory):

        self.allow_base_class = allow_base_class
        self.manager_path = Path(manager_path).resolve()
        self.import_manager = import_manager

        self.verbose = verbose
        self.logger = logger
        self.name_logger_factory = name_logger_factory
        if self.logger is None:
            self.logger = set_logger (self.name_logger_factory, path_results=self.manager_path,
                                      verbose=self.verbose)

    # **************************************************
    # get manager, load it / import it
    # **************************************************
    def get_experiment_manager (self):
        if experiment_manager is not None:
            em = experiment_manager
            self.logger.debug ('returning registered experiment manager')
        else:
            self.logger.debug ('experiment manager not registered yet, importing experiment manager')
            try:
                self.import_or_load_manager()
            except FileNotFoundError:
                self.logger.debug ('No experiment manager to import was found, setting base manager.')
                self.set_base_manager ()
            em = self.get_experiment_manager ()

        self.logger.debug (f'returning experiment manager {em}')
        return em

    def import_or_load_manager (self):
        if self.import_manager:
            em = self.import_written_manager ()
        else:
            em = self.load_manager ()
        global experiment_manager
        experiment_manager = em

    def import_written_manager (self):
        info_path =self.manager_path / 'info'
        self.info = joblib.load (info_path / 'last.pk')

        spec = importlib.util.spec_from_file_location(self.info['import_module_string'],
                                                      self.info['source_path'])
        manager_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(manager_module)
        Manager = getattr (manager_module, self.info['class_name'])
        em = Manager ()

        self.load_pickle_and_set_em_fields (em)
        return em

    def load_manager (self):
        whole_object_path = self.manager_path / 'whole'
        self.logger.debug (f'loading manager from {whole_object_path}')
        with open(whole_object_path / 'last.pk', 'rb') as f: em = cloudpickle.load (f)
        return em

    def load_pickle_and_set_em_fields (self, em, manager_path=None):
        manager_path = manager_path if manager_path is not None else self.manager_path
        fields_path = manager_path / 'fields'
        dict_fields = joblib.load (fields_path / 'last.pk')
        self.logger.debug (f'loading pickled em fields from {fields_path}')
        for k in dict_fields:
            setattr (em, k, dict_fields[k])

    # ***********************************************************
    # register manager, persist manager
    # ***********************************************************
    def register_manager (self, experiment_manager_to_register):
        global experiment_manager
        experiment_manager = experiment_manager_to_register

    def write_manager (self, em):
        name_subclass = em.__class__.__name__
        registered_name = em.registered_name
        import_module_string = em.__class__.__module__
        try:
            source_path = inspect.getfile(em.__class__)
        except TypeError:
            source_path = ''
        self.info = {'source_path': source_path,
                     'import_module_string': import_module_string,
                     'class_name': name_subclass}
        # store em fields in pickle and cloud-pickle files
        self.pickle_object (em=em)

    def pickle_object (self, em=None, manager_path=None, store_info=True):
        manager_path = manager_path if manager_path is not None else self.manager_path
        manager_path = Path(manager_path).resolve ()

        whole_object_path = manager_path / 'whole'
        fields_path = manager_path / 'fields'
        info_path = manager_path / 'info'
        whole_object_path.mkdir (parents=True, exist_ok=True)
        fields_path.mkdir (parents=True, exist_ok=True)
        info_path.mkdir (parents=True, exist_ok=True)

        em = em if em is not None else self.get_experiment_manager ()

        # fields pickle file
        dict_fields = self.em_pickable_fields (em=em)
        joblib.dump (dict_fields, fields_path / f'{em.registered_name}.pk')
        joblib.dump (dict_fields, fields_path / 'last.pk')

        # store pickable and non-pickable fields
        fields = {k: getattr (em, k) for k in em.avoid_saving_fields}
        for k in em.avoid_saving_fields: setattr (em, k, None)
        with open(whole_object_path / f'{em.registered_name}.pk', 'wb') as f:  cloudpickle.dump (em, f)
        with open(whole_object_path / 'last.pk', 'wb') as f: cloudpickle.dump (em, f)
        for k in em.avoid_saving_fields: setattr (em, k, fields[k])

        # info file
        if store_info:
            joblib.dump (self.info, info_path / f'{em.registered_name}.pk')
            joblib.dump (self.info, info_path / 'last.pk')

    def em_pickable_fields (self, em=None):
        em = self.get_experiment_manager () if em is None else em
        pickable_fields = get_pickable_fields (em)
        pickable_fields = {k:pickable_fields[k] for k in pickable_fields
                           if k not in em.non_pickable_fields}
        return pickable_fields

    # **********************************************************
    # change manager
    # **********************************************************
    def change_manager (self, name_manager):
        self.previous_manager = self.get_experiment_manager ()
        self.overwrite_last_manager (name_manager)

        self.reset_manager()
        self.import_or_load_manager()

    def overwrite_last_manager (self, name_manager):
        whole_object_path = self.manager_path / 'whole'
        fields_path = self.manager_path / 'fields'
        info_path = self.manager_path / 'info'

        shutil.copy (whole_object_path / f'{name_manager}.pk', whole_object_path / 'last.pk')
        shutil.copy (fields_path / f'{name_manager}.pk', fields_path / 'last.pk')
        shutil.copy (info_path / f'{name_manager}.pk', info_path / 'last.pk')

    def switch_back (self):
        self.register_manager (self.previous_manager)
        self.write_manager (self.previous_manager)

    # **********************************************************
    #  list stored managers and print current one
    # **********************************************************
    def list_subclasses (self):
        self.list_pickled_managers ()
        self.print_current_manager ()

    def list_pickled_managers (self):
        managers = glob.glob (f'{self.manager_path}/fields/*.pk')
        managers = [Path(x).name.split('.pk')[0] for x in managers]
        managers = sorted([x for x in managers if x != 'last'])
        manager_classes = [manager.split('-')[0] for manager in managers]
        folders = [manager.split('-')[1] for manager in managers]
        prev_class = ''
        for i in range(len(managers)):
            if manager_classes[i] != prev_class:
                print (f'{manager_classes[i]}:')
            print (f'    {folders[i]:50}{managers[i]}')
            prev_class = manager_classes[i]

        #print (f'managers: {sorted(managers)}')

    def print_current_manager (self):
        em = self.get_experiment_manager ()
        print (f'experiment manager registered: {em.__class__.__name__}')
        print (f'registered name: {em.registered_name}')

    # **********************************************************
    #  reset and delete managers
    # **********************************************************
    def reset_manager (self):
        self.register_manager (None)

    def set_base_manager (self):
        from ..experiment_manager import ExperimentManager
        em = ExperimentManager()
        self.register_manager (em)

    def delete_and_reset_all (self):
        if self.manager_path.exists ():
            self.logger.debug (f'deleting {self.manager_path}')
            shutil.rmtree (str(self.manager_path))

        self.set_base_manager ()