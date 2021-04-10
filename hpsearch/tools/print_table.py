import pandas as pd
from IPython.display import display
import argparse

import sys
sys.path.append('.')
sys.path.append('src')
import hpsearch.config.get_paths as get_paths
import hpsearch.utils.experiment_utils as ut

default_root = 'sac'
default_metric = 'cost_test'
default_class = 0
default_op = 'min' 

parser = argparse.ArgumentParser(description='print table') 
# Datasets
parser.add_argument('--root', type=str, default=default_root, help='name of root folder')
parser.add_argument('--base', type=str, default='', help='full root path')
parser.add_argument('-m', '--metric', type=str, default=default_metric, help='metric score')
parser.add_argument('-d',type=int, default=0, help='number of root folder option')
parser.add_argument('-e', type=int, nargs='+', default=[], help='experiment numbers')
parser.add_argument('-a', type=bool, default=False)
parser.add_argument ('-b', '--best', action= "store_true", help='include experiment with best performance (on given run id!!)')
parser.add_argument ('-i', '--id', type=int, default=0, help='run id') 
parser.add_argument('-c', type=bool, default=True)
parser.add_argument('--compact', type=int, default=0, help='compact parameters to this number of characters') 
parser.add_argument('--op', default=default_op, type=str)
parser.add_argument('--round', default=2, type=int, help='round scores to this number of digits')
pars = parser.parse_args()
metric = '%d_%s' %(pars.id,pars.metric)

if pars.d == 1:
    pars.root = 'squeezenet2'
elif pars.d == 2:
    pars.root = 'squeezenet2msmt'
elif pars.d == 3:
    pars.root = 'allexperiments'


def print_table (pars):
    if type(pars) is dict:
        from sklearn.datasets.base import Bunch
        pars = Bunch(**pars)
        
    if pars.base != '':
        root_path = pars.base
    else:
        root_path = get_paths.get_path_experiments (folder = pars.root)
        
       
    df = pd.read_csv('%s/experiments_data.csv' %root_path,index_col=0)

    if pars.a:
        display (df[metric])

    if pars.best:
        if pars.op == 'min':
            eb = df[metric].idxmin()
        else:
            eb = df[metric].idxmax()
        parameters = ut.get_parameters_columns(df.loc[eb:eb+1], True)
        print ('\n*****************************')
        print ('parameters for %d:' %eb)
        display (df.loc[eb,parameters])
        print ('score:')
        display (df.loc[eb,metric])


    df_scores = None
    print ('\n*****************************')
    for e in pars.e:
        parameters = ut.get_parameters_columns(df.loc[e:e+1], True)
        print ('\nparameters for %d:' %e)
        display (df.loc[e,parameters])
        print ('scores for all experiments:')
        df_scores = ut.get_experiment_scores(df.loc[[e]], suffix_results='_%s' %pars.metric, remove_suffix=True)
        display(df_scores.round(pars.round))
        print ('score:')
        display (df.loc[e,metric])

    df2 = None
    if len(pars.e) > 0 and pars.c:
        e = pars.e
        if pars.best:
            e += [eb]
        parameters = ut.get_parameters_columns(df.loc[e], True)
        print ('\ncomparison')
        display (df.loc[e,parameters])
        print ('score')
        display (df.loc[e,metric])

        print ('with unique parameters:')
        _, df2 = ut.get_parameters_unique(df.loc[e])
        if pars.compact > 0:
            prev_cols = df2.columns.copy()
            df2, dict_rename = ut.compact_parameters (df2, pars.compact)
            for k, kor in zip(df2.columns, prev_cols):
                print ('{} => {}'.format(k, kor))
        display(df2)

    return df, df2, df_scores
    
df, df2, df_scores = print_table (pars)
