# Welcome to HPSearch
> Experiment tracking framework.


`HPSearch` is flexible experiment tracking framework that that provides features such as a simple and powerful query mechanism for studying and visualizing the performance of past experiments meeting given criteria, the possibility to resume a previous experiment with or without modifying the original hyper-parameters (e.g., extending the number of epochs of a promising past experiment, or gradually changing the hyper-parameters to obtain an approximate curriculum learning type of approach, etc.), the capability of visualizing the learning evolution of multiple experiments based on different metrics, and many other features.

Recently, many different experiment tracking frameworks have been created, such as `mlflow`, `weight and biases`, `tensorboard`, `neptune`, and many others. While few of these frameworks are open-source, e.g., `mlflow` and `tensorboard`,  they usually have limited or non-existent query capabilities, and do not allow to easily resume previous experiments. `HPSearch` is an open-source framework that targets all of these requirements. 

## Key features

`HPSearch` provides, among others, the following features:

- Query the performance of past experiments meeting desired criteria. This can be done either from command line with a simple command, or programmatically. Queried experiments are shown as a table sorted by performance, and visualized in graphical form, comparing the evolution of the metrics of the selected experiments during training.
- Visualize the evolution of current experiments and compare them against previous ones using multiple metrics
- Resume previous experiments with or without modifying their original hyper-parameters. This can be applied, for instance, when we start by performing a quick exploration of hyper-parameters by allocating a small time budget for each experiment. Once this is done, we may want to increase the exploration of  a subset of experiments that were promising, e.g., by extending their number of epochs, or using curriculum learning to gradually changing their hyper-parameters across epochs. We may also want to change only to explore hyper-parameters affecting the final part of a pipeline, where the first steps are dedicated to pre-processing and normalization techniques that might be computationally expensive and which we want to reuse. With `HPSearch`, it is easy to do that, and annotate the fact that this was done when characterizing the new experiments.
- Good support for default values. When introducing a new hyper-parameter, all previous experiments are automatically assigned a default value for such parameter. This makes it easy to avoid repeating previous experiments in the case when the default value is one of the possible values to be explored.
- High level of decoupling between the experiment tracking code and the model code.

## Installation

HPSearch is pip installable:

```bash
pip install hpsearch
```

## Documentation 

Documentation can be found [here](https://jaume-jci.github.io/hpsearch/) 
