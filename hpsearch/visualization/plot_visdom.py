import numpy as np
#import matplotlib.pyplot as plt
import os
import pickle
import pandas as pd
from IPython.display import display
import visdom
import hpsearch.config.get_paths as get_paths
import hpsearch.utils.experiment_utils as ut
    
    
def do_hack (path_results, name_file, hack):
    if os.path.exists('%s/%s' %(path_results, 'testing_reward_list.pk')):
        ter, tec = pickle.load(open('%s/%s' %(path_results, 'testing_reward_list.pk'),'rb'))
        trr, trc = pickle.load(open('%s/%s' %(path_results, 'training_reward_list.pk'),'rb'))
        history = dict(cost_train=trc, reward_train=trr, cost_test=tec, reward_test=ter)
        pickle.dump(history, open('%s/%s' %(path_results, name_file), 'wb'))
            
def plot_multiple_histories (experiments, run_number=0, root_path=None, root_folder=None, metrics='all', 
                             metrics_second=[], parameters = None, compare = True, 
                             ylegend=0.5, name_file='model_history', hack=True,
                             op='max', include_parameters_in_legend=False):
    
    if root_path is None:
        root_path = get_paths.get_path_experiments(folder=root_folder)
    
    df = pd.read_csv('%s/experiments_data.csv' %root_path,index_col=0)
    df2 = ut.get_experiment_parameters (df.loc[experiments], only_not_null=True)
    parameters2, df2 = ut.get_parameters_unique(df2)
    #df2 = df.loc[experiments,parameters2]
    
    #parameters2 = ut.get_parameters_columns(df.loc[experiments], True)
    #df2 = df.loc[experiments,parameters2]
    #parameters2 = []
    #for k in df2.columns:
    #    if len(df2[k].unique()) > 1:
    #        parameters2 += [k]
    #df2 = df.loc[experiments,parameters2]

    if compare or parameters is not None:        
        if parameters is None:
            parameters = parameters2 
        df = df.loc[experiments,parameters]
    
    if type(metrics)==str and (metrics == 'all'):
        path_results = get_paths.get_path_results (experiments[0], run_number=run_number, root_path=root_path)
        do_hack (path_results, name_file, hack)
        history = pickle.load(open('%s/%s' %(path_results, name_file),'rb'))
        metrics = history.keys()
    if type(metrics) == str:
        metrics = [metrics]
    if type(metrics_second) == str:
        metrics_second = [metrics_second]
    df = ut.replace_with_default_values (df)
    df2 = ut.replace_with_default_values (df2)
    df_show = df.copy()
    vis = visdom.Visdom()
    #print (df2)
    #vis.text(df2.to_html())
    for (imetric,metric) in enumerate(metrics):
        title = metric
        histories = []
        for experiment_id in experiments:
            path_results = get_paths.get_path_results (experiment_id, run_number=run_number, root_path=root_path)
            do_hack (path_results, name_file, hack)
            if os.path.exists('%s/%s' %(path_results, name_file)):
                history = pickle.load(open('%s/%s' %(path_results, name_file),'rb'))
                values = [float(x) for x in history[metric]]
                if compare and include_parameters_in_legend:
                    label = '{}-{}'.format(experiment_id, list(dict(df.loc[experiment_id]).values()))
                else:
                    label = '{}'.format(experiment_id)
                histories += [dict(y=values, 
                                   mode="markers+lines", 
                                   type='custom',
                                   name = label)]
                #if len(metrics_second) > 0:
                if True:
                    if op == 'min':
                        imin = int(np.array(history[metric]).argmin())
                    else:
                        imin = int(np.array(history[metric]).argmax())
                    vmin = float(history[metric][imin])
                    histories += [dict(x = [imin], 
                                       y=[vmin], 
                                       mode="markers", 
                                       type='custom', 
                                       name = '', 
                                       marker={'color': 'red', 'symbol': 104, 'size': "10"})]
                    title += ' [%d]: %.2f' %(experiment_id, vmin)
                    df_show.loc[experiment_id, metric] = vmin
                    df2.loc[experiment_id, metric] = vmin
                if (imetric == 0):
                    for metric_second in metrics_second:
                        values = [float(x) for x in history[metric_second]]
                        if compare and include_parameters_in_legend:
                            label = '{}: {}-{}'.format(metric_second, experiment_id, list(dict(df.loc[experiment_id]).values()))
                        else:
                            label = '{}: {}'.format(metric_second, experiment_id)
                        histories += [dict(y=values, 
                                           mode="markers+lines", 
                                           type='custom',
                                           name = label)]
                        if op == 'min':
                            imin = int(np.array(history[metric_second]).argmin())
                        else:
                            imin = int(np.array(history[metric_second]).argmax())
                        vmin = float(history[metric_second][imin])
                        histories += [dict(x = [imin], 
                                           y=[vmin], 
                                           mode="markers", 
                                           type='custom', 
                                           name = '', 
                                           marker={'color': 'red', 'symbol': 104, 'size': "10"})]
                        title += ' [%d]: %.2f' %(experiment_id, vmin)
                        df_show.loc[experiment_id, metric_second] = vmin
                        df2.loc[experiment_id, metric_second] = vmin

                #print (title)
                layout = dict(title=title, xaxis={'title': 'epoch'}, yaxis={'title': metric}, legend= {'x':1, 'y':ylegend})

        vis._send({'data': histories, 'layout': layout, 'win': metric})
        vis.text (df_show.to_html(justify='left', col_space=100), win= f'{metric}_parameters')
        display(df2)
        
def send_plot(xarray, yarray, window_name = '', ylegend=None, xlabel='', ylabel=None, log_scale=False, name='', traces=[]):

    vis = visdom.Visdom()
    if ylabel is None:
        ylabel = window_name
        
    if (len(traces) == 0) or (len(xarray) > 0) or (len(yarray) > 0):
        xvalues = [float(x) for x in xarray]
        yvalues = [float(x) for x in yarray]
        traces += [dict(x = xvalues, y=yvalues, mode="markers+lines", type='custom', name = name)]
    if ylegend is not None:
        legend = dict(legend={'x':1, 'y':ylegend})
    else:
        legend = dict()
  
    xaxis = {'title': xlabel}
    if log_scale:
        xaxis['type'] = 'log'
    layout = dict(title=window_name, xaxis=xaxis, yaxis={'title': ylabel}, **legend)

    vis._send({'data': traces, 'layout': layout, 'win': window_name})
    
    return traces
