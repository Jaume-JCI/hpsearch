# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/copy_experiment.ipynb (unless otherwise specified).

__all__ = ['copy_experiment_contents', 'copy_code', 'main', 'copy_experiment_contents_and_code',
           'copy_code_with_experiment_paths', 'parse_args', 'parse_arguments_and_run', 'main']

# Cell
import argparse
import sys
import inspect
import shutil
import joblib
import os
import re
from distutils.dir_util import copy_tree

from dsblocks.utils.utils import check_last_part

from ..experiment_manager import print_parameters
from ..config.hpconfig import get_experiment_manager
from .query import query
import hpsearch.config.hp_defaults as dflt

# Cell
def copy_experiment_contents (experiment=None, folder=None, destination_folder='.',
                              run=0, desired=None, target_model=None,
                              destination_model=None, manager_path=dflt.manager_path):

    os.makedirs (destination_folder, exist_ok=True)

    em = get_experiment_manager (manager_path=manager_path)

    # 3 write code about calling run_experiment
    path_experiments = em.path_experiments
    path_experiment = em.get_path_experiment (experiment)
    shutil.copy (f'{path_experiment}/parameters.pk',
                 f'{destination_folder}/separate_parameters.pk')
    path_results = em.get_path_results (experiment, run)
    if desired is not None and 'path_results' in desired:
        check_last_part (path_results, desired['path_results'])
    copy_tree (f'{path_results}', destination_folder)
    target_model = (target_model if target_model is not None
                    else em.target_model_file)
    destination_model = (destination_model if destination_model is not None
                    else em.destination_model_file)
    if target_model is not None and destination_model is not None:
        shutil.copy (f'{path_results}/{target_model}',
                     f'{destination_folder}/{destination_model}')

# Cell
def copy_code (source_folder, destination_folder, file=None,
               path_experiment=None, manager_path=dflt.manager_path):

    os.makedirs (destination_folder, exist_ok=True)
    destination_path = (f'{destination_folder}/best_experiment.py' if file is None
                        else f'{destination_folder}/{file}')
    path_experiment = (source_folder if path_experiment is None
                            else path_experiment)
    path_results = source_folder
    fdest = open (destination_path, 'wt')

    # 1 write code before definition of subclassed manager
    em = get_experiment_manager (manager_path=manager_path)
    source_path = inspect.getfile(em.__class__)
    fsrc = open (source_path, 'rt')
    original = fsrc.read ()
    fsrc.close ()
    original.replace ('from hpsearch.experiment_manager import ExperimentManager', '')

    # 2 write code from base manager
    try:
        r = re.findall (f'class\s+{em.__class__.__name__}\s*\(.*\)', original)
        assert len(r) == 1, 'class not found'
        name_base_class = re.findall ('\(.*\)', r[0])[0][1:-1]
    except Exception as e:
        print (f'{e}')
        name_base_class = 'ExperimentManager'

    base_manager = f'class {name_base_class} ():'
    base_manager = base_manager + '''
    def __init__ (self, *args, **kwargs):
        pass
'''
    r= re.findall (f'class\s+{em.__class__.__name__}', original)
    assert len(r) == 1, 'class not found'
    r = original.find (r[0])
    original = (original[:r-1] + base_manager + '\n' + original[r:])
    fdest.write (original)

    # 3 write code about calling run_experiment
    try:
        parameters, other_parameters, *_ = joblib.load (f'{path_experiment}/separate_parameters.pk')
    except FileNotFoundError:
        parameters, other_parameters, *_ = joblib.load (f'{path_experiment}/parameters.pk')
    parameters = print_parameters(parameters, dict_name='    parameters')

    path_results_str = '{path_results}'
    run_experiment = (
f'''
def main (**kwargs):
    path_results = {path_results}
    all_parameters = joblib.load (f'{path_results_str}/parameters.pk')
{parameters}
    all_parameters.update (parameters)
    all_parameters.update (**kwargs)
    em = {em.__class__.__name__} ()
    em.run_experiment (all_parameters, path_results)

if __name__ == '__main__':
    main ()
'''
    )
    fdest.write (run_experiment)
    fdest.close ()

# Cell
def copy_experiment_contents_and_code (experiment=None, folder=None,
                                       content='.',
                                       code='.',
                                       run=0,
                                       file=None,
                                       target_model=None,
                                       destination_model=None,
                                       desired=None,
                                       manager_path=dflt.manager_path):
    copy_experiment_contents (experiment=experiment, folder=folder,
                              destination_folder=content,
                              run=run, target_model=target_model,
                              destination_model=destination_model,
                              desired=desired, manager_path=manager_path)
    copy_code (content, code, file=file,
               path_experiment=content,
               manager_path=manager_path)

# Cell
def copy_code_with_experiment_paths (experiment=None, folder=None,
                                     destination_folder='.', file=None,
                                     run=0, desired=None, manager_path=dflt.manager_path):
    em = get_experiment_manager (manager_path=manager_path)
    path_experiments = em.path_experiments
    path_experiment = em.get_path_experiment (experiment)
    path_results = em.get_path_results (experiment, run)
    copy_code (path_results, destination_folder, file=file,
               path_experiment=path_experiment,
               manager_path=manager_path)



# Cell
def parse_args (args):
    parser = argparse.ArgumentParser(description='copy experiment')
    parser.add_argument('-e', '--experiment', type=int, default=None,
                        help="experiment number")
    parser.add_argument('--run', type=int, default=None,  help="run number")
    parser.add_argument('--folder', type=str, default=None, help='name of experiments folder')
    parser.add_argument('--content', type=str,
                        default='.', help='path to folder containing experiment results')
    parser.add_argument('--code', type=str,
                        default='.', help='path to folder containing experiment results')
    parser.add_argument('--file', type=str, default=None, help='destination code file')
    parser.add_argument('--target_model', type=str, default=None,
                        help='target model file')
    parser.add_argument('--destination_model', type=str, default=None,
                        help='destination model file')
    parser.add_argument('-p', '--path', default=dflt.manager_path, type=str)

    pars = parser.parse_args(args)

    return pars

def parse_arguments_and_run (args, desired = None):

    pars = parse_args(args)
    pars = vars(pars)
    pars['manager_path'] = pars['path']
    del pars['path']
    copy_experiment_contents_and_code (**pars, desired=desired)

def main():
    parse_arguments_and_run (sys.argv[1:])