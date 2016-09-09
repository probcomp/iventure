from collections import namedtuple
import random
import datetime
import os


# output is either None or a pandas.DataFrae
# exception is the currently traceback string
LogEntry = namedtuple('LogEntry', ['type', 'input', 'output', 'exception'])

class TextLogger(object):

    def new_session(self, username, session_id):
        home = os.path.expanduser("~")
        self.filename = os.path.join(home, 'iventure_logs', session_id + '.txt')

    def _write_entry(self, f, label, entry):
        f.write(':' + label + ':' + entry + '\n')

    def log(self, time, counter, entry):
        with open(self.filename, 'a') as f:
            f.write('---\n')
            self._write_entry(f, 'TIME', time)
            self._write_entry(f, 'COUNTER', str(counter))
            self._write_entry(f, 'TYPE', entry.type)
            self._write_entry(f, 'INPUT', entry.input)
            self._write_entry(f, 'OUTPUT', '' if entry.output is None else entry.output.to_string())
            self._write_entry(f, 'EXCEPTION', '' if entry.exception is None else entry.exception)

# TODO implement DBLogger which takes a .db file as input

class Session(object):

    def __init__(self, username, loggers):
        self.loggers = loggers
        self.counter = 0
        rand = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
        session_id = username + '_' + datetime.datetime.now().isoformat() + '_' + rand
        for logger in self.loggers:
            logger.new_session(username, session_id)
        print "Session ID", session_id

    def log(self, entry):
        self.counter += 1
        time = datetime.datetime.now().isoformat()
        for logger in self.loggers:
            logger.log(time, self.counter, entry)


