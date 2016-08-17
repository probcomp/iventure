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
%mml create population ...
```
or, for multi-line schemas.
```
%%mml
drop population xyz;
create population xyz for t (...);
```
#### Write BQL programs
```
%bql estimate mutual information of x with y within xyz;
```
or, for multi-line queries
```
%%bql
create temp table depprobs as
    estimate dependence probability from pairwise variables of xyz;
.plot select * from depprobs
```

### Examples
For a big example including complex venturescript/mml models, please visit
[gpmcc](satellites/satellites_mml.ipynb).

