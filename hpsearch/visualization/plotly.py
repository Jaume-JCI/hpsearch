import plotly.graph_objs as go
import plotly.offline as offline
import numpy as np

def imshow (z, x=None, y=None, title=None, xlabel=None, ylabel=None):
    offline.init_notebook_mode (connected=True)
    
    trace = go.Heatmap(x=x, y=y, z=z)
    traces=[trace]
    dict_layout = dict()
    if title is not None:
        dict_layout.update(title=title)
    if xlabel is not None:
        dict_layout.update(xaxis=go.layout.XAxis(title=xlabel))
    if ylabel is not None:
        dict_layout.update(yaxis=go.layout.YAxis(title=ylabel))
        
    offline.iplot(dict(data=traces, layout=go.Layout(**dict_layout)))

def plot (x, y=None, style='b', label='', title=None, xlabel=None, ylabel=None, traces=[]):    
    offline.init_notebook_mode (connected=True)
    traces = add_trace (x, y, style, label = label, traces=traces)
    dict_layout = dict()
    if title is not None:
        dict_layout.update(title=title)
    if xlabel is not None:
        dict_layout.update(xaxis=go.layout.XAxis(title=xlabel))
    if ylabel is not None:
        dict_layout.update(yaxis=go.layout.YAxis(title=ylabel))
    offline.iplot(dict(data=traces, layout=go.Layout(**dict_layout)))
    
    return traces

def add_trace (x, y=None, style='b', label='', traces=[]):
    if y is None or type(y) is str:
        if type(y) is str:
            style = y
        y = x
        x = np.arange(len(y))
    d = symbol2marker (style)
    if type(x)==np.ndarray:
        x = x.ravel()
    if type(y)==np.ndarray:
        y = y.ravel()
        
    traces += [go.Scatter(x=x, y=y, name=label, **d)]
    
    
    return traces
   
    
def symbol2marker (symbol):
    d = dict()
    if len(symbol) > 1 and symbol[-2:] == '--':
        d.update(line=dict(dash='dash'))
    elif symbol[-1] == ':':
        d.update(line=dict(dash='dot'))
    if symbol[0]=='r':
        d.update(marker=dict(color='red'))
    elif symbol[0]=='b':
        d.update(marker=dict(color='blue'))
    elif symbol[0]=='c':
        d.update(marker=dict(color='cyan'))
    elif symbol[0]=='m':
        d.update(marker=dict(color='magenta'))
    elif symbol[0]=='k':
        d.update(marker=dict(color='black'))
    elif symbol[0]=='y':
        #d.update(marker=dict(color='brown'))
        d.update(marker=dict(color = 'rgba(200, 200, 0, 1)'))
    elif symbol[0]=='g':
        d.update(marker=dict(color='green'))
    elif symbol[0]=='o':
        d.update(marker=dict(color='orange'))
    else:
        d.update(marker=dict(color='blue'))
        
    if (len(symbol) > 2) and symbol[1:3] == '.-':
        d.update(mode='markers+lines')
    elif (len(symbol) > 1) and symbol[1] == '-':
        d.update(mode='lines')
    elif (len(symbol) > 1) and symbol[1] == '.':
        d.update(mode='markers')
    else:
        d.update(mode='lines')
    return d

def plot_df (df, x=None, message=None):

    offline.init_notebook_mode (connected=True)
    
    if message is not None:
        print (message)

    # show each individual time-series
    offline.iplot([
        {'x': df[x] if x is not None else df.index,
         'y': df[col],
         'name': col
        }  for col in df.columns])
