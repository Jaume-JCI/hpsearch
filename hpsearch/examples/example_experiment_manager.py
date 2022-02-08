# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/examples/example_experiment_manager.ipynb (unless otherwise specified).

__all__ = ['ExampleExperimentManager']

# Cell
from ..experiment_manager import ExperimentManager
import hpsearch
import os

# Cell
class ExampleExperimentManager (ExperimentManager):

    def __init__ (self, **kwargs):
        super().__init__(**kwargs)

    def run_experiment (self, parameters={}, path_results='./results'):
        dict_results = {}
        if parameters.get('my_first',0) > 0.5:
            dict_results['my_score'] = parameters.get('my_second',1) - parameters.get('my_third', 2)
        else:
            dict_results['my_score'] = parameters.get('my_second',1) * parameters.get('my_third', 2)
        return dict_results

    def get_default_parameters (self, parameters):
        defaults = dict(my_first=5,
                        my_second=10,
                        my_third=100)
        return defaults