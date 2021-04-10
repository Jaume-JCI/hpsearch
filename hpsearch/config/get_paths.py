try:
    from hpconfig.get_paths import get_path_experiments
except ImportError:
    from hpsearch.config._get_paths import get_path_experiments

try:
    from hpconfig.get_paths import get_path_alternative
except ImportError:
    from hpsearch.config._get_paths import get_path_alternative
    
try:
    from hpconfig.get_paths import get_path_data
except ImportError:
    from hpsearch.config._get_paths import get_path_data
    
    
def get_path_experiment (experiment_id, root_path=None, root_folder=None):
    if root_path is None:
        root_path = get_path_experiments(folder=root_folder)
    path_experiment = '%s/experiments/%05d' %(root_path,experiment_id)
    return path_experiment

def get_path_results (experiment_id, run_number, root_path=None, root_folder=None):
    path_experiment = get_path_experiment (experiment_id, root_path=root_path, root_folder=root_folder)
    path_results = '%s/%d' %(path_experiment,run_number)
    return path_results

