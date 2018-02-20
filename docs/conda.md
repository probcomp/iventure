# Setting up a conda environment with probcomp repositories and their dependencies.

These instructions are tested on `Ubuntu 16.04.5`, different Linux distributions
might require small modifications. All of these commands perform a local
installation for the current user, they do not modify any system-wide state or
require root access.

#### Retrieve the installation required files.

```bash
$ wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
$ wget https://raw.githubusercontent.com/probcomp/notebook/master/files/conda_python2.txt -O /tmp/conda_python2.txt
$ wget https://raw.githubusercontent.com/probcomp/notebook/master/files/conda_probcomp_edge.txt -O /tmp/conda_probcomp_edge.txt
```

#### Install conda.

```bash
$ bash /tmp/miniconda.sh -b -p ${HOME}/miniconda
$ export PATH="${HOME}/miniconda/bin:${PATH}"
$ conda update conda
$ conda install --yes conda-build
```

#### Create a conda environment containing the software.

```bash
$ conda create -n probcomp --yes \
    -c probcomp -c cidermole -c fritzo -c ursusest \
    python=2.7 --file /tmp/conda_python2.txt --file /tmp/conda_probcomp_edge.txt
```

#### Activate the environment and run some tests.

```bash
$ conda activate probcomp
$ python -m pytest --pyargs bayeslite --pyargs iventure
```

Remember to update your `PATH` so that the `conda` command can be found.
