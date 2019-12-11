
import bebi103
import numpy as np
import tqdm
import holoviews as hv
import bokeh
import bokeh.io
from bokeh.models import ColumnDataSource, Whisker
from bokeh.plotting import figure, show
import pandas as pd


def draw_bs_sample(data):
    """Draw a bootstrap sample from a 1D data set."""
    return np.random.choice(data, size=len(data))

def mean_conf_int(data, size=1):
    """Draw boostrap replicates of the mean from 1D data set
        and calculates the 95% confidence interval."""
    out = np.empty(size)
    for i in range(size):
        out[i] = np.mean(draw_bs_sample(data))
    return np.percentile(out, [2.5, 97.5])

def draw_bs_reps_mle(mle_iid_fun, data, args=(), size=1, progress_bar=False):
    """Draw nonparametric bootstrap replicates of maximum likelihood estimator.

    Parameters
    ----------
    mle_iid_fun : function
        Function with call signature mle_fun(data, *args) that computes
        a MLE for the parameters
    data : one-dimemsional Numpy array
        Array of measurements
    args : tuple, default ()
        Arguments to be passed to `mle_fun()`.
    size : int, default 1
        Number of bootstrap replicates to draw.
    progress_bar : bool, default False
        Whether or not to display progress bar.

    Returns
    -------
    output : numpy array
        Bootstrap replicates of MLEs.
    """
    if progress_bar:
        iterator = tqdm.tqdm(range(size))
    else:
        iterator = range(size)

    return np.array([mle_iid_fun(draw_bs_sample(data), *args) for _ in iterator])

def draw_gamma(alpha, b, size=1):
    '''Draws size # of samples from a gamma distribution'''
    return np.random.gamma(alpha, 1/b, size=size)

def draw_double_poisson(beta1, beta2, size = 1):
    '''Draws size # of samples from our double poisson arrival distribution'''
    return np.random.exponential(1/beta1, size) + np.random.exponential(1/beta2, size)

def gen_gamma_data(params, size, rg):
    return np.random.gamma(params[0], 1/params[1], size=size)


def get_gamma_conf_int(data, alpha, b):
    """Get the confidence intervals from parametric bootstrap for a Gamma Distribution"""
    bs_reps = bebi103.draw_bs_reps_mle(
        mle_iid,
        gen_gamma_data,
        data=data,
        mle_args=(),
        gen_args=(),
        size=len(data),
        n_jobs=1,
        progress_bar=True,
    )
    return bs_reps

def plot_MLE_conf_int(df_estimates, variable_name, x_axis, unit=""):
    """Plot the confidence interval of estimates over our MLE
    Arguments:
        df_estimates = dataframe with column parameter indicating the name of the
            parameter of the MLE, column values with the value of the parameter
            optimized with the ground truth data, columns 2.5 percentile and
            97.5 percentile with the lower and upper bound of the confidence
            interval
        variable_name = the name of the parameter that we want to graph the
            confidence interval of
        x_axis = The values that we want to graph as the x_axis

    Returns:
        p: bohek graph object that can be shown with show()
    """

    df_var_estimates = df_estimates[df_estimates['parameter'] == variable_name]

    p = figure(
        plot_width=600,
        plot_height=300,
        title="Estimates of {} with 95% confidence intervals".format(
            variable_name
        ),
        y_axis_label="{} {}".format(variable_name, unit),
        x_axis_label=x_axis,
        y_range=(min(df_var_estimates['2.5 percentile']) * 0.9,
                 max(df_var_estimates['97.5 percentile']) * 1.1)
    )

    base, lower, upper = [], [], []
    source_error = ColumnDataSource(data=dict(
        base=df_var_estimates[x_axis],
        lower=df_var_estimates['2.5 percentile'],
        upper=df_var_estimates['97.5 percentile']
    ))

    p.add_layout(
        Whisker(source=source_error, base="base", upper="upper", lower="lower")
    )
    for i, tif_ind in enumerate(list(df_var_estimates[x_axis].unique())):
        y = df_var_estimates[df_var_estimates[x_axis] == tif_ind]['value']
        color = colors[i % len(colors)]
        p.circle(x=tif_ind, y=y, color=color)
    return p
