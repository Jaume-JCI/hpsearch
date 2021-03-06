# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_tests/utils/tst.experiment_utils.ipynb (unless otherwise specified).

__all__ = ['generate_data_exp_utils', 'test_get_experiment_data', 'test_get_parameters_and_scores',
           'test_get_scores_names', 'test_get_monitored_training_metrics', 'test_get_runs_with_results',
           'test_get_parameters_unique', 'test_compact_parameters', 'test_replace_with_default_values',
           'test_remove_defaults', 'test_find_rows_with_parameters_dict', 'test_find_rows_with_parameters_dict_corner',
           'test_summarize_results', 'test_query', 'test_summary']

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
from hpsearch.config import hp_defaults as dflt

# Comes from experiment_utils.ipynb, cell
def generate_data_exp_utils (name_folder):
    path_experiments = f'test_{name_folder}/debug'
    manager_path = f'{path_experiments}/managers'
    em = DummyExperimentManager (path_experiments=path_experiments, manager_path=manager_path,
                                 verbose=0)
    em.remove_previous_experiments (parent=True)
    run_multiple_experiments(em=em, nruns=5, noise=0.1, verbose=False,
                             parameters_multiple_values=dict(offset=[0.1, 0.3, 0.6], epochs=[5, 10, 100]))
    run_multiple_experiments(em=em, nruns=5, noise=0.1, verbose=False, rate=0.0001,
                             parameters_multiple_values=dict(offset=[0.1, 0.3, 0.6], epochs=[5, 10, 100]))
    return em

# Comes from experiment_utils.ipynb, cell
def test_get_experiment_data ():
    path_experiments = 'get_experiment_data'
    em = generate_data (path_experiments)

    df = get_experiment_data ()
    reference = em.get_experiment_data ()
    pd.testing.assert_frame_equal (df, reference)

    em.remove_previous_experiments (parent=True)

# Comes from experiment_utils.ipynb, cell
def test_get_parameters_and_scores ():
    path_experiments = 'test_get_parameters_and_scores'
    em = generate_data (path_experiments)
    df = em.get_experiment_data ()

    # ************************************************************
    # get_parameters_columns
    # ************************************************************
    expected_result = [(dflt.parameters_col, x, '') for x in ['epochs', 'noise', 'offset', 'rate']]
    assert get_parameters_columns (df) == expected_result

    mi_offset = (dflt.parameters_col, 'offset', '')
    offset = df[mi_offset].values.copy()
    md ('- We can take only those which have at least some value that is not None.')
    df.loc[:, mi_offset] = None
    expected_result = [(dflt.parameters_col, x, '') for x in ['epochs', 'noise', 'rate']]
    assert get_parameters_columns (df, only_not_null=True) == expected_result

    md ('- If only some elements are None for a given parameter, we still include it.')
    df.loc[:, mi_offset] = offset
    df.loc[2, mi_offset] = None
    expected_result = [(dflt.parameters_col, x, '') for x in ['epochs', 'noise', 'offset', 'rate']]
    assert get_parameters_columns (df, only_not_null=True)==expected_result
    df.loc[:, mi_offset] = offset

    # ************************************************************
    # get_experiment_parameters
    # ************************************************************
    md ('- Same as get_parameters_columns, but returning dataframe of parameter values.')
    result = get_experiment_parameters (df)
    assert result.shape == (9, 4)
    expected_result = [(dflt.parameters_col, x, '') for x in ['epochs', 'noise', 'offset', 'rate']]
    assert result.columns.tolist() == expected_result

    # ************************************************************
    # get_scores_columns
    # ************************************************************
    md ('- Retrieve all columns that have scores, for all runs')
    expected_result = [(dflt.scores_col, x, y) for x in ['test_accuracy', 'validation_accuracy']
                       for y in range(5)]
    assert get_scores_columns (df) == expected_result

    md ('- Retrieve all columns for given score name, for all runs')
    expected_result = [('scores', 'test_accuracy', 0), ('scores', 'test_accuracy', 1),
                       ('scores', 'test_accuracy', 2), ('scores', 'test_accuracy', 3),
                       ('scores', 'test_accuracy', 4)]
    assert get_scores_columns (df, score_name='test_accuracy') == expected_result

    md ('- Retrieve all columns for given score name, for given runs')
    expected_result = [(dflt.scores_col, x, y) for x in ['test_accuracy']
                       for y in [2, 4]]
    assert get_scores_columns (df, score_name='test_accuracy', run_number=[2, 4]) == expected_result

    # ************************************************************
    # get_experiment_scores
    # ************************************************************
    md ('- Same, but returning dataframe with selected scores values:')
    result = get_experiment_scores (df)
    display (result)
    assert result.shape==(9,10)

    result = get_experiment_scores (df, score_name='test_accuracy')
    display (result)
    assert result.shape==(9,5)

    result = get_experiment_scores (df, score_name='test_accuracy', run_number=[2,4])
    display (result)
    assert result.shape==(9,2)

    md ('- We can remove the metric name and only keep the run number in each column:')
    result = get_experiment_scores (df, score_name='test_accuracy', run_number=[2,4], remove_score_name=True)
    display (result)
    assert result.shape==(9,2)

    # ************************************************************
    # get_scores_columns, first usage example: we do not indicate the name of the score
    # ************************************************************
    expected_result = [(dflt.scores_col, x, y) for x in ['test_accuracy', 'validation_accuracy']
                       for y in range(5)]
    assert get_scores_columns (df)==expected_result

    # ************************************************************
    # get_scores_columns, second usage: we indicate the name of the score
    # ************************************************************
    result = get_scores_columns (df, run_number=range(5), score_name='validation_accuracy')
    expected_result = [(dflt.scores_col, 'validation_accuracy', y) for y in range(5)]
    assert result == expected_result
    em.remove_previous_experiments (parent=True)

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
    df2.loc[7, (dflt.scores_col, 'test_accuracy', 3)]=np.nan
    scores_names=get_scores_names (df2, run_number=3, experiment=7)
    print (scores_names)
    assert scores_names==['validation_accuracy']

    em.remove_previous_experiments (parent=True)

