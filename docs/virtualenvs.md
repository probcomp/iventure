# Setting up a python virtualenv with probcomp repositories and their dependencies.

These instructions are tested on `Ubuntu 16.04.5`, different Linux distributions
might require small modifications.

#### Retrieve required packages from the Ubuntu standard repositories.

```bash
sudo apt-get update -qq && \
  sudo apt-get upgrade -qq && \
  sudo apt-get install -qq \
    build-essential \
    ccache \
    cython \
    git \
    libboost-all-dev \
    libgsl0-dev \
    pandoc \
    python-apsw \
    python-flask \
    python-jsonschema \
    python-matplotlib \
    python-nose \
    python-nose-testconfig \
    python-numpy \
    python-pandas \
    python-pexpect \
    python-pip \
    python-pytest \
    python-requests \
    python-scipy \
    python-six \
    python-sklearn \
    python-statsmodels \
    python-virtualenv \
    ; # end of package list
```

#### Create a virtualenv in `$WRKDIR` called `.pyenv2.7`.

```bash
$ virtualenv --system-site-packages /path/to/venv
```

#### Activate the virtual environment, and ensure the right python interpreter is being used.

```bash
$ . /path/to/venv/bin/activate
$ which python
```

#### Upgrade pip and install python requirements from `pip`, using the `requirements.txt` file from the toplevel directory of this repository.

```bash
$ pip install --upgrade pip
$ pip install jupyter==1.0.0
```

#### Retrieve probcomp repositories from Github.

```bash
$ PROJECTS="
bayeslite-apsw
bayeslite
cgpm
crosscat
iventure
Venturecxx
"

$ for project in $PROJECTS; do
    git clone git@github.com:probcomp/"$project".git
  done
```

#### Build the probcomp repositories.

```bash
$ for project in $PROJECTS; do
    cd $project
    python setup.py build
    pip install --no-deps .
    cd ..
  done
````

#### Verify the installation is successful.

```bash
$ python -c 'import iventure.magics'
```

### Optional: Run the test suite for probcomp repositories (may take a while).

```bash
$ for project in bayeslite cgpm crosscat Venturecxx; do
    cd $project
    ./check.sh
    cd ..
  done
```
