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

import datetime
import os
import random

from collections import namedtuple


# `output` is either `None` or a `pandas.DataFrame`.
# `exception` is the currently traceback string.
LogEntry = namedtuple('LogEntry', ['type', 'input', 'output', 'exception'])

class TextLogger(object):

    def new_session(self, username, session_id, root):
        # XXX Is username being used?
        home = os.path.expanduser('~')
        if not os.path.exists(os.path.join(home, root)):
            os.mkdir(os.path.join(home, root))
        self.filename = os.path.join(home, root, session_id + '.txt')

    def _write_entry(self, f, label, entry):
        f.write(':' + label + ':' + entry + '\n')

    def log(self, time, counter, entry):
        with open(self.filename, 'a') as f:
            f.write('---\n')
            self._write_entry(f, 'TIME', time)
            self._write_entry(f, 'COUNTER', str(counter))
            self._write_entry(f, 'TYPE', entry.type)
            self._write_entry(f, 'INPUT', entry.input)
            self._write_entry(
                f, 'OUTPUT',
                '' if entry.output is None else entry.output.to_string())
            self._write_entry(
                f, 'EXCEPTION',
                '' if entry.exception is None else entry.exception)

# TODO implement DBLogger which takes a .db file as input

class Session(object):

    def __init__(self, username, loggers, root):
        self.loggers = loggers
        self.counter = 0
        # XXX Global random state!
        rand = str(random.choice('0123456789ABCDEF'))
        session_id = \
            username + '_' + datetime.datetime.now().isoformat() + '_' + rand
        for logger in self.loggers:
            logger.new_session(username, session_id, root)
        print 'session_id: %s' % (session_id,)

    def log(self, entry):
        self.counter += 1
        time = datetime.datetime.now().isoformat()
        for logger in self.loggers:
            logger.log(time, self.counter, entry)
