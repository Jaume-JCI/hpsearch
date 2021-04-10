import pandas as pd
import numpy as np
import pickle
import os
import sys
import time
from sklearn.model_selection import ParameterGrid

# CSP API
from hpsearch.config import get_paths
from hpsearch.config.default_parameters import get_default_parameters


##############################################################
# Routines for comparing results in experiments
##############################################################

def remove_defaults (parameters):
    defaults = get_default_parameters(parameters)
    for key in defaults.keys():
        if key in parameters.keys() and (parameters[key] == defaults[key]):
            del parameters[key]
    return parameters

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
        path_experiments = get_paths.get_path_experiments(path_experiments=path_experiments, folder = folder_experiments)
    
    if query_other_parameters:
        path_csv = '%s/other_parameters.csv' %path_experiments
    else:
        path_csv = '%s/experiments_data.csv' %path_experiments
    experiment_data = pd.read_csv(path_csv, index_col=0)
    
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
  
    d=summarize_results(path_experiments = path_experiments, 
                      folder_experiments = folder_experiments,
                      intersection = intersection, 
                      experiments = experiments, 
                      suffix_results=suffix_results, 
                      min_results=min_results, 
                      class_ids = classes, 
                      parameters = None,
                      output='all',
                      data = experiment_data,
                      ascending=ascending,
                      suffix_test_set = suffix_test_set,
                      stats = stats)
                      
    return d['mean'], d

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
    """Obtains summary scores for the desired list of experiments. Uses the experiment_data csv for that purpose
    
    Example use: 
        - restricting class_ids:
            summarize_results(class_ids= [1058,1059],suffix_results='_m3');
    
        - with a predetermined list of class_ids:
            summarize_results(class_ids='qualified',suffix_results='_m3',min_results=96);
    """
    
    
    if data is None:
        if path_experiments is None:
            path_experiments = get_paths.get_path_experiments(path_experiments=path_experiments, folder = folder_experiments)
        path_csv = '%s/experiments_data.csv' %path_experiments
        path_pickle = path_csv.replace('csv', 'pk')
        if os.path.exists (path_pickle):
            experiment_data = pd.read_pickle (path_pickle)
        else:
            experiment_data = pd.read_csv(path_csv, index_col=0)
        clear_access (path_csv)
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
        print ('%d out of %d experiments have %d class_ids completed' %(experiment_data.shape[0], number_before, min_results))
    
    # Take only those class_ids where all experiments provide some score
    if intersection:
        number_before = len(result_columns)
        all_have_results = ~experiment_data.loc[:,result_columns].isnull().any(axis=0)
        result_columns = (np.array(result_columns)[all_have_results]).tolist()
        print ('%d out of %d class_ids for whom all the selected experiments have completed' %(len(result_columns), number_before))
        
    print ('total data examined: %d experiments with at least %d class_ids each' %(experiment_data.shape[0],experiment_data['num_results'].min()))
        
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
    
def summary (df, experiments = None, score=None, compact=True):
    if experiments is not None:
        df = df.loc[experiments]
    if compact:
        _, df = get_parameters_unique(df)
    parameters_columns = get_parameters_columns(df, True)
    scores_columns = ut.get_scores_columns (df, suffix_results=score)
    df = df.loc[experiments,parameters_columns + scores_columns]
    df = df.rename (columns={'0_%s' %score: score})
    return df
    
def get_parameters_columns (experiment_data, only_not_null=False):
    parameters =  [par for par in experiment_data.columns if not par[0].isdigit() and (par.find('time_')<0) and (par.find('date')<0)]
    if only_not_null:
        parameters = np.array(parameters)[~experiment_data.loc[:,parameters].isnull().all(axis=0)].tolist()
    return parameters

def get_experiment_parameters (experiment_data, only_not_null=False):
    return experiment_data[get_parameters_columns (experiment_data, only_not_null=only_not_null)]
    
def get_scores_columns (experiment_data=None, suffix_results='', class_ids = None):
    ''' Determine the columnns that provide evaluation scores. We assume that they start with the class number, and that the other columns do not start with a digit'''
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
            scores_columns = [col for col in scores_columns if (len(col.split('_'))==1)]
    return scores_columns
    
def get_experiment_scores (experiment_data = None, suffix_results = '', class_ids = None, remove_suffix=False):
    df = experiment_data[get_scores_columns (experiment_data, suffix_results=suffix_results, class_ids=class_ids)]
    if remove_suffix:
        df.columns=[c.split('_')[0] for c in df.columns]
    return df
    
def find_rows_with_parameters_dict (experiment_data, parameters_dict, create_if_not_exists=True, exact_match=True, ignore_keys=[], precision = 1e-10):
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
                        matching_condition[idx]=True
                    else:
                        matching_condition[idx]=False
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

def get_classes_with_results (experiment_data = None, suffix_results = '', class_ids = None):
    '''Gets the list of class_ids for whom there are results in experiment_data.
    
    Example usage with summarize_results:
        import hpsearch.utils.vc_experiment_utils as ut
        d=ut.summarize_results(class_ids='qualified',suffix_results='_auc_roc', min_results=10);
        ch=ut.get_classes_with_results(d['original'].loc[d['mean'].index],suffix_results='_auc_roc');
    '''
    result_columns = get_scores_columns (experiment_data, suffix_results=suffix_results, class_ids=class_ids)
    completed_results = ~experiment_data.loc[:,result_columns].isnull()
    completed_results = completed_results.all(axis=0)
    completed_results = completed_results.iloc[np.where(completed_results)]
    completed_results = completed_results.index

    return [int(x[:-len(suffix_results)]) for x in completed_results]

def get_parameters_unique(df):
    parameters = []
    for k in df.columns:
        if len(df[k].unique()) > 1:
            parameters += [k]
    return parameters, df[parameters]

def compact_parameters (df, number_characters=1):
    par_or = df.columns
    par_new = [''.join(y[0].upper()+y[1:number_characters] for y in x.split('_')) for x in par_or]
    dict_rename = {k:v for k,v in zip(par_or, par_new)}
    df = df.rename (columns = dict_rename)
    
    return df, dict_rename

def replace_with_default_values (df, parameters={}):
    defaults = get_default_parameters(parameters=parameters)
    for k in df.columns:
        df.loc[df[k].isna(), k] = defaults.get(k)
    return df