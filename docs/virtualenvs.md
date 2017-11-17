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

#### Create a virtual environment and install jupyter.

```bash
$ virtualenv --system-site-packages /path/to/venv
$ . /path/to/venv/bin/activate
$ pip install --upgrade pip
$ pip install jupyter==1.0.0
```

#### Retrieve probcomp repositories from Github and build.

```bash
$ for project in bayeslite cgpm crosscat iventure Venturecxx; do
    git clone git@github.com:probcomp/"${project}".git
    cd "${project}"
    python setup.py build
    pip install --no-deps .
    cd ..
  done
```

#### Verify import of iventure.

```bash
$ python -c 'import iventure.magics'
```

### Optional: Run the test suite for probcomp repositories (may take a while).

```bash
$ for project in bayeslite cgpm crosscat iventure Venturecxx; do
    cd "${project}"
    ./check.sh
    cd ..
  done
```
