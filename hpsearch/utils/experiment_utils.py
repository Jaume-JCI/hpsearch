# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/utils/experiment_utils.ipynb (unless otherwise specified).

__all__ = ['get_experiment_data', 'get_parameters_columns', 'get_experiment_parameters', 'get_scores_columns',
           'get_experiment_scores', 'get_scores_names', 'get_monitored_training_metrics', 'get_classes_with_results',
           'get_parameters_unique', 'compact_parameters', 'replace_with_default_values', 'remove_defaults',
           'find_rows_with_parameters_dict', 'summarize_results', 'query', 'summary']

# Cell
import pandas as pd
import numpy as np
import pickle
import os
import sys
import time
from sklearn.model_selection import ParameterGrid
import warnings
warnings.filterwarnings('ignore')

# Cell
def get_experiment_data (path_experiments=None, folder_experiments=None, experiments=None):
    """
    Returns data stored from previous experiments in the form DataFrame.

    If path_experiments is not given, it uses the default one.
    """
    from ..config.hpconfig import get_experiment_data
    return get_experiment_data (path_experiments=path_experiments, folder_experiments=folder_experiments,
                                experiments=experiments)

# Cell
def get_parameters_columns (experiment_data, only_not_null=False):
    parameters =  [par for par in experiment_data.columns if not par[0].isdigit() and (par.find('time_')<0) and (par.find('date')<0)]
    if only_not_null:
        parameters = np.array(parameters)[~experiment_data.loc[:,parameters].isnull().all(axis=0)].tolist()
    return parameters

# Cell
def get_experiment_parameters (experiment_data, only_not_null=False):
    return experiment_data[get_parameters_columns (experiment_data, only_not_null=only_not_null)]

# Cell
def get_scores_columns (experiment_data=None, suffix_results='', class_ids = None):
    """
    Determine the columnns that provide evaluation scores.

    We assume that they start with the class number, and that the other columns
    do not start with a digit.
    """
    if class_ids is not None:
        scores_columns = ['%d%s' %(col,suffix_results) for col in class_ids]
    else:
        if experiment_data is None:
            raise ValueError ('Either experiment_data or class_ids should be different than None')
        scores_columns = [col for col in experiment_data.columns if col[0].isdigit()]
        # For some experiments, we have multiple scores per class (e.g., due to different evaluation criteria). The argument suffix_results can be used to select the appropriate score.
        if len(suffix_results) > 0:
            scores_columns = [col for col in scores_columns if (len(col.split(suffix_results))==2) and (len(col.split(suffix_results)[1])==0) and (col.split(suffix_results)[0].isdigit()) ]
        else:
            # We assume that default scores are in columns whose names only have the class number
            scores_columns = [col for col in scores_columns if (len(col.split('_'))>=1)]
    return scores_columns

# Cell
def get_experiment_scores (experiment_data = None, suffix_results = '', class_ids = None, remove_suffix=False):
    df = experiment_data[get_scores_columns (experiment_data, suffix_results=suffix_results, class_ids=class_ids)]
    if remove_suffix:
        df.columns=[c.split('_')[0] for c in df.columns]
    return df

# Cell
def get_scores_names (experiment_data=None, run_number=None, experiment=None, only_valid=True):
    """
    Determine the names of the scores included in experiment data.

    We assume that the score columns start with the class number, and that the other columns do not start with a digit.

    If run_number is provided, we provide the scores stored for that run number. If, in addition to this,
    experiment is provided, and only_valid=True, we provide only the scores that are not NaN for the given
    experiment number.
    """

    if run_number is None:
        scores_names = np.unique([('_'.join(col.split('_')[1:]) if (len(col.split('_')) > 1) else '')
                                    for col in experiment_data.columns if col[0].isdigit()])

    else:
        scores_names = [col.split(f'{run_number}')[1] for col in experiment_data.columns if col.startswith(str(run_number))]
        scores_names = [('_'.join(col.split('_')[1:]) if (len(col.split('_')) > 1) else '')
                                    for col in scores_names]
        if (experiment is not None) and only_valid:
            scores_names = [name for name in scores_names if not np.isnan(experiment_data.loc[experiment, f'{run_number}_{name}'])]
        scores_names = list(np.sort(scores_names))
    # remove special names
    scores_names = [name for name in scores_names if name != 'finished']
    return scores_names

# Cell
def get_monitored_training_metrics (experiment, run_number=0, history_file_name='model_history.pk',
                                    path_results=None, root_path=None, root_folder=None):
    if path_results is None:
        from ..config.hpconfig import get_path_results
        path_results = get_path_results(experiment, run_number, root_path=root_path, root_folder=root_folder)
    path_history = f'{path_results}/{history_file_name}'
    if os.path.exists(path_history):
        history=pickle.load(open(path_history,'rb'))
        return list(history.keys())
    else:
        return []

