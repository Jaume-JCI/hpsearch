# Welcome to HPSearch
> Experiment tracking framework that can be applied to your code without needing to modify it.


`HPSearch` is an experiment tracking framework that can be applied to any existing code without requiring any modification of the original codebase. In addition to experiment tracking, `HPSearch` provides an easy to use query mechanism for studying and visualizing the performance of past experiments meeting given criteria, the capability of visualizing the evolution of current experiments and compare them against previous ones using multiple metrics, the possibility to resume a previous experiment with or without modifying the original hyper-parameters (e.g., extending the number of epochs of a promising past experiment, or gradually changing the hyper-parameters to obtain an approximate curriculum learning type of approach, etc.), and more features.

Recently, many different experiment tracking frameworks have been created, such as `mlflow`, `weight and biases`, `tensorboard`, `neptune`, and many others. While few of these frameworks are open-source, e.g., `mlflow` and `tensorboard`,  they usually require an explicit modification of the existing codebase to track the performance of experiments, have very limited or non-existent query capability, and do not allow to easily resume previous experiments in a flexible and out-of-the-box manner. `HPSearch` is an open-source framework that targets all of these requirements. 

## Key features

`HPSearch` provides, among others, the following features:

- Track experiments without modifying the existing codebase. While we can achieve a similar degree of decoupling with other frameworks, this usually requires the user to implement a layer that provides this decoupling. In contrast, `HPSearch` is designed to obtain this decoupling straight away.
- Query the performance of past experiments meeting desired criteria. This can be done either from command line with a simple command, or programmatically. Queried experiments are shown as a table sorted by performance, and visualized in graphical form, comparing the evolution of the metrics of the selected experiments during training.
- Visualize the evolution of current experiments and compare them against previous ones using multiple metrics
- Resume previous experiments with or without modifying their original hyper-parameters. This can be applied, for instance, when we start by performing a quick exploration of hyper-parameters by allocating a small time budget for each experiment. Once this is done, we may want to increase the exploration of  a subset of experiments that were promising, e.g., by extending their number of epochs, or using curriculum learning to gradually changing their hyper-parameters across epochs. We may also want to change only to explore hyper-parameters affecting the final part of a pipeline, where the first steps are dedicated to pre-processing and normalization techniques that might be computationally expensive and which we want to reuse. With `HPSearch`, it is easy to do that, and annotate the fact that this was done when characterizing the new experiments.
- Possibility to apply an ensemble of successful models without changing your code.
- Good support for default values. When introducing a new hyper-parameter, all previous experiments are automatically assigned a default value for such parameter. This makes it easy to avoid repeating previous experiments in the case when the default value is one of the possible values to be explored.

## Installation

HPSearch is pip installable:

```bash
pip install hpsearch
```
