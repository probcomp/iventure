## Interactive Environment For Probabilistic Programming in Venturescript, Metamodeling Language, and Bayesian Query Language

[![Build Status](https://travis-ci.org/probcomp/iventure.svg?branch=master)](https://travis-ci.org/probcomp/iventure)

## Installing

```
$ git clone git@github.com:probcomp/iventure
$ python setup.py build
```

Make sure to add `iventure` to your `PYTHONPATH`. The two key source files are
`magics.py`, which provides Jupyter notebook cell magics, and `manager.py`,
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
%bql ESTIMATE MUTUAL INFORMATION OF x WITH y WITHIN xyz;
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
