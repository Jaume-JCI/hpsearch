import argparse
import sys
sys.path.append('.')
sys.path.append('src')
import pandas as pd
import pickle
import hpsearch.visualization.plot_visdom as pv
import hpsearch.config.get_paths as get_paths


default_root = 'sac'
default_metric = 'cost_test'
default_op = 'min'
include_loss = False

# example call:
example_call =  'seemetric.py -e 43 33\n'
example_call += 'seemetric.py -e 43 33 --metric rank1 loss\n'


# metrics
if include_loss:
    default_metrics = [default_metric, 'loss']
else:
    default_metrics = [default_metric]

parser = argparse.ArgumentParser(description='show metrics in visdom browser') 
# Datasets
parser.add_argument('-e', nargs='+', default=[-1], type=int,
                    help="experiments")
parser.add_argument('--metric', nargs='+', type=str, default=default_metrics, help="metrics")
parser.add_argument('--root', type=str, default=default_root)
parser.add_argument('-d',type=int, default=0)
parser.add_argument('-l','--labels',nargs='+', default=None, type=str)
parser.add_argument('--run', default=0, type=int)
parser.add_argument('--op', default=default_op, type=str)
parser.add_argument('--file', default='model_history.pk', type=str)

pars = parser.parse_args()

if pars.d == 1:
    pars.root = 'squeezenet2'
elif pars.d == 2:
    pars.root = 'squeezenet2msmt'
elif pars.d == 3:
    pars.root = 'lrbatch'
 
exps = pars.e
if exps[0] == -1:
    root_path = get_paths.get_path_experiments (folder = pars.root)
    experiment_number = pickle.load(open('%s/current_experiment_number.pkl' %root_path,'rb'))
    exps[0] = experiment_number

if len(exps)>1 and (exps[1] == -2):
    root_path = get_paths.get_path_experiments (folder = pars.root)
    df = pd.read_csv('%s/experiments_data.csv' %root_path,index_col=0)
    if pars.op=='max':
        exps[1] = df['0_%s' %default_metric].idxmax()
    else:
        exps[1] = df['0_%s' %default_metric].idxmin()

pv.plot_multiple_histories(exps, run_number=pars.run, root_folder=pars.root,metrics=pars.metric, parameters=pars.labels, name_file=pars.file)
