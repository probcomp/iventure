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

from bayeslite import bql_quote_name
from bayeslite.exception import BQLError

from iventure import utils_bql


def guess_schema(bdb, table, reasons):
    """Returns a guessed MML schema for a population derived from `table`."""
    df = utils_bql.query(bdb, 'GUESS SCHEMA FOR %s' % (table,))
    columns = df['column'].tolist()
    stattypes = df['stattype'].tolist()
    reasons = df['reason'].tolist() if reasons else [''] * len(columns)

    guesses = {
        c: [stattypes[i], reasons[i]]
        for i, c in enumerate(columns)
    }

    schema = StringIO.StringIO()
    nominal = []
    numerical = []
    ignore = []
    unknown = []

    for col in guesses.keys():
        if len(col) == 0:
            raise BQLError(bdb,
                'Empty column name(s) in table %s' % (table,))
        guessed_type_reason = guesses[col]
        stattype = guessed_type_reason[0].lower()
        reason = guessed_type_reason[1]
        if stattype == 'nominal':
            nominal.append([col, reason])
        elif stattype == 'numerical':
            numerical.append([col, reason])
        elif stattype == 'ignore':
            ignore.append([col, reason])
        elif stattype == 'key':
            ignore.append([col, reason])
        else:
            unknown.append([col, reason])

    if unknown:
        raise ValueError('Unknown guessed stattypes: %s' % (repr(unknown),))

    stattype_columns_pairs = [
        ['NOMINAL', nominal],
        ['NUMERICAL', numerical],
        ['IGNORE', ignore]
    ]

    for i, [stattype, columns] in enumerate(stattype_columns_pairs):
        if not columns:
            continue
        schema.write('IGNORE' if stattype == 'IGNORE' else 'MODEL \n')
        for j in xrange(len(columns)):
            [col, reason] = columns[j]
            schema.write('\t %s' % (bql_quote_name(col),))
            # Do not append a comma for last item in list.
            if j < len(columns) - 1:
                schema.write(',')
            # Add space between the last variable and 'AS' for proper parsing.
            else:
                schema.write(' ')
            if len(reason) > 0:
                schema.write(" # %s" % (reason,))
            schema.write('\n')
        if stattype != 'IGNORE':
            schema.write('AS \n\t%s' %(stattype,))
        if i < len(stattype_columns_pairs) - 1:
            schema.write(';\n')

    result = schema.getvalue()
    schema.close()
    return result
