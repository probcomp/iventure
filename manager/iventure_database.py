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

import os
import sqlite3

import pandas as pd
import pytest


def cursor_to_df(cursor):
    """Converts SQLite3 cursor to a pandas DataFrame."""
    # Do this in a savepoint to enable caching from row to row in BQL
    # queries.
    df = pd.DataFrame.from_records(cursor)
    if not df.empty:
        df.columns = [desc[0] for desc in cursor.description]
    return df


def ivdb_initialize_schema(db):
    db.execute('''
        CREATE TABLE users (
            username    TEXT COLLATE NOCASE NOT NULL PRIMARY KEY,
    );''')
    db.execute('''
        CREATE TABLE servers (
            username    TEXT COLLATE NOCASE NOT NULL,
            port        INTEGER NOT NULL UNIQUE,
            pid         INTEGER NOT NULL UNIQUE,
            PRIMARY KEY (username),
            FOREIGN KEY (username) REFERENCES users(username)
    );''',)


def ivdb_create_user(db, username):
    db.execute('''
        INSERT INTO users VALUES ?
    ''', (username,))


def ivdb_delete_user(db, username):
    if not ivdb_has_user(db, username):
        raise ValueError('No such user: %s.' % (username),)
    db.execute('''
        DELETE FROM users WHERE username = ?
    ''', (username,))


def ivdb_has_user(db, username):
    result = db.execute('''
        SELECT username FROM users WHERE username = ?
    ''', (username, )).fetchall()
    assert len(result) in [0,1]
    return len(result) == 1


def ivdb_has_user_session(db, username):
    result = db.execute('''
        SELECT username FROM servers WHERE username = ?
    ''', (username, )).fetchall()
    assert len(result) in [0,1]
    return len(result) == 1


def ivdb_user_port(db, username):
    if not ivdb_has_user(db, username):
        raise ValueError('No such user: %s.' % (username),)
    cursor = db.execute('''
        SELECT port FROM servers WHERE username = ?
    ''', (username,))
    return next(cursor)[0]


def ivdb_user_pid(db, username):
    if not ivdb_has_user(db, username):
        raise ValueError('No such user: %s.' % (username),)
    cursor = db.execute('''
        SELECT pid FROM servers WHERE username = ?
    ''', (username,))
    return next(cursor)[0]



if __name__ == '__main__':
    # Poor man's test suite

    os.remove('foo.sqlite3')
    db = sqlite3.Connection('foo.sqlite3')

    ivdb_initialize_schema(db)

    assert ivdb_generate_port(db) == 60000

    ivdb_create_user(db, 'mohamed')
    ivdb_create_user(db, 'salman')

    assert ivdb_user_port(db, 'mohamed') == 60000
    assert ivdb_user_port(db, 'salman') == 60001
    assert ivdb_generate_port(db) == 60002

    assert ivdb_has_user(db, 'mohamed')
    assert ivdb_has_user(db, 'salman')
    assert not ivdb_has_user(db, 'mohameds')

    ivdb_delete_user(db, 'mohamed')
    assert not ivdb_has_user(db, 'mohamed')

    assert ivdb_generate_port(db) == 60000

    with pytest.raises(ValueError):
        ivdb_delete_user(db, 'mohamed')
