from .search import (
    closest,
    previous,
)

try:
    import matplotlib
except ModuleNotFoundError:
    pass
else:
    from .plotting import (
        decorate,
        DFT_FONT_PARAMS,
        DFT_PARAMS,
        MultiPlotIterator,
        PlotDesigner,
        plotiter,
    )
