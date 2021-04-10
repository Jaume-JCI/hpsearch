import platform


def get_path_experiments (path_experiments = None, folder = None):
    """Gives the root path to the folder where results of experiments are stored."""
    path_experiments_windows= 'data/hpsearch'
    path_experiments_linux = path_experiments_windows
    
    if platform.system() == 'Windows':
        path_experiments = path_experiments_windows
    else:
        path_experiments = path_experiments_linux
        
    if folder != None:
        path_experiments = '%s/%s' %(path_experiments, folder)
        
    return path_experiments
    

def get_path_alternative (path_results):
    root1 = 'data/hpsearch'
    #root1 = '/mnt/datascience-vol'
    root2 = '/mnt/datascience-vol'
    path_alternative = path_results.replace(root1, root2)
    
    return path_alternative