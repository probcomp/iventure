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

import StringIO
import argparse
import getpass
import re
import sys
import traceback

from collections import OrderedDict


from bayeslite import bayesdb_open
from bayeslite import bayesdb_register_metamodel
from bayeslite import bql_quote_name

from bayeslite.core import bayesdb_get_population
from bayeslite.core import bayesdb_has_population
from bayeslite.metamodels.cgpm_metamodel import CGPM_Metamodel
from bayeslite.metamodels.crosscat import CrosscatMetamodel
from bayeslite.parse import bql_string_complete_p

from cgpm.factor.factor import FactorAnalysis
from cgpm.kde.mvkde import MultivariateKde
from cgpm.knn.mvknn import MultivariateKnn
from cgpm.regressions.forest import RandomForest
from cgpm.regressions.linreg import LinearRegression
from cgpm.regressions.ols import OrdinaryLeastSquares

from IPython.core.magic import Magics
from IPython.core.magic import line_cell_magic
from IPython.core.magic import line_magic
from IPython.core.magic import magics_class
from IPython.display import display_html

from iventure.sessions import LogEntry
from iventure.sessions import Session
from iventure.sessions import TextLogger

from iventure import utils_bql
from iventure import utils_mml
from iventure import utils_plot
from iventure import utils_sql
from iventure.jsviz import jsviz


def VsCGpm(outputs, inputs, rng, *args, **kwds):
    try:
        from cgpm.venturescript.vscgpm import VsCGpm
    except ImportError:
        raise NotImplementedError(
            'This notebook does not support VentureScript.')
    return VsCGpm(outputs, inputs, rng, *args, **kwds)

def InlineVsCGpm(outputs, inputs, rng, *args, **kwds):
    try:
        from cgpm.venturescript.vsinline import InlineVsCGpm
    except ImportError:
        raise NotImplementedError(
            'This notebook does not support VentureScript.')
    return InlineVsCGpm(outputs, inputs, rng, *args, **kwds)


def convert_from_stack_dict(stack_dict):
    import venture.lite.value as vv
    venture_value = vv.VentureValue.fromStackDict(stack_dict)
    return convert_from_venture_value(venture_value)


def convert_from_venture_value(venture_value):
    """Convert a stack dict to python object."""
    import venture.lite.value as vv
    from venture.lite.types import Dict
    if isinstance(venture_value, vv.VentureDict):
        shallow = Dict().asPythonNoneable(venture_value)
        deep = OrderedDict()
        for key, value in shallow.iteritems():
            deep[convert_from_venture_value(key)] = \
                convert_from_venture_value(value)
        return deep
    elif isinstance(venture_value, vv.VentureNumber):
        return venture_value.getNumber()
    elif isinstance(venture_value, vv.VentureInteger):
        return venture_value.getInteger()
    elif isinstance(venture_value, vv.VentureString):
        return venture_value.getString()
    elif isinstance(venture_value, vv.VentureBool):
        return venture_value.getBool()
    elif isinstance(venture_value, vv.VentureAtom):
        return venture_value.getAtom()
    elif isinstance(venture_value, vv.VentureArray):
        return [
            convert_from_venture_value(val)
            for val in venture_value.getArray()
        ]
    elif isinstance(venture_value, vv.VentureArrayUnboxed):
        return [
            convert_from_venture_value(val)
            for val in venture_value.getArray()
        ]
    elif isinstance(venture_value, vv.VentureMatrix):
        return venture_value.matrix
    elif isinstance(venture_value, vv.VenturePair):
        return [
            convert_from_venture_value(val)
            for val in venture_value.getArray()
        ]
    else:
        raise ValueError(
            'Venture value cannot be converted', str(venture_value))

