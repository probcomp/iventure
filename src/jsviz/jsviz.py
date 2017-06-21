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


import json

from pkg_resources import resource_string

import numpy as np

from IPython.display import Javascript

from iventure import utils_plot


def enable_inline():
    """Enable inline JavaScript code to execute in an iventure notebook."""
    js_src = resource_string('iventure.jsviz', 'inline.js')
    return Javascript(js_src)

def interactive_bar(df):
    """Create an interactive barplot visualization."""
    js_src = resource_string('iventure.jsviz', 'bar.js')
    return Javascript(
        js_src \
        + ';bar(' \
        + df.to_json(orient='split') \
        + ')'
    )

def interactive_depprob(df_dep, df_data=None, schema=None):
    """Create an interactive dependence probability visualization."""
    js_src = resource_string('iventure.jsviz', 'depprob.js')
    assert len(df_dep.columns) == 3
    df_dep.columns = ['name0', 'name1', 'value']
    if df_data is not None and schema is not None:
        return Javascript(
            js_src \
            + 'depprob_demo(' \
            + df_dep.to_json()
            + ', ' \
            + df_data.to_json(orient='records') \
            + ', ' \
            + schema \
            + ')'
        )
    else:
        return Javascript(
            js_src \
            + 'depprob_demo(' \
            + df_dep.to_json() \
            + ')'
        )

def interactive_heatmap(df):
    """Create an interactive heatmap visualization."""
    js_src = resource_string('iventure.jsviz', 'heatmap.js')

    pivot = df.pivot(
        index=df.columns[-3],
        columns=df.columns[-2],
        values=df.columns[-1],
    )
    pivot.fillna(0, inplace=True)
    D = pivot.as_matrix()
    ordering = utils_plot._clustermap_ordering(D)
    labels = list(np.asarray(pivot.columns)[ordering[0]])
    return Javascript(
        js_src \
        + 'heatmap(' \
        + df.to_json(orient='split') \
        + ',' \
        + json.dumps(labels) \
        + ')'
    )

def interactive_pairplot(df, schema):
    """Create an interactive pairplot visualization."""
    js_src = resource_string('iventure.jsviz', 'pairplot.js')
    return Javascript(
        js_src \
        + ';pairplot(' \
        + df.to_json(orient='split') \
        + ',' \
        + json.dumps(schema) \
        + ')'
    )

def interactive_scatter(df):
    """Create an interactive scatter plot visualization."""
    df.dropna(inplace=True)
    js_src = resource_string('iventure.jsviz', 'scatter.js')
    return Javascript(
        js_src \
        + ';scatter(' \
        + df.to_json(orient='split') \
        + ')'
    )
