# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/visualization/tst.plot_utils.ipynb (unless otherwise specified).

__all__ = ['test_plot_default']

# Cell
import pytest
import pandas as pd
import os
import joblib
from IPython.display import display
from dsblocks.utils.nbdev_utils import md

from hpsearch.visualization.plot_utils import *

# Comes from plot_utils.ipynb, cell
def test_plot_default ():
    traces = add_trace([1,2,3,30,60], 'b', label='first line')
    plot([10,20,30,40,100], 'y', label='second line', title='My title', xlabel = 'epochs', ylabel='percentage', traces=traces);