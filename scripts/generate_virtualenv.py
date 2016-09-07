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
import subprocess
import shutil


def title(line):
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    return '%s%s%s' % (OKBLUE, line, ENDC)


DIR_IVENTURE = '/scratch/iventure'
FILE_REQUIREMENTS = 'requirements.txt'

# Retrieve the current directory of this script.
path_script = os.path.dirname(os.path.abspath(__file__))
path_requirements = os.path.join(path_script, FILE_REQUIREMENTS)

# Navigate to the iventure directory.
os.chdir(DIR_IVENTURE)

# ------------------------------------------------------------------------------

print title('Creating the virtualenv')

if os.path.exists('./.pyenv2.7.6'):
    print '\tRemoving existing virtualenv'
    shutil.rmtree('./.pyenv2.7.6')

subprocess.check_call('virtualenv -p /usr/bin/python .pyenv2.7.6', shell=True)

# ------------------------------------------------------------------------------

print title('Adding matplotlib libraries.')
# Add soft-links for matplotlib plotting.
os.chdir('.pyenv2.7.6/lib/python2.7/site-packages')
subprocess.check_call(
    'ln -s /usr/lib/python2.7/dist-packages/sip.so .', shell=True)
subprocess.check_call(
    'ln -s /usr/lib/python2.7/dist-packages/PyQt4 .', shell=True)

os.chdir(DIR_IVENTURE)

# ------------------------------------------------------------------------------

print title('Installing pip requirements.')

result = subprocess.Popen(
    'bash -c "source ./.pyenv2.7.6/bin/activate; pip install -r %s "'\
        % (path_requirements,),
    shell=True)
result.communicate()

# ------------------------------------------------------------------------------

print title('Adding probcomp libraries')
with open('.pyenv2.7.6/bin/activate', 'a') as f:

    f.writelines(str.join(
        os.linesep, [
            'export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}'
                '/scratch/fs/bayeslite-apsw/build/lib.linux-x86_64-2.7"',
            'export PYTHONPATH=$PYTHONPATH:'
                '/scratch/fs/bayeslite/build/lib.linux-x86_64-2.7',
            'export PYTHONPATH=$PYTHONPATH:/scratch/fs/bdbcontrib',
            'export PYTHONPATH=$PYTHONPATH:/scratch/fs/cgpm',]))

    f.write(os.linesep)

    f.writelines(str.join(
        os.linesep, [
            'export BAYESDB_DISABLE_VERSION_CHECK=1',
            'export BAYESDB_WIZARD_MODE=1',
            'export GPMCCDEBUG=1',]))

    f.write(os.linesep)

# Now clone the git repositories.

subprocess.check_call('git clone ')

# ------------------------------------------------------------------------------

print title('Done')

# Go back to the script.
os.chdir(path_script)
