##
 # Copyright (c) 2015. Qubole Inc
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 #     http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 #    limitations under the License.
##
import os
from setuptools import setup, find_packages
import versioneer

versioneer.VCS = 'git'
versioneer.versionfile_source = 'qdstsdb/_version.py'
versioneer.versionfile_build = 'qdstsdb/_version.py'
versioneer.tag_prefix = '' # tags are like 1.2.0
versioneer.parentdir_prefix = 'qdstsdb-' # dirname like 'myproject-1.2.0'

with open('requirements.txt') as f:
    required = f.read().splitlines()


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="qdstsdb",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Rajat Venkatesh",
    author_email="https://github.com/vrajat",
    description="Install and run OpenTSDB on Qubole Data Service",
    keywords="qubole opentsdb",
    url="http://packages.python.org/qdstsdb",
    packages=find_packages(),
    scripts=[],
    entry_points={
        'console_scripts': ['qdstsdb=qdstsdb.command_line:main'],
    },
    install_requires=required,
    long_description=read('README.md'),
)
