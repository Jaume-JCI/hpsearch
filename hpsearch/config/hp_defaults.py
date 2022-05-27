# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/config/hp_defaults.ipynb (unless otherwise specified).

__all__ = ['allow_base_class', 'name_epoch', 'name_last_epoch', 'name_model_history', 'model_file_name',
           'path_experiments', 'defaults', 'folder', 'metric', 'op', 'result_file', 'min_iterations',
           'use_previous_best', 'name_logger', 'manager_path', 'verbose', 'parameters_col', 'scores_col',
           'run_info_col', 'stats_col', 'num_results_col', 'name_logger_factory']

# Cell
allow_base_class=False
name_epoch='epochs'
name_last_epoch='last_epoch'
name_model_history='model_history.pk'
model_file_name='model.h5'
path_experiments='results/hpsearch'
defaults={}
folder=None
metric='accuracy'
op='max'
result_file='dict_results.pk'
min_iterations=50
use_previous_best=True
name_logger='experiment_manager'
manager_path='em_obj'
verbose=0
parameters_col='parameters'
scores_col='scores'
run_info_col='run_info'

# Cell
stats_col='stats'
num_results_col='overall'

# Cell
name_logger_factory = 'manager_factory'