olanalytics
---



# Introduction

The module ***olanalytics*** provide common analytics operations such as:

> TO BE DOCUMENTED



## Installation

One can install olutils using pip install command:

    ```bash
    pip install olanalytics
    ```

## Usage

> TO BE DOCUMENTED


Multi-plotting:

```python
import matplotlib.pyplot as plt
import numpy as np

from olanalytics import plotiter

for i in plotiter(range(5), n_cols=3):
    x = [i + k/10 for k in range(10)]
    y = [np.sin(xk) for xk in x]
    plt.plot(x, y)
```
