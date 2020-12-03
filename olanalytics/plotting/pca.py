import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from olutils import DFT, read_params

from .multiplot import plotiter

LIGHT_GREY = (220/255, 220/255, 220/255)
DFT_PALETTE = None

JET_CMAP = plt.get_cmap('jet')
PLOT_KWARGS = {'alpha' : 0.3, 's' : 20, 'marker':'+', 'color': LIGHT_GREY}


def jet_colors(n):
    return JET_CMAP(np.linspace(0, 1.0, n))


def get_colors(n, palette=DFT):
    """Return n colors given the reference palette"""
    palette = None if palette is DFT else palette
    if callable(palette):
        palette = palette(n)
    return sns.color_palette(palette, n)


def plot_projection_base(T, c1, c2, **kwargs):
    """Plot projection of transformed data on given principal components"""
    plot_kwargs = read_params(kwargs, PLOT_KWARGS)
    plt.scatter(
        T[:, c1-1],
        T[:, c2-1],
        **plot_kwargs,
    )


def plot_projection(T, c1, c2,
                    targets=None, column=None, w_others=False,
                    other_color=DFT, other_alpha=DFT, palette=DFT):
    """Plot projection of transformed data on given principal components

    Args:
        T (numpy.ndarray)   : Transformed data
        c1 (int)            : Number of first principal component (starts with 1)
        c2 (int)            : Number of second principal component (starts with 1)

        targets (list|int)      : color dots related to target-values
        column (pandas.Series)  : column to read to identify dots
        w_others (bool)         : also plot dots not within targets

        other_color (tuple)     : color of other dots
        other_alpha (float)     : alpha of other dots
        palette (str|iterable|callable)  : palette to use to create colors
            @see `https://seaborn.pydata.org/tutorial/color_palettes.html`
            examples: None (dft), "cubehelix", "Spectral", jet_colors
    """
    with_targets = isinstance(targets, np.ndarray) or targets is not None
    if with_targets:
        assert column is not None, "When targets is given, column associated to T must be given"
        column.reset_index(drop=True, inplace=True)  # We want column index to match T indexes
    else:
        w_others = False

    if isinstance(targets, int):
        targets = column.value_counts().iloc[:targets].index
        targets = list(targets)

    plt.xlabel(f"PC_{c1}", fontsize=15)
    plt.ylabel(f"PC_{c2}", fontsize=15)
    plt.title('2 component PCA', fontsize=20)

    if w_others:
        indexes = column[np.logical_not(column.isin(targets))].index
        plot_projection_base(
            T[indexes], c1, c2,
            color=other_color,
            alpha=other_alpha,
        )
    if with_targets:
        colors = get_colors(len(targets), palette=palette)
        for target, color in zip(targets, colors):
            indexes = column[column == target].index
            plot_projection_base(T[indexes], c1, c2, color=color)
        leg = plt.legend((["others"] if w_others else []) + list(targets))
        for lh in leg.legendHandles:
            lh.set_alpha(1)
    else:
        plot_projection_base(T, c1, c2, color=get_colors(1, palette=palette)[0])
    plt.grid()


def plot_projections(T, nb_graphs=4, ncols=2, **kwargs):
    """Plot {nb_graphs} pca-projections of X on PC

    2 PC per projection
    """
    for i in plotiter(range(0, nb_graphs), n_cols=ncols):
        plot_projection(T, 2*i+1, 2*i+2, **kwargs)
