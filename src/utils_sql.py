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

from StringIO import StringIO

from bayeslite import bql_quote_name


def regression_to_sql(df, table=None):
    """Convert df output of BQL REGRESS to a SQL SELECT query."""
    if df.shape[1] != 2:
        raise ValueError('Exactly two columns required.')
    variables = df[df.columns[0]]
    coefficients = df[df.columns[1]]

    intercept = coefficients[variables=='intercept'].iloc[0]

    numericals = {
        var: coefficients[variables==var].iloc[0]
        for var in variables
        if '_dum_' not in var and var != 'intercept'
    }

    nominals = set([c.split('_dum_')[0] for c in variables if '_dum_' in c])
    categories = {
        var : {
            v.split('_dum_')[1]: coefficients[variables==v].iloc[0]
            for v in variables if '%s_dum_' % (var,) in v
        }
        for var in nominals
    }

    def compile_numerical(variable, coefficient):
        return '%1.4f  *  %s' % (coefficient, bql_quote_name(variable))
    def compile_nominal_case(variable, categories):
        cases = str.join('\n', [
            '\t\t\tWHEN \'%s\' THEN %1.4f' % (category, coefficient)
            for category, coefficient in categories.iteritems()
        ])
        return 'CASE %s\n%s\n\t\t\tELSE NULL\n\t\tEND'\
            % (bql_quote_name(variable), cases,)

    # Write query to the buffer.
    out = StringIO()
    # SELECT
    out.write('SELECT\n\t\t')
    # Intercept.
    out.write('%1.4f\n\t' % (intercept,))
    # Numerical variables.
    out.writelines([
        '+\t%s\n\t' % (compile_numerical(var, coef))
        for var, coef in numericals.iteritems()
    ])
    # Nominal variables.
    for i, variable in enumerate(categories):
        out.write('+\t%s'% compile_nominal_case(variable, categories[variable]))
        out.write('\n')
        if i < len(categories) - 1:
            out.write('\t')
    # FROM table.
    if table:
        out.write('\rFROM %s' % (bql_quote_name(table),))
    return out.getvalue()
