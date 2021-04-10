# coding: utf-8
import pickle
import sys
import os
import numpy as np
import pandas as pd
import time
import datetime
from sklearn.model_selection import ParameterGrid
from sklearn.datasets.base import Bunch
import platform
import pprint
import subprocess
import json
from multiprocessing import Process
import logging
import traceback
import shutil

# hpsearch config
from hpsearch.config.default_parameters import get_default_parameters
from hpsearch.config import get_paths

# hpsearch core API
from hpsearch.utils.resume_from_checkpoint import make_resume_from_checkpoint, exists_current_checkpoint, finished_all_epochs, obtain_last_result
from hpsearch.utils import experiment_utils
from hpsearch.utils.experiment_utils import remove_defaults
from hpsearch.utils.organize_experiments import remove_defaults_from_experiment_data


class ExperimentManager (object):

    def __init__ (self):
        self.parameters_non_pickable = {}

    def run_experiment_pipeline (self, run_number=0, path_results='./results', parameters = {}):
        """ Runs complete learning pipeline: loading / generating data, building and learning model, applying it to data, and evaluating it."""
        start_time = time.time()
        
        # record all parameters except for non-pickable ones
        record_parameters (path_results, parameters)
        
        # integrate non-pickable parameters into global dictionary
        parameters.update (self.parameters_non_pickable)
        self.parameters_non_pickable = {}
        
        logger = logging.getLogger("experiment_manager")
        
        # #####################################
        # Evaluation
        # #####################################
        if not parameters.get('just_visualize', False):
            time_before = time.time()
            score_dict = self._run_experiment (parameters=parameters, path_results=path_results, run_number=run_number)
            logger.info ('time spent for evaluation: {}'.format(time.time()-time_before))
        else:
            score_dict = None
            
        # #####################################
        # Visualization
        # #####################################
        if parameters.get('visualization', False):
            raise ValueError ('not implemented')
            
        # #####################################
        # Final scores
        # #####################################        
        score_name = parameters.get('suffix_results','')
        if len(score_name) > 0:
            if score_name[0] == '_':
                score_name = score_name[1:]
            if score_dict.get(score_name) is not None:
                logger.info ('score: %f' %(score_dict.get(score_name)))
        
        spent_time = time.time() - time_before

        return score_dict, spent_time

    # *************************************************************************
    #   run_experiment methods
    # *************************************************************************
    def _run_experiment (self, parameters={}, path_results='./results', run_number=None):

        parameters['run_number'] = run_number
    
        # wrap parameters
        parameters = Bunch(**parameters)
                                                    
        if parameters.get('use_process', False):
            return self.run_experiment_in_separate_process (parameters, path_results)
        else:
            return self.run_experiment (parameters=parameters, path_results=path_results)
            
    def run_experiment_in_separate_process (self, parameters={}, path_results='./results'):
        
        parameters['return_results']=False
        p = Process(target=self.run_experiment_saving_results, args=(parameters, path_results))
        p.start()
        p.join()

        dict_results = pickle.load (open ('%s/dict_results.pk' %path_results, 'rb'))
        
        return dict_results
        
    def run_experiment_saving_results (self, parameters={}, path_results='./results'):
        dict_results = self.run_experiment (parameters=parameters, path_results=path_results)
        pickle.dump (dict_results, open ('%s/dict_results.pk' %path_results, 'wb'))
        
    def run_experiment (self, parameters={}, path_results='./results'):
        raise NotImplementedError ('This method needs to be defined in subclass')
        
        
    # *************************************************************************
    # *************************************************************************
    def create_experiment_and_run (self, parameters = {}, other_parameters = {}, root_path=None, run_number=0, log_message=None):

        # ****************************************************
        #  preliminary set-up: logger and root_path
        # ****************************************************
        logger = logging.getLogger("experiment_manager")
        if log_message is not None:
            logger.info ('**************************************************')
            logger.info (log_message)
            logger.info ('**************************************************')
            other_parameters['log_message'] = log_message
    
        # insert path to experiment script file that called the experiment manager
        other_parameters = other_parameters.copy()
        insert_experiment_script_path (other_parameters, logger)

        # get root_path and create directories
        if root_path is None:
            root_path = get_paths.get_path_experiments(folder = other_parameters.get('root_folder'))
        os.makedirs (root_path, exist_ok = True)
            
        # ****************************************************
        #   get experiment number given parameters
        # ****************************************************
        parameters = remove_defaults (parameters)
        
        path_csv = '%s/experiments_data.csv' %root_path
        path_pickle = path_csv.replace('csv', 'pk')
        experiment_number, experiment_data = load_or_create_experiment_values (path_csv, parameters)
        
        #save_other_parameters (experiment_number, other_parameters, root_path)

        # if old experiment, we can require that given parameters match with experiment number
        if other_parameters.get('experiment_number') is not None and experiment_number != other_parameters.get('experiment_number'):
            raise ValueError ('expected number: {}, found: {}'.format (other_parameters.get('experiment_number'), experiment_number))
        other_parameters['experiment_number'] = experiment_number
        
        # ****************************************************
        # get key_score and suffix_results
        # ****************************************************
        if other_parameters.get('key_score') is not None:
            other_parameters['suffix_results'] = '_' + other_parameters['key_score']
        suffix_results = other_parameters.get('suffix_results', '')
        if len(suffix_results) > 0 and suffix_results[0] == '_':
            key_score = suffix_results[1:]
        else:
            key_score = suffix_results
        
        # ****************************************************
        #   get run_id, if not given
        # ****************************************************
        if run_number is None:
            run_number = 0
            name_score = '%d%s' %(run_number, suffix_results)
            while not isnull(experiment_data, experiment_number, name_score):
                logger.info ('found previous run for experiment number {}, run {}, with score {} = {}'.format(experiment_number, run_number, key_score, experiment_data.loc[experiment_number, name_score]))
                run_number += 1
                name_score = '%d%s' %(run_number, suffix_results)
            logger.info ('starting experiment {} with run number {}'.format(experiment_number, run_number))
            
        else:
            name_score = '%d%s' %(run_number, suffix_results)
            if not isnull(experiment_data, experiment_number, name_score):
                previous_result = experiment_data.loc[experiment_number, name_score]
                logger.info ('found completed: experiment number: %d, run number: %d - score: %f' %(experiment_number, run_number, previous_result))
                logger.info (parameters)
                if other_parameters.get('repeat_experiment', False):
                    logger.info ('redoing experiment')
            
        # ****************************************************
        #   remove unfinished experiments
        # ****************************************************
        if other_parameters.get('remove_not_finished', False):
            name_finished = '%d_finished' %run_number
            if not isnull(experiment_data, experiment_number, name_finished):
                finished = experiment_data.loc[experiment_number, name_finished]
                logger.info ('experiment {}, run number {}, finished {}'.format(experiment_number, run_number, finished))
                if not finished:
                    experiment_data.loc[experiment_number, name_score] = None
                    experiment_data.to_csv (path_csv)
                    experiment_data.to_pickle (path_pickle)
                    logger.info ('removed experiment {}, run number {}, finished {}'.format(experiment_number, run_number, finished))
            if other_parameters.get('only_remove_not_finished', False):
                return None, {}

        unfinished_flag = False
        
        # ****************************************************
        #   check conditions for skipping experiment
        # ****************************************************
        if not isnull(experiment_data, experiment_number, name_score) and not other_parameters.get('repeat_experiment', False) and not other_parameters.get('just_visualize', False):
            if other_parameters.get('check_finished', False) and not finished_all_epochs(parameters, get_paths.get_path_results (experiment_number, run_number=run_number, root_path=root_path), other_parameters.get('name_epoch','max_epoch')):
                unfinished_flag = True
            else:
                logger.info ('skipping...')
                return previous_result, {key_score: previous_result}
        elif isnull(experiment_data, experiment_number, name_score) and other_parameters.get('recompute_metrics', False) and not other_parameters.get('force_recompute_metrics', False):
            logger.info ('experiment not found, skipping %d due to only recompute_metrics' %run_number)
            return None, {}
        
        # ****************************************************
        # log info
        # ****************************************************
        logger.info ('running experiment %d' %experiment_number)
        logger.info ('run number: %d' %run_number)
        logger.info ('\nparameters:\n%s' %mypprint(parameters))
        
        # ****************************************************
        #  get paths
        # ****************************************************
        # path_root_experiment folder
        path_root_experiment = '%s/experiments/%05d' %(root_path,experiment_number)
        mymakedirs(path_root_experiment, exist_ok=True)
            
        # path_experiment folder (where results are)
        path_experiment = '%s/%d' %(path_root_experiment, run_number)
        mymakedirs(path_experiment, exist_ok=True)
        
        # path to save big files
        path_experiment_big_size = get_paths.get_path_alternative (path_experiment)
        os.makedirs (path_experiment_big_size, exist_ok = True)
        other_parameters['path_results_big'] = path_experiment_big_size
        
        # ****************************************************
        # get git and record parameters
        # ****************************************************
        # get git revision number
        other_parameters['git_hash'] = get_git_revision_hash(root_path)
        
        # write parameters in root experiment folder
        record_parameters (path_root_experiment, parameters, other_parameters)
        
        # store hyper_parameters in dictionary that maps experiment_number with hyper_parameter values
        store_parameters (root_path, experiment_number, parameters)
        
        # ****************************************************************
        # loggers
        # ****************************************************************
        logger_experiment = set_logger ("experiment", path_experiment)
        logger_experiment.info ('script: {}, line number: {}'.format(other_parameters['script_path'], other_parameters['lineno']))
        if os.path.exists(other_parameters['script_path']):
            shutil.copy (other_parameters['script_path'], path_experiment)
            shutil.copy (other_parameters['script_path'], path_root_experiment)
        
        # summary logger
        logger_summary = set_logger ("summary", root_path, mode='w', stdout=False, just_message=True, filename='summary.txt')
        logger_summary.info ('\n\n{}\nexperiment: {}, run: {}\nscript: {}, line number: {}\nparameters:\n{}{}'.format('*'*100, experiment_number, run_number, other_parameters['script_path'], other_parameters['lineno'], mypprint(parameters), '*'*100))
        if other_parameters.get('rerun_script') is not None:
            logger_summary.info ('\nre-run:\n{}'.format(other_parameters['rerun_script']))
        # same file in path_experiments
        logger_summary2 = set_logger ("summary", path_experiment, mode='w', stdout=False, just_message=True, filename='summary.txt')
        logger_summary2.info ('\n\n{}\nexperiment: {}, run: {}\nscript: {}, line number: {}\nparameters:\n{}{}'.format('*'*100, experiment_number, run_number, other_parameters['script_path'], other_parameters['lineno'], mypprint(parameters), '*'*100))
        
        # ****************************************************************
        # Do final adjustments to parameters
        # ****************************************************************
        parameters = parameters.copy()
        parameters.update(other_parameters)
        
        # add default parameters - their values are overwritten by input values, if given
        parameters_with_defaults = get_default_parameters(parameters)
        parameters_with_defaults.update(parameters)
        parameters = parameters_with_defaults
        
        # pick from previous epoch if exists
        resuming_from_prev_epoch_flag = False
        if parameters.get('prev_epoch', False):
            logger.info('trying prev_epoch')
            name_epoch = parameters.get('name_epoch','max_epoch')
            experiment_data2 = experiment_data.copy()
            if ((not unfinished_flag) and (other_parameters.get('repeat_experiment', False) or other_parameters.get('just_visualize', False))) or other_parameters.get('avoid_resuming', False):
                experiment_data2 = experiment_data2.drop(experiment_number,axis=0)
            prev_experiment_number = find_closest_epoch (experiment_data2, parameters, name_epoch=name_epoch)
            if prev_experiment_number is not None:
                logger.info('using prev_epoch: %d' %prev_experiment_number)
                prev_path_results = get_paths.get_path_results (prev_experiment_number, run_number=run_number, root_path=root_path)
                found = make_resume_from_checkpoint (parameters, prev_path_results)
                if found:
                    logger.info ('found previous exp: %d' %prev_experiment_number)
                    if prev_experiment_number == experiment_number:
                        other_parameters['use_previous_best'] = parameters.get('use_previous_best', True)
                        logger.info ('using previous best')

                resuming_from_prev_epoch_flag = found
                
        if not resuming_from_prev_epoch_flag and parameters.get('from_exp', None) is not None:
            prev_experiment_number = parameters.get('from_exp', None)
            logger.info('using previous experiment %d' %prev_experiment_number)
            prev_path_results = get_paths.get_path_results (prev_experiment_number, run_number=run_number, root_path=root_path)
            make_resume_from_checkpoint (parameters, prev_path_results, use_best=True)

        # ****************************************************************
        #   Analyze if experiment was interrupted
        # ****************************************************************
        if parameters.get('skip_interrupted', False):
            was_interrumpted = exists_current_checkpoint (parameters, path_experiment)
            was_interrumpted = was_interrumpted or obtain_last_result (parameters, path_experiment) is not None
            if was_interrumpted:
                logger.info ('found intermediate results, skipping...')
                return None, {}
                
        # ****************************************************************
        # retrieve last results in interrupted experiments
        # ****************************************************************
        run_pipeline = True
        if parameters.get('use_last_result', False):
            experiment_result = obtain_last_result (parameters, path_experiment)
            if experiment_result is None and parameters.get('run_if_not_interrumpted', False):
                run_pipeline = True
            elif experiment_result is None:
                return None, {}
            else:
                run_pipeline = False
        
        # ****************************************************************
        # run experiment
        # ****************************************************************
        if run_pipeline:
            experiment_result, time_spent = self.run_experiment_pipeline (run_number, 
                                        path_experiment, 
                                        parameters=parameters)
            finished = True
        else:
            finished = False
            
        if other_parameters.get('just_visualize', False):
            return None, {}
        # ****************************************************************
        #  Retrieve and store results
        # ****************************************************************
        if type(experiment_result)==dict:
            dict_results = experiment_result
            for key in dict_results.keys():
                if key != '':
                    experiment_data.loc[experiment_number, '%d_%s' %(run_number, key)]=dict_results[key]
                else:
                    experiment_data.loc[experiment_number, '%d' %run_number]=dict_results[key]
                logger.info('{} - {}: {}'.format(run_number, key, dict_results[key]))
        else:
            experiment_data.loc[experiment_number, name_score]=experiment_result
            logger.info('{} - {}: {}'.format(run_number, name_score, experiment_result))
            dict_results = {name_score:experiment_result}
        
        if isnull(experiment_data, experiment_number, 'time_'+str(run_number)) and finished:
            experiment_data.loc[experiment_number,'time_'+str(run_number)]=time_spent
        experiment_data.loc[experiment_number, 'date']=datetime.datetime.time(datetime.datetime.now())
        experiment_data.loc[experiment_number, '%d_finished' %run_number]=finished
        
        experiment_data.to_csv(path_csv)
        experiment_data.to_pickle(path_pickle)
        
        save_other_parameters (experiment_number, other_parameters, root_path)
        
        logger_summary2.info ('\nresults:\n{}'.format(dict_results))
        logger.info ('finished experiment %d' %experiment_number)
        
        # return final score
        result = dict_results.get(name_score)
        return result, dict_results

    def grid_search (self, parameters_multiple_values={}, parameters_single_value={}, other_parameters = {}, 
                     root_path=None, run_numbers=[0], random_search=False, 
                     load_previous=False, log_message='', nruns = None, keep='multiple'):
        
        other_parameters = other_parameters.copy()
        
        os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
        if nruns is not None:
            run_numbers = range (nruns)
        
        if root_path is None:
            root_path = get_paths.get_path_experiments(folder  = other_parameters.get('root_folder'))
        path_results_base = root_path
        
        mymakedirs(path_results_base,exist_ok=True)
        
        if keep=='multiple':
            parameters_single_value = {k:parameters_single_value[k] for k in parameters_single_value.keys() if k not in parameters_multiple_values}
        elif keep=='single':
            parameters_multiple_values = {k:parameters_multiple_values[k] for k in parameters_multiple_values.keys() if k not in parameters_single_value}
        else:
            raise ValueError ('parameter keep {} not recognized: it must be either multiple or single'.format(keep))
        
        parameters_multiple_values_all = parameters_multiple_values
        parameters_multiple_values_all = list(ParameterGrid(parameters_multiple_values_all))
        
        logger = set_logger ("experiment_manager", path_results_base)
        if log_message != '':
            other_parameters['log_message'] = log_message
        insert_experiment_script_path (other_parameters, logger)
        
        if random_search:
            path_random_hp = '%s/random_hp.pk' %path_results_base
            if load_previous and os.path.exists(path_random_hp):
                parameters_multiple_values_all = pickle.load(open(path_random_hp,'rb'))
            else:
                parameters_multiple_values_all = list(np.random.permutation(parameters_multiple_values_all))
                pickle.dump (parameters_multiple_values_all, open(path_random_hp,'wb'))
        for (i_hp, parameters_multiple_values) in enumerate(parameters_multiple_values_all):
            parameters = parameters_multiple_values.copy()
            parameters.update(parameters_single_value)
            
            for (i_run, run_number) in enumerate(run_numbers):
                logger.info('processing hyper-parameter %d out of %d' %(i_hp, len(parameters_multiple_values_all)))
                logger.info('doing run %d out of %d' %(i_run, len(run_numbers)))
                logger.info('%s' %log_message)

                self.create_experiment_and_run (parameters=parameters, other_parameters = other_parameters, 
                                           run_number=run_number, root_path=path_results_base)
        
        # This solves an intermitent issue found in TensorFlow (reported as bug by community)
        import gc
        gc.collect()
        
    def run_multiple_repetitions (self, parameters={}, other_parameters = {}, 
                     root_path=None, log_message='', nruns = None, run_numbers=[0]):
        
        other_parameters = other_parameters.copy()

        if nruns is not None:
            run_numbers = range (nruns)
        
        logger = set_logger ("experiment_manager", root_path)
        results = np.zeros((len(run_numbers),))
        for (i_run, run_number) in enumerate(run_numbers):
                logger.info('doing run %d out of %d' %(i_run, len(run_numbers)))
                logger.info('%s' %log_message)

                results[i_run], dict_results  = self.create_experiment_and_run (parameters=parameters, other_parameters = other_parameters, 
                                           run_number=run_number, root_path=root_path)
                if dict_results.get('is_pruned', False):
                    break
        
        mu, std = results.mean(), results.std()
        logger.info ('mean {}: {}, std: {}'.format(other_parameters.get('key_score',''), mu, std))
        
        dict_results[other_parameters.get('key_score','cost')] = mu
        
        return mu, std, dict_results
                                   
                                           
    def hp_optimization (self, parameter_sampler = None, root_path=None, log_message=None, parameters={}, other_parameters={}, nruns=None):
    
        import optuna
        from optuna.pruners import SuccessiveHalvingPruner, MedianPruner
        from optuna.samplers import RandomSampler, TPESampler
        from optuna.integration.skopt import SkoptSampler
        
        if root_path is None:
            root_path = get_paths.get_path_experiments(folder  = other_parameters.get('root_folder'))

        other_parameters = other_parameters.copy()
            
        os.makedirs(root_path, exist_ok=True)
        logger = set_logger ("experiment_manager", root_path)
        if log_message != '':
            other_parameters['log_message'] = log_message
        insert_experiment_script_path (other_parameters, logger)
        
        # n_warmup_steps: Disable pruner until the trial reaches the given number of step.
        sampler_method = other_parameters.get('sampler_method', 'random')
        pruner_method = other_parameters.get('pruner_method', 'halving')
        n_evaluations = other_parameters.get('n_evaluations', 20)
        seed = other_parameters.get('seed', 0)
        if sampler_method == 'random':
            sampler = RandomSampler(seed=seed)
        elif sampler_method == 'tpe':
            sampler = TPESampler(n_startup_trials=other_parameters.get('n_startup_trials', 5), seed=seed)
        elif sampler_method == 'skopt':
            # cf https://scikit-optimize.github.io/#skopt.Optimizer
            # GP: gaussian process
            # Gradient boosted regression: GBRT
            sampler = SkoptSampler(skopt_kwargs={'base_estimator': "GP", 'acq_func': 'gp_hedge'})
        else:
            raise ValueError('Unknown sampler: {}'.format(sampler_method))

        if pruner_method == 'halving':
            pruner = SuccessiveHalvingPruner(min_resource=1, reduction_factor=4, min_early_stopping_rate=0)
        elif pruner_method == 'median':
            pruner = MedianPruner(n_startup_trials=5, n_warmup_steps=n_evaluations // 3)
        elif pruner_method == 'none':
            # Do not prune
            pruner = MedianPruner(n_startup_trials=other_parameters.get('n_trials', 10), n_warmup_steps=n_evaluations)
        else:
            raise ValueError('Unknown pruner: {}'.format(pruner_method))

        logger.info ("Sampler: {} - Pruner: {}".format(sampler_method, pruner_method))
        
        #study = optuna.create_study(sampler=sampler, pruner=pruner)
        study_name = other_parameters.get('study_name', 'hp_study')  # Unique identifier of the study.
        study = optuna.create_study(study_name=study_name, storage='sqlite:///%s/%s.db' %(root_path, study_name), sampler=sampler, pruner=pruner, load_if_exists=True)
    
        def objective(trial):

            hp_parameters = parameters.copy()
            self.parameters_non_pickable = dict(trial=trial)
            
            if parameter_sampler is not None:
                hp_parameters.update(parameter_sampler(trial))
            
            if nruns is None:
                _, dict_results = self.create_experiment_and_run (parameters=hp_parameters, other_parameters = other_parameters, root_path=root_path, run_number=other_parameters.get('run_number'))
            else:
                mu_best, std_best, dict_results = self.run_multiple_repetitions (parameters=hp_parameters, other_parameters = other_parameters, root_path=root_path, nruns=nruns)
            
            if dict_results.get('is_pruned', False):
                raise optuna.structs.TrialPruned()

            return dict_results[other_parameters.get('key_score', 'cost')]

        optuna.logging.disable_propagation()
        study.optimize(objective, n_trials=other_parameters.get('n_trials', 10), n_jobs=other_parameters.get('n_jobs', 1))

        logger.info ('Number of finished trials: {}'.format(len(study.trials)))
        logger.info ('Best trial:')
        trial = study.best_trial
        logger.info ('Value: {}'.format(trial.value))
        logger.info ('best params: {}'.format (study.best_params))
        best_value = trial.value
        
        nruns_best = other_parameters.get('nruns_best', 0)
        if nruns_best > 0:
            logger.info ('running best configuration %d times' %nruns_best)
            parameters.update (study.best_params)
            mu_best, std_best, _ = self.run_multiple_repetitions (parameters=parameters, other_parameters = other_parameters, 
                                            root_path=root_path, nruns=nruns_best)
            best_value = mu_best
        
        return best_value
       
    def rerun_experiment (self, experiments=[], run_numbers=[0], nruns = None, root_path=None, root_folder = None, 
                          other_parameters={}, parameters = {}, parameter_sampler = None, parameters_multiple_values = None, 
                          log_message='', only_if_exists=False):
        
        other_parameters = other_parameters.copy()

        if root_folder is not None:
            other_parameters['root_folder'] = root_folder

        if root_path is None:
            root_path = get_paths.get_path_experiments(folder  = other_parameters.get('root_folder'))
        
        logger = set_logger ("experiment_manager", root_path)
        
        if nruns is not None:
            run_numbers = range (nruns)
        
        parameters_original = parameters
        other_parameters_original = other_parameters
        for experiment_id in experiments:
            check_experiment_matches = (parameters_multiple_values is None) and (parameter_sampler is None)
            parameters, other_parameters = load_parameters (experiment=experiment_id, root_path=root_path, root_folder = root_folder, 
                                                            other_parameters=other_parameters_original, parameters = parameters_original, 
                                                            check_experiment_matches=check_experiment_matches)
                
            # we need to set the following flag to False, since otherwise when we request to store the intermediate results 
            # and the experiment did not start, we do not run the experiment
            if other_parameters.get('use_last_result', False) and not other_parameters_original.get('use_last_result', False):
                logger.debug ('changing other_parameters["use_last_result"] to False')
                other_parameters['use_last_result'] = False
            logger.info (f'running experiment {experiment_id} with parameters:\n{parameters}\nother_parameters:\n{other_parameters}')
            
            if parameter_sampler is not None:
                logger.info ('running hp_optimization')
                insert_experiment_script_path (other_parameters, logger)
                self.hp_optimization (parameter_sampler = parameter_sampler, root_path=root_path, log_message=log_message, 
                                        parameters=parameters, other_parameters=other_parameters)
            elif parameters_multiple_values is not None:
                self.grid_search (parameters_multiple_values=parameters_multiple_values, parameters_single_value=parameters, 
                                    other_parameters = other_parameters, root_path=root_path, run_numbers=run_numbers, log_message=log_message)
            else:
                if only_if_exists:
                    run_numbers = [run_number for run_number in run_numbers if os.path.exists('%s/%d' %(path_root_experiment, run_number))]
                
                script_parameters = {} 
                insert_experiment_script_path (script_parameters, logger)
                other_parameters['rerun_script'] = script_parameters
                self.run_multiple_repetitions (parameters=parameters, other_parameters = other_parameters, root_path=root_path, 
                                                log_message=log_message, run_numbers=run_numbers)
        
    def rerun_experiment_pipeline (self, experiments, run_numbers=None, root_path=None, root_folder=None, new_parameters={}, save_results=False):
        
        if root_path is None:
            root_path = get_paths.get_path_experiments(folder=root_folder)
        for experiment_id in experiments:
            path_root_experiment = get_paths.get_path_experiment (experiment_id, root_path=root_path)
            
            parameters, other_parameters=pickle.load(open('%s/parameters.pk' %path_root_experiment,'rb'))
            parameters = parameters.copy()
            parameters.update(other_parameters)
            parameters.update(new_parameters)
            for run_number in run_numbers:
                path_experiment = '%s/%d/' %(path_root_experiment, run_number)
                path_data = get_paths.get_path_data (run_number, root_path, parameters)
                score, _ = self.run_experiment_pipeline (run_number, path_experiment, parameters = parameters)

                if save_results:
                    experiment_number = experiment_id
                    path_csv = '%s/experiments_data.csv' %root_path
                    path_pickle = path_csv.replace('csv', 'pk')
                    if os.path.exists(path_pickle):
                        experiment_data = pd.read_pickle (path_pickle)
                    else:
                        experiment_data = pd.read_csv (path_csv, index_col=0)
                    if type(score)==dict:
                        for key in score.keys():
                            if key != '':
                                experiment_data.loc[experiment_number, '%d_%s' %(run_number, key)]=score[key]
                            else:
                                experiment_data.loc[experiment_number, '%d' %run_number]=score[key]
                    else:
                        experiment_data.loc[experiment_number, name_score]=score
                    experiment_data.to_csv(path_csv)
                    experiment_data.to_pickle(path_pickle)
            
    def rerun_experiment_par (self, experiments, run_numbers=None, root_path=None, root_folder=None, parameters={}):
        
        if root_path is None:
            root_path = get_paths.get_path_experiments(folder=root_folder)
        for experiment_id in experiments:
            path_root_experiment = get_paths.get_path_experiment (experiment_id, root_path=root_path)
            
            for run_number in run_numbers:
                path_experiment = '%s/%d/' %(path_root_experiment, run_number)
                self.run_experiment_pipeline (run_number, path_experiment, parameters = parameters)
     
    def record_intermediate_results (self, experiments=range(100), run_numbers=range(100), root_path=None, root_folder=None, new_parameters={}, remove=False):
        
        if remove:
            new_parameters.update (remove_not_finished=True, only_remove_not_finished=True)
        else:
            new_parameters.update (use_last_result=True)
        
        self.rerun_experiment_and_save(experiments=experiments, run_numbers=run_numbers, 
            root_path=root_path, root_folder=root_folder, 
            new_parameters=new_parameters)
        
# ##################################################
# ##################################################
def get_git_revision_hash(root_path=None):
    try:
        git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
        git_hash = str(git_hash)
        json.dump(git_hash, open('%s/git_hash.json' %root_path, 'wt'))
    except:
        logger = logging.getLogger("experiment_manager")
        if root_path is not None:
            logger.info ('could not get git hash, retrieving it from disk...')
            git_hash = json.load(open('%s/git_hash.json' %root_path, 'rt'))
        else:
            logger.info ('could not get git hash, using empty string...')
            git_hash = ''
            
    return str(git_hash)
    
def record_parameters (path_save, parameters, other_parameters=None):
    with open('%s/parameters.txt' %path_save, 'wt') as f:
        f.write('%s\n' %mypprint(parameters, dict_name='parameters'))
        if other_parameters is not None:
            f.write('\n\n%s\n' %mypprint(other_parameters, dict_name='other_parameters'))
    if other_parameters is not None:
        pickle.dump ([parameters,other_parameters],open('%s/parameters.pk' %path_save, 'wb'))
    else:
        pickle.dump (parameters,open('%s/parameters.pk' %path_save, 'wb'))
    try:
        json.dump(parameters,open('%s/parameters.json' %path_save, 'wt'))
    except:
        pass
    if other_parameters is not None:
        try:
            json.dump(parameters,open('%s/other_parameters.json' %path_save, 'wt'))
        except:
            pass
    
def mypprint(parameters, dict_name=None):
    if dict_name is not None:
        text = '%s=dict(' %dict_name
        tpad = ' ' * len(text)
    else:
        text = '\t'
        tpad = '\t'
    for idx, (key, value) in enumerate(sorted(parameters.items(), key=lambda x: x[0])):
        if type(value) is str:
            value = '%s%s%s' %("'",value,"'")
        text += '{}={}'.format(key, value)
        if idx < (len(parameters)-1):
            text += ',\n{}'.format(tpad)

    if dict_name is not None:
        text += ')\n'
    else:
        text += '\n'

    return text
    
def mymakedirs (path, exist_ok=False):
    '''work around for python 2.7'''
    if exist_ok:
        try:
            os.makedirs(path)
        except:
            pass
    else:
        os.makedirs(path)
    
def find_closest_epoch (experiment_data, parameters, name_epoch='max_epoch'):
    '''Finds experiment with same parameters except for number of epochs, and takes the epochs that are closer but lower than the one in parameters.'''
    
    experiment_numbers, _, _ = experiment_utils.find_rows_with_parameters_dict (experiment_data, parameters, ignore_keys=[name_epoch,'prev_epoch'])

    defaults = get_default_parameters(parameters)
    current_epoch = parameters.get(name_epoch, defaults.get(name_epoch))
    if current_epoch is None:
        current_epoch = -1
    if len(experiment_numbers) > 1:
        epochs = experiment_data.loc[experiment_numbers,name_epoch]
        epochs[epochs.isnull()]=current_epoch
        epochs = epochs.loc[epochs<=current_epoch]
        if epochs.shape[0] == 0:
            return None
        else:
            return epochs.idxmax()
    elif len(experiment_numbers) == 1:
        return experiment_numbers[0]
    else:
        return None
    
def load_or_create_experiment_values (path_csv, parameters, precision=1e-15):

    logger = logging.getLogger("experiment_manager")
    path_pickle = path_csv.replace('csv', 'pk')
    experiment_numbers = []
    changed_dataframe = False
       
    if os.path.exists (path_pickle) or os.path.exists (path_csv):
        if os.path.exists (path_pickle):
            experiment_data = pd.read_pickle (path_pickle)
        else:
            experiment_data = pd.read_csv (path_csv, index_col=0)
            experiment_data.to_pickle(path_pickle)
            
        experiment_data, removed_defaults = remove_defaults_from_experiment_data (experiment_data)
            
        # Finds rows that match parameters. If the dataframe doesn't have any parameter with that name, a new column is created and changed_dataframe is set to True
        experiment_numbers, changed_dataframe, _ = experiment_utils.find_rows_with_parameters_dict (experiment_data, parameters, precision = precision)
        
        changed_dataframe = changed_dataframe or removed_defaults

        if len(experiment_numbers) > 1:
            logger.info ('more than one matching experiment: ', experiment_numbers)
    else:
        experiment_data = pd.DataFrame()
            
    if len(experiment_numbers) == 0:
        experiment_data = experiment_data.append (parameters, ignore_index=True)
        changed_dataframe = True
        experiment_number = experiment_data.shape[0]-1
    else:
        experiment_number = experiment_numbers[0]
        
    if changed_dataframe:
        experiment_data.to_csv(path_csv)
        experiment_data.to_pickle(path_pickle)
        
    return experiment_number, experiment_data

def store_parameters (root_path, experiment_number, parameters):
    """ Keeps track of dictionary to map experiment number and parameters values for the different experiments."""
    path_hp_dictionary = '%s/parameters.pk' %root_path
    if os.path.exists(path_hp_dictionary):
        all_parameters = pickle.load (open(path_hp_dictionary,'rb'))
    else:
        all_parameters = {}
    if experiment_number not in all_parameters.keys():
        str_par = '\n\nExperiment %d => parameters: \n%s\n' %(experiment_number,mypprint(parameters))
        f = open('%s/parameters.txt' %root_path, 'at')
        f.write(str_par)
        f.close()
        all_parameters[experiment_number] = parameters
        pickle.dump (all_parameters, open(path_hp_dictionary,'wb'))
        
    # pickle number of current experiment, for visualization
    pickle.dump(experiment_number, open('%s/current_experiment_number.pkl' %root_path,'wb'))

def isnull (experiment_data, experiment_number, name_column):
    return (name_column not in experiment_data.columns) or (experiment_data.loc[experiment_number, name_column] is None) or np.isnan(experiment_data.loc[experiment_number, name_column])
    

def get_experiment_number (root_path, parameters = {}):
    
    path_csv = '%s/experiments_data.csv' %root_path
    path_pickle = path_csv.replace('csv', 'pk')
    experiment_number, _ = load_or_create_experiment_values (path_csv, parameters)
    
    return experiment_number
    
def get_experiment_numbers (path_results_base, parameters_single_value, parameters_multiple_values_all):
    
    experiment_numbers = []
    
    parameters_multiple_values_all = list(ParameterGrid(parameters_multiple_values_all))
    
    for (i_hp, parameters_multiple_values) in enumerate(parameters_multiple_values_all):
        parameters = parameters_multiple_values.copy()
        parameters.update(parameters_single_value)
        parameters = remove_defaults (parameters)
    
        experiment_number = get_experiment_number (path_results_base, parameters=parameters)
        experiment_numbers.append(experiment_number)
        
    return experiment_numbers

def set_logger (name, path_results, stdout=True, mode='a', just_message = False, filename='logs.txt'):
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    for hdlr in logger.handlers[:]:  # remove all old handlers
        logger.removeHandler(hdlr)
    
    #if not logger.hasHandlers():
                
    # Create handlers
    if stdout:
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.DEBUG)
        c_format = logging.Formatter('%(message)s')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)
        
    f_handler = logging.FileHandler('%s/%s' %(path_results, filename), mode = mode)
    f_handler.setLevel(logging.DEBUG)
    if just_message:
        f_format = logging.Formatter('%(asctime)s - %(message)s')
    else:
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)
    logger.propagate = 0
    
    return logger

