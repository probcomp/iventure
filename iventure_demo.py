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
import sys

import bdbcontrib.bql_utils as bqu
import bdbcontrib.plot_utils as bpu
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
from bayeslite.parse import bql_string_complete_p
from bayeslite.shell.pretty import pp_list
from bdbcontrib import Population
from cgpm.regressions.forest import RandomForest
from cgpm.regressions.linreg import LinearRegression
from cgpm.venturescript.vscgpm import VsCGpm

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
        self._ripl = vs.make_ripl()
        self._ripl.set_mode('church_prime')
        self._venturescript = []

    @line_cell_magic
    def venturescript(self, line, cell=None):
        script = line if cell is None else cell
        # XXX Whattakludge!
        self._venturescript.append(script)
        self._ripl.execute_program(script)

    @line_magic
    def bayesdb(self, line):
        path = line
        if self._bdb is not None:
            self._bdb.close()
            self._bdb = None
        self._bdb = bayesdb_open(path)
        self._path = path

        cgpm_registry = {
            'venturescript': self._VsCGpm,
            'linear_regression': LinearRegression,
            'random_forest': RandomForest,
        }
        mm = CGPM_Metamodel(cgpm_registry, multiprocess=1)
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
    def bql(self, line, cell=None):
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
            out.write(line)
            if out.getvalue() and bql_string_complete_p(out.getvalue()):
                ok = True
        try:
            cursor = self._bdb.execute(out.getvalue())
        except (BQLError, BQLParseError) as e:
            sys.stderr.write('%s' % (e,))
        else:
            return bqu.cursor_to_df(cursor)

    def _cmd(self, cmd):
        assert cmd.startswith('.')
        sp = cmd.find(' ')
        if sp == -1:
            sp = len(cmd)
        if cmd[1:sp] not in self._CMDS:
            sys.stderr.write('Unknown command: %s\n' % (cmd[1:sp],))
            return
        args = cmd[min(sp + 1, len(cmd)):]
        return self._CMDS[cmd[1:sp]](self, args)

    @line_cell_magic
    def mml(self, line, cell=None):
        # XXX Kludge!
        return self.bql(line, cell)

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
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        bpu.barplot(self._bdb, df)

    def _cmd_heatmap(self, query):
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        bpu.heatmap(df)

    def _cmd_histogram(self, query):
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        bpu.histogram(self._bdb, df)

    def _cmd_plot(self, query):
        cursor = self._bdb.execute(query)
        df = bqu.cursor_to_df(cursor)
        bpu.pairplot(self._bdb, df)

    _CMDS = {
        'bar': _cmd_bar,
        'csv': _cmd_csv,
        'heatmap': _cmd_heatmap,
        'histogram': _cmd_histogram,
        'nullify': _cmd_nullify,
        'plot': _cmd_plot,
        'population': _cmd_population,
        'table': _cmd_table,
    }

def load_ipython_extension(ipython):
    ipython.register_magics(VentureMagics)
