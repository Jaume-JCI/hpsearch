# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/examples/dummy_experiment_manager.ipynb (unless otherwise specified).

__all__ = ['FakeModel', 'DummyExperimentManager', 'run_multiple_experiments', 'remove_previous_experiments']

# Cell
import numpy as np
import pickle

class FakeModel (object):

    overfitting_epochs = 20

    def __init__ (self, offset=0.5, rate=0.01, epochs=10, noise=0.0, verbose=True):
        # hyper-parameters
        self.offset = offset
        self.rate = rate
        self.epochs = epochs

        # fake internal weight
        self.weight = 0

        # fake accuracy
        self.accuracy = 0

        # noise
        self.noise = noise

        # other parameters
        self.verbose = verbose

        self.history = {}
        self.current_epoch = 0

    def fit (self):
        number_epochs = int(self.epochs)
        if self.verbose:
            print (f'fitting model with {number_epochs} epochs')

        if self.current_epoch==0:
            self.accuracy = self.offset

        for epoch in range(number_epochs):
            self.weight += self.rate
            if self.current_epoch < self.overfitting_epochs:
                self.accuracy += self.rate
            else:
                self.accuracy -= self.rate
            if self.verbose:
                print (f'epoch {epoch}: accuracy: {self.accuracy}')

            # we keep track of the evolution of different metrics to later be able to visualize it
            self.store_intermediate_metrics ()

            # increase current epoch by 1
            self.current_epoch += 1

    def store_intermediate_metrics (self):
        validation_accuracy, test_accuracy = self.score()
        if 'validation_accuracy' not in self.history:
            self.history['validation_accuracy'] = []
        self.history['validation_accuracy'].append(validation_accuracy)

        if 'test_accuracy' not in self.history:
            self.history['test_accuracy'] = []
        self.history['test_accuracy'].append(test_accuracy)

        if 'accuracy' not in self.history:
            self.history['accuracy'] = []
        self.history['accuracy'].append(self.accuracy)

    def save_model_and_history (self, path_results):
        pickle.dump (self.weight, open(f'{path_results}/model_weights.pk','wb'))
        pickle.dump (self.history, open(f'{path_results}/model_history.pk','wb'))

    def load_model_and_history (self, path_results):
        if os.path.exists(f'{path_results}/model_weights.pk'):
            self.weight = pickle.load (open(f'{path_results}/model_weights.pk','rb'))
            self.history = pickle.load (open(f'{path_results}/model_history.pk','rb'))
            self.current_epoch = len(self.history['accuracy'])
            if self.current_epoch > 0:
                self.accuracy = self.history['accuracy'][-1]
            else:
                self.accuracy = self.offset
        else:
            print (f'model not found in {path_results}')

    def score (self):
        # validation accuracy
        validation_accuracy = self.accuracy + np.random.randn() * self.noise

        # test accuracy
        if self.epochs < 10:
            test_accuracy = self.accuracy + 0.1
        else:
            test_accuracy = self.accuracy - 0.1
        test_accuracy = test_accuracy + np.random.randn() * self.noise

        # make accuracy be in interval [0,1]
        validation_accuracy = max(min(validation_accuracy, 1.0), 0.0)
        test_accuracy = max(min(test_accuracy, 1.0), 0.0)

        return validation_accuracy, test_accuracy

    # fake load_data which does nothing
    def load_data (self):
        pass


# Cell
from ..experiment_manager import ExperimentManager
import hpsearch
import os
from ..visualization import plot_utils

class DummyExperimentManager (ExperimentManager):

    def __init__ (self):
        super().__init__()

    def run_experiment (self, parameters={}, path_results='./results'):
        # extract hyper-parameters used by our model. All the parameters have default values if they are not passed.
        offset = parameters.get('offset', 0.5)   # default value: 0.5
        rate = parameters.get('rate', 0.01)   # default value: 0.01
        epochs = parameters.get('epochs', 10) # default value: 10
        noise = parameters.get('noise', 0.0)

        # other parameters that do not form part of our experiment definition
        # changing the values of these other parameters, does not make the ID of the experiment change
        verbose = parameters.get('verbose', True)

        # build model with given hyper-parameters
        model = FakeModel (offset=offset, rate=rate, epochs=epochs, noise = noise, verbose=verbose)

        # load training, validation and test data (fake step)
        model.load_data()

        # fit model with training data
        model.fit ()

        # save model weights and evolution of accuracy metric across epochs
        model.save_model_and_history(path_results)

        # evaluate model with validation and test data
        validation_accuracy, test_accuracy = model.score()

        # store model
        self.model = model

        # the function returns a dictionary with keys corresponding to the names of each metric.
        # We return result on validation and test set in this example
        dict_results = dict (validation_accuracy = validation_accuracy,
                             test_accuracy = test_accuracy)

        return dict_results

    # implementing the following method is not necessary but recommended
    def get_default_parameters (self, parameters):
        """Indicate the default value for each of the hyper-parameters used."""
        defaults = dict(offset=0.5,
                        rate=0.01,
                        epochs=10)
        return defaults

    # implementing the following method is not necessary but recommended
    def get_path_experiments (self, path_experiments = None, folder = None):
        """Gives the root path to the folder where results of experiments are stored."""
        path_experiments = f'{os.path.dirname(hpsearch.__file__)}/../results'
        if folder != None:
            path_experiments = f'{path_experiments}/{folder}'
        return path_experiments

    # implementing the following method is not necessary but recommended
    def get_default_operations (self):
        default_operations = dict (root='',
                                   metric='validation_accuracy',
                                   op='max')

        return default_operations

    def experiment_visualization (self, experiments=None, run_number=0, root_path=None, root_folder=None,
                                  name_file='model_history.pk', metric='test_accuracy', backend='matplotlib',
                                  **kwargs):
        if root_path is None:
            root_path = self.get_path_experiments(folder=root_folder)
        traces = []
        for experiment_id in experiments:
            path_results = self.get_path_results (experiment_id, run_number=run_number, root_path=root_path)
            if os.path.exists('%s/%s' %(path_results, name_file)):
                history = pickle.load(open('%s/%s' %(path_results, name_file),'rb'))
                label = '{}'.format(experiment_id)
                traces = plot_utils.add_trace ((1-np.array(history[metric]))*20, style='A.-', label=label,
                                               backend=backend, traces=traces)
        plot_utils.plot(title=metric, xlabel='epoch', ylabel=metric, traces=traces, backend=backend)

# Cell
def run_multiple_experiments (nruns=1, noise=0.0, verbose=True, rate=0.03):
    em = DummyExperimentManager ()
    parameters_single_value = dict(rate=rate, noise=noise)   # parameters where we use a fixed value
    parameters_multiple_values=dict(offset=[0.1, 0.3, 0.6], epochs=[5, 15, 30]) # parameters where we try multiple values
    other_parameters = dict(verbose=verbose) # parameters that control other aspects that are not part of our experiment definition (a new experiment is not created if we assign different values for these parametsers)
    em.grid_search (log_message='fixed rate, multiple epochs values',
            parameters_single_value=parameters_single_value,
            parameters_multiple_values=parameters_multiple_values,
            other_parameters=other_parameters,
            nruns=nruns)


# Cell
import shutil
import os

def remove_previous_experiments():
    em = DummyExperimentManager ()
    path_results = em.get_path_experiments()
    if os.path.exists(path_results):
        shutil.rmtree(path_results)