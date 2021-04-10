import argparse

from hpsearch.experiment_manager import create_experiment_and_run, grid_search, record_intermediate_results

# python experiments/intermediate.py -r -f pretrain_dqn

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='run experiment') 
    parser.add_argument('-s', '--store', action= "store_true") 
    parser.add_argument('-r', '--remove', action= "store_true") 
    parser.add_argument('-f', '--folder', default = 'sac', type=str) 
    parser.add_argument('-m', '--metric', default='cost_test', type=str) 
    parser.add_argument('-n', '--num-results', default=50, type=int) 


    pars = parser.parse_args()

    other_parameters=dict(key_score=pars.metric, root_folder = pars.folder, min_iterations=pars.num_results)
    print (other_parameters)

    if pars.store:
        record_intermediate_results(root_folder=pars.folder, new_parameters=other_parameters) 
    if pars.remove:
        record_intermediate_results(root_folder=pars.folder, remove=True, new_parameters=other_parameters)
   
