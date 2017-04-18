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

import pandas as pd

from bayeslite import bql_quote_name
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
    for col in columns:
        qcol = bql_quote_name(col)
        bdb.sql_execute(sql.format(qcol), (value,))


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
