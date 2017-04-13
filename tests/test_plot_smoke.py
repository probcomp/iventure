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


HISTNOM_DF = {
    'DF1': pd.DataFrame(['foo', 'foo', 'bar', 'foo', 'quux']),
    'DF2': pd.DataFrame([('f',0), ('f',1), ('b',2), ('f',3), ('q',4)]),
}

HISTNOM_NORMED = {
    'None': None,
    'True': True,
    'False': False,
}


@pytest.mark.parametrize('axname,dfname,normedname',
    [(axname, dfname, normedname)
        for axname in sorted(AX.keys())
        for dfname in sorted(HISTNOM_DF.keys())
        for normedname in sorted(HISTNOM_NORMED.keys())])
def test_histogram_nominal_smoke(axname, dfname, normedname):
    ax = AX[axname]()
    df = HISTNOM_DF[dfname]
    normed = HISTNOM_NORMED[normedname]
    kwargs = {} if normed is None else {'normed': normed}
    uplt.histogram_nominal(df, ax=ax, **kwargs)


HISTNUM_DF = {
    'DF1': pd.DataFrame([41.2, 87, -3, -3, 41.2]),
    'DF2': pd.DataFrame([(41.2,'x'),(87,'y'),(-3,'z'),(-3,'w'),(41.2,'v')]),
}

HISTNUM_NORMED = {
    'None': None,
    'True': True,
    'False': False,
}


@pytest.mark.parametrize('axname,dfname,normedname',
    [(axname, dfname, normedname)
        for axname in sorted(AX.keys())
        for dfname in sorted(HISTNUM_DF.keys())
        for normedname in sorted(HISTNUM_NORMED.keys())])
def test_histogram_numerical_smoke(axname, dfname, normedname):
    if dfname == 'DF1':
        # XXX pytest.xfail() doesn't fail if the test passes.  Grr.
        pytest.xfail('automatic labelling is broken')
    ax = AX[axname]()
    df = HISTNUM_DF[dfname]
    normed = HISTNUM_NORMED[normedname]
    kwargs = {} if normed is None else {'normed': normed}
    uplt.histogram_numerical(df, ax=ax, **kwargs)


CHMAP_DF = {
    'DF': pd.DataFrame([
        ['foo', 'foo', 42],
        ['foo', 'bar', 41],
        ['foo', 'baz', 43],
        ['bar', 'foo', 48],
        ['bar', 'bar', 40],
        ['bar', 'baz', 47],
        ['baz', 'foo', 39],
        ['baz', 'bar', 40],
        ['baz', 'baz', 41],
    ]),
}


@pytest.mark.parametrize('axname,dfname',
    [(axname, dfname)
        for axname in sorted(AX.keys())
        for dfname in sorted(CHMAP_DF.keys())])
def test_clustermap_smoke(axname, dfname):
    ax = AX[axname]()
    df = CHMAP_DF[dfname]
    # XXX figsize
    uplt.clustermap(df, ax=ax)

@pytest.mark.parametrize('axname,dfname',
    [(axname, dfname)
        for axname in sorted(AX.keys())
        for dfname in sorted(CHMAP_DF.keys())])
def test_heatmap_smoke(axname, dfname):
    ax = AX[axname]()
    df = CHMAP_DF[dfname]
    # XXX figsize
    uplt.heatmap(df, ax=ax)
