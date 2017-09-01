# Contributing guide and notes for hackers

#### Branch Names

Should be `[year][month][day]-[username]-[branch-description...]`. For example a
well named branch is `20170901-fsaad-update-contributing`.

#### Merging feature branches

When merging a feature branch into master, always create an explicit merge
commit using `merge --no-ff`; never merge via fast-forward (i.e. rebase). While
this topic is
[controversial](https://www.atlassian.com/git/articles/git-team-workflows-merge-or-rebase);
probcomp has standardized on merge commits across all repositories.

#### Deleting branches

Please do not delete branches, history should be maintained.

#### Copyright headers

Files should have appropriate copyright headers, refer to `src/__init__.py`
for the probcomp template.

#### Python coding style

Generally follow [PEP 8](https://www.python.org/dev/peps/pep-0008/), 80-char
max, with these exceptions:

- New line, instead of alignment, for continuation lines. For function
  definitions, no new line and use eight spaces.

    ##### Example 1

    _Yes_

    ```python
    model = cgpm.crosscat.state.State(
        X, outputs=[1,2,3,4], inputs=None,
        cctypes=['normal', 'bernoulli', 'poisson', 'lognormal'],
        rng=np.random.RandomState(0))

    ```

    _No_
    ```python
    model = cgpm.crosscat.state.State(X, outputs=[1,2,3], inputs=None,
                                      cctypes=['normal', 'bernoulli', 'poisson',
                                        'lognormal'],
                                      rng=np.random.RandomState(0))
    ```

    ##### Example 2

    _Yes_
    ```python
    def generate_mh_sample(x, logpdf_target, jump_std, D, num_samples=1,
            num_burn=1, num_chains=7 num_lag=1, rng=None):
        ...body...
    ```

    _Yes_
    ```python
    def generate_mh_sample(
            x, logpdf_target, jump_std, D, num_samples=1,
            num_burn=1, num_chains=7 num_lag=1, rng=None):
        ...body...
    ```

    _No_
    ```python
    def generate_mh_sample(x, logpdf_target, jump_std, D, num_samples=1,
                           num_burn=1, num_chains=7 num_lag=1, rng=None):
        ...body...
    ```

- Use single-quoted strings `'hello world'` instead of double quotes `"hello
  world"` in source code.

- For doc strings, use double quotes `"""docstring here"""`, instead of single
  quotes `'''docstring here'''.

#### Python imports

Should be organized as follows, with each block separated by one blank line:

1. standard library
2. third-party packages
3. sister (probcomp) packages
4. current package imports, named
5. current package imports, relative

Each import block should be organized alphabetically. First write all
unqualified imports (`import foo`), then all named imports (`from baz import
nix`). Here is an example.

```python
import math
import multiprocessing as mp

from array import ArrayType
from struct import pack

import numpy as np

from scipy.misc import logsumexp
from scipy.stats import geom
from scipy.stats import norm

import bayeslite.core
import bayeslite.math_util

from cgpm.crosscat.state import State
from cgpm.utils import general as gu

from . import utils
```

Using `from foo import *` is generally prohibited, unless there is an
exceptional reason.

#### Testing

The tip of every branch merged into master __must__ pass `./check.sh`, and be
consistent with the code conventions here. New functionality must always be
associated with test -- fixing bugs should preferably include a test as well
(less strict).

#### Entropy

Please, never, ever used global random state when avoidable. Every source of
random bits must be managed explicitly.

A notable exception is Julia code, which has less support for manging entropy
than e.g. python and usually draws from global entropy.
