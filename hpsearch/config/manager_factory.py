# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/config/manager_factory.ipynb (unless otherwise specified).

__all__ = ['ManagerFactory', 'experiment_manager']

# Cell
import inspect
import shutil
import hpsearch
import os
import logging
import pickle
import pdb

experiment_manager = None

class ManagerFactory (object):
    def __init__ (self, allow_base_class=True, verbose=0):
        self.allow_base_class = allow_base_class
        self.logger = logging.getLogger("experiment_manager")
        if verbose > 1:
            self.logger.setLevel('DEBUG')
        self.obtain_paths()
        #pdb.set_trace()

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
        self.class_two_base_file = f'{self.destination_path_folder}/class_two_base.pk'
        self.current_path = os.path.abspath(os.path.curdir)
        print (f'current path: {self.current_path}')

    def write_manager (self, experiment_manager):
        name_subclass = experiment_manager.__class__.__name__
        try:
            source_path = inspect.getfile(experiment_manager.__class__)
            self.obtain_paths()
            self.write_manager_subclass (name_subclass, source_path, self.current_path)

            self.load_class_two_module ()
            self.class_two_module.update({name_subclass: source_path})
            self.class_two_base.update({name_subclass: self.current_path})
            pickle.dump (self.class_two_module, open(self.class_two_module_file, 'wb'))
            pickle.dump (self.class_two_base, open(self.class_two_base_file, 'wb'))
        except Exception as e:
            print (f'write_manager failed with exception {e}')

    def write_manager_subclass (self, name_subclass, source_path, base_path=None):
        if base_path is None:
            base_path = self.current_path
        os.makedirs(self.destination_path_folder, exist_ok=True)
        shutil.copy (source_path, self.destination_path_module)

        f = open (self.destination_path_import, 'wt')
        f.write ('import sys\n')
        f.write (f'sys.path.append("{base_path}")\n')
        f.write (f'from hpsearch.app_config.subclassed_manager import {name_subclass} as Manager')
        f.close()

    def load_class_two_module (self):
        if os.path.exists (self.class_two_module_file):
            self.class_two_module = pickle.load (open(self.class_two_module_file,'rb'))
        else:
            self.class_two_module = {}

        if os.path.exists (self.class_two_base_file):
            self.class_two_base = pickle.load (open(self.class_two_base_file,'rb'))
        else:
            self.class_two_base = {}

    def change_manager (self, name_subclass):
        self.previous_manager = self.get_experiment_manager ()
        self.obtain_paths()
        self.load_class_two_module ()
        if name_subclass not in self.class_two_module:
            raise ValueError (f'{name_subclass} not in dictionary class_two_module={self.class_two_module}')
        if name_subclass in self.class_two_base:
            base_path = self.class_two_base[name_subclass]
        else:
            base_path = self.current_path
        self.write_manager_subclass (name_subclass, self.class_two_module[name_subclass], base_path)
        self.reset_manager()
        self.import_written_manager()

    def switch_back (self):
        self.register_manager (self.previous_manager)
        self.write_manager (self.previous_manager)

    def print_current_manager (self):
        em = self.get_experiment_manager ()
        print (f'experiment manager registered: {em.__class__.__name__}')

    def list_subclasses (self):
        self.load_class_two_module ()
        print (f'subclasses: {self.class_two_module.keys()}')
        self.print_current_manager()

    def import_written_manager (self):
        global experiment_manager
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
        experiment_manager = em


    def get_experiment_manager (self):

        if experiment_manager is not None:
            em = experiment_manager
            self.logger.debug ('returning registered experiment manager')
        else:
            self.logger.debug ('experiment manager not registered yet, importing experiment manager')
            self.import_written_manager()
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
            self.logger.debug ('deleting')
            os.remove(self.class_two_module_file)

        self.set_base_manager ()