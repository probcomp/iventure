# -*- coding: utf-8 -*-

#   Copyright (c) 2010-2016, MIT Probabilistic Computing Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


import matplotlib.pyplot as plt
import pandas as pd
import pytest


import iventure.utils_plot as uplt


AX = {
    'None': lambda: None,
    'subplots': lambda: plt.subplots()[1]
}


SCATTER_DF = {
    'DF1': pd.DataFrame([[1], [3], [5], [7]]),
    'DF2': pd.DataFrame([[1,2], [3,4], [5,6], [7,8]]),
    'DF3': pd.DataFrame([[1,2,'x'], [3,4,'y'], [5,6,'z'], [7,8,'w']]),
}

SCATTER_COLORS = {
    'None': None,
    'COLOR': ['red', 'green', 'blue', 'yellow'],
}


@pytest.mark.parametrize('axname,dfname,colorsname',
    [(axname, dfname, colorsname)
        for axname in sorted(AX.keys())
        for dfname in sorted(SCATTER_DF.keys())
        for colorsname in sorted(SCATTER_COLORS.keys())])
def test_scatter_smoke(axname, dfname, colorsname):
    df = SCATTER_DF[dfname]
    colors = SCATTER_COLORS[colorsname]
    ax = AX[axname]()
    kwargs = {} if colors is None else {'colors': colors}
    if dfname == 'DF1':
        with pytest.raises(ValueError):
            uplt.scatter(df, ax=ax, **kwargs)
    elif dfname == 'DF2' and colorsname == 'COLOR':
        # Can't color without labels.
        pass
    else:
        uplt.scatter(df, ax=ax, **kwargs)


BAR_DF = {
    'toosmall': pd.DataFrame([[1],[3],[5]]),
    'goldilocks': pd.DataFrame([[1,2],[3,4],[5,6]]),
    'toolarge': pd.DataFrame([[1,2,'x'],[3,4,'y'],[5,6,'z']]),
}


@pytest.mark.parametrize('axname,dfname',
    [(axname, dfname)
        for axname in sorted(AX.keys())
        for dfname in sorted(BAR_DF.keys())])
def test_bar_smoke(axname, dfname):
    ax = AX[axname]()
    df = BAR_DF[dfname]
    if dfname != 'goldilocks':
        with pytest.raises(ValueError):
            uplt.bar(df, ax=ax)
    else:
        uplt.bar(df, ax=ax)


@pytest.mark.parametrize('axname,dfname',
    [(axname, dfname)
        for axname in sorted(AX.keys())
        for dfname in sorted(BAR_DF.keys())])
def test_barh_smoke(axname, dfname):
    ax = AX[axname]()
    df = BAR_DF[dfname]
    if dfname != 'goldilocks':
        with pytest.raises(ValueError):
            uplt.barh(df, ax=ax)
    else:
        uplt.barh(df, ax=ax)
