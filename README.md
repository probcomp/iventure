## Interactive Venturescript, Metamodeling Language, and Bayesian Query Language Environment

## Installing

```
$ git clone git@github.com:probcomp/iventure
$ python setup.py build
```

Make sure to add `iventure` to your `PYTHONPATH`. The two key source files are
`magics.py`, which provides Jupyter ntoebook cell magics, and `manager.py`,
which provides server management for Jupyter kernels.

## Magics Usage

The `magics.py` contains cell magics which allow for interactive probabilistic
programming in a Jupyter notebook.

In the first cell of a Jupyter notebook, load the extension.
```
%load_ext iventure.magics
```

#### Open a bdb file
```
%bayesdb foo.bdb
```

#### Write MML programs
```
%mml CREATE POPULATION ...
```
or, for multi-line schemas.
```
%%mml
DROP POPULATION xyz;
CREATE POPULATION xyz for t (...);
```

#### Write BQL programs
```
%bql ESTIMULATE MUTUAL INFORMATION OF  x WITH y WITHIN xyz;
```
or, for multi-line queries
```
%%bql
CREATE TEMP TABLE depprobs AS
    ESTIMATE DEPENDENCE PROBABILITY FROM PARIWSE VARIABLES OF xyz;
.plot SELECT * FROM depprobs
```

#### Use dot commands for BQL shorthands
```
%bql .nullify satellites_t NaN
%bql .population satellites_p
```

#### Use dot commands with BQL for plotting
```
%bql .scatter SELECT apogee_km, perigee_km FROM satellites_t LIMIT 100;
```

## Manager Usage

The `manager.py` is used to manage a batch of UNIX users sharing a common
python virtualenv, and infrastructure for creating Jupyter servers on a per-user
basis.

Please see a [virtualenvs.md](docs/virtualenvs.md) for a detailed description of
setting up (i) the shared root directory, (ii) python virtualenv, and (iii) UNIX
group permissions, which are required by `manager.py`.

#### Create a new user

```
./manager.py user_create <username>
```

#### Launch a Jupyter server

```
./manager.py server_launch <username>
```
Note that only 1 server per user (which supports several notebooks), is allowed.

#### Stop a Jupyter server

```
./manager.py server_stop <username>
```

#### Restart a Jupyter server

```
./manager.py server_restart <username>
```

In general, restarting an entire Jupyter server should be a rare event. Instead,
kernels/notebooks within a server are restarted through the web interface, which
suffices to reload and apply any patches to the python install.

While notebooks often crash, servers are not expected to crash.

## Session capture

User activity in a Jupyter notebook which executes `%load_ext iventure.magics`
is stored in plain-text under `$HOME/.iventure_logs`.

## Examples

Please see https://github.com/probcomp/iventure-notebooks for examples of
notebooks using `iventure`.