# Comes from experiment_utils.ipynb, cell
def test_get_monitored_training_metrics ():
    em = generate_data_exp_utils ('get_monitored_training_metrics')

    monitored_metrics = get_monitored_training_metrics (0)
    print (monitored_metrics)
    assert monitored_metrics==['validation_accuracy', 'test_accuracy', 'accuracy']

    em.remove_previous_experiments (parent=True)

# Comes from experiment_utils.ipynb, cell
def test_get_runs_with_results ():
    em = generate_data ('get_runs_with_results')

    df = em.get_experiment_data ()
    # we need to introduce experiment_data df, and score_name
    result = get_runs_with_results (df, score_name='validation_accuracy')
    display (result)
    assert result==[0,1,2,3,4]

    # we can also restrict to certain run_number
    result = get_runs_with_results (df, score_name='validation_accuracy', run_number=[0,2])
    display (result)
    assert result==[0,2]
    em.remove_previous_experiments (parent=True)

# Comes from experiment_utils.ipynb, cell
def test_get_parameters_unique ():
    em = generate_data_exp_utils ('get_parameters_unique')
    df = em.get_experiment_data ()

    # keeps only those parameters with more than one value,
    # removing 'noise' in this case, since it has the same value in all rows
    result = get_parameters_unique (df)
    assert result[1].shape==(18,28)
    assert result[0].tolist() == [(dflt.parameters_col, 'epochs', ''), (dflt.parameters_col, 'offset', ''),
                         (dflt.parameters_col, 'rate', '')]

    em.remove_previous_experiments (parent=True)

# Comes from experiment_utils.ipynb, cell
def test_compact_parameters ():
    em = generate_data_exp_utils ('compact_parameters')
    df = em.get_experiment_data ()

    result = compact_parameters (df, number_characters=2)
    display (result[0].head())
    assert result[0].columns.tolist() == [('parameters',   'Ep', ''),
            ('parameters',   'No', ''),
            ('parameters',   'Of', ''),
            ('parameters',   'Ra', ''),
            (  'run_info',   'Da',  0),
            (  'run_info',   'Da',  1),
            (  'run_info',   'Da',  2),
            (  'run_info',   'Da',  3),
            (  'run_info',   'Da',  4),
            (  'run_info',   'Fi',  0),
            (  'run_info',   'Fi',  1),
            (  'run_info',   'Fi',  2),
            (  'run_info',   'Fi',  3),
            (  'run_info',   'Fi',  4),
            (  'run_info',   'Ti',  0),
            (  'run_info',   'Ti',  1),
            (  'run_info',   'Ti',  2),
            (  'run_info',   'Ti',  3),
            (  'run_info',   'Ti',  4),
            (    'scores', 'TeAc',  0),
            (    'scores', 'TeAc',  1),
            (    'scores', 'TeAc',  2),
            (    'scores', 'TeAc',  3),
            (    'scores', 'TeAc',  4),
            (    'scores', 'VaAc',  0),
            (    'scores', 'VaAc',  1),
            (    'scores', 'VaAc',  2),
            (    'scores', 'VaAc',  3),
            (    'scores', 'VaAc',  4)]

    assert result[1]=={'epochs': 'Ep', 'noise': 'No', 'offset': 'Of', 'rate': 'Ra', 'date': 'Da',
                       'finished': 'Fi', 'time': 'Ti', 'test_accuracy': 'TeAc', 'validation_accuracy': 'VaAc'}

    em.remove_previous_experiments (parent=True)

