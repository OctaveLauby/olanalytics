import matplotlib.pyplot as plt


def set_size(width=17, height=4):
    """Pretty doll function to reshape plot box in notebook"""
    plt.rcParams['figure.figsize'] = [width, height]


def set_style(style='seaborn-deep'):
    """"Set plot style"""
    try:
        plt.style.use(style)
    except OSError:
        raise ValueError(
            f"Style {style} not available"
            f": Check plt.style.available for list of available styles"
        )
