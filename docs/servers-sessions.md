# iVenture Server and Sessions

## Overview

- Each student in the class is a “user”.

- Each user will be assigned one port number on probcomp-1.

- Each user will be assigned one local unix account on probcomp-1.

- The username will be their kerberos account name, prefixed with “pp_”
  (relationship to kerberos ID will not be exercised).

- The purpose of the separate unix accounts is to restrict permissions, since
  they can execute arbitrary Python code on probcomp-1 under these accounts.

- Initially, it will not be possible to ssh into these unix accounts. All
  interaction will be done through the Jupyter browser interface.

- Multiple distinct notebooks using the same Jupyter server can be open
  simultaneously.

- There will be one long-running Jupyter server process for each user, connected
  to that port. A Jupyter server process is not expected to crash, even if
  some of the Python kernel(s) it is running crash.

- We will manage the user accounts and the Jupyter server processes using a
  command-line utility called `iventure_manager` (see below for more details).

- A sqlite3 database stores the necessary metadata for users/ports/servers/pids.

- Only one server for a user may be running at a time.

- The users are expected to limit themselves to the cell magics of iVenture.
  They should not need to execute Python code in the cells, and this will be
  discouraged and unsupported. The plotting facilities of iVenture should
  suffice for all plotting needs for the problem sets.

- The first cell of each Jupyter notebook on the server must be:
```
% load_ext iventure
% login <username>
```
where the <username> is matched with the assigned user port.

## Managing user accounts and servers

A simple command-line utility `iventure_manager` shall be used to manage the
users, with the following interface:

```
$ ./iventure_manager create_user <user>
```
- creates a fresh unix account with user, which must start with `pp_`.
- adds the user to the `iventure` group.
- creates a port number for the user
- configures the user's `.jupyter/jupyter_notebook_config.py` file with the
  assigned (i) port number, and (ii) password.

```
$ ./iventure_manager start_server <user>
```

- launches jupyter notebook in the home directory of the user, with their
  specified port number, using nohup, returning the pid.
- only one server instance per user is permitted.

```
$ ./iventure_manager stop_server <kerberos>
```

- terminates the jupyter notebook server, by pid.

```
$ ./iventure_manager restart_server <kerberos>
```

- `stop_server` followed by `start_server`

The utility will be backed by a simple sqlite3 database.

```
TABLE usernames (
       username    TEXT PRIMARY KEY
       port        INTEGER
);
TABLE servers (
       username     TEXT
       port         INT
       pid          TEXT
       FOREIGN KEY username REFERENCES usernames(username);
       FOREIGN KEY port REFERENCES usernames(port);
);
```

## Session capture

The initial session capture design is focused on human-readable text file logs,
but also provisions for future addition of co-occuring machine-readable logs to
a database.

The human-readable logs are intended primarily for debugging, not for analysis
of user experience.

Each notebook session is associated with a single `VentureMagics` instance,
which is created by `load_ext`.
(VentureMagics class: https://github.com/probcomp/iventure/blob/master/iventure.py)

To support session capture, the VentureMagics instance will have the following
additional fields:
 - `username`: initially None, set by `%login` line magic.
 - `start_timestamp`: initially None, set at `%login` is run.
 - `traced` (always True for now, but exists to provision for optional).
 - `session_counter`: integer initialized to zero, incremented once every
 cell/line execution

Each log will initially be implemented in a plaintext file The `%login` shell
magics will generate the session ID.

The session ID will be: `<username>_<start_timestamp>_<random>`.
The session ID serves as the reference to the session record.
Session ID will be printed as output.

One file for each notebook session / `VentureMagics` instance.

Location on probcomp1: `/home/pp_<kerberos>/.iventure/logs/<session_id>.txt`

Each cell/line magics (`venturescript`, `sql`, `bql`, `mml`) will check the
value of `self.traced` and will append the following records to the `.txt` file,
which will begin with a reserved character `:` to ease future parsing. Python
`logging` may be used.

`:TIME:<timestamp>`
`:COUNTER:<int>`
`:TYPE:<bql|sql|mml|venturescript>`
`:INPUT:<content of the cell/line, possibly multiline>`
`:OUTPUT:<content (??), possibly multiline>`
`:EXCEPTIONS:<content text, possibly multiline>`

Text of any exceptions raised during execution of the input. The exception may
need to be re-raised to propagate it to the cell output.

The implementation will provision for storing to a common sqlite3 database
instead or in addition to, the separate text files. The sqlite3 database will be
shared with the user account server above.

```
TABLE sessions (
       id   TEXT
       username     TEXT
       start_time   DATETIME?
       FOREIGN KEY username REFERENCES usernames(username)
);
TABLE cells (
       session_id   TEXT
       counter      INT
       type         TEXT
       input        TEXT
       output       TEXT
       exceptions   TEXT
       status       TEXT (SUCCESS or USER_ERROR or LIB_ERROR)
       FOREIGN KEY session_id REFERENCES sessions(id);
);
```

Each cell/line magic either returns `None` or Pandas `DataFrame` object. In the
initial plaintext logging, the pandas dataframe will be pretty-printed in the
log. We will provision for serializing the dataframe into an easier-to-parse
format (e.g. using cPickle) in a future version.

### Features not initially supported in first version

- Machine-readable logs (e.g. the dataframes outputs will be initially pretty
printed not pickled).

- Full tracing of session state, including incremental checkpoints in `.bdb`
state between each line/cell magic.

- Reproducibility, setting seeds manually.

- Logging or serializing the generated plots as part of the session record.
