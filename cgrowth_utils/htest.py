import numpy as np

def draw_perm_sample(x, y):
    """Generate a permutation sample."""
    concat_data = np.concatenate((x, y))
    np.random.shuffle(concat_data)

def draw_perm_reps_diff_var(x, y, size=1):
    """Generate array of permuation replicates for variance."""
    out = np.empty(size)
    for i in range(size):
        x_perm, y_perm = draw_perm_sample(x, y)
        # Adjust the np.var equation for sample variance
        x_var = np.var(x_perm) * len(x) / (len(x) - 1)
        y_var = np.var(y_perm) * len(y) / (len(y) - 1)
        out[i] = x_var - y_var
    return out
