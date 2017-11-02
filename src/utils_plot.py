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

import matplotlib.cm
import matplotlib.colors
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

from iventure import jsviz


def density(df, ax=None, **kwargs):
    """Density plot of the data in df.

    If df has one column, then a regular kdeplot is produced. If df has two
    columns, then the final column is used as the label for each data point.
    """
    if df.shape[1] not in [1, 2]:
        raise ValueError('Only one or two columns allowed: %s' % df.columns)
    else:
        df = _preprocess_dataframe(df)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    labels, colors = _retrieve_labels_colors(
        df.iloc[:,1] if df.shape[1] == 2 else [0] * len(df))
    if 'colors' in kwargs:
        assert len(kwargs['colors']) == len(labels)
        colors = kwargs['colors']
    if 'shade' in kwargs:
        assert kwargs['shade'] in ['True', 'False']
        if kwargs['shade'] == 'False':
            shade = False
    else:
        shade = True
    if 'rug' in kwargs:
        assert kwargs['rug'] in ['True', 'False']
        if kwargs['rug'] == 'False':
            rug = False
    else:
        rug = True
    from .seaborn import apionly as sns
    sns.set_style('white')
    for label, color in zip(labels, colors):
        points = _filter_points(df, labels, label)
        sns.kdeplot(
            points.iloc[:,0], color=color, shade=shade, ax=ax, legend=False)
        if rug:
            sns.rugplot(points.iloc[:,0], color=color, ax=ax)
    ax.set_xlabel(df.columns[0], fontweight='bold')
    ax.set_ylabel('Density', fontweight='bold')
    ax.grid()

    # Adjust limits.
    if kwargs:
        _handle_kwargs(ax, **kwargs)

    ax.get_figure().set_size_inches(4, 3.5)

    return fig

def scatter(df, ax=None, **kwargs):
    """Scatter the NUMERICAL data points in df.

    If df has two columns, then a regular scatter plot is produced. If df has
    three columns, then the final column is used as the label for each data
    point.
    """
    if df.shape[1] not in [2, 3]:
        raise ValueError('Only two or three columns allowed: %s' % df.columns)
    else:
        df = _preprocess_dataframe(df)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    labels, colors = _retrieve_labels_colors(
        df.iloc[:,2] if df.shape[1] == 3 else [0] * len(df))
    if 'colors' in kwargs:
        assert len(kwargs['colors']) == len(labels)
        colors = kwargs['colors']
    for label, color in zip(labels, colors):
        points = _filter_points(df, labels, label)
        ax.scatter(points.iloc[:,0], points.iloc[:,1], color=color, label=label)
    ax.set_xlabel(df.columns[0], fontweight='bold')
    ax.set_ylabel(df.columns[1], fontweight='bold')
    ax.grid()

    # Plot the legend if there are three columns.
    if df.shape[1] == 3:
        _plot_legend(fig, ax)

    # Adjust limits.
    if kwargs:
        _handle_kwargs(ax, **kwargs)

    return fig


def bar(df, ax=None, **kwargs):
    """Vertical barplot of data in df.

    First column is (nominal) names, second column is (numerical) values.
    """
    if df.shape[1] != 2:
        raise ValueError('Two columns required: %s.' % (df.columns,))
    else:
        df = _preprocess_dataframe(df)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    xlabels = df.ix[:,0].values
    if len(set(xlabels)) != len(xlabels):
        raise ValueError('Unique nominal values required: %s.' % (xlabels,))

    ax.bar([x-.5 for x in xrange(df.shape[0])], df.ix[:,1].values, alpha=0.7)

    ax.set_xticks(range(df.shape[0]))
    ax.set_xticklabels(xlabels, rotation=90)
    ax.set_xlim([-1, df.shape[0] - .5])

    ax.set_xlabel(df.columns[0])
    ax.set_ylabel(df.columns[1])
    ax.grid()

    return fig


def barh(df, ax=None, **kwargs):
    """Horizontal barplot of data in df.

    First column is (nominal) names, second column is (numerical) values.
    """
    if df.shape[1] != 2:
        raise ValueError('Two columns required: %s.' % (df.columns,))
    else:
        df = _preprocess_dataframe(df)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()

    ylabels = df.ix[:,0].values
    if len(set(ylabels)) != len(ylabels):
        raise ValueError('Unique nominal values required: %s.' % (ylabels,))

    ax.barh([x-.5 for x in xrange(df.shape[0])], df.ix[:,1].values, alpha=0.7)

    ax.set_yticks(range(df.shape[0]))
    ax.set_yticklabels(ylabels)
    ax.set_ylim([-1, df.shape[0]-.5])
    ax.set_xlim([None, 1.1 * df.ix[:,1].max()])

    ax.set_ylabel(df.columns[0])
    ax.set_xlabel(df.columns[1])
    ax.grid()

    return fig


