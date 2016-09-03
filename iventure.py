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

import itertools
import StringIO
import argparse
import sys

import matplotlib.pyplot as plt
import matplotlib.cm
import matplotlib.colors
import pandas as pd

import bdbcontrib.bql_utils as bqu
import venture.shortcuts as vs

from bayeslite import BQLError
from bayeslite import BQLParseError
from bayeslite import bayesdb_open
from bayeslite import bayesdb_read_csv_file
from bayeslite import bayesdb_register_metamodel
from bayeslite import bql_quote_name

from bayeslite.core import bayesdb_get_population
from bayeslite.core import bayesdb_has_population

from bayeslite.metamodels.cgpm_metamodel import CGPM_Metamodel
from bayeslite.metamodels.crosscat import CrosscatMetamodel
from bayeslite.parse import bql_string_complete_p
from bayeslite.shell.pretty import pp_list

from bdbcontrib import Population

from cgpm.factor.factor import FactorAnalysis
from cgpm.kde.mvkde import MultivariateKde
from cgpm.knn.mvknn import MultivariateKnn
from cgpm.regressions.forest import RandomForest
from cgpm.regressions.linreg import LinearRegression
from cgpm.venturescript.vscgpm import VsCGpm
from cgpm.venturescript.vsinline import InlineVsCGpm

from IPython.core.error import UsageError
from IPython.core.magic import Magics
from IPython.core.magic import cell_magic
from IPython.core.magic import line_cell_magic
from IPython.core.magic import line_magic
from IPython.core.magic import magics_class

@magics_class
class VentureMagics(Magics):
    def __init__(self, shell):
        super(VentureMagics, self).__init__(shell)
        self._bdb = None
        self._path = None
        self._ripl = vs.make_ripl()
        # self._ripl.set_mode('church_prime')
        self._venturescript = []

    @line_cell_magic
    def venturescript(self, line, cell=None):
        script = line if cell is None else cell
        # XXX Whattakludge!
        self._venturescript.append(script)
        self._ripl.execute_program(script)

    @line_magic
    def bayesdb(self, line):
        parser = argparse.ArgumentParser()
        parser.add_argument('path', help='Path of bdb file.')
        parser.add_argument('-j', action='store_true', help='Multiprocessing.')
        args = parser.parse_args(line.split())
        if self._bdb is not None:
            self._bdb.close()
            self._bdb = None

        self._path = args.path
        self._bdb = bayesdb_open(pathname=args.path, builtin_metamodels=False)

        # Register lovecat.
        if args.j:
            import crosscat.MultiprocessingEngine as ccme
            crosscat = ccme.MultiprocessingEngine(cpu_count=None)
        else:
            import crosscat.LocalEngine as ccle
            crosscat = ccle.LocalEngine()
        metamodel = CrosscatMetamodel(crosscat)
        bayesdb_register_metamodel(self._bdb, metamodel)

        # Register cgpm.
        cgpm_registry = {
            'factor_analysis': FactorAnalysis,
            'linear_regression': LinearRegression,
            'multivariate_kde': MultivariateKde,
            'multivariate_knn': MultivariateKnn,
            'random_forest': RandomForest,
            'venturescript': self._VsCGpm,
            'inline_venturescript': InlineVsCGpm,
        }
        mm = CGPM_Metamodel(cgpm_registry, multiprocess=args.j)
        bayesdb_register_metamodel(self._bdb, mm)

    def _VsCGpm(self, outputs, inputs, rng, *args, **kwds):
        if 'source' not in kwds:
            kwds['source'] = '\n'.join(self._venturescript)
        return VsCGpm(outputs, inputs, rng, *args, **kwds)

    @line_cell_magic
    def sql(self, line, cell=None):
        query = line if cell is None else cell
        cursor = self._bdb.sql_execute(query)
        return bqu.cursor_to_df(cursor)

    @line_cell_magic
    def mml(self, line, cell=None):
        if cell is None:
            ucmds = [line]
        else:
            ucmds = cell.split('\n')
        cmds = [ucmd.encode('US-ASCII') for ucmd in ucmds]
        cmd_q = None
        bql_q = []
        for cmd in cmds:
            assert not cmd_q or not bql_q
            if cmd.isspace():
                continue
            if cmd_q:
                self._cmd(cmd_q)
                cmd_q = None
            if cmd.startswith('.'):
                if bql_q:
                    self._bql(bql_q)
                    bql_q = []
                cmd_q = cmd
            else:
                bql_q.append(cmd)
        assert not cmd_q or not bql_q
        if cmd_q:
            return self._cmd(cmd_q)
        if bql_q:
            return self._bql(bql_q)

    @line_cell_magic
    def bql(self, line, cell=None):
        if cell is None:
            ucmds = [line]
        else:
            ucmds = cell.split(';')
        cmds = [ucmd.encode('US-ASCII').strip() for ucmd in ucmds]
        result = None
        for cmd in cmds:
            if cmd.isspace() or len(cmd) == 0:
                continue
            if cmd.startswith('.'):
                result = self._cmd(cmd)
            else:
                result = self._bql([cmd])
        return result

    def _bql(self, lines):
        out = StringIO.StringIO()
        ok = False
        for line in lines:
            if ok:
                try:
                    self._bdb.execute(out.getvalue())
                except (BQLError, BQLParseError) as e:
                    sys.stderr.write('%s' % (e,))
                    return
                out = StringIO.StringIO()
                ok = False
            out.write('%s ' % (line, ))
            if out.getvalue() and bql_string_complete_p(out.getvalue()):
                ok = True
        try:
            cursor = self._bdb.execute(out.getvalue())
        except (BQLError, BQLParseError) as e:
            sys.stderr.write('%s' % (e,))
        else:
            return bqu.cursor_to_df(cursor)

    def _cmd(self, cmd):
        assert cmd[0] == '.'
        sp = cmd.find(' ')
        if sp == -1:
            sp = len(cmd)
        dot_command = cmd[1:sp].strip()
        if dot_command not in self._CMDS:
            sys.stderr.write('Unknown command: %s\n' % (dot_command,))
            return
        args = cmd[min(sp + 1, len(cmd)):]
        return self._CMDS[dot_command](self, args)

    def _cmd_csv(self, args):
        tokens = args.split()   # XXX
        if len(tokens) != 2:
            sys.stderr.write('Usage: .csv <table> </path/to/data.csv>\n')
            return
        table = tokens[0]
        path = tokens[1]
        bayesdb_read_csv_file(self._bdb, table, path, header=True,
            create=True, ifnotexists=False)

    def _cmd_nullify(self, args):
        tokens = args.split()   # XXX
        if len(tokens) != 2:
            sys.stderr.write('Usage: .nullify <table> <value>')
        table = tokens[0]
        expression = tokens[1]
        value = self._bdb.execute('SELECT %s' % (expression,)).fetchvalue()
        bqu.nullify(self._bdb, table, value)

    def _cmd_table(self, args):
        table = args
        qt = bql_quote_name(table)
        cursor = self._bdb.sql_execute('PRAGMA table_info(%s)' % (table,))
        return bqu.cursor_to_df(cursor)

    def _cmd_population(self, args):
        population = args
        if not bayesdb_has_population(self._bdb, population):
            raise ValueError('No such population: %r' % (population,))
        population_id = bayesdb_get_population(self._bdb, population)
        cursor = self._bdb.sql_execute('''
            SELECT 'variable' AS type, name, stattype AS value
                FROM bayesdb_variable
                WHERE population_id = :population_id
            UNION
            SELECT 'generator' AS type, name, metamodel AS value
                FROM bayesdb_generator
                WHERE population_id = :population_id
        ''', {'population_id': population_id})
        return bqu.cursor_to_df(cursor)

    # Plotting.

    def _cmd_bar(self, query):
        import bdbcontrib.plot_utils as bpu
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        bpu.barplot(self._bdb, df)

    def _cmd_heatmap(self, query):
        import bdbcontrib.plot_utils as bpu
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        bpu.heatmap(df)

    def _cmd_histogram(self, query):
        import bdbcontrib.plot_utils as bpu
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        bpu.histogram(self._bdb, df)

    def _cmd_plot(self, query):
        import bdbcontrib.plot_utils as bpu
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        bpu.pairplot(self._bdb, df)

    def _cmd_scatter(self, query):
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        scatter(df)

    def _cmd_hist(self, query):
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        hist(df)

    def _cmd_histn(self, query):
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        hist(df, normed=True)

    _CMDS = {
        'bar': _cmd_bar,
        'csv': _cmd_csv,
        'heatmap': _cmd_heatmap,
        'histogram': _cmd_histogram,
        'hist': _cmd_hist,
        'histn': _cmd_histn,
        'nullify': _cmd_nullify,
        'plot': _cmd_plot,
        'population': _cmd_population,
        'scatter': _cmd_scatter,
        'table': _cmd_table,
    }


