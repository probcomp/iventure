# Setting up a conda environment with probcomp repositories and their dependencies

These instructions are tested on `Ubuntu 18.04`, different Linux distributions
might require small modifications. All of these commands perform a local
installation for the current user, they do not modify any system-wide state or
require root access.

#### Retrieve the required installation files.

```bash
$ wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
$ wget https://raw.githubusercontent.com/probcomp/notebook/master/files/conda_python2.txt -O /tmp/conda_python2.txt
$ wget https://raw.githubusercontent.com/probcomp/notebook/master/files/conda_probcomp.txt -O /tmp/conda_probcomp.txt
```

#### Install conda and environment containing the probcomp software.

```bash
$ bash /tmp/miniconda.sh -b -p ${HOME}/miniconda
$ . ${HOME}/miniconda/etc/profile.d/conda.sh
$ conda install --yes conda=4.6.14 conda-build
$ conda create -n probcomp --yes --file /tmp/conda_python2.txt python=2.7
$ conda install -n probcomp --quiet --yes \
    -c probcomp -c cidermole -c fritzo -c ursusest \
    --file /tmp/conda_probcomp.txt
```

Optional: The line `. ${HOME}/miniconda/etc/profile.d/conda.sh` needs to be run
for the `conda` command to be available, consider adding this line to your
`.bashrc` or `.zshrc` file.

#### Activate the environment and run some tests.

```bash
$ conda activate probcomp
$ python -m pytest --pyargs bayeslite --pyargs iventure
```

#### Developing a project.

To develop a project, such as bayeslite, first uninstall it from conda, and
build the source directly.

```bash
$ conda remove --force bayeslite
$ git clone git@github.com:probcomp/bayeslite
$ python setup.py install
```
