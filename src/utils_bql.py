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

import pandas as pd
import numpy as np

from bayeslite import bql_quote_name

from bayeslite.core import bayesdb_has_table
from bayeslite.core import bayesdb_table_column_names
from bayeslite.core import bayesdb_table_has_column

from bayeslite.util import cursor_value


def nullify(bdb, table, value):
    """Replace specified values in a SQL table with ``NULL``."""
    qtable = bql_quote_name(table)
    cursor = bdb.sql_execute('pragma table_info(%s)' % (qtable,))
    columns = [row[1] for row in cursor]
    if value == '\'\'':
        sql = 'UPDATE %s SET {0} = NULL WHERE {0} = \'\'' % (qtable,)
    else:
        sql = 'UPDATE %s SET {0} = NULL WHERE {0} = ?' % (qtable,)
    cells_changed = 0
    for col in columns:
        qcol = bql_quote_name(col)
        old_changes = bdb._sqlite3.totalchanges()
        bdb.sql_execute(sql.format(qcol), (value,))
        rows_changed = bdb._sqlite3.totalchanges() - old_changes
        cells_changed += rows_changed
    return cells_changed


def cardinality(bdb, table, columns=None):
    """Compute the number of unique values in the columns of a table."""
    qtable = bql_quote_name(table)
    # If no columns specified then use all.
    if not columns:
        cursor = bdb.sql_execute('PRAGMA table_info(%s)' % (qtable,))
        columns = [row[1] for row in cursor]
    names = []
    counts = []
    for column in columns:
        qcolumn = bql_quote_name(column)
        cursor = bdb.sql_execute('''
            SELECT COUNT (DISTINCT %s) FROM %s
        ''' % (qcolumn, qtable))
        names.append(column)
        counts.append(cursor_value(cursor))
    return pd.DataFrame({'name': names, 'distinct_count': counts})


def cursor_to_df(cursor):
    """Converts SQLite3 cursor to a pandas DataFrame."""
    # Perform in savepoint to enable caching from row to row in BQL queries.
    with cursor.connection.savepoint():
        df = pd.DataFrame.from_records(cursor, coerce_float=True)
    if not df.empty:
        df.columns = [desc[0] for desc in cursor.description]
        for col in df.columns:
            try:
                df[col] = df[col].astype(float)
            except ValueError:
                pass
    return df


def query(bdb, bql, bindings=None, logger=None):
    """Execute the `bql` query on the `bdb` instance."""
    if bindings is None:
        bindings = ()
    if logger:
        logger.info("BQL [%s] %s", bql, bindings)
    cursor = bdb.execute(bql, bindings)
    return cursor_to_df(cursor)


def subsample_table_columns(bdb, table, new_table, limit, keep, seed):
    """Return a subsample of the columns in the table."""
    if not bayesdb_has_table(bdb, table):
        raise ValueError('No such table: %s' % (table,))
    if bayesdb_has_table(bdb, new_table):
        raise ValueError('Table already exists: %s' % (new_table,))
    unknown = [k for k in keep if not bayesdb_table_has_column(bdb, table, k)]
    if unknown:
        raise ValueError('No such columns: %s' % (unknown,))
    num_sample = limit - len(keep)
    if num_sample < 0:
        raise ValueError('Must sample at least as many columns to keep.')
    subselect_columns = [
        column for column in bayesdb_table_column_names(bdb, table)
        if column not in keep
    ]
    rng = np.random.RandomState(seed)
    subsample_columns = rng.choice(
        subselect_columns,
        replace=False,
        size=min(len(subselect_columns), num_sample)
    )
    qt = bql_quote_name(table)
    qnt = bql_quote_name(new_table)
    qc = ','.join(map(bql_quote_name, itertools.chain(keep, subsample_columns)))
    cursor = bdb.execute('''
        CREATE TABLE %s AS SELECT %s FROM %s
    ''' % (qnt, qc, qt))
    return cursor_to_df(cursor)
