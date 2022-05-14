# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/utils/tst.experiment_utils.ipynb (unless otherwise specified).

__all__ = ['generate_data_exp_utils', 'test_get_experiment_data', 'test_get_parameters_and_scores',
           'test_get_scores_names', 'test_get_monitored_training_metrics', 'test_get_classes_with_results',
           'test_get_parameters_unique', 'test_compact_parameters', 'test_replace_with_default_values',
           'test_remove_defaults', 'test_find_rows_with_parameters_dict', 'test_summarize_results', 'test_query',
           'test_summary']

# Cell
import pytest
import pandas as pd
import numpy as np
import os
import joblib
from IPython.display import display
from dsblocks.utils.nbdev_utils import md

from hpsearch.utils.experiment_utils import *
from hpsearch.examples.dummy_experiment_manager import (DummyExperimentManager,
                                                        run_multiple_experiments)
from hpsearch.examples.complex_dummy_experiment_manager import generate_data, init_em

# Comes from experiment_utils.ipynb, cell
def generate_data_exp_utils (name_folder):
    path_experiments = f'test_{name_folder}'
    manager_path = f'{path_experiments}/managers'
    em = DummyExperimentManager (path_experiments=path_experiments, manager_path=manager_path,
                                 verbose=0)
    em.remove_previous_experiments ()
    run_multiple_experiments(em=em, nruns=5, noise=0.1, verbose=False,
                             values_to_explore=dict(offset=[0.1, 0.3, 0.6], epochs=[5, 10, 100]))
    run_multiple_experiments(em=em, nruns=5, noise=0.1, verbose=False, rate=0.0001,
                             values_to_explore=dict(offset=[0.1, 0.3, 0.6], epochs=[5, 10, 100]))
    return em

# Comes from experiment_utils.ipynb, cell
def test_get_experiment_data ():
    path_experiments = 'test_get_experiment_data'
    em = generate_data (path_experiments)

    df = get_experiment_data ()
    reference = em.get_experiment_data ()
    pd.testing.assert_frame_equal (df, reference)

    em.remove_previous_experiments ()

# Comes from experiment_utils.ipynb, cell
def test_get_parameters_and_scores ():
    path_experiments = 'test_get_parameters_and_scores'
    em = generate_data (path_experiments)
    df = em.get_experiment_data ()

    # ************************************************************
    # get_parameters_columns
    # ************************************************************
    assert get_parameters_columns (df) ==['epochs', 'offset', 'rate', 'noise']

    offset = df.offset.values.copy()
    md ('- We can take only those which have at least some value that is not None.')
    df.loc[:, 'offset'] = None
    assert get_parameters_columns (df, only_not_null=True)==['epochs', 'rate', 'noise']

    md ('- If only some elements are None for a given parameter, we still include it.')
    df.loc[:, 'offset'] = offset
    df.loc[2, 'offset'] = None
    assert get_parameters_columns (df, only_not_null=True)==['epochs', 'offset', 'rate', 'noise']
    df.loc[:, 'offset'] = offset

    # ************************************************************
    # get_experiment_parameters
    # ************************************************************
    md ('- Same as get_parameters_columns, but returning dataframe of parameter values.')
    result = get_experiment_parameters (df)
    assert result.shape == (9, 4)
    assert sorted(result.columns) == sorted(['epochs', 'offset', 'rate', 'noise'])

    # ************************************************************
    # get_scores_columns
    # ************************************************************
    md ('- Retrieve all columns that have scores, for all runs')
    assert get_scores_columns (df) == ['0_validation_accuracy',
     '0_test_accuracy',
     '0_finished',
     '1_validation_accuracy',
     '1_test_accuracy',
     '1_finished',
     '2_validation_accuracy',
     '2_test_accuracy',
     '2_finished',
     '3_validation_accuracy',
     '3_test_accuracy',
     '3_finished',
     '4_validation_accuracy',
     '4_test_accuracy',
     '4_finished']

    md ('- Retrieve all columns for given score name, for all runs')
    assert get_scores_columns (df, suffix_results='_test_accuracy') == [
         '0_test_accuracy',
         '1_test_accuracy',
         '2_test_accuracy',
         '3_test_accuracy',
         '4_test_accuracy']

    md ('- Retrieve all columns for given score name, for given runs')
    assert get_scores_columns (df, suffix_results='_test_accuracy', class_ids=[2, 4]) == [
     '2_test_accuracy',
     '4_test_accuracy']

    # ************************************************************
    # get_experiment_scores
    # ************************************************************
    md ('- Same, but returning dataframe with selected scores values:')
    result = get_experiment_scores (df)
    display (result)
    assert result.shape==(9,15)

    result = get_experiment_scores (df, suffix_results='_test_accuracy')
    display (result)
    assert result.shape==(9,5)

    result = get_experiment_scores (df, suffix_results='_test_accuracy', class_ids=[2,4])
    display (result)
    assert result.shape==(9,2)

    md ('- We can remove the metric name and only keep the run number in each column:')
    result = get_experiment_scores (df, suffix_results='_test_accuracy', class_ids=[2,4], remove_suffix=True)
    display (result)
    assert result.shape==(9,2)

    # ************************************************************
    # get_scores_columns, first usage example: we do not indicate the name of the score
    # ************************************************************
    assert get_scores_columns (df)==['0_validation_accuracy', '0_test_accuracy', '0_finished',
                                     '1_validation_accuracy', '1_test_accuracy', '1_finished',
                                     '2_validation_accuracy', '2_test_accuracy', '2_finished',
                                     '3_validation_accuracy', '3_test_accuracy', '3_finished',
                                     '4_validation_accuracy', '4_test_accuracy', '4_finished']

    # ************************************************************
    # get_scores_columns, second usage: we indicate the name of the score
    # ************************************************************
    result = get_scores_columns (df, class_ids=range(5), suffix_results='_validation_accuracy')
    assert result == ['0_validation_accuracy', '1_validation_accuracy', '2_validation_accuracy',
                     '3_validation_accuracy', '4_validation_accuracy']
    em.remove_previous_experiments ()