def histogram_nominal(df, ax=None, **kwargs):
    """Histogram the NOMINAL data points in df.

    If df has one column, then a regular histogram is produced. If df has two
    columns, then the final column is used as the label for each data point.
    """
    if df.shape[1] not in [1, 2]:
        raise ValueError('Only one or two columns allowed: %s' % df.columns)
    else:
        df = _preprocess_dataframe(df)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    # Retrieve the nominal values, sorted by overall frequency.
    nominals = df.iloc[:,0].value_counts().index.tolist()
    # Retrieve the labels.
    labels, colors = _retrieve_labels_colors(
        df.iloc[:,1] if df.shape[1] == 2 else [0] * len(df))
    # Compute the offset for each label.
    offset = len(labels)/2 + len(labels) % 2
    width = 0.25
    # Compute the distance between the bars based on the number of labels.
    spacing = len(labels) / 3 + 1
    indices = range(0, spacing*len(nominals), spacing)
    assert len(indices) == len(nominals)
    # Histogram each series.
    for i, (label, color) in enumerate(zip(labels, colors)):
        points = _filter_points(df, labels, label)
        raw_counts = points.iloc[:,0].value_counts()
        normalizer = float(sum(raw_counts)) if 'normed' in kwargs else 1.
        counts = [raw_counts.get(n, 0) / normalizer for n in nominals]
        ax.barh(
            [index - 0.2*offset + i*width for index in indices],
            counts, width, color=color, alpha=.7, label=label)
    # Fix up the axes and their labels.
    ax.set_xlabel('Frequency', fontweight='bold')
    ax.set_ylabel(df.columns[0], fontweight='bold')
    ax.set_yticks(indices)
    ax.set_yticklabels(nominals, fontweight='bold')
    # Fix up the x-axis.
    largest = ax.get_xlim()[1]
    ax.set_xlim([0, 1.1*largest])
    ax.grid()

    # Plot the legend if there are two columns.
    if df.shape[1] == 2:
        _plot_legend(fig, ax)

    return fig


def histogram_numerical(df, ax=None, **kwargs):
    """Histogram the NUMERICAL data points in df.

    If df has one column, then a regular histogram is produced. If df has two
    columns, then the final column is used as the label for each data point.
    """
    if df.shape[1] not in [1, 2]:
        raise ValueError('Only one or two columns allowed: %s' % df.columns)
    else:
        df = _preprocess_dataframe(df)
    if ax is None:
        fig, ax = plt.subplots()
    else:
        fig = ax.get_figure()
    labels, colors = _retrieve_labels_colors(
        df.iloc[:,1] if df.shape[1] == 2 else [0] * len(df))
    data = [df[df.iloc[:,1]==l].iloc[:,0].values for l in labels]\
        if df.shape[1] == 2 else df.iloc[:,0]
    ax.hist(
        data, 10, normed=kwargs.pop('normed', None), histtype='bar',
        color=colors, label=labels, alpha=0.7)
    # Fix up the axes and their labels.
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.set_xlabel(df.columns[0], fontweight='bold')
    # Fix up the y-axis.
    largest = ax.get_ylim()[1]
    ax.set_ylim([0, 1.1*largest])
    ax.grid()

    # Plot the legend if there are two columns.
    if df.shape[1] == 2:
        _plot_legend(fig, ax)

    # Adjust limits.
    if kwargs:
        _handle_kwargs(ax, **kwargs)
    return fig


def clustermap(df, ax=None, **kwargs):
    """Plot a clustermap by pivoting the last 3 columns of `df`.

    The `df` is typically returned from an ESTIMATE PAIRWISE query in BQL.
    """
    if len(df.columns) < 3:
        raise ValueError('At least three columns requried: %s' % (df.columns,))
    # Pivot the matrix.
    pivot = df.pivot(
        index=df.columns[-3],
        columns=df.columns[-2],
        values=df.columns[-1],
    )
    pivot.fillna(0, inplace=True)
    # Check if all values are between 0 and 1 to set vmin and vmax.
    (vmin, vmax) = (None, None)
    if all(0 <= v <= 1 for v in df.iloc[:,-1]):
        (vmin, vmax) = (0, 1)
    zmatrix =  _clustermap(
        pivot.as_matrix(),
        xticklabels=pivot.columns.tolist(),
        yticklabels=pivot.index.tolist(),
        vmin=vmin,
        vmax=vmax
    )
    # Heuristics for the size.
    figsize = kwargs.pop('figsize', None)
    if figsize is None:
        half_root_col = (df.shape[0] ** .5) / 2.
        figsize = (half_root_col, .8 * half_root_col)
    zmatrix.fig.set_size_inches(figsize)
    return zmatrix


