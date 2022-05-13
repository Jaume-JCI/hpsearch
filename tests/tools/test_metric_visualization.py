# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/tools/tst.metric_visualization.ipynb (unless otherwise specified).

__all__ = ['test_metric_visualization', 'test_several_visualizations', 'test_several_metrics',
           'test_several_metrics_same_plot', 'test_parse_arguments_and_visualize']

# Cell
import pytest
import pandas as pd
import os
import joblib
from IPython.display import display
from dsblocks.utils.nbdev_utils import md

from hpsearch.tools.metric_visualization import *
from hpsearch.examples.dummy_experiment_manager import generate_data

# Comes from metric_visualization.ipynb, cell
def test_metric_visualization ():
    em = generate_data ('metric_visualization')

    print ('default visualization')
    metric_visualization()

    print ('visualizing test_accuracy, and experiments -2 and 0')
    metric_visualization(experiments=[-2, 0], metric='test_accuracy', manager_path=em.manager_path)

    print ('using matplotlib as backend')
    metric_visualization(experiments=[3, 7], metric='test_accuracy', backend='matplotlib',
                         manager_path=em.manager_path)

    em.remove_previous_experiments ()

# Comes from metric_visualization.ipynb, cell
def test_several_visualizations ():
    em = generate_data ('several_visualizations')

    metric_visualization(experiments=[3, 7], metric='test_accuracy', backend='matplotlib',
                         visualization_options={'visualization': ['history', 'metric_correlation',
                                                                  'custom'],
                                                'metric_1': 'validation_accuracy',
                                                'metric_2': 'test_accuracy'},
                         manager_path=em.manager_path)
    em.remove_previous_experiments ()

# Comes from metric_visualization.ipynb, cell
def test_several_metrics ():
    em = generate_data ('several_metrics')

    metric_visualization (experiments=[-1,-2], metric=['test_accuracy', 'validation_accuracy'],
                          backend='matplotlib', manager_path=em.manager_path)

    em.remove_previous_experiments ()

# Comes from metric_visualization.ipynb, cell
def test_several_metrics_same_plot ():
    em = generate_data ('several_metrics_same_plot')

    metric_visualization (experiments=[-1], metric=['validation_accuracy'],
                          metrics_second=['test_accuracy'],
                          backend='matplotlib', manager_path=em.manager_path)

    em.remove_previous_experiments ()

# Comes from metric_visualization.ipynb, cell
def test_parse_arguments_and_visualize ():
    em = generate_data ('parse_arguments_and_visualize')

    visualization_options = "{'visualization': ['history', 'metric_correlation', 'custom'], " \
                         "'metric_1': 'validation_accuracy', 'metric_2': 'test_accuracy'}"

    command = '-e 3 7 -m test_accuracy -b matplotlib -v '.split ()
    command += [f'{visualization_options}']
    command += f'-p {em.manager_path}'.split()

    parse_arguments_and_visualize (command)

    em.remove_previous_experiments ()