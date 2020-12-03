import matplotlib.pyplot as plt


def set_size(width=17, height=4):
    """Pretty doll function to reshape plot box in notebook"""
    plt.rcParams['figure.figsize'] = [width, height]


def set_style(style='seaborn-deep'):
    """"Set plot style"""
    plt.style.use(style)
