# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/tools/tst.change_manager.ipynb (unless otherwise specified).

__all__ = ['test_change_manager_list', 'test_change_manager_parse_and_run']

# Cell
import pytest
import pandas as pd
import os
import joblib
from pathlib import Path
from IPython.display import display
from block_types.utils.nbdev_utils import md
from block_types.utils.utils import remove_previous_results
import cloudpickle

from hpsearch.tools.change_manager import *
from hpsearch.config.manager_factory import ManagerFactory
from hpsearch.examples.example_experiment_manager import ExampleExperimentManager
from hpsearch.examples.dummy_experiment_manager import DummyExperimentManager

# Comes from change_manager.ipynb, cell
def test_change_manager_list ():
    # the following lists stored experiment managers, keeping the current experiment manager
    path_results = 'test_change_manager_list'
    manager_path = f'{path_results}/manager'
    path_experiments = f'{path_results}/experiments'

    manager_factory = ManagerFactory (manager_path=manager_path)
    manager_factory.delete_and_reset_all ()

    assert os.path.exists (path_results)
    assert os.listdir (path_results)==[]

    print ('\ninitial list')
    em_before = manager_factory.get_experiment_manager ()
    change_manager (None, manager_path=manager_path)
    em_after = manager_factory.get_experiment_manager ()
    assert em_before.__class__.__name__ == em_after.__class__.__name__

    assert os.listdir (manager_path)==['logs.txt']

    # **************************************************************
    # same but using ExampleExperimentManager as registered manager
    # **************************************************************
    em = ExampleExperimentManager(path_experiments=path_experiments)
    manager_factory.register_manager (em)
    manager_factory.write_manager (em)

    assert sorted(os.listdir (manager_path))==['fields', 'info', 'logs.txt', 'whole']
    assert sorted(os.listdir (f'{manager_path}/whole'))==['ExampleExperimentManager-default.pk', 'last.pk']
    assert sorted(os.listdir (f'{manager_path}/info'))==['ExampleExperimentManager-default.pk', 'last.pk']
    assert sorted(os.listdir (f'{manager_path}/fields'))==['ExampleExperimentManager-default.pk', 'last.pk']

    print ('\nlist after storing ExampleExperimentManager')
    em_before = manager_factory.get_experiment_manager ()
    change_manager (None, manager_path=manager_path)
    em_after = manager_factory.get_experiment_manager ()
    assert em_before.__class__.__name__ == em_after.__class__.__name__

    assert sorted(os.listdir (f'{manager_path}/whole'))==['ExampleExperimentManager-default.pk', 'last.pk']

    # we store a third EM (DummyExperimentManager) and list the two
    # stored managers
    print ('\nlist after storing DummyExperimentManager')
    em = DummyExperimentManager (path_experiments=path_experiments)
    manager_factory.register_manager(em)
    manager_factory.write_manager(em)
    assert manager_factory.get_experiment_manager().__class__.__name__ == 'DummyExperimentManager'
    change_manager (None, manager_path=manager_path)

    assert sorted(os.listdir (f'{manager_path}/whole'))==['DummyExperimentManager-default.pk', 'ExampleExperimentManager-default.pk', 'last.pk']

    whole_object_path = Path(f'{manager_path}/whole')
    em=cloudpickle.load (open (whole_object_path / 'last.pk', 'rb'))
    assert em.__class__.__name__=='DummyExperimentManager'

    # we change the registered manager back to the first one
    print ('\nlist after changing manager')
    change_manager('ExampleExperimentManager-default', manager_path=manager_path)
    assert manager_factory.get_experiment_manager().__class__.__name__ == 'ExampleExperimentManager'
    em=cloudpickle.load (open (whole_object_path / 'last.pk', 'rb'))
    assert em.__class__.__name__=='ExampleExperimentManager'

    remove_previous_results (path_results)

# Comes from change_manager.ipynb, cell
def test_change_manager_parse_and_run ():
    # the following lists stored experiment managers, keeping the current experiment manager
    path_results = 'test_change_manager_parse_and_run'
    manager_path = f'{path_results}/manager'
    path_experiments = f'{path_results}/experiments'

    # *********************************
    # write managers
    # *********************************
    em = ExampleExperimentManager(path_experiments=path_experiments, manager_path=manager_path)
    em.register_and_store_subclassed_manager ()

    em = DummyExperimentManager(path_experiments=path_experiments, manager_path=manager_path)
    em.register_and_store_subclassed_manager ()

    assert sorted(os.listdir (f'{manager_path}/whole'))==['DummyExperimentManager-default.pk', 'ExampleExperimentManager-default.pk', 'last.pk']

    # *********************************
    # *********************************
    command = f'-l -p {manager_path}'
    parse_arguments_and_run (command.split())

    command = f'-m ExampleExperimentManager-default -p {manager_path}'
    parse_arguments_and_run (command.split())

    command = f'-l -p {manager_path}'
    parse_arguments_and_run (command.split())

    remove_previous_results (path_results)