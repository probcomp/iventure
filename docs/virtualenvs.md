# Setting up a shared python virtualenv with group permissions.

#### Create a fresh directory and store its path in `$SHOME` (for shared home).

```
export SHOME=/path/to/my/dir
$ mkdir $SHOME
```

#### Create a virtualenv in `$SHARED_HOME` called `.pyenv2.7.6`.

```
$ cd $SHOME
$ virtualenv -p /usr/bin/python .pyenv2.7.6
```

#### Activate the virtual environment, and ensure the right python interpreter is being referenced.

```
$ source .pyenv2.7.6/bin/activate
$ which python # should return $SHOME/.pyenv2.7.6/bin/python
```

#### Install python requirements from `pip`, using the `requirements.txt` file from this directory (may take a while).

```
$ pip install -r /path/to/requirements.txt
```

#### [Optional] Link `matplotlib` libraries for the nicer `Qt` backend to the virtualenv. This step will only work if the `python-qt4` is installed system-wide.

```
$ cd .pyenv2.7.6/lib/python2.7/site-packages
$ ln -s /usr/lib/python2.7/dist-packages/sip.so .
$ ln -s /usr/lib/python2.7/dist-packages/PyQt4 .
```

#### Retrieve the probcomp repositories from Github.

```
$ cd $SHOME
$ git clone git@github.com:probcomp/bayeslite-apsw.git
$ git clone git@github.com:probcomp/bayeslite.git
$ git clone git@github.com:probcomp/bdbcontrib.git
$ git clone git@github.com:probcomp/cgpm.git
$ git clone git@github.com:probcomp/crosscat.git
$ git clone git@github.com:probcomp/iventure.git
$ git clone git@github.com:probcomp/Venturecxx.git
```

Two repositories require checking out non-default branches.

```
$ cd $SHOME/bayeslite
$ git fetch
$ git checkout 20160801-fsaad-syntax-bonanza

$ cd $SHOME/crosscat
$ git fetch
$ git checkout 20160907-fsaad-progress-hack
```

The default `master` branch suffices for the rest of the repositories.

#### Build the probcomp repositories.

First prevent python from generating `.pyc` files.

```
$ echo PYTHONDONTWRITEBYTECODE=1 >> .pyenv2.7.6/bin/activate
$ source .pyenv2.7.6/bin/activate
```

For each cloned repository $REPO, build the repository.

```
$ for REPO in bayeslite-apsw bayeslite bdbcontrib cgpm crosscat Venturecxx;
    do cd $SHOME/$REPO;
    python setup.py build; cd ..;
    done
````

Do not use `python setup.py install`, because it invokes `pip` in unpredictable
ways. The required dependencies have already been installed.

#### Link the probcomp repositories to the virtualenv and configure some flags.

Run the following command to append the repositories to `PYTHONPATH`. Note that
it might be necessary to change the `build/lib .linux-x86_64-2.7` suffix to
match the actual `build/` directories produced in the previous step.

```
$ echo '
export PYTHONPATH=${SHOME}/bayeslite-apsw/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${SHOME}/bayeslite/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${SHOME}/bdbcontrib/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${SHOME}/cgpm/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${SHOME}/crosscat/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${SHOME}/iventure/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${SHOME}/Venturecxx/build/lib.linux-x86_64-2.7

export BAYESDB_DISABLE_VERSION_CHECK=1
export BAYESDB_WIZARD_MODE=1
export GPMCCDEBUG=1' >> .pyenv2.7.6/bin/activate
```

#### Verify the installation is successful.

Reactivate the virtualenv.

```
$ source .pyenv2.7.6/bin/activate
```

For each cloned repository, run the test suite (optional, may take a while).

```
$ for REPO in bayeslite-apsw bayeslite bdbcontrib cgpm crosscat Venturecxx;
    do cd $SHOME/$REPO;
    ./check.sh; cd ..;
    done
```

#### Create a new UNIX group `$G` for `$SHOME` and its subdirectories, and add yourself to the group.

The purpose of the group `$G` is to control the file/access permissions for all
users which are managed by `iventure_manager.py`.

```
$ addgroup $G
$ adduser $USER $G
```

#### Change permissions of `$SHOME` to the group.

```
$ chmod -R g+s $SHOME
$ chown -R $USER:$G $SHOME
```

TODO: Ask Taylor about getting all the future new files in the `$SHOME`
directory to inherit the group `$G`.
