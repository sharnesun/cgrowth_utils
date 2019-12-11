import numpy as np
import scipy.stats as st
import scipy.optimize
import warnings
import pandas as pd


def log_like_iid_gamma(params, n):
    """Log likelihood for i.i.d. Gamma measurements, parametrized
    by alpha, b=1/beta."""
    alpha, b = params

    if alpha <= 0 or b <= 0:
        return -np.inf

    return np.sum(st.gamma.logpdf(n, alpha, scale=1/b))

def log_like_iid_succ_mi_poisson(params, n):
    """Log likelihood for i.i.d. successive microtubule poisson measurements,
    parametrized by beta1, beta2."""
    b1, b2 = params

    # Handling troubling edge cases for beta1 and beta2
    if b1 <= 0 or b2 <= 0:
        return -np.inf

    if b2 <= b1:
        return -np.inf

    if abs(b1 - b2) < 1e-5:
        return np.sum(log_like_iid_gamma([2, 1/b1], n))

    # Using the properties of log, we have split off beta1 * beta2/(beta2 - beta1)
    log_like = (np.log(b1 * b2) - np.log(b2 - b1)) * len(n)

    # We pulled out an e^ (-beta1 * t) and this is the sum we have for the rest of our PDF
    logs = [-b1 * t + np.log(1 - np.exp((b1 - b2) * t)) for t in n]
    log_like += sum(logs)
    return log_like

def mle_iid_succ_mi_poisson(n, init_params=[1,2]):
    return mle_iid(n, log_like_iid_succ_mi_poisson, init_params)

def mle_iid(n, log_like_fun=log_like_iid_gamma, init_params=[3, 3]):
    """Perform maximum likelihood estimates for parameters for i.i.d.
    with specified log likelihood function and initial parameters"""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        res = scipy.optimize.minimize(
            fun=lambda params, n: -log_like_fun(params, n),
            x0=np.array(init_params),
            args=(n,),
            method='Powell'
        )

    if res.success:
        return res.x
    else:
        raise RuntimeError('Convergence failed with message', res.message)
