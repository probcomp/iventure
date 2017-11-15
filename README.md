## Interactive Environment For Probabilistic Programming for Probabilistic Data Analysis

[![Build Status](https://travis-ci.org/probcomp/iventure.svg?branch=master)](https://travis-ci.org/probcomp/iventure)

## About

iventure serves as a jupyter-based front-end for [BayesDB](https://github.com/probcomp/bayeslite).

## Installing

For access to iventure, please refer to the release webpage of the
[Probabilistic Computing Stack](http://probcomp.org/open-probabilistic-programming-stack/).

## Tutorial Notebooks

Please refer to the following tutorial notebooks for illustrative probabilistic
data analysis tasks on real-world datasets:

- [Exploratory analysis](https://probcomp-1.csail.mit.edu/20170720-darpa/gapminder-exploratory.html)
  on Gapminder, a dataset of global macroeconomic indicators of education,
  poverty, environment and health.

- [Predictive analysis](https://probcomp-1.csail.mit.edu/20170720-darpa/satellites-predictive.html)
  on a table of Earth satellites from the Union of Concerned Scientists.

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