def heatmap(df, ax=None, **kwargs):
    """Plot a heatmap by pivoting the last 3 columns of `df`.

    The `df` is a "tidy-dataframe" i.e. from an ESTIMATE PAIRWISE query in BQL.
    """
    if len(df.columns) < 3:
        raise ValueError('At least three columns requried: %s' % (df.columns,))
    from .seaborn import apionly as sns
    # Pivot the matrix.
    pivot = df.pivot(
        index=df.columns[-3],
        columns=df.columns[-2],
        values=df.columns[-1],
    )
    pivot.fillna(0, inplace=True)
    # Check if all values are between 0 and 1 to set vmin and vmax.
    (vmin, vmax) = (None, None)
    if all(0 <= v <= 1 for v in df.iloc[:,-1]):
        (vmin, vmax) = (0, 1)
    # Apply the optimal ordering from a clustermap.
    D = pivot.as_matrix()
    (xordering, yordering) = _clustermap_ordering(D)
    xticklabels = np.asarray(pivot.columns)[xordering]
    yticklabels = np.asarray(pivot.index)[yordering]
    D = D[:,xordering]
    D = D[yordering,:]
    # Apply 0-1 binary thresholding.
    threshold = kwargs.get('threshold', None)
    if threshold is not None:
        D[D<threshold] = 0
        D[D>=threshold] = 1
    # Plot the heatmap.
    ax = sns.heatmap(
        D,
        xticklabels=xticklabels,
        yticklabels=yticklabels,
        linewidths=0.2,
        cbar=kwargs.get('cbar', True),
        cmap=kwargs.get('cmap', 'BuGn'),
        ax=ax,
        vmin=vmin,
        vmax=vmax,
    )
    # Heuristics for the size.
    figsize = kwargs.pop('figsize', None)
    if figsize is None:
        half_root_col = (df.shape[0] ** .5) / 2.5
        figsize = (half_root_col, .8 * half_root_col)
    ax.get_figure().set_size_inches(figsize)
    return ax


def _clustermap(
        D, xticklabels=None, yticklabels=None, vmin=None, vmax=None, **kwargs):
    from . import seaborn as sns
    sns.set_style('white')
    if xticklabels is None:
        xticklabels = range(D.shape[0])
    if yticklabels is None:
        yticklabels = range(D.shape[1])
    zmatrix = sns.clustermap(
        D,
        xticklabels=xticklabels,
        yticklabels=yticklabels,
        linewidths=0.2,
        cmap='BuGn',
        vmin=vmin,
        vmax=vmax,
    )
    plt.setp(zmatrix.ax_heatmap.get_yticklabels(), rotation=0)
    plt.setp(zmatrix.ax_heatmap.get_xticklabels(), rotation=90)
    return zmatrix


def _clustermap_ordering(D):
    """Returns the ordering of variables in D according to the clustermap."""
    zmatrix = _clustermap(D)
    plt.close(zmatrix.fig)
    xordering = zmatrix.dendrogram_col.reordered_ind
    yordering = zmatrix.dendrogram_row.reordered_ind
    return (xordering, yordering)


def tidy_pairwise(array, index=None, columns=None, xlabel=None, ylabel=None,
        vlabel=None):
    """Convert a pairwise matrix into a tidy data frame."""
    if index is None:
        index = range(np.shape(array)[0])
    if columns is None:
        columns = range(np.shape(array)[0])
    assert array.shape == (len(index), len(columns))
    xlabel = xlabel or 'var0'
    ylabel = ylabel or 'var1'
    vlabel = vlabel or 'value'
    data = [
        (ind, col, array[i,j])
        for i, ind in enumerate(index)
        for j, col in enumerate(columns)
    ]
    return pd.DataFrame(data, columns=[xlabel, ylabel, vlabel])


def _preprocess_dataframe(df):
    """Drops null values from df, and returns an error if no rows remain."""
    df = df.dropna()
    if len(df) == 0:
        raise ValueError('No valid values in dataframe!')
    return df


def _plot_legend(fig, ax):
    """Plots legend on the side of a figure."""
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), framealpha=0)


def _handle_kwargs(ax, **kwargs):
    """Handles keyword arguments for scales."""
    # Adjust axes?
    if 'xmin' in kwargs:
        ax.set_xlim([float(kwargs['xmin']), ax.get_xlim()[1]])
    if 'xmax' in kwargs:
        ax.set_xlim([ax.get_xlim()[0], float(kwargs['xmax'])])
    if 'ymin' in kwargs:
        ax.set_ylim([float(kwargs['ymin']), ax.get_ylim()[1]])
    if 'ymax' in kwargs:
        ax.set_ylim([ax.get_ylim()[0], float(kwargs['ymax'])])
    # Change to logarithmic scales?
    if 'xlog' in kwargs:
        ax.set_xscale('log', basex=int(kwargs['xlog']))
    if 'ylog' in kwargs:
        ax.set_yscale('log', basey=int(kwargs['ylog']))
    if 'xlabel' in kwargs:
        ax.set_xlabel(kwargs['xlabel'], fontweight='bold')
    if 'ylabel' in kwargs:
        ax.set_ylabel(kwargs['ylabel'], fontweight='bold')


def _filter_points(df, labels, label):
    """Returns all rows with the specified label (using last column in df)."""
    return df[df.iloc[:,-1]==label] if len(labels) > 1 else df


def _retrieve_labels_colors(items):
    """Returns unique entries (and assigns a color to each) from a list."""
    # Extract unique labels.
    labels = sorted(set(items))
    # Retrieve the colors.
    mapper = matplotlib.cm.ScalarMappable(
        cmap=matplotlib.cm.jet,
        norm=matplotlib.colors.Normalize(vmin=0, vmax=len(labels)-1))
    colors = mapper.to_rgba(xrange(len(labels)))
    return labels, colors