@magics_class
class VentureMagics(Magics):

    def __init__(self, shell):
        import warnings
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        super(VentureMagics, self).__init__(shell)
        self._bdb = None
        self._path = None
        self.__ripl = None
        self._riplseed = None
        # self._ripl.set_mode('church_prime')
        self._venturescript = []
        username = getpass.getuser()
        # TODO add SQLLogger
        self.session = Session(username, [TextLogger()], '.iventure_logs')

    @property
    def _ripl(self):
        if self.__ripl is None:
            try:
                import venture.shortcuts as vs
            except ImportError:
                raise NotImplementedError(
                    'This notebook does not support VentureScript.')
            self.__ripl = vs.make_lite_ripl(seed=self._riplseed)
        assert self.__ripl is not None
        return self.__ripl

    def _retrieve_raw(self, line, cell=None):
        return '\n'.join([
            line if line is not None else '',
            cell if cell is not None else ''
        ])


    def logged_cell(func):
        def logged_cell_wrapper(self, line, cell=None):
            # Attempts to write a log entry. As there is no guarantee that the
            # target of the log file will always be writeable throughout the
            # lifetime of the session, fail silently if the file cannot be
            # written. Refer to https://github.com/probcomp/iventure/issues/15
            raw = self._retrieve_raw(line, cell)
            try:
                output = func(self, line, cell)
            except:
                exception = traceback.format_exc()
                try:
                    self.session.log(
                        LogEntry(func.__name__, raw, None, exception))
                except IOError:
                    pass
                raise
            else:
                try:
                    self.session.log(LogEntry(__name__, raw, output, None))
                except IOError:
                    pass
                return output
        return logged_cell_wrapper

    @line_magic
    def get_ripl(self, line):
        return self._ripl

    @line_magic
    def get_bdb(self, line):
        return self._bdb

    @logged_cell
    @line_magic
    def ripl(self, line, cell=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--seed', type=float,  help='deteriministic')
        parser.add_argument(
            '--plugins', type=str, nargs = '+',  help='list of plugins')
        args = parser.parse_args(line.split())
        self.__ripl = None
        if args.seed is not None:
            self._riplseed = args.seed
            print 'Set seed of a new VentureScript RIPL to %.2f.' % (args.seed,)
        if args.plugins is not None:
            for plugin in args.plugins:
                print 'Loading plugin: %s' % (plugin,)
                self._ripl.load_plugin(plugin)

    @logged_cell
    @line_cell_magic
    def venturescript(self, line, cell=None):
        script = line if cell is None else cell
        try:
            results = self._ripl.execute_program(script, type=True)
            # XXX Whattakludge!  Store the cell for later use by the VS CGPM
            self._venturescript.append(script)
            # use matlab convention where semicolon at end means don't print
            import string
            if string.rstrip(script)[-1] != ";":
                return convert_from_stack_dict(results[-1]["value"])
        except Exception as e:
            print "An error has occurred:"
            print e

    @logged_cell
    @line_magic
    def bayesdb(self, line, cell=None):
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


        # Small hack for the VsCGpm, which takes in the venturescript source
        # from %venturescript cells!
        def _VsCGpm(outputs, inputs, rng, *args, **kwds):
            if 'source' not in kwds:
                kwds['source'] = '\n'.join(self._venturescript)
            return VsCGpm(outputs, inputs, rng, *args, **kwds)

        # Register cgpm.
        cgpm_registry = {
            'factor_analysis': FactorAnalysis,
            'inline_venturescript': InlineVsCGpm,
            'linear_regression': LinearRegression,
            'multivariate_kde': MultivariateKde,
            'multivariate_knn': MultivariateKnn,
            'ordinary_least_squares': OrdinaryLeastSquares,
            'random_forest': RandomForest,
            'venturescript': _VsCGpm,
        }
        mm = CGPM_Metamodel(cgpm_registry, multiprocess=args.j)
        bayesdb_register_metamodel(self._bdb, mm)
        return 'Loaded: %s' % (self._path)

    @logged_cell
    @line_cell_magic
    def sql(self, line, cell=None):
        if cell is None:
            ucmds = [line]
        else:
            ucmds = cell.split(';')
        cmds = [ucmd.encode('US-ASCII').strip() for ucmd in ucmds]
        cursor = None
        for cmd in cmds:
            if cmd.isspace() or len(cmd) == 0:
                continue
            if cmd.startswith('.'):
                self._cmd(cmd, sql=True)
                cursor = None
            else:
                cursor = self._bdb.sql_execute(cmd)
        return utils_bql.cursor_to_df(cursor) if cursor else None

    @logged_cell
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
            if cmd.isspace() or not cmd:
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

    @logged_cell
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
                self._bdb.execute(out.getvalue())
                out = StringIO.StringIO()
                ok = False
            out.write('%s\n' % (line,))
            if out.getvalue() and bql_string_complete_p(out.getvalue()):
                ok = True
        cursor = self._bdb.execute(out.getvalue())
        return utils_bql.cursor_to_df(cursor)

    @line_magic
    def multiprocess(self, line, cell=None):
        switch = False if line == 'off' else True
        old = self._bdb.metamodels['cgpm'].set_multiprocess(switch)
        def word(b): return "on" if b else "off"
        print "Multiprocessing turned %s from %s." % (word(switch), word(old))

    @line_magic
    def vizgpm(self, line, cell=None):
        return jsviz.enable_inline()

    def _cmd(self, cmd, sql=None):
        assert cmd[0] == '.'
        space = cmd.find(' ')
        if space == -1:
            space = len(cmd)
        dot_command = cmd[1:space].strip()
        args = cmd[min(space + 1, len(cmd)):]
        if dot_command in self._CMDS:
            return self._CMDS[dot_command](self, args)
        elif dot_command in self._PLTS:
            # Find the keyword arguments, if any.
            matches = re.findall('--[^\\s]+?=[^\\s]*', args)
            kwargs = dict([re.split('--|=',m)[1:] for m in matches])
            # Remove kwargs from args.
            for m in matches:
                args = str.replace(args, m, '')
            args = str.strip(args)
            return self._PLTS[dot_command](self, args, sql=sql, **kwargs)
        else:
            sys.stderr.write('Unknown command: %s\n' % (dot_command,))
            return

    def _cmd_nullify(self, args):
        '''Convert <value> in <table> to SQL NULL.

        Usage: .nullify <table> <value>
        '''
        tokens = args.split()   # XXX
        if len(tokens) != 2:
            sys.stderr.write('Usage: .nullify <table> <value>')
        table = tokens[0]
        expression = tokens[1]
        value = self._bdb.execute('SELECT %s' % (expression,)).fetchvalue()
        cells_changed = utils_bql.nullify(self._bdb, table, value)
        print "Nullified %d cells" % (cells_changed,)
        return None

    def _cmd_table(self, args):
        '''Returns a table of the PRAGMA schema of <table>.

        Usage: .table <table>
        '''
        table = args
        qt = bql_quote_name(table)
        cursor = self._bdb.sql_execute('PRAGMA table_info(%s)' % (qt,))
        return utils_bql.cursor_to_df(cursor)

    def _cmd_population(self, args):
        '''Returns a table of the variables and metamodels for <population>.

        Usage: .population <population>
        '''
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
        return utils_bql.cursor_to_df(cursor)

    def _cmd_guess_schema(self, args):
        '''Returns an MML schema using the guessed stattypes for <table>.

        Using the `--reasons` flag includes the heuristic reasons for the
        stattype guesses.

        Usage: .guess_schema [--reasons] <table>
        '''
        tokens = args.split()
        if len(tokens) == 1:
            reasons = False
            table = tokens[0]
        elif len(tokens) == 2:
            assert tokens[0] == '--reasons'
            reasons = True
            table = tokens[1]
        schema = utils_mml.guess_schema(self._bdb, table, reasons)
        # XXX Rather than return the schema, print it to the console. Returning
        # the raw string will not cause the notebook to pretty-print it.
        print schema

    def _cmd_regress_sql(self, args):
        '''Returns an SQL SELECT using the regression coefficients.

        Usage: .regress_sql --table=<table> REGRESS ...
        '''
        # XXX Copypasta, write a proper parser.
        # Find the keyword arguments, if any.
        matches = re.findall('--[^\\s]+?=[^\\s]*', args)
        kwargs = dict([re.split('--|=',m)[1:] for m in matches])
        # Remove kwargs from args.
        for m in matches:
            args = str.replace(args, m, '')
        args = str.strip(args)
        if 'table' not in kwargs:
            sys.stderr.write('Please specify --table=')
            return
        c = self._bdb.execute(args)
        df = utils_bql.cursor_to_df(c)
        select_query = utils_sql.regression_to_sql(df, table=kwargs['table'])
        print select_query

    def _cmd_assert(self, query, sql=None):
        '''Displays an HTML div indicating whether a bql/sql test passed or
        failed, i.e. whether the query returned true (1) or false (0).

        Usage: .assert <query>
        '''
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        if df.shape != (1,1):
            sys.stderr.write(
                'The query must return a table with exactly one '\
                'row and one column, received shape: %s' % (df.shape,))
            return
        if df.iloc[0, 0] not in [0, 1]:
            sys.stderr.write(
                'The query must return 1 (True) or 0 (False), received: %s'
                % (repr(df.iloc[0,0]))
            )
            return
        if df.iloc[0, 0] == 1:
            display_html("""
                <div class="alert alert-success">
                <strong>Test passed</strong>
                </div>
            """, raw=True)
        else:
            display_html("""
                <div class="alert alert-danger">
                <strong>Test failed</strong>
                </div>
            """, raw=True)

    # Plotting.

    def _cmd_clustermap(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        utils_plot.clustermap(df)

    def _cmd_heatmap(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        utils_plot.heatmap(df, **kwargs)

    def _cmd_density(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        utils_plot.density(df, **kwargs)

    def _cmd_bar(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        utils_plot.bar(df, **kwargs)

    def _cmd_barh(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        utils_plot.barh(df, **kwargs)

    def _cmd_scatter(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        utils_plot.scatter(df, **kwargs)

    def _cmd_histogram_nominal(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        utils_plot.histogram_nominal(df, **kwargs)

    def _cmd_histogram_numerical(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        utils_plot.histogram_numerical(df, **kwargs)

    def _cmd_interactive_bar(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        return jsviz.interactive_bar(df)

    def _cmd_interactive_heatmap(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        # XXX Take the last three columns of the dataframe. This behavior is
        # intended to allow BQL PAIRWISE queries to be passed through directly
        # to %bql .interactive_heatmap. Unfortunately, PAIRWISE will return
        # four columns, where the first column is the population_id, and the
        # second, third, and fourth are name0, name1, and value, respectively.
        df = df.iloc[:,-3:]
        table = kwargs.get('table', None)
        label0 = kwargs.get('label0', None)
        label1 = kwargs.get('label1', None)
        if table and label0 and label1:
            qt = bql_quote_name(table)
            qc0 = bql_quote_name(label0)
            qc1 = bql_quote_name(label1)
            c = self._bdb.sql_execute('''
                SELECT %s, %s FROM %s
            ''' % (qc0, qc1, qt))
            df_lookup = utils_bql.cursor_to_df(c)
            lookup = dict(zip(df_lookup[label0], df_lookup[label1]))
            df = df.replace({df.columns[0]: lookup, df.columns[1]: lookup})
        return jsviz.interactive_heatmap(df)

    def _cmd_interactive_pairplot(self, query, sql=None, **kwargs):
        population = kwargs.get('population', None)
        if population is None:
            raise ValueError('Specify --population=<name> argument.')
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        schema = utils_mml.get_schema_as_list(self._bdb, population)
        for colname in df.columns:
            drop = True
            for entry in schema:
                if entry['name'] == colname:
                    drop = False
            if drop:
                print "Ignoring non-modelled column %s" % (colname,)
                del df[colname]
        return jsviz.interactive_pairplot(df, schema)

    def _cmd_interactive_scatter(self, query, sql=None, **kwargs):
        c = self._bdb.sql_execute(query) if sql else self._bdb.execute(query)
        df = utils_bql.cursor_to_df(c)
        return jsviz.interactive_scatter(df)

    _CMDS = {
        'assert': _cmd_assert,
        'guess_schema': _cmd_guess_schema,
        'nullify': _cmd_nullify,
        'population': _cmd_population,
        'regress_sql': _cmd_regress_sql,
        'table': _cmd_table,
    }

    _PLTS = {
        'bar': _cmd_bar,
        'barh': _cmd_barh,
        'clustermap': _cmd_clustermap,
        'density': _cmd_density,
        'heatmap' : _cmd_heatmap,
        'histogram_nominal': _cmd_histogram_nominal,
        'histogram_numerical': _cmd_histogram_numerical,
        'interactive_bar' : _cmd_interactive_bar,
        'interactive_heatmap' : _cmd_interactive_heatmap,
        'interactive_pairplot' : _cmd_interactive_pairplot,
        'interactive_scatter' : _cmd_interactive_scatter,
        'scatter': _cmd_scatter,
    }


def load_ipython_extension(ipython):
    ipython.register_magics(VentureMagics)
