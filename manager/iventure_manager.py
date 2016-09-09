# -*- coding: utf-8 -*-

#   Copyright (c) 2010-2016, MIT Probabilistic Computing Project
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import notebook.auth
import os
import sqlite3
import subprocess


FNULL = open(os.devnull, 'w')


def unix_user_exists(username):
    retcode = subprocess.call(
        ['id', '-u', username], stdout=FNULL, stderr=FNULL)
    return True if retcode == 0 else False


def unix_group_exists(groupname):
    retcode = subprocess.call([
        'egrep',
        '-i',
        '^%s' % (groupname,),
        '/etc/group'
        ], stdout=FNULL, stderr=FNULL)
    return True if retcode == 0 else False


def unix_user_create(username, home):
    # Create the user without a password or home directory.
    process = subprocess.Popen([
        'sudo',
            'adduser',
            '--gecos',
            '""',
            '--disabled-password',
            '--home',
            home,
            username,
        ])
    process.wait()


def unix_user_ingroup(username, groupname):
    if not unix_user_exists(username):
        raise ValueError('No such user exists in UNIX: %s' % (username,))
    try:
        retcode = subprocess.check_call(
            'id -nG %s | grep -c %s' % (username, groupname),
            shell=True, stdout=FNULL, stderr=FNULL)
        return True if retcode == 0 else False
    except subprocess.CalledProcessError:
        return False


def unix_user_home(username):
    if not unix_user_exists(username):
        raise ValueError('No such user exists in UNIX: %s' % (username,))
    process = subprocess.Popen(
        'getent passwd %s | cut -d: -f6' % (username,),
        shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output, _err = process.communicate()
    return output.strip()


def unix_user_addgroup(username, groupname):
    process = subprocess.Popen(['sudo', 'adduser', username, groupname,])
    process.wait()


def jupyter_create_config(username, groupname, venv):
    # Retrieve information about the user home directory.
    file_config = os.path.join(
        unix_user_home(username), '.jupyter', 'jupyter_notebook_config.py')

    # Retrieve a password for the jupyter server.
    passwd = notebook.auth.passwd()

    # Create a .jupyter/jupter_notebook_config.py file, and append the
    # necessary files.
    process = subprocess.Popen(
        'sudo -iu %s sh -c ". %s/bin/activate; '
        'cd ~; '
        'jupyter notebook --generate-config -y;"; '
        'sudo sh -c "chown %s:%s %s; sudo chmod g+w %s;"'
            % (username, venv, username,
                groupname, file_config, file_config),
        shell=True)
    process.wait()

    # Append the necessary lines to the config file.
    with open(file_config, 'a') as f:
        # Prepare the lines to append.
        # XXX Update these to use nginx.
        lines = str.join(os.linesep, [
            '# XXX Following created by iventure_manager.py',
            'c.NotebookApp.open_browser = False',
            'c.NotebookApp.ip = u\"0.0.0.0\"',
            'c.NotebookApp.password = u"%s"' % (passwd,),
        ])
        f.write(os.linesep)
        f.write(lines)


def jupyter_launch_server(username, venv):
    # Run this in the background now.
    subprocess.Popen(
        'sudo -iu %s sh -c ". %s/bin/activate;'
        'cd ~; '
        'nohup jupyter notebook;"'
            % (username, venv,),
            shell=True)

    # Kill the two parent processes which spawned the notebook.


class IVentureManager(object):


    CONFIG = {
        'database' : 'iventure_manager.sqlite3',
        'root_directory': os.path.join('/','scratch','iventure'),
        'unix_group': 'iventure',
    }


    def __init__(self, database=None, unix_group=None, root_directory=None):
        self.db = database
        self.unix_group = IVentureManager.CONFIG['unix_group']
        self.root_directory = IVentureManager.CONFIG['root_directory']


    def create_user(self, username):
        # Create UNIX username, if does not exist.
        if not unix_user_exists(username):
            unix_user_create(
                username, home=os.path.join(self.root_directory, username))

        # Add username to the group if not member.
        if not unix_user_ingroup(username, self.unix_group):
            unix_user_addgroup(username, self.unix_group)
            unix_user_addgroup(username, 'users')

        # Prepare the jupyter server configruation.
        pass


    def start_server(self, username):
        venv = os.path.join(self.root_directory,'.pyenv2.7.6','bin','activate')
        jupyter_launch_server(username, venv)

    def stop_server(self, username):
        pass

    def restart_server(self, username):
        pass

if False:
    # Create a user fs-test.
    assert not unix_user_exists('fs-test')
    unix_user_create('fs-test', '/scratch/iventure')
    unix_user_addgroup('fs-test', 'iventure')
