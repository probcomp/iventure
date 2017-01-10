# Setting up a python virtualenv with probcomp repositories and their dependencies.

These instructions are tested on `Ubuntu 14.04.5`, different Linux distributions
might require small modifications.

#### Create a fresh directory and store its path in `$WRKDIR` (for working directory).

```bash
$ export WRKDIR=/path/to/my/dir
$ mkdir $WRKDIR
```

#### Create a virtualenv in `$WRKDIR` called `.pyenv2.7`.

```bash
$ cd $WRKDIR
$ virtualenv -p /usr/bin/python .pyenv2.7
```

#### Activate the virtual environment, and ensure the right python interpreter is being referenced.

```bash
$ source .pyenv2.7/bin/activate
$ which python
```

#### Upgrade `pip` to the latest version.

```bash
$ pip install -U pip
```

#### Install python requirements from `pip`, using the `requirements.txt` file from the toplevel directory of this repository (may take a while).

```bash
$ pip install -r /path/to/requirements.txt
```

### Add some environment variables to the virtualenv `activate` script.

```bash
$ echo '
export PYTHONDONTWRITEBYTECODE=1
export BAYESDB_DISABLE_VERSION_CHECK=1
export BAYESDB_WIZARD_MODE=1
export GPMCCDEBUG=1' >> .pyenv2.7/bin/activate

$ source .pyenv2.7/bin/activate
```

#### Retrieve the probcomp repositories from Github.

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
    git clone git@github.com:probcomp/$project.git
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
$ python -c 'import iventure'
```

### [[OPTIONAL]] Run the test suite for probcomp repositories (may take a while).

```bash
$ for project in bayeslite cgpm crosscat Venturecxx; do
    cd $project
    ./check.sh
    cd ..
  done
```

### [[OPTIONAL]] Activate the `Qt` backend for `matplotlib`.

#### Obtain `python-qt4` from the Ubuntu standard repositories.

```bash
sudo apt-get install python-qt4
```

#### Create soft links to the system install in the `.pyenv2.7` virtualenv.

```bash
$ cd .pyenv2.7/lib/python2.7/site-packages
$ ln -s /usr/lib/python2.7/dist-packages/sip.so .
$ ln -s /usr/lib/python2.7/dist-packages/PyQt4 .
```

### [[OPTIONAL]] Setting UNIX group permissions for the virtualenv.

#### Create a new UNIX group `$GRP` for `$WRKDIR` and its subdirectories, and add yourself to the group.

The purpose of the group `$GRP` is to control the file/access permissions for
all users which are managed by `iventure_manager.py`.

```bash
$ addgroup $GRP
$ adduser $USER $GRP
```

#### Change permissions of `$WRKDIR` to the new group `$GRP`.

```bash
$ chmod -R g+s $WRKDIR
$ chown -R $USER:$GRP $WRKDIR
```
