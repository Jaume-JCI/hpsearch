# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools/query.ipynb (unless otherwise specified).

__all__ = ['query', 'do_query_and_show', 'parse_args', 'parse_arguments_and_query', 'main']

# Cell
import warnings
warnings.filterwarnings('ignore')

import argparse
import sys
sys.path.append('.')
from collections import namedtuple
from IPython.display import display
import pandas as pd

# hpsearch api
import hpsearch.utils.experiment_utils as ut
import hpsearch.config.hp_defaults as dflt

# Cell
def query (pv={}, pf={}, pall=[], pexact=False, folder=None,
           metric=None, experiments=None, runs=None, op=None, stats=['mean'],
           results=0, other_parameters=False, **kwargs):

    result_query = ut.query(folder_experiments=folder, score_name=metric, experiments=experiments,
                            run_number=runs, parameters_fixed=pf, parameters_variable=pv,
                            parameters_all=pall, exact_match=pexact, ascending=op=='min',
                            stats=stats, min_results=results,
                            query_other_parameters=other_parameters, **kwargs)

    return result_query

# Cell
def do_query_and_show (pall=[], best=None, compact=0, exact=False, experiments=None, pf={}, last=None,
                       metric=None, op=None, other_parameters=False, input_range=None, results=0,
                       folder=None, round=2, runs=None, show=False, stats=['mean'], pv={},
                       sort=None, display_all_columns=False, col_width=None,
                       manager_path=dflt.manager_path, **kwargs):

    from ..config.hpconfig import get_experiment_manager
    em = get_experiment_manager (manager_path=manager_path)
    if folder is not None or metric is not None or op is not None:
        if folder is not None: em.set_path_experiments (folder=folder)
        if metric is not None: em.key_score = metric
        if op is not None: em.op = op

    df = query (pv=pv, pf=pf, pall=pall, pexact=exact, folder=em.folder,
               metric=em.key_score, experiments=experiments, runs=runs, op=em.op, stats=stats,
               results=results, other_parameters=other_parameters, **kwargs)
    df = ut.replace_with_default_values (df)
    if sort is not None:
        stats_cols = df[dflt.stats_col].columns.get_level_values(1)
        pars_cols = df[dflt.parameters_col].columns.get_level_values(0)
        if sort in stats_cols:
            score_name_sort = df[dflt.stats_col].columns.get_level_values(0).unique()
            if len(score_name_sort)>1: print (f'sorting using first score_name from {score_name_sort}')
            score_name_sort = score_name_sort[0]
            sort_col = (dflt.stats_col, score_name_sort, sort)
        elif sort in pars_col:
            sort_col = (dflt.parameters_col, sort, '')
        else:
            raise ValueError (f'sort must be in {stats_cols.tolist()+pars_cols.tolist()}')
        df = df.sort_values(by=sort_col, ascending=(em.op=='min'))
    if experiments is None:
        experiments = []
    if last is not None:
        experiments += range(df.index.max()-last+1, df.index.max()+1)
    if best is not None:
        experiments += list(df.index[:best])
    if input_range is not None:
        assert len(input_range) == 2
        experiments += range(input_range[0], input_range[1])
    if len(experiments) > 0:
        df = df.loc[[x for x in df.index if x in experiments]]

    if col_width is not None:
        pd.set_option('max_colwidth', col_width)

    if (round is not None) and (round != 0):
        stats_col = pd.MultiIndex.from_product ([[dflt.stats_col],
                                                 df[dflt.stats_col].columns.get_level_values(0).unique(),
                                                 stats])
        df[stats_col] = df[stats_col].round(round)
    if display_all_columns:
        display (df)

    print (f'experiments: {list(df.index)}')
    print (f'min experiment #: {df.index.min()}, max experiment #: {df.index.max()}')

    print ('result of query:')
    _, df2 = ut.get_parameters_unique(df)
    #df2.index.name = 'experiment #'
    if compact > 0:
        prev_cols = df2.columns.copy()
        df2, dict_rename = ut.compact_parameters (df2, compact)
        for k, kor in zip(df2.columns, prev_cols):
            print (f'{k} => {kor}')
    display (df2)

    if show:
        import hpsearch.visualization.plot_visdom as pv
        pv.plot_multiple_histories(df.index, folder=em.folder,metrics=em.key_score, parameters=None)
    return df2

# Cell
def parse_args(args):
    default_always = ''

    parser = argparse.ArgumentParser(description='show metrics in visdom browser')
    # Datasets
    parser.add_argument('-m','--metric', type=str, default=None, help="metrics scores")
    parser.add_argument('--stats', type=str, nargs='+', default=['mean'],  help="statistics for multiple runs")
    parser.add_argument('--experiments', type=int, nargs='+', default=None,  help="experiment numbers")
    parser.add_argument('--folder', type=str, default=None)
    parser.add_argument('-v', type=str, default='{}', help='variable parameters')
    parser.add_argument('-f', type=str, default='{}', help='fixed parameters')
    parser.add_argument('-a', type=str, default='[]', help='all parameters')
    parser.add_argument('-e', '--exact', action= "store_true", help='exact match')
    parser.add_argument('--last', type=int, default=None, help='include these last experiments')
    parser.add_argument('--best', type=int, default=None, help='include these best experiments')
    parser.add_argument('--range', type=int, nargs='+', default=None, help='include this range of experiments')
    parser.add_argument('-c', '--compact', type=int, default=0, help='compact parameters to this number of characters')
    parser.add_argument('--results', type=int, default=0, help='min number of results to consider')
    parser.add_argument('-s', '--show', action= "store_true")
    parser.add_argument('--other', action= "store_true")
    parser.add_argument('--always', type=str, default = default_always)
    parser.add_argument('--op', default=None, type=str)
    parser.add_argument('--round', default=2, type=int, help='round scores to this number of digits')
    parser.add_argument('--runs', default=None, type=int, nargs='+', help='query restricted to run number provided')
    parser.add_argument('--sort', default=None, type=str)
    parser.add_argument('--width', default=None, type=int, help='max column width')
    parser.add_argument('-p', '--path', default=dflt.manager_path, type=str)
    pars = parser.parse_args(args)

    pars.v = eval(pars.v)
    pars.f = eval(pars.f)
    pars.a = eval(pars.a)
    pars.always = eval('dict(%s)' %pars.always)
    pars.f.update(pars.always)

    print (f'dictionary of query terms={pars.f}')

    return pars

# Cell
def parse_arguments_and_query (args):

    pars = parse_args(args)

    do_query_and_show (pall=pars.a, best=pars.best, compact=pars.compact, exact=pars.exact,
                       experiments=pars.experiments, pf=pars.f, last=pars.last,
                       metric=pars.metric, op=pars.op, other_parameters=pars.other,
                       input_range=pars.range, results=pars.results, folder=pars.folder,
                       round=pars.round, runs=pars.runs, show=pars.show, stats=pars.stats,
                       pv=pars.v, sort=pars.sort, col_width=pars.width, manager_path=pars.path)

def main():
    parse_arguments_and_query (sys.argv[1:])