# Comes from experiment_utils.ipynb, cell
def test_get_scores_names ():
    em = generate_data_exp_utils ('get_scores_names')

    df = em.get_experiment_data ()
    scores_names = get_scores_names (df)
    print (scores_names)
    assert scores_names == ['test_accuracy', 'validation_accuracy']

    scores_names=get_scores_names (df, run_number=3, experiment=7)
    print(scores_names)
    assert list(np.sort(scores_names))==['test_accuracy', 'validation_accuracy']

    # test when only some scores are valid
    df2 = df.copy()
    df2.loc[7, '3_test_accuracy']=np.nan
    scores_names=get_scores_names (df2, run_number=3, experiment=7)
    print (scores_names)
    assert scores_names==['validation_accuracy']

    em.remove_previous_experiments()

# Comes from experiment_utils.ipynb, cell
def test_get_monitored_training_metrics ():
    em = generate_data_exp_utils ('get_monitored_training_metrics')

    monitored_metrics = get_monitored_training_metrics (0)
    print (monitored_metrics)
    assert monitored_metrics==['validation_accuracy', 'test_accuracy', 'accuracy']

    em.remove_previous_experiments()

# Comes from experiment_utils.ipynb, cell
def test_get_classes_with_results ():
    em = generate_data ('get_classes_with_results')

    df = em.get_experiment_data ()
    # we need to introduce experiment_data df, and suffix_results
    result = get_classes_with_results (df, suffix_results='_validation_accuracy')
    display (result)
    assert result==[0,1,2,3,4]

    # we can also restrict to certain class_ids
    result = get_classes_with_results (df, suffix_results='_validation_accuracy', class_ids=[0,2])
    display (result)
    assert result==[0,2]
    em.remove_previous_experiments()

# Comes from experiment_utils.ipynb, cell
def test_get_parameters_unique ():
    em = generate_data_exp_utils ('get_parameters_unique')
    df = em.get_experiment_data ()

    # keeps only those parameters with more than one value,
    # removing 'noise' in this case, since it has the same value in all rows
    result = get_parameters_unique (df[['epochs','offset','rate', 'noise']])
    assert result[1].shape==(18,3)
    assert result[0] == ['epochs', 'offset', 'rate']

    em.remove_previous_experiments()

