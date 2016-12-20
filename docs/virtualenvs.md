# Setting up a python virtualenv with probcomp repositories and their dependencies.

#### Create a fresh directory and store its path in `$WRKDIR` (for workding directory).

```
export WRKDIR=/path/to/my/dir
$ mkdir $WRKDIR
```

#### Create a virtualenv in `$WRKDIR` called `.pyenv2.7.6`.

```
$ cd $WRKDIR
$ virtualenv -p /usr/bin/python .pyenv2.7.6
```

#### Activate the virtual environment, and ensure the right python interpreter is being referenced.

```
$ source .pyenv2.7.6/bin/activate
$ which python # should return $WRKDIR/.pyenv2.7.6/bin/python
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
$ cd $WRKDIR
$ git clone git@github.com:probcomp/bayeslite-apsw.git
$ git clone git@github.com:probcomp/bayeslite.git
$ git clone git@github.com:probcomp/cgpm.git
$ git clone git@github.com:probcomp/crosscat.git
$ git clone git@github.com:probcomp/iventure.git
$ git clone git@github.com:probcomp/Venturecxx.git
```

The `master` branch suffices for the repositories.

#### Build the probcomp repositories.

First prevent python from generating `.pyc` files.

```
$ echo PYTHONDONTWRITEBYTECODE=1 >> .pyenv2.7.6/bin/activate
$ source .pyenv2.7.6/bin/activate
```

For each cloned repository $REPO, build the repository.

```
$ for REPO in bayeslite-apsw bayeslite cgpm crosscat Venturecxx;
    do cd $WRKDIR/$REPO;
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
export PYTHONPATH=${WRKDIR}/bayeslite-apsw/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${WRKDIR}/bayeslite/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${WRKDIR}/cgpm/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${WRKDIR}/crosscat/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${WRKDIR}/iventure/build/lib.linux-x86_64-2.7
export PYTHONPATH=${PYTHONPATH}:${WRKDIR}/Venturecxx/build/lib.linux-x86_64-2.7

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
$ for REPO in bayeslite-apsw bayeslite cgpm crosscat Venturecxx;
    do cd $WRKDIR/$REPO;
    ./check.sh; cd ..;
    done
```

## [[Optional]] Setting UNIX group permissions for the virtualenv

#### Create a new UNIX group `$GRP` for `$WRKDIR` and its subdirectories, and add yourself to the group.

The purpose of the group `$GRP` is to control the file/access permissions for all
users which are managed by `iventure_manager.py`.

```
$ addgroup $GRP
$ adduser $USER $GRP
```

#### Change permissions of `$WRKDIR` to the new group `$GRP`.

```
$ chmod -R g+s $WRKDIR
$ chown -R $USER:$GRP $WRKDIR
```

TODO: Ask Taylor about getting all the future new files in the `$WRKDIR`
directory to inherit the group `$GRP`.