def insert_experiment_script_path (other_parameters, logger):
    if other_parameters.get('script_path') is None:
        stack_level = other_parameters.get('stack_level', -3)
        stack = traceback.extract_stack()[stack_level]
        other_parameters['script_path'] = stack.filename
        other_parameters['lineno'] = stack.lineno
        logger.info ('experiment script: {}, line: {}'.format(stack.filename, stack.lineno))
        if 'stack_level' in other_parameters: 
            del other_parameters['stack_level']

            
# 
def load_parameters (experiment=None, root_path=None, root_folder = None, other_parameters={}, parameters = {}, check_experiment_matches=True):
    
    if root_folder is not None:
        other_parameters['root_folder'] = root_folder

    if root_path is None:
        root_path = get_paths.get_path_experiments(folder  = other_parameters.get('root_folder'))
        
    path_root_experiment = get_paths.get_path_experiment (experiment, root_path=root_path)
    
    logger = set_logger ("experiment_manager", root_path)
    
    if os.path.exists('%s/parameters.pk' %path_root_experiment): 
        parameters2, other_parameters2=pickle.load(open('%s/parameters.pk' %path_root_experiment,'rb'))
        
        other_parameters2.update(other_parameters)
        other_parameters = other_parameters2
        
        # if we don't add or modify parameters, we require that the old experiment number matches the new one
        if (len(parameters) == 0) and check_experiment_matches:
            logger.info ('requiring experiment number to be {}'.format(experiment))
            other_parameters['experiment_number'] = experiment
        elif 'experiment_number' in other_parameters:
            del other_parameters['experiment_number']
        
        parameters2.update(parameters)
        parameters = parameters2
    else:
        raise FileNotFoundError ('file {} not found'.format ('%s/parameters.pk' %path_root_experiment))
        
    return parameters, other_parameters

def save_other_parameters (experiment_number, other_parameters, root_path):
    parameters_to_save = {}
    for k in other_parameters.keys():
        if type(other_parameters[k]) is str:
            parameters_to_save[k] = other_parameters[k]
        elif np.isscalar(other_parameters[k]) and np.isreal(other_parameters[k]):
            parameters_to_save[k] = other_parameters[k]
        
    path_csv = '%s/other_parameters.csv' %root_path
    df = pd.DataFrame (index = [experiment_number], data=parameters_to_save)
    
    if os.path.exists (path_csv):
        df_all = pd.read_csv (path_csv, index_col=0)
        df_all = pd.concat([df_all, df], sort=True)
        df_all = df_all.loc[~df_all.index.duplicated(keep='last')]
    else:
        df_all = df
    df_all.to_csv (path_csv)