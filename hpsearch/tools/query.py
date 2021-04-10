import argparse
import sys
sys.path.append('.')
sys.path.append('src')
from collections import namedtuple
from IPython.display import display
# csp api
import hpsearch.utils.experiment_utils as ut

default_root = 'sac'
default_metric = 'cost_test'
default_always = ''
default_op = 'min' 

#python print_table2.py -d 2 -f "dict(optim='sgd')"

parser = argparse.ArgumentParser(description='show metrics in visdom browser')
# Datasets
parser.add_argument('-m','--metric', type=str, default=default_metric, help="metrics scores")
parser.add_argument('--stats', type=str, nargs='+', default=['mean'],  help="statistics for multiple runs")
parser.add_argument('--experiments', type=int, nargs='+', default=None,  help="experiment numbers")
parser.add_argument('-r','--root', type=str, default=default_root)
parser.add_argument('-v', type=str, default='{}', help='variable parameters')
parser.add_argument('-f', type=str, default='{}', help='fixed parameters')
parser.add_argument('-a', type=str, default='[]', help='all parameters')
parser.add_argument('-e', '--exact', action= "store_true", help='exact match') 
parser.add_argument('--last', type=int, default=None, help='include these last experiments') 
parser.add_argument('--best', type=int, default=None, help='include these best experiments')
parser.add_argument('--range', type=int, nargs='+', default=None, help='include this range of experiments')
parser.add_argument('-c', '--compact', type=int, default=0, help='compact parameters to this number of characters') 
parser.add_argument('--results', type=int, default=0, help='min number of results to consider') 
parser.add_argument('-d', type=int, default=0)
parser.add_argument('-s', '--show', action= "store_true")
parser.add_argument('--other', action= "store_true")
parser.add_argument('--always', type=str, default = default_always)
parser.add_argument('--op', default=default_op, type=str)
parser.add_argument('--round', default=2, type=int, help='round scores to this number of digits')
parser.add_argument('--runs', default=None, type=int, nargs='+', help='query restricted to run number provided')
pars = parser.parse_args()

pars.v = eval(pars.v)
pars.f = eval(pars.f)
pars.a = eval(pars.a)
pars.always = eval('dict(%s)' %pars.always)
pars.f.update(pars.always)

print ('dictionary of query terms=%s' %pars.f)

if pars.d == 1:
    pars.root = 'squeezenet2'
elif pars.d == 2:
    pars.root = 'squeezenet2msmt'
elif pars.d == 3:
    pars.root = 'allexperiments'
    
def query (pars, other_parameters=False):
    pv, pf, pall, pexact = pars.v, pars.f, pars.a, pars.exact
    
    result_query = ut.query(folder_experiments=pars.root, suffix_results='_'+pars.metric, experiments = pars.experiments,
                        classes=pars.runs, parameters_fixed=pf, parameters_variable=pv, parameters_all = pall, exact_match=pexact, 
                        ascending=pars.op=='min', stats=pars.stats, min_results=pars.results, query_other_parameters=other_parameters)
    
    if not other_parameters:
        result_query = result_query[1]
        result_query = result_query['stats']

    return result_query 


if __name__ == '__main__':

    df = query (pars, other_parameters=pars.other)
    if pars.experiments is None:
        pars.experiments = []
    if pars.last is not None:
        pars.experiments += range(df.index.max()-pars.last+1, df.index.max()+1)
    if pars.best is not None:
        pars.experiments += list(df.index[:pars.best])
    if pars.range is not None:
        assert len(pars.range) == 2
        pars.experiments += range(pars.range[0], pars.range[1])
    if len(pars.experiments) > 0: 
        df = df.loc[[x for x in df.index if x in pars.experiments]]
    df = ut.replace_with_default_values (df)
    if (pars.round is not None) and (pars.round != 0):
        df[pars.stats] = df[pars.stats].round(pars.round)
    display (df)
    
    print ('index: ')
    print (df.index)
    print ('min: {}, max: {}'.format(df.index.min(), df.index.max()))

    print ('with unique parameters:')
    _, df2 = ut.get_parameters_unique(df)
    if pars.compact > 0:
        prev_cols = df2.columns.copy()
        df2, dict_rename = ut.compact_parameters (df2, pars.compact)
        for k, kor in zip(df2.columns, prev_cols):
            print ('{} => {}'.format(k, kor))
    display (df2)
            
    if pars.show:
       import hpsearch.visualization.plot_visdom as pv
       pv.plot_multiple_histories(df.index, root_folder=pars.root,metrics=pars.metric, parameters=None)