# Comes from experiment_utils.ipynb, cell
def test_compact_parameters ():
    em = generate_data_exp_utils ('compact_parameters')
    df = em.get_experiment_data ()

    result = compact_parameters (df, number_characters=2)
    display (result[0].head())
    assert all(result[0].columns == ['Ep', 'Of', 'Ra', 'No', '0VaAc', '0TeAc', 'Ti0', 'Da', '0Fi', '1VaAc',
           '1TeAc', 'Ti1', '1Fi', '2VaAc', '2TeAc', 'Ti2', '2Fi', '3VaAc', '3TeAc',
           'Ti3', '3Fi', '4VaAc', '4TeAc', 'Ti4', '4Fi'])

    assert result[1]=={'epochs': 'Ep',
         'offset': 'Of',
         'rate': 'Ra',
         'noise': 'No',
         '0_validation_accuracy': '0VaAc',
         '0_test_accuracy': '0TeAc',
         'time_0': 'Ti0',
         'date': 'Da',
         '0_finished': '0Fi',
         '1_validation_accuracy': '1VaAc',
         '1_test_accuracy': '1TeAc',
         'time_1': 'Ti1',
         '1_finished': '1Fi',
         '2_validation_accuracy': '2VaAc',
         '2_test_accuracy': '2TeAc',
         'time_2': 'Ti2',
         '2_finished': '2Fi',
         '3_validation_accuracy': '3VaAc',
         '3_test_accuracy': '3TeAc',
         'time_3': 'Ti3',
         '3_finished': '3Fi',
         '4_validation_accuracy': '4VaAc',
         '4_test_accuracy': '4TeAc',
         'time_4': 'Ti4',
         '4_finished': '4Fi'}

    em.remove_previous_experiments()

# Comes from experiment_utils.ipynb, cell
def test_replace_with_default_values ():
    em = generate_data_exp_utils ('replace_with_default_values')

    df = em.get_experiment_data ()
    df=replace_with_default_values(df)
    assert (df.epochs.values == ([5.]*3 + [10.]*3 + [100.]*3)*2).all()

    em.remove_previous_experiments()

# Comes from experiment_utils.ipynb, cell
def test_remove_defaults ():
    em = init_em ('remove_defaults')
    result, dict_results = em.create_experiment_and_run (parameters={'offset':0.1, 'rate': 0.05})

    parameters = remove_defaults ({'offset':0.1, 'rate': 0.05})
    assert parameters=={'offset':0.1, 'rate': 0.05}

    parameters = remove_defaults ({'offset':0.1, 'rate': 0.01, 'epochs': 10})
    assert parameters=={'offset':0.1}

    parameters = remove_defaults ({'offset':0.5, 'rate': 0.000001, 'epochs': 10})
    assert parameters=={'rate': 0.000001, 'epochs': 10}

    parameters = remove_defaults ({'offset':0.5, 'rate': 0.000001, 'epochs': 100})
    assert parameters=={'rate': 0.000001}

    em.remove_previous_experiments ()

# Comes from experiment_utils.ipynb, cell
def test_find_rows_with_parameters_dict ():
    em = generate_data_exp_utils ('find_rows_with_parameters_dict')

    df = em.get_experiment_data ()
    result = find_rows_with_parameters_dict (df, dict (rate=0.0001))
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[]
    assert not changed_dataframe

    result = find_rows_with_parameters_dict (df, dict (rate=0.0001), exact_match=False)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows == [9, 10, 11, 12, 13, 14, 15, 16, 17]

    result = find_rows_with_parameters_dict (df, dict (rate=0.0001, epochs=5, offset=0.6), exact_match=False,
                                        ignore_keys=['epochs'])
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[11, 14, 17]

    df.loc[16, 'rate']=0.00011
    result = find_rows_with_parameters_dict (df, dict (rate=0.0001), exact_match=False)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[9, 10, 11, 12, 13, 14, 15, 17]

    result = find_rows_with_parameters_dict (df, dict (rate=0.0001), exact_match=False, precision = 0.0001)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[9, 10, 11, 12, 13, 14, 15, 16, 17]

    result = find_rows_with_parameters_dict (df, dict (new_par=4), exact_match=False)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert changed_dataframe
    assert df.shape == (18, 26)
    assert matching_rows==[]
    assert 'new_par' in df.columns
    assert matching_rows==[]

    em.remove_previous_experiments ()

