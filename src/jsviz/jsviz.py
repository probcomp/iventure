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
    js_src = resource_string('iventure.jsviz', 'iventure-jsviz.js')
    loader_src = resource_string('iventure.jsviz', 'loader.js')
    return Javascript(js_src + ';' + loader_src)


def enable_dev_inline(host = 'localhost', port = '9999'):
    """Enable inline JavaScript using the dev server for iventure-jsviz"""
    script = '''
var cell = element.is('.output_subarea') ? element : element.next();
window.iventureReady = new Promise(resolve => {{
    $.getScript('http://{host}:{port}/iventure-jsviz.js', function() {{
        cell.append('<p>Loaded iventure-jsviz dev mode from {host}:{port}</p>');
        cell.append('<p>Version: ' + iventureJsviz.VERSION + '</p>');
        resolve();
    }})
}});
    '''
    return Javascript(script.format(host=host, port=port))


def whenReady(script):
    """execute your JS script when iventure-jsviz is ready"""
    return Javascript("""
        var cell = element.is('.output_subarea') ? element : element.next();
        if (typeof iventureReady === 'undefined') {
          throw new Error('iventure-jsviz not loaded, did you enable_inline?');
        }
        iventureReady.then(function() {
        """ + script + """
        })
        .catch(function(error) {
          cell.append('Error Loading Viz:');
          cell.append($('<pre>').text(error.stack));
          console.error(error);
        })
    """)


def interactive_bar(df):
    """Create an interactive barplot visualization."""
    return whenReady(
        'interactive_bar(cell, %s)' % (
            df.to_json(orient='split')
        )
    )


def interactive_depprob(df_dep, df_data=None, schema=None):
    """Create an interactive dependence probability visualization."""
    assert len(df_dep.columns) == 3
    if df_data is not None and schema is not None:
        return whenReady(
            'interactive_depprob(cell, %s, %s, %s)' % (
                df_dep.to_json(orient='split'),
                df_data.to_json(orient='records'),
                schema
            )
        )
    else:
        return whenReady(
            'interactive_depprob(cell, %s)' % (
                df_dep.to_json(orient='split')
            )
        )


def interactive_heatmap(df):
    """Create an interactive heatmap visualization."""

    pivot = df.pivot(
        index=df.columns[-3],
        columns=df.columns[-2],
        values=df.columns[-1],
    )
    pivot.fillna(0, inplace=True)
    D = pivot.as_matrix()
    ordering = utils_plot._clustermap_ordering(D)
    labels = list(np.asarray(pivot.columns)[ordering[0]])
    return whenReady(
        'interactive_heatmap(cell, %s, %s)' % (
            df.to_json(orient='split'),
            json.dumps(labels)
        )
    )


def interactive_pairplot(df, schema):
    """Create an interactive pairplot visualization."""
    return whenReady(
        'interactive_pairplot(cell, %s, %s)' % (
            df.to_json(orient='split'),
            json.dumps(schema),
        )
    )


def interactive_scatter(df):
    """Create an interactive scatter plot visualization."""
    df.dropna(inplace=True)
    return whenReady(
        'interactive_scatter(cell, %s)' % (
            df.to_json(orient='split')
        )
    )
