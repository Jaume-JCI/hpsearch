# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/07_example_wrapper.ipynb (unless otherwise specified).

__all__ = ['ExampleExperimentManager']

# Cell
import warnings
warnings.filterwarnings('ignore')
import sys
from .experiment_manager import ExperimentManager

class ExampleExperimentManager (ExperimentManager):

    def __init__ (self):
        super().__init__()

    def run_experiment (self, parameters={}, path_results='./results'):
        dict_results = {}
        if parameters.get('my_first',0) > 0.5:
            dict_results['my_score'] = parameters.get('my_second',1) - parameters.get('my_third', 2)
        else:
            dict_results['my_score'] = parameters.get('my_second',1) * parameters.get('my_third', 2)
        return dict_results