def scatter(df, ax=None):
    """Scatter the NUMERICAL data points in df.

    If df has two columns, then a regular scatter plot is produced. If df has
    three columns, then the final column is used as the label for each data
    point.
    """
    if ax is None:
        fig, ax = plt.subplots()
    if df.shape[1] not in [2, 3]:
        raise ValueError('Only two or three columns allowed: %s' % df.columns)
    labels, colors = _retrieve_labels_colors(
        df.iloc[:,2] if df.shape[1] == 3 else [0] * len(df))
    for label, color in zip(labels, colors):
        points = _filter_points(df, labels, label)
        ax.scatter(points.iloc[:,0], points.iloc[:,1], color=color, label=label)
    ax.set_xlabel(df.columns[0], fontweight='bold')
    ax.set_ylabel(df.columns[1], fontweight='bold')
    ax.grid()
    # Plot the legend.
    if len(labels) > 1:
        _plot_legend(fig, ax)
    return fig


def hist(df, ax=None, normed=None):
    """Histogram the NOMINAL data points in df.

    If df has one column, then a regular histogram is produced. If df has two
    columns, then the final column is used as the label for each data point.
    """
    if ax is None:
        fig, ax = plt.subplots()
    if df.shape[1] not in [1, 2]:
        raise ValueError('Only one or two columns allowed: %s' % df.columns)
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
        normalizer = float(sum(raw_counts)) if normed else 1.
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


def _plot_legend(fig, ax):
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), framealpha=0)


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


def load_ipython_extension(ipython):
    ipython.register_magics(VentureMagics)
