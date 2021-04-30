# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/visualization/metric_correlation.ipynb (unless otherwise specified).

__all__ = ['plot_metric_relationship']

# Cell
from ..utils import experiment_utils as ut
from . import plotly
import numpy as np

def plot_metric_relationship (metric_1, metric_2, folder_experiments=None, run_numbers=None,
                              experiments=None, experiment_subset=None,
                              backend='visdom'):
    df = ut.get_experiment_data (folder_experiments=folder_experiments, experiments=experiments)
    df_metric_1 = ut.get_experiment_scores (experiment_data=df, suffix_results=f'_{metric_1}', remove_suffix=True, class_ids=run_numbers)
    df_metric_2 = ut.get_experiment_scores (experiment_data=df, suffix_results=f'_{metric_2}', remove_suffix=True, class_ids=run_numbers)

    traces=plotly.add_trace(df_metric_1.values, df_metric_2.values, traces=[], style='A.', label='all experiments', backend=backend);

    if experiment_subset is not None:
        df_metric_1_subset = ut.get_experiment_scores (experiment_data=df.loc[experiment_subset], suffix_results=f'_{metric_1}', remove_suffix=True, class_ids=run_numbers)
        df_metric_2_subset = ut.get_experiment_scores (experiment_data=df.loc[experiment_subset], suffix_results=f'_{metric_2}', remove_suffix=True, class_ids=run_numbers)
        traces=plotly.add_trace(df_metric_1_subset.values, df_metric_2_subset.values, traces=traces, style='A.', label=f'selected subset', backend=backend);

    plotly.plot(np.linspace(df_metric_1.values.min(), df_metric_1.values.max(), 100),
                np.linspace(df_metric_2.values.min(), df_metric_2.values.max(), 100),
                traces=traces, style='A-', label='linear', title=f'{metric_1} vs {metric_2}', xlabel=metric_1, ylabel=metric_2, backend=backend);