# Cell
def get_classes_with_results (experiment_data = None, suffix_results = '', class_ids = None):
    """
    Gets the list of class_ids for whom there are results in experiment_data.
    """
    assert experiment_data is not None, 'experiment_data must be introduced'
    result_columns = get_scores_columns (experiment_data, suffix_results=suffix_results, class_ids=class_ids)
    completed_results = ~experiment_data.loc[:,result_columns].isnull()
    completed_results = completed_results.all(axis=0)
    completed_results = completed_results.iloc[np.where(completed_results)]
    completed_results = completed_results.index

    return [int(x[:-len(suffix_results)]) for x in completed_results]

# Cell
def get_parameters_unique(df):
    parameters = []
    for k in df.columns:
        if len(df[k].unique()) > 1:
            parameters += [k]
    return parameters, df[parameters]

# Cell
def compact_parameters (df, number_characters=1):
    par_or = df.columns
    par_new = [''.join(y[0].upper()+y[1:number_characters] for y in x.split('_')) for x in par_or]
    dict_rename = {k:v for k,v in zip(par_or, par_new)}
    df = df.rename (columns = dict_rename)

    return df, dict_rename

# Cell
def replace_with_default_values (df, parameters={}):
    from ..config.hpconfig import get_default_parameters

    parameters_names = get_parameters_columns (df)

    for k in df.columns:
        experiments_idx=np.argwhere(df[k].isna().ravel()).ravel()
        experiments=df.index[experiments_idx]
        for experiment in experiments:
            parameters = df.loc[experiment, parameters_names].copy()
            parameters[parameters.isna().values] = None
            parameters = parameters.to_dict()
            parameters = {k:parameters[k] for k in parameters if parameters[k] is not None}
            defaults = get_default_parameters(parameters)
            df.loc[experiment, k] = defaults.get(k)
    return df

# Cell
def remove_defaults (parameters):
    from ..config.hpconfig import get_default_parameters

    defaults = get_default_parameters(parameters)
    for key in defaults.keys():
        if key in parameters.keys() and (parameters[key] == defaults[key]):
            del parameters[key]
    return parameters

# Cell
def find_rows_with_parameters_dict (experiment_data, parameters_dict, create_if_not_exists=True,
                                    exact_match=True, ignore_keys=[], precision = 1e-10):
    """ Finds rows that match parameters. If the dataframe doesn't have any parameter with that name, a new column is created and changed_dataframe is set to True."""
    changed_dataframe = False
    matching_all_condition = pd.Series([True]*experiment_data.shape[0])
    existing_keys = [par for par in parameters_dict.keys() if par not in ignore_keys]
    for parameter in existing_keys:
        if parameter not in experiment_data.columns:
            if create_if_not_exists:
                experiment_data[parameter] = None
                changed_dataframe = True
            else:
                raise ValueError ('parameter %s not found in experiment_data' %parameter)
        if parameters_dict[parameter] is None:
            matching_condition = experiment_data[parameter].isnull()
        elif experiment_data[parameter].isnull().all():
            matching_condition = ~experiment_data[parameter].isnull()
        elif (type(parameters_dict[parameter]) == float) or (type(parameters_dict[parameter]) == np.float32) or (type(parameters_dict[parameter]) == np.float64):
            if parameters_dict[parameter] == np.floor(parameters_dict[parameter]):
                matching_condition = experiment_data[parameter]==parameters_dict[parameter]
            else:
                matching_condition = experiment_data[parameter]==parameters_dict[parameter]
                for idx, v in enumerate(experiment_data[parameter]):
                    if (type(v) == float or type(v) == np.float32 or type(v) == np.float64) and (np.abs(v-parameters_dict[parameter]) < precision):
                        matching_condition.iloc[idx]=True
                    else:
                        matching_condition.iloc[idx]=False
        else:
            matching_condition = experiment_data[parameter]==parameters_dict[parameter]

        matching_all_condition = matching_all_condition & matching_condition.values

    # We assume that all the columns correspond to parameters, except for those that start with a digit (corresponding to the class evaluated) and those that start with time (giving an estimation of the computational cost)
    if exact_match:
        rest_parameters = get_parameters_columns (experiment_data)
        rest_parameters = [par for par in rest_parameters if par not in parameters_dict.keys()]
        rest_parameters = [par for par in rest_parameters if par not in ignore_keys]
        for parameter in rest_parameters:
            matching_condition = experiment_data[parameter].isnull()
            matching_all_condition = matching_all_condition & matching_condition.values

    matching_rows = matching_all_condition.index[matching_all_condition].tolist()

    return matching_rows, changed_dataframe, matching_all_condition

# Cell
def summarize_results(path_experiments = None,
                      folder_experiments = None,
                      intersection = False,
                      experiments = None,
                      suffix_results='',
                      min_results=0,
                      class_ids = None,
                      parameters = None,
                      output='all',
                      data = None,
                      ascending=False,
                      suffix_test_set = None,
                      stats = ['mean','median','rank','min','max','std']):
    """Obtains summary scores for the desired list of experiments. Uses the experiment_data csv for
    that purpose

    Example use:
        - restricting class_ids:
            summarize_results(class_ids= [1058,1059],suffix_results='_m3');

        - with a predetermined list of class_ids:
            summarize_results(class_ids='qualified',suffix_results='_m3',min_results=96);
    """


    if data is None:
        experiment_data = get_experiment_data (path_experiments=path_experiments, folder_experiments=folder_experiments)
        experiment_data_original = experiment_data.copy()
        if experiments is not None:
            experiment_data = experiment_data.loc[experiments,:]
        if parameters is not None:
            experiment_rows, _, _ = find_rows_with_parameters_dict (experiment_data, parameters, create_if_not_exists=False, exact_match=False)
            experiment_data = experiment_data.loc[experiment_rows]
    else:
        experiment_data = data.copy()
        experiment_data_original = experiment_data.copy()

    # Determine the columnns that provide evaluation scores.
    result_columns = get_scores_columns (experiment_data, suffix_results=suffix_results, class_ids=class_ids)

    experiment_data.loc[:,'num_results'] = np.sum(~experiment_data.loc[:,result_columns].isnull(),axis=1)
    if min_results > 0:
        number_before = experiment_data.shape[0]
        experiment_data = experiment_data[experiment_data.num_results>=min_results]
        print (f'{experiment_data.shape[0]} out of {number_before} experiments have {min_results} runs completed')

    # Take only those class_ids where all experiments provide some score
    if intersection:
        number_before = len(result_columns)
        all_have_results = ~experiment_data.loc[:,result_columns].isnull().any(axis=0)
        result_columns = (np.array(result_columns)[all_have_results]).tolist()
        print (f'{len(result_columns)} out of {number_before} runs for whom all the selected experiments have completed')

    print (f'total data examined: {experiment_data.shape[0]} experiments with at least {experiment_data["num_results"].min()} runs done for each one')

    scores = -experiment_data.loc[:,result_columns].values
    rank = np.argsort(scores,axis=0)
    rank = np.argsort(rank,axis=0).astype(np.float32)
    rank[experiment_data.loc[:,result_columns].isnull()]=np.nan

    parameters = get_parameters_columns(experiment_data, True)
    experiment_data.loc[:,'mean'] = experiment_data.loc[:,result_columns].mean(axis=1)
    experiment_data.loc[:,'min'] = experiment_data.loc[:,result_columns].min(axis=1)
    experiment_data.loc[:,'max'] = experiment_data.loc[:,result_columns].max(axis=1)
    experiment_data.loc[:,'std'] = experiment_data.loc[:,result_columns].std(axis=1)
    experiment_data.loc[:,'median'] = experiment_data.loc[:,result_columns].median(axis=1)
    experiment_data.loc[:,'rank'] = np.nanmean(rank,axis=1)
    experiment_data.loc[:,'good'] = (experiment_data.loc[:,result_columns]>=0.1666666).sum(axis=1)

    scores_to_return = dict(mean=['mean'], median=['median'], rank=['rank'], good=['good'])
    if suffix_test_set is not None:
        def add_score_to_return (suffix_test_set_i):
            result_columns_test_set = get_scores_columns (experiment_data, suffix_results=suffix_test_set_i, class_ids=class_ids)
            experiment_data.loc[:,'mean%s' %suffix_test_set_i] = experiment_data.loc[:,result_columns_test_set].mean(axis=1)
            experiment_data.loc[:,'median%s' %suffix_test_set_i] = experiment_data.loc[:,result_columns_test_set].median(axis=1)
            scores_test_set = -experiment_data.loc[:,result_columns_test_set].values
            rank_test_set = np.argsort(scores_test_set,axis=0)
            rank_test_set = np.argsort(rank_test_set,axis=0).astype(np.float32)
            rank_test_set[experiment_data.loc[:,result_columns].isnull()]=np.nan
            experiment_data.loc[:,'rank%s' %suffix_test_set_i] = np.nanmean(rank_test_set,axis=1)
            experiment_data.loc[:,'good%s' %suffix_test_set_i] = (experiment_data.loc[:,result_columns_test_set]>=0.1666666).sum(axis=1)
            for k in scores_to_return.keys():
                scores_to_return[k] += ['%s%s' %(k, suffix_test_set_i)]
        if type(suffix_test_set) == str:
            suffix_test_set = [suffix_test_set]
        for suffix_test_set_i in suffix_test_set:
            add_score_to_return(suffix_test_set_i)

    if output == 'all':
        summary = dict (mean = experiment_data.loc[:,parameters+scores_to_return['mean']].sort_values(by='mean',ascending=ascending),
                        median = experiment_data.loc[:,parameters+scores_to_return['median']].sort_values(by='median',ascending=ascending),
                        rank = experiment_data.loc[:,parameters+scores_to_return['rank']].sort_values(by='rank'),
                        good = experiment_data.loc[:,parameters+scores_to_return['good']].sort_values(by='good',ascending=False),
                        stats = experiment_data.loc[:,parameters+stats].sort_values(by='mean',ascending=ascending),
                        unordered = experiment_data.loc[:,parameters],
                        allcols = experiment_data,
                        original = experiment_data_original
                        )
    elif output == 'stats':
        summary = experiment_data.loc[:,parameters+['mean','median','rank']]
    elif output == 'unordered':
        summary = experiment_data.loc[:,parameters]
    elif output == 'allcols':
        summary = experiment_data
    elif output == 'original':
        summary = experiment_data_original
    else:
        summary = experiment_data.loc[:,parameters+[output]].sort_values(by=output, ascending=output=='rank')


    return summary