# Comes from experiment_utils.ipynb, cell
def test_replace_with_default_values ():
    em = generate_data_exp_utils ('replace_with_default_values')

    df = em.get_experiment_data ()
    df=replace_with_default_values(df)
    mi_epoch = (dflt.parameters_col, 'epochs', '')
    assert (df[mi_epoch].values == ([5.]*3 + [10.]*3 + [100.]*3)*2).all()

    em.remove_previous_experiments (parent=True)

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

    em.remove_previous_experiments (parent=True)

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

    mi_rate = (dflt.parameters_col, 'rate', '')
    df.loc[16, mi_rate]=0.00011
    result = find_rows_with_parameters_dict (df, dict (rate=0.0001), exact_match=False)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[9, 10, 11, 12, 13, 14, 15, 17]

    result = find_rows_with_parameters_dict (df, dict (rate=0.0001), exact_match=False, precision = 0.0001)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[9, 10, 11, 12, 13, 14, 15, 16, 17]

    result = find_rows_with_parameters_dict (df, dict (new_par=4), exact_match=False)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert changed_dataframe
    assert df.shape == (18, 30)
    assert matching_rows==[]
    assert (dflt.parameters_col, 'new_par', '') in df.columns
    assert matching_rows==[]

    em.remove_previous_experiments (parent=True)

# Comes from experiment_utils.ipynb, cell
def test_find_rows_with_parameters_dict_corner ():
    df = pd.DataFrame ({'a': ['1.0', '0.0', 'False', '1', '1', 'True'],
                        'b': [1,     2,     'yes',   'no',  1,   True],
                        'c': ['a',     'b',     'yes',   'no',  'c',  'd']})
    df.columns = pd.MultiIndex.from_tuples ([('parameters','a',''),
                                             ('parameters','b',''),
                                             ('parameters','c','')])
    result = find_rows_with_parameters_dict (df, dict (a=False, c='yes'), exact_match=False)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[2]

    result = find_rows_with_parameters_dict (df, dict (a=False, c='no'), exact_match=False)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[]

    result = find_rows_with_parameters_dict (df, dict (a=True, b=True), exact_match=False)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[0, 4, 5]

    result = find_rows_with_parameters_dict (df, dict (a=0.0), exact_match=False)
    matching_rows, changed_dataframe, matching_all_condition = result
    assert matching_rows==[1, 2]

