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

import pandas as pd

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

    # Plot the legend.
    if len(labels) > 1:
        _plot_legend(fig, ax)

    # Adjust limits.
    if kwargs:
        _handle_kwargs(ax, **kwargs)

    return fig


def bar(df, ax=None):
    """Histogram the NOMINAL data points in df.

    If df has one column, then a regular histogram is produced. If df has two
    columns, then the final column is used as the label for each data point.
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

    ax.bar([x - .5 for x in xrange(df.shape[0])], df.ix[:, 1].values, alpha=0.7)

    ax.set_xticks(range(df.shape[0]))
    ax.set_xticklabels(xlabels, rotation=90)
    ax.set_xlim([-1, df.shape[0] - .5])

    ax.set_xlabel(df.columns[0])
    ax.set_ylabel(df.columns[1])
    ax.grid()

    return fig

def hist(df, ax=None, **kwargs):
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

    # Plot the legend.
    if len(labels) > 1:
        _plot_legend(fig, ax)

    return fig


def histogram(df, ax=None, **kwargs):
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

    # Plot the legend.
    if len(labels) > 1:
        _plot_legend(fig, ax)

    # Adjust limits.
    if kwargs:
        _handle_kwargs(ax, **kwargs)
    return fig


def _preprocess_dataframe(df):
    df = df.dropna()
    if len(df) == 0:
        raise ValueError('No valid values in dataframe!')
    return df


def _plot_legend(fig, ax):
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), framealpha=0)


def _handle_kwargs(ax, **kwargs):
    # Adjust axes if necessary.
    if 'xmin' in kwargs:
        ax.set_xlim([float(kwargs['xmin']), ax.get_xlim()[1]])
    if 'xmax' in kwargs:
        ax.set_xlim([ax.get_xlim()[0], float(kwargs['xmax'])])
    if 'ymin' in kwargs:
        ax.set_ylim([float(kwargs['ymin']), ax.get_ylim()[1]])
    if 'ymax' in kwargs:
        ax.set_ylim([ax.get_ylim()[0], float(kwargs['ymax'])])
    # Change to logarithmic scales.
    if 'xlog' in kwargs:
        ax.set_xscale('log', basex=int(kwargs['xlog']))
    if 'ylog' in kwargs:
        ax.set_yscale('log', basey=int(kwargs['ylog']))

def _unroll_dataframe(df):
    if len(df.columns) == 0:
        raise ValueError('At least one column required: %s' % df.columns)
    new_df = pd.concat(
        [pd.DataFrame([[value, col] for value in df[col]])
        for col in df.columns])
    new_df.columns = ['value', 'label']
    return new_df


def _filter_points(df, labels, label):
    return df[df.iloc[:,-1]==label] if len(labels) > 1 else df


def _retrieve_labels_colors(items):
    # Extract unique labels.
    labels = set(items)
    # Retrieve the colors.
    mapper = matplotlib.cm.ScalarMappable(
        cmap=matplotlib.cm.jet,
        norm=matplotlib.colors.Normalize(vmin=0, vmax=len(labels)-1))
    colors = mapper.to_rgba(xrange(len(labels)))
    return labels, colors