# Cell
def query (path_experiments = None,
              folder_experiments = None,
              intersection = False,
              experiments = None,
              suffix_results='',
              min_results=0,
              classes = None,
              parameters_fixed = {},
              parameters_variable = {},
              parameters_all = [],
              exact_match = True,
              output='all',
              ascending=False,
              suffix_test_set = None,
              stats = ['mean','median','rank','min','max','std'],
              query_other_parameters=False):

    if path_experiments is None:
        from ..config.hpconfig import get_path_experiments
        path_experiments = get_path_experiments()

    path_pickle = None
    if query_other_parameters:
        path_csv = '%s/other_parameters.csv' %path_experiments
    else:
        path_pickle = '%s/experiments_data.pk' %path_experiments
        if not os.path.exists(path_pickle):
            path_pickle = None
            path_csv = '%s/experiments_data.csv' %path_experiments
    if path_pickle is not None:
        experiment_data = pd.read_pickle(path_pickle)
    else:
        experiment_data = pd.read_csv(path_csv, index_col=0)

    non_valid_pars = set(parameters_fixed.keys()).difference(set(experiment_data.columns))
    if len(non_valid_pars) > 0:
        print (f'\n**The following query parameters are not valid: {list(non_valid_pars)}**')
        print (f'\nValid parameters:\n{sorted(get_parameters_columns(experiment_data))}\n')

    parameters_multiple_values_all = list(ParameterGrid(parameters_variable))
    experiment_numbers = []
    for (i, parameters_multiple_values) in enumerate(parameters_multiple_values_all):
        parameters = parameters_multiple_values.copy()
        parameters.update(parameters_fixed)
        parameters_none = {k:v for k,v in parameters.items() if v is None}
        parameters_not_none = {k:v for k,v in parameters.items() if v is not None}

        parameters = remove_defaults (parameters_not_none)
        parameters.update(parameters_none)

        experiment_numbers_i, _, _ = find_rows_with_parameters_dict (experiment_data, parameters, ignore_keys=parameters_all, exact_match = exact_match)
        experiment_numbers += experiment_numbers_i

    experiment_data = experiment_data.iloc[experiment_numbers]

    if experiments is not None:
        experiment_data = experiment_data.loc[experiments]

    if query_other_parameters:
        return experiment_data

    d=summarize_results(path_experiments=path_experiments,
                      folder_experiments=folder_experiments,
                      intersection=intersection,
                      experiments=experiments,
                      suffix_results=suffix_results,
                      min_results=min_results,
                      class_ids=classes,
                      parameters=None,
                      output='all',
                      data=experiment_data,
                      ascending=ascending,
                      suffix_test_set=suffix_test_set,
                      stats=stats)

    return d['mean'], d

# Cell
def summary (df, experiments = None, score=None, compact=True):
    if experiments is not None:
        df = df.loc[experiments]
    if compact:
        _, df = get_parameters_unique(df)
    parameters_columns = get_parameters_columns(df, True)
    scores_columns = get_scores_columns (df, suffix_results=score)
    df = df[parameters_columns + scores_columns]
    df.columns=[c.split('_')[0] for c in df.columns]
    return df