## Interactive Venturescript, Metamodeling Language, and Bayesian Query Language Environment

### Installing
The extension is contained in `iventure.py`.

First add `iventure.py` to your python path. The easiest way is to create a
symlink to the extension to `~/.ipython`:
```
$ cd ~/.ipython
$ ln -s /path/to/iventure/iventure.py .
```
Note: If all your IPython notebooks will be in this directory, you can skip
this skip, but it is not recommended to do so.

### Usage
In the Jupyter notebook, load up extension in the first cell:
```
%load_ext iventure
```
#### Open a bdb file:
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

### Examples

Please see https://github.com/probcomp/iventure-notebooks.

