# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/config/manager_factory.ipynb (unless otherwise specified).

__all__ = ['experiment_manager', 'get_pickable_fields', 'ManagerFactory']

# Cell
import inspect
import shutil
import hpsearch
import os
import logging
import cloudpickle
import joblib
import pickle
import dill
from pathlib import Path
import glob

from block_types.utils.utils import set_logger

import hpsearch.config.hp_defaults as dflt

experiment_manager = None

# Cell
def get_pickable_fields (obj):
    dict_fields = vars(obj)
    return {k:dict_fields[k] for k in dict_fields if dill.pickles (dict_fields[k])}

# Cell
class ManagerFactory (object):
    def __init__ (self, allow_base_class=True, manager_path=dflt.manager_path,
                  import_manager=False, verbose=dflt.verbose, logger=None,
                  name_logger=dflt.name_logger):

        self.allow_base_class = allow_base_class
        self.obtain_paths()
        self.method = 1
        self.manager_path = Path(manager_path).resolve()
        self.import_manager = import_manager

        self.verbose = verbose
        self.logger = logger
        self.name_logger = name_logger
        if self.logger is None:
            self.logger = set_logger (self.name_logger, path_results=self.manager_path,
                                      verbose=self.verbose)

    def register_manager (self, experiment_manager_to_register):
        global experiment_manager
        experiment_manager = experiment_manager_to_register

    def obtain_paths (self):
        destination_path_folder = os.path.dirname (hpsearch.__file__)
        destination_path_folder = f'{destination_path_folder}/app_config'
        destination_path_module = f'{destination_path_folder}/subclassed_manager.py'
        self.destination_path_folder = destination_path_folder
        self.destination_path_module = destination_path_module
        self.destination_path_import = f'{destination_path_folder}/subclassed_manager_import.py'
        self.class_two_module_file = f'{self.destination_path_folder}/class_two_module.pk'
        self.class_two_import_file = f'{self.destination_path_folder}/class_two_import.pk'
        self.class_two_base_file = f'{self.destination_path_folder}/class_two_base.pk'
        self.current_path = os.path.abspath(os.path.curdir)
        #print (f'current path: {self.current_path}')

    def determine_import_string (self, source_path, base_path, experiment_manager):
        if self.method==1:
            import_module_string = experiment_manager.__class__.__module__
        elif self.method==2:
            if source_path.startswith(base_path + '/'):
                split_list = source_path.split(base_path + '/')
                import_module_string = split_list[1]
                import_module_string = import_module_string.replace('/','.')
                import_module_string = import_module_string.replace('.py', '')
            else:
                self.logger.warning (f'current path {base_path} not found in source path {source_path}')
                import_module_string = 'hpsearch.app_config.subclassed_manager'
        self.import_module_string = import_module_string
        return import_module_string

    def write_manager (self, em):
        name_subclass = em.__class__.__name__
        try:
            source_path = inspect.getfile(em.__class__)
            self.obtain_paths()
            import_module_string = self.determine_import_string (source_path, self.current_path, em)
            self.write_manager_subclass (name_subclass, source_path, self.current_path, import_module_string)

            self.load_class_two_module ()
            self.class_two_module.update({name_subclass: source_path})
            self.class_two_import.update({name_subclass: import_module_string})
            self.class_two_base.update({name_subclass: self.current_path})
            pickle.dump (self.class_two_module, open(self.class_two_module_file, 'wb'))
            pickle.dump (self.class_two_import, open(self.class_two_import_file, 'wb'))
            pickle.dump (self.class_two_base, open(self.class_two_base_file, 'wb'))

            # store em fields in pickle and cloud-pickle files
            self.pickle_object (em=em)
        except Exception as e:
            self.logger.warning (f'write_manager failed with exception {e}')
            raise (e)

    def em_pickable_fields (self, em=None):
        em = self.get_experiment_manager () if em is None else em
        pickable_fields = get_pickable_fields (em)
        pickable_fields = {k:pickable_fields[k] for k in pickable_fields
                           if k not in em.non_pickable_fields}
        return pickable_fields

    def write_manager_subclass (self, name_subclass, source_path, base_path=None,
                                import_module_string=None):
        if base_path is None:
            base_path = self.current_path
        os.makedirs(self.destination_path_folder, exist_ok=True)

        # 1 copy subclass module's source file
        shutil.copy (source_path, self.destination_path_module)

        # 2 copy import statement
        f = open (self.destination_path_import, 'wt')
        f.write ('import sys\n')
        f.write (f'sys.path.append("{base_path}")\n')
        f.write (f'from {import_module_string} import {name_subclass} as Manager')
        f.close()

    def write_pickle_of_subclass (self, name_manager, manager_path=None, extension='.cpk'):
        manager_path = manager_path if manager_path is not None else self.manager_path
        shutil.copy (manager_path / f'{name_manager}{extension}', manager_path / f'last{extension}')

    def pickle_object (self, em=None, manager_path=None):
        manager_path = manager_path if manager_path is not None else self.manager_path

        self.manager_path.mkdir (parents=True, exist_ok=True)
        em = em if em is not None else self.get_experiment_manager ()
        dict_fields = self.em_pickable_fields (em=em)
        joblib.dump (dict_fields, manager_path / f'{em.registered_name}.pk')
        joblib.dump (dict_fields, manager_path / 'last.pk')

        # 4 store pickable and non-pickable fields
        cloudpickle.dump (em, open(manager_path / f'{em.registered_name}.cpk', 'wb'))
        cloudpickle.dump (em, open(manager_path / 'last.cpk', 'wb'))

    def load_class_two_module (self):
        if os.path.exists (self.class_two_module_file):
            self.class_two_module = pickle.load (open(self.class_two_module_file,'rb'))
        else:
            self.class_two_module = {}

        if os.path.exists (self.class_two_import_file):
            self.class_two_import = pickle.load (open(self.class_two_import_file,'rb'))
        else:
            self.class_two_import = {}
            self.logger.warning ('class2import not found, switching to original method')
            self.method = 2

        if os.path.exists (self.class_two_base_file):
            self.class_two_base = pickle.load (open(self.class_two_base_file,'rb'))
        else:
            self.class_two_base = {}

    def change_manager (self, name_manager):
        self.previous_manager = self.get_experiment_manager ()
        if self.import_manager:
            self.write_manager_to_import (name_manager)
            self.write_pickle_of_subclass (name_manager, extension='.pk')
        else:
            self.write_pickle_of_subclass (name_manager, extension='.cpk')
        self.reset_manager()
        self.import_or_load_manager()

    def write_manager_to_import (self, name_manager):
        name_subclass = name_manager.split ('-')[0]
        self.obtain_paths()
        self.load_class_two_module ()
        if name_subclass not in self.class_two_module:
            raise ValueError (f'{name_subclass} not in dictionary class_two_module={self.class_two_module}')
        if name_subclass in self.class_two_base:
            base_path = self.class_two_base[name_subclass]
        else:
            base_path = self.current_path
        self.write_manager_subclass (name_subclass, self.class_two_module[name_subclass], base_path,
                                    self.class_two_import[name_subclass])

    def switch_back (self):
        self.register_manager (self.previous_manager)
        self.write_manager (self.previous_manager)

    def print_current_manager (self):
        em = self.get_experiment_manager ()
        print (f'experiment manager registered: {em.__class__.__name__}')
        print (f'registered name: {em.registered_name}')

    def list_subclasses (self):
        if self.import_manager:
            self.list_pickled_managers (extension='.pk')
        else:
            self.list_pickled_managers (extension='.cpk')
        self.print_current_manager()

    def list_subclass_modules (self):
        self.load_class_two_module ()
        print (f'subclasses: {self.class_two_module.keys()}')

    def list_pickled_managers (self, extension='.cpk'):
        managers = glob.glob (f'{self.manager_path}/*{extension}')
        managers = [Path(x).name.split(extension)[0] for x in managers]
        managers = [x for x in managers if x != 'last']
        print (f'managers: {managers}')

    def load_pickle_and_set_em_fields (self, em, manager_path=None):
        manager_path = manager_path if manager_path is not None else self.manager_path
        dict_fields = joblib.load (manager_path / 'last.pk')
        self.logger.debug (f'loading pickled em fields from {manager_path}')
        for k in dict_fields:
            setattr (em, k, dict_fields[k])

    def load_manager (self, manager_path=None):
        manager_path = manager_path if manager_path is not None else self.manager_path
        self.logger.debug (f'loading manager from {manager_path}')
        em = cloudpickle.load (open(manager_path / f'last.cpk', 'rb'))
        return em

    def import_or_load_manager (self):
        if self.import_manager:
            em = self.import_written_manager ()
        else:
            em = self.load_manager ()
        global experiment_manager
        experiment_manager = em

    def import_written_manager (self):
        try:
            import hpsearch.app_config.subclassed_manager_import as subclass_module
            from importlib import reload
            reload (subclass_module)

            from ..app_config.subclassed_manager_import import Manager
            em = Manager()
            self.logger.debug ('returning subclassed manager')
        except ImportError:
            if not self.allow_base_class:
                raise ImportError (f'it was not possible to import subclassed manager, and allow_base_class=False')
            self.logger.debug ('importing base class ExperimentManager')
            from ..experiment_manager import ExperimentManager
            em = ExperimentManager()
        self.load_pickle_and_set_em_fields (em)
        return em

    def get_experiment_manager (self):
        if experiment_manager is not None:
            em = experiment_manager
            self.logger.debug ('returning registered experiment manager')
        else:
            self.logger.debug ('experiment manager not registered yet, importing experiment manager')
            self.import_or_load_manager()
            em = self.get_experiment_manager ()

        self.logger.debug (f'returning experiment manager {em}')
        return em

    def reset_manager (self):
        self.register_manager (None)

    def set_base_manager (self):
        from ..experiment_manager import ExperimentManager
        em = ExperimentManager()
        self.register_manager (em)

    def delete_and_reset_all (self):
        self.obtain_paths()
        self.logger.debug (self.destination_path_module)
        if os.path.exists(self.destination_path_module):
            self.logger.debug ('deleting')
            os.remove(self.destination_path_module)
        if os.path.exists(self.destination_path_import):
            self.logger.debug ('deleting')
            os.remove(self.destination_path_import)

        self.load_class_two_module ()
        if os.path.exists(self.class_two_module_file):
            self.logger.debug (f'deleting {self.class_two_module_file}')
            os.remove(self.class_two_module_file)

        if os.path.exists(self.class_two_import_file):
            self.logger.debug (f'deleting {self.class_two_import_file}')
            os.remove(self.class_two_import_file)

        if os.path.exists(self.class_two_base_file):
            self.logger.debug (f'deleting {self.class_two_base_file}')
            os.remove(self.class_two_base_file)

        if self.manager_path.exists ():
            self.logger.debug (f'deleting {self.manager_path}')
            shutil.rmtree (self.manager_path)

        self.set_base_manager ()