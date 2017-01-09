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

import os
import sqlite3
import subprocess

import notebook.auth


FNULL = open(os.devnull, 'w')


def unix_group_exists(groupname):
    retcode = subprocess.call([
        'egrep',
        '-i',
        '^%s' % (groupname,),
        '/etc/group'
        ], stdout=FNULL, stderr=FNULL)
    return True if retcode == 0 else False


def unix_port_active(port):
    result = subprocess.check_output(
        'nc -s0 127.0.0.1 %d >/dev/null </dev/null; echo $?' % (port,),
        shell=True)
    code = int(str.strip(result))
    return True if code == 0 else False


def unix_user_adddir(username, dir_name):
    subprocess.Popen(
        'sudo -iu %s sh -c "mkdir %s"' % (username, dir_name,),
        shell=True)


def unix_user_addgroup(username, groupname):
    process = subprocess.Popen(['sudo', 'adduser', username, groupname,])
    process.wait()


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


def unix_user_delete(username):
    # Delete the specified username, preserving the home directory.
    process = subprocess.Popen([
        'sudo',
            'deluser',
            username,
        ])
    process.wait()


def unix_user_exists(username):
    retcode = subprocess.call(
        ['id', '-u', username], stdout=FNULL, stderr=FNULL)
    return True if retcode == 0 else False


def unix_user_home(username):
    if not unix_user_exists(username):
        raise ValueError('No such user exists in UNIX: %s' % (username,))
    process = subprocess.Popen(
        'getent passwd %s | cut -d: -f6' % (username,),
        shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output, _err = process.communicate()
    return output.strip()


def unix_user_id(username):
    if not unix_user_exists(username):
        raise ValueError('No such users exists in UNIX: %s' % (username,))
    process = subprocess.Popen(
        ['id', '-u', username],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
    output, _err = process.communicate()
    return int(output)


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