# Comes from experiment_utils.ipynb, cell
def test_summarize_results ():
    em = init_em ('summarize_results')
    em.run_multiple_repetitions (parameters=dict(offset=0.1, rate=0.01), nruns=3)
    em.run_multiple_repetitions (parameters=dict(offset=0.2, rate=0.001), nruns=5)
    em.run_multiple_repetitions (parameters=dict(offset=0.3, rate=0.02), nruns=2)

    md ('\n\n')
    summary = summarize_results ()
    display (summary)
    mi_num_results = (dflt.num_results_col, 'num_results', '')
    assert summary[mi_num_results].sum() == 10
    assert summary.shape==(3, 13)

    md ('\n\n')
    md ('- We can restrict the metric to be the indicated one:')
    summary = summarize_results (score_name='validation_accuracy')
    display (summary)
    assert summary[mi_num_results].sum() == 10
    assert summary.shape==(3, 8)
    assert set(['mean','median','min','max','std'])==set(summary[dflt.stats_col, 'validation_accuracy'].columns)

    md ('\n\n')
    md ('- We can restrict the experiments to be analyzed:')
    summary = summarize_results (score_name='validation_accuracy', experiments=[0, 2])
    display (summary)
    assert summary.shape==(2, 8)
    assert summary.index==[0,2]


    md ('\n\n')
    md ('- We can indicate more than one metric:')
    summary = summarize_results (score_name=['validation_accuracy', 'test_accuracy'])
    display (summary)

    md ('\n\n')
    md ('- We can also restrict the stats to be provided:')
    summary = summarize_results (score_name='validation_accuracy', stats=['mean', 'min', 'max'])
    assert summary.shape == (3, 6)
    assert set(['mean','min','max'])==set(summary[dflt.stats_col, 'validation_accuracy'].columns)

    md ('\n\n')
    md ('- We can filter those results that have less than X runs: ')
    summary = summarize_results (score_name='validation_accuracy', min_results=5)
    display (summary)
    assert summary[mi_num_results].sum() == 5
    assert summary.shape==(1, 8)

    md ('\n\n')
    md ('- We can filter by experiment number and/or number of results, and retrieve the original dataframe,'
        'plus new columns with stats: ')
    summary = summarize_results (score_name='validation_accuracy', experiments=[0,2])
    display (summary)
    assert summary.shape==(2, 8)
    assert all(summary.index==[2, 0])
    assert (sorted(summary.columns.get_level_values(1).unique().tolist())==
            sorted(['offset', 'rate', 'num_results', 'validation_accuracy']))
    assert summary['stats','validation_accuracy'].columns.tolist()==['max', 'mean', 'median', 'min', 'std']
    em.remove_previous_experiments (parent=True)

# Comes from experiment_utils.ipynb, cell
def test_query ():
    em = generate_data_exp_utils ('query')

    summary = query (parameters_fixed=dict (rate=0.0001))
    assert summary.empty

    md ('the dataframe only has mean. Results are sorted by mean score')
    summary = query (parameters_fixed=dict (rate=0.0001), exact_match=False)
    par = lambda parameter: (dflt.parameters_col, parameter, '')
    stat = lambda statv: (dflt.stats_col, 'test_accuracy', statv)
    assert (summary.shape[0]==9 and (summary[par('rate')]==0.0001).all() and
            len(summary[par('offset')].unique())==3 and
            summary[stat('mean')].iloc[0]>summary[stat('mean')].iloc[1]
            and summary[stat('mean')].iloc[1] > summary[stat('mean')].iloc[2])

    display (summary)
    md ('The second output d contains a field "stats" which is a dataframe. Results are sorted by mean score')
    assert (summary['stats','validation_accuracy'].columns.tolist()==[
        'max', 'mean', 'median', 'min', 'std'])
    assert summary.shape==(9, 15)

    md ('We can request parameter be in specific list of values')
    summary = query (parameters_fixed=dict(rate=0.0001), exact_match=False,
                  parameters_variable=dict(epochs=[5,10], offset=[0.1, 0.3]))
    assert sorted(summary[par('epochs')].unique()) == [5,10]
    assert sorted(summary[par('offset')].unique()) == [0.1, 0.3]
    assert summary.shape==(4, 15)
    display (summary)

    md ('If we want a value that is the default, we need to indicate None')
    summary = query (parameters_fixed=dict(rate=0.0001), exact_match=False,
              parameters_variable=dict(epochs=[10, None], offset=[0.1, 0.3]))
    assert summary.shape==(4, 15)
    assert summary[par('epochs')].isna().sum() == 2
    assert (summary[par('epochs')] == 10).sum() == 2
    display (summary)

    em.remove_previous_experiments (parent=True)

# Comes from experiment_utils.ipynb, cell
def test_summary ():
    em = init_em ('summary')
    em.run_multiple_repetitions (parameters=dict(offset=0.1, rate=0.01), nruns=3)
    em.run_multiple_repetitions (parameters=dict(offset=0.2, rate=0.001), nruns=5)
    em.run_multiple_repetitions (parameters=dict(offset=0.3, rate=0.02), nruns=2)
    df = em.get_experiment_data()
    result = summary (df, score='validation_accuracy')
    display (result)
    assert result.columns.tolist() == ['offset', 'rate', 0, 1, 2, 3, 4]
    assert result.shape == (3, 7)
    em.remove_previous_experiments (parent=True)