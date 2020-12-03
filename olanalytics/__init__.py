from .dt import (
    DatetimeDescription,
    dtloc2pos,
)
from .generators import (
    CustomCurve,
    CustomTimedCurve,
    timeseries,
)
from .search import (
    closest,
    previous,
)
from .tracking import trackedfunc

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