# Comes from experiment_utils.ipynb, cell
def test_summarize_results ():
    em = init_em ('summarize_results')
    em.run_multiple_repetitions (parameters=dict(offset=0.1, rate=0.01), nruns=3)
    em.run_multiple_repetitions (parameters=dict(offset=0.2, rate=0.001), nruns=5)
    em.run_multiple_repetitions (parameters=dict(offset=0.3, rate=0.02), nruns=2)

    md ('\n\n')
    md ('- We need to indicate the metric to be retrieved, otherwise it will count '
        'as many results as num_results*num_metrics: ')
    d = summarize_results ()
    display (d['mean'])
    assert d['mean'].num_results.sum() == 30
    assert d['mean'].shape[0]==3

    md ('\n\n')
    md ('- The metric is indicated with `_` at the beginning: ')
    d = summarize_results (suffix_results='_validation_accuracy')
    display (d['mean'])
    assert d['mean'].num_results.sum() == 10
    assert d['mean'].shape[0]==3

    md ('\n\n')
    md ('- We can filter those results that have less than X runs: ')
    d = summarize_results (suffix_results='_validation_accuracy', min_results=5)
    display (d['mean'])
    assert d['mean'].num_results.sum() == 5
    assert d['mean'].shape[0]==1

    md ('\n\n')
    md ('- We can filter by experiment number and/or number of results, and retrieve the original dataframe,'
        'plus new columns with stats: ')
    d = summarize_results (suffix_results='_validation_accuracy', experiments=[0,2], output='allcols')
    display (d)
    assert d.shape[0]==2
    assert all(d.index==[0,2])
    assert {'mean', 'min', 'max', 'std', 'median'}.issubset(d.columns)
    em.remove_previous_experiments ()

# Comes from experiment_utils.ipynb, cell
def test_query ():
    em = generate_data_exp_utils ('query')

    dmean, d = query (parameters_fixed=dict (rate=0.0001))
    assert dmean.empty

    md ('the dataframe only has mean. Results are sorted by mean score')
    dmean, d = query (parameters_fixed=dict (rate=0.0001), exact_match=False)
    assert dmean.shape[0]==9 and (dmean.rate==0.0001).all() and len(dmean.offset.unique())==3 and dmean['mean'].iloc[0]>dmean['mean'].iloc[1] and dmean['mean'].iloc[1] > dmean['mean'].iloc[2]
    display (dmean)
    md ('The second output d contains a field "stats" which is a dataframe. Results are sorted by mean score')
    assert {'mean', 'median', 'rank', 'min', 'max', 'std'}.issubset(d['stats'])
    display (d['stats'])

    md ('We can request parameter be in specific list of values')
    dmean, d = query (parameters_fixed=dict(rate=0.0001), exact_match=False,
                  parameters_variable=dict(epochs=[5,10], offset=[0.1, 0.3]))
    assert sorted(dmean.epochs.unique()) == [5,10]
    assert sorted(dmean.offset.unique()) == [0.1, 0.3]
    assert dmean.shape[0]==4
    display (dmean)

    md ('If we want a value that is the default, we need to indicate None')
    dmean, d = query (parameters_fixed=dict(rate=0.0001), exact_match=False,
              parameters_variable=dict(epochs=[10, None], offset=[0.1, 0.3]))
    assert dmean.shape[0]==4
    assert dmean.epochs.isna().sum() == 2
    assert (dmean.epochs == 10).sum() == 2
    display (dmean)

    em.remove_previous_experiments ()

# Comes from experiment_utils.ipynb, cell
def test_summary ():
    em = init_em ('summary')
    em.run_multiple_repetitions (parameters=dict(offset=0.1, rate=0.01), nruns=3)
    em.run_multiple_repetitions (parameters=dict(offset=0.2, rate=0.001), nruns=5)
    em.run_multiple_repetitions (parameters=dict(offset=0.3, rate=0.02), nruns=2)
    df = em.get_experiment_data()
    result = summary (df, score='_validation_accuracy')
    display (result)
    assert all(result.columns == ['offset', 'rate', '0', '1', '2', '3', '4'])
    assert result.shape[0] == 3
    em.remove_previous_experiments ()