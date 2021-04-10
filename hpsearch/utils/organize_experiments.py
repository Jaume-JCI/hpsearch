import pandas as pd
import numpy as np

from hpsearch.config.default_parameters import get_default_parameters

from hpsearch.utils import experiment_utils

def join_experiments (path_source, path_destination, key_score=None):
    experiment_data_source = pd.read_pickle ('%s/experiments_data.pk' %path_source)
    experiment_data_destination = pd.read_pickle ('%s/experiments_data.pk' %path_destination)
    experiment_data_source, changed_source = remove_defaults_from_experiment_data (experiment_data_source)
    experiment_data_destination, changed_destination = remove_defaults_from_experiment_data (experiment_data_destination)
    
    for experiment_number_source in range(experiment_data_source.shape[0]):
        path_experiment_source = '%s/experiments/%05d' %(path_source, experiment_number_source)
        parameters_source, _ = pickle.load(open('%s/parameters.pk' %path_experiment_source,'rb'))
        experiment_number_destination, changed_dataframe, _ = experiment_utils.find_rows_with_parameters_dict (experiment_data_destination, parameters_source)
        path_experiment_destination = '%s/experiments/%05d' %(path_destination, experiment_number_destination)
        if changed_dataframe:
            # move folders
            os.rename (path_experiment_source, path_experiment_destination)
            # copy results to dataframe
            missing_cols = [col for col in experiment_data_source.columns if col not in experiment_data_destination.columns]
            for column in missing_cols:
                experiment_data_destination[column] = None
            experiment_data_destination.loc[experiment_number_destination] = experiment_data_source.loc[experiment_number_source]
        else:
            class_ids_source = [int(x) for x in os.listdir(path_experiment_source) if os.path.isdir('%s/%s' %(path_experiment_source, x))]
            class_ids_destination = [int(x) for x in os.listdir(path_experiment_destination) if os.path.isdir('%s/%s' %(path_experiment_destination, x))]
            last_id_destination = max(class_ids_destination)
            
            class_ids_both = [x for x in class_ids_source if x in class_ids_destination]
            class_ids_source = [x for x in class_ids_source if x not in class_ids_both]
            class_ids_destination = [x for x in class_ids_destination if x not in class_ids_both]
            for (idx, class_id_source) in enumerate(class_ids_both):
                if key_score is not None:
                    scores_name = '%d_%s' %(class_id_source, key_score)
                    if experiment_data_source.loc[experiment_number_source, scores_name] != experiment_data_destination.loc[experiment_number_destination, scores_name]:
                        is_new = True
                else:
                    is_new = False
                    scores_name_source = [x for x in experiment_data_source.columns if x.startswith('%d_' %class_id_source)]
                    scores_name_source = [x for x in scores_name_source if not np.isnan(experiment_data_source.loc[experiment_number_source, x])]
                    for scores_name in scores_name_source:
                        if experiment_data_source.loc[experiment_number_source, scores_name] != experiment_data_destination.loc[experiment_number_destination, scores_name]:
                            is_new = True
                            break
                if not is_new:
                    del class_ids_both[idx]
            class_ids_source += class_ids_both
            class_ids_destination += class_ids_both
                
            last_id_source = len(class_ids_source)
            new_ids_destination = range(last_id_destination+1, last_id_destination+last_id_source)
            for (new_id_destination, class_id_source) in zip(new_ids_destination, class_ids_source):
                # move folders
                os.rename ('%s/%d' %(path_experiment_source, class_id_source), '%s/%d' %(path_experiment_destination, new_id_destination))
                # copy results to dataframe
                scores_name_source = [x for x in experiment_data_source.columns if x.startswith('%d_' %class_id_source)]
                scores_name_destination = ['%d_%s' (new_id_destination, x[len('%d_' %class_id_source):]) for x in scores_name_source]
                for score_name_source, score_name_destination in zip(scores_name_source, scores_name_destination):
                    experiment_data_destination.loc[experiment_number_destination, score_name_destination] = experiment_data_source.loc[experiment_number_source, score_name_source]
        
        experiment_data_destination.to_csv ('%s/experiments_data.csv' %path_destination)
        experiment_data_destination.to_pickle ('%s/experiments_data.pk' %path_destination)
        
def remove_defaults_from_experiment_data (experiment_data):
    experiment_data_original = experiment_data.copy()
    parameters_names = experiment_utils.get_parameters_columns (experiment_data)
    parameters_data = experiment_data_original[parameters_names]
    changed_df = False
    for experiment_number in range(experiment_data.shape[0]):
        good_params = ~(experiment_data.loc[experiment_number, parameters_names].isna()).values
        parameters_names_i = np.array(parameters_names)[good_params]
        parameters_names_i = parameters_names_i.tolist()
        parameters = experiment_data.loc[experiment_number, parameters_names_i].to_dict()

        defaults = get_default_parameters(parameters)
        default_names = [default_name for default_name in defaults.keys() if default_name in parameters_names_i]
        
        for default_name in default_names:
            has_default = experiment_data.loc[experiment_number, default_name] == defaults[default_name]
            if has_default:
                print ('found experiment with default in experiment_number {}, parameter {}, values: {}'.format(experiment_number, default_name, experiment_data.loc[experiment_number, default_name]))
                changed_df = True
                experiment_data.loc[experiment_number, default_name] = None
    
    # check if there are repeated experiments
    if changed_df:
        if experiment_data[parameters_names].duplicated().any():
            print ('duplicated experiments: {}'.format(experiment_data[parameters_names].duplicated()))
            experiment_data = experiment_data_original
            changed_df = False
        
    return experiment_data, changed_df
