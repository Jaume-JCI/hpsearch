import pickle
import os
import numpy as np

def make_resume_from_checkpoint (parameters, prev_path_results, use_best=False):

    model_extension = parameters.get('model_extension', 'h5')
    model_name = parameters.get('model_name', 'checkpoint_')
    epoch_offset = parameters.get('epoch_offset', 0)
    name_best_model = parameters.get('name_best_model', 'best_model')

    found = False
    if os.path.exists('%s/model_history.pk' %prev_path_results):
        parameters['resume_summary'] = '%s/model_history.pk' %prev_path_results
        found = True
        if use_best:
            parameters['resume'] = '%s/%s.%s' %(prev_path_results, name_best_model, model_extension)
        else:
            summary = pickle.load(open('%s/model_history.pk' %prev_path_results, 'rb'))
            prev_epoch = summary.get('last_epoch',-1)
            if prev_epoch >= 0:
                parameters['resume'] = '%s/%s%d.%s' %(prev_path_results, model_name, prev_epoch+epoch_offset, model_extension)
        if not os.path.exists(parameters['resume']):
            parameters['resume'] = ''
            found = False 

    return found
    
def exists_current_checkpoint (parameters, path_results):

    model_extension = parameters.get('model_extension', 'h5')

    return os.path.exists('%s/best_model.%s' %(path_results, model_extension))
        
def finished_all_epochs (parameters, path_results, name_epoch='max_epoch'):
    from hpsearch.config.default_parameters import get_default_parameters
    
    finished = True
    defaults = get_default_parameters(parameters)
    current_epoch = parameters.get(name_epoch, defaults.get(name_epoch))
    
    if os.path.exists('%s/model_history.pk' %path_results):
        summary = pickle.load(open('%s/model_history.pk' %path_results, 'rb'))
        prev_epoch = summary.get('last_epoch',-1)
        if (prev_epoch+1) >= current_epoch:
            finished = True
        else:
            finished = False
    else:
        finished = False

    return finished
    
def obtain_last_result (parameters, path_results):
    
    if parameters.get('use_last_result_from_dict', False):
        return obtain_last_result_from_dict (parameters, path_results)
    name_result_file = parameters.get('result_file', 'model_history.pk')
    path_results_file = '%s/%s' %(path_results, name_result_file)
    dict_results = None
    if os.path.exists (path_results_file):
        history = pickle.load(open(path_results_file, 'rb'))
        metrics = parameters.get('key_scores')
        if metrics is None:
            metrics = history.keys()
        ops = parameters.get('ops')
        if ops is None:
            ops = ['max'] * len(metrics)
        if type(ops) is str:
            ops = [ops] * len(metrics)
        if type(ops) is dict:
            ops_dict = ops
            ops = ['max'] * len(metrics)
            i = 0
            for k in metrics:
                if k in ops_dict.keys():
                    ops[i] = ops_dict[k]
                i += 1
        dict_results = {}
        max_last_position = -1
        for metric, op in zip(metrics, ops):
            if metric in history.keys():
                history_array = history[metric]
                score = min(history_array) if op == 'min' else max(history_array)
                last_position = np.where(np.array(history_array).ravel()==0)[0]
                if len(last_position) > 0:
                    last_position = last_position[0] - 1
                else:
                    last_position = len(history_array)
                dict_results[metric] = score
            else:
                last_position = -1
            max_last_position = max(last_position, max_last_position)
        
        dict_results['last'] = max_last_position
        if max_last_position < parameters.get('min_iterations', 50):
            dict_results = None
            print ('not storing result from {} with iterations {}'.format(path_results, max_last_position))
        else:
            print ('storing result from {} with iterations {}'.format(path_results, max_last_position))
        
    return dict_results
        
def obtain_last_result_from_dict (parameters, path_results):
    name_result_file = parameters.get('result_file', 'dict_results.pk')
    path_results_file = '%s/%s' %(path_results, name_result_file)
    dict_results = None
    if os.path.exists (path_results_file):
        dict_results = pickle.load(open(path_results_file, 'rb'))
        if 'last' not in dict_results.keys() and 'epoch' in dict_results.keys():
            dict_results['last'] = dict_results['epoch']
        max_last_position = dict_results['last']
        if max_last_position < parameters.get('min_iterations', 50):
            dict_results = None
            print ('not storing result from {} with iterations {}'.format(path_results, max_last_position))
        else:
            print ('storing result from {} with iterations {}'.format(path_results, max_last_position))
    
    return dict_results