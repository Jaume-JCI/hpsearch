# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/examples/complex_dummy_experiment_manager.ipynb (unless otherwise specified).

__all__ = ['ComplexDummyExperimentManager', 'DummyManagerAvoidSaving', 'init_em', 'run_multiple_experiments',
           'remove_previous_experiments', 'generate_data']

# Cell
import os
import shutil
import os
import pytest
import numpy as np

from .dummy_experiment_manager import DummyExperimentManager, FakeModel
import hpsearch.examples.dummy_experiment_manager as dummy_em
from ..visualization import plot_utils
import hpsearch

# Cell
class ComplexDummyExperimentManager (DummyExperimentManager):

    def __init__ (self, model_file_name='model_weights.pk', **kwargs):
        super().__init__ (model_file_name=model_file_name, **kwargs)
        self.raise_error_if_run = False
        self.desired_path_results_previous_experiment = None
        self.desired_epochs = None
        self.desired_current_epoch = None

    def run_experiment (self, parameters={}, path_results='./results'):

        # useful for testing: in some cases the experiment manager should not call run_experiment
        if self.raise_error_if_run:
            raise RuntimeError ('run_experiment should not be called')

        # extract hyper-parameters used by our model. All the parameters have default values if they are not passed.
        offset = parameters.get('offset', 0.5)   # default value: 0.5
        rate = parameters.get('rate', 0.01)   # default value: 0.01
        epochs = parameters.get('epochs', 10) # default value: 10
        noise = parameters.get('noise', 0.0)
        if parameters.get('actual_epochs') is not None:
            epochs = parameters.get('actual_epochs')

        # other parameters that do not form part of our experiment definition
        # changing the values of these other parameters, does not make the ID of the experiment change
        verbose = parameters.get('verbose', True)

        # build model with given hyper-parameters
        model = FakeModel (offset=offset, rate=rate, epochs=epochs, noise = noise, verbose=verbose)

        # load training, validation and test data (fake step)
        model.load_data()

        # start from previous experiment if indicated by parameters
        path_results_previous_experiment = parameters.get('prev_path_results')
        if path_results_previous_experiment is not None:
            model.load_model_and_history (path_results_previous_experiment)
            assert self.desired_path_results_previous_experiment is None or self.desired_path_results_previous_experiment==path_results_previous_experiment

        # fit model with training data
        model.fit ()

        # check
        assert self.desired_epochs is None or self.desired_epochs==model.epochs
        assert self.desired_current_epoch is None or self.desired_current_epoch==model.current_epoch

        # save model weights and evolution of accuracy metric across epochs
        model.save_model_and_history(path_results)

        # simulate ctrl-c
        if parameters.get ('halt', False):
            raise KeyboardInterrupt ('stopped')

        # evaluate model with validation and test data
        validation_accuracy, test_accuracy = model.retrieve_score()

        # store model
        self.model = model

        # the function returns a dictionary with keys corresponding to the names of each metric.
        # We return result on validation and test set in this example
        dict_results = dict (validation_accuracy = validation_accuracy,
                             test_accuracy = test_accuracy)

        return dict_results

class DummyManagerAvoidSaving (ComplexDummyExperimentManager):
    def __init__ (self, **kwargs):
        self.my_new_field = [2, 1, 3]
        self.greeting_message = 'good morning!'
        super ().__init__ (avoid_saving_fields=['my_new_field', 'greeting_message'], **kwargs)

# Cell
def init_em (name_folder, **kwargs):
    path_experiments = f'test_{name_folder}/default'
    manager_path = f'{path_experiments}/managers'
    em = ComplexDummyExperimentManager (path_experiments=path_experiments, manager_path=manager_path, **kwargs)

    em.remove_previous_experiments(parent=True)

    with pytest.raises (FileNotFoundError):
        os.listdir(em.path_experiments)

    return em

# Cell
def run_multiple_experiments (**kwargs):
    dummy_em.run_multiple_experiments (EM=ComplexDummyExperimentManager, **kwargs)

def remove_previous_experiments ():
    dummy_em.remove_previous_experiments (EM=ComplexDummyExperimentManager)

# Cell
def generate_data (name_folder, nruns=5, noise=0.1, verbose_model=False, verbose=0,
                   parameters_multiple_values=None, parameters_single_value=None,
                   other_parameters={}, em_args={}, **kwargs):
    np.random.seed (42)
    path_experiments = f'test_{name_folder}/default'
    manager_path = f'{path_experiments}/managers'
    em = ComplexDummyExperimentManager (path_experiments=path_experiments, manager_path=manager_path,
                                        verbose=verbose, **kwargs)
    em.remove_previous_experiments (parent=True)
    run_multiple_experiments (em=em, nruns=nruns, noise=noise, verbose=verbose,
                              values_to_explore=parameters_multiple_values,
                              parameters_single_value=parameters_single_value,
                              other_parameters=other_parameters, em_args=em_args)
    return em