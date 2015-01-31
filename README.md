Installation
============
Virtualenv
----------
Pip supports installation from private git repos. 
The command to install pip in a virtualenv (or when the account has to git): 

    pip install git+ssh://git@github.com/vrajat/quboletsdb.git@<version>

System (as root/sudo)
---------------------
If you want to install using root, you need access to git and consequently the correct ssh keys.
Create a file to override ssh with the following bash command.

    ssh -i /home/<user>/.ssh/id_rsa $@

On aws machines, user will be *ec2-user*.
Login as root.

    export GIT_SSH=/home/<user>/ssh_wrapper
    pip install git+ssh://git@github.com/vrajat/quboletsdb.git@<version>

Configuration
=============    
You'll need to store S3 Access keys in ~/.qdsrc. The format is:

    [default]
    access_key = <access key>
    secret_key = <secret key>

Development Setup
=================
VirtualEnv
----------
1. Make sure you have [virtualenv](https://pypi.python.org/pypi/virtualenv) setup.
2. Create a virtualenv for this project.
3. Ignore egg-info in [git](https://help.github.com/articles/ignoring-files#global-gitignore).
4. Activate the virtualenv every time. (Ugh! One more thing to forget)
5. Change to source directory
6. Run develop script


    mkdir ~/python-envs;
    virtualenv ~/python-envs/tsdb;

    source ~/python-envs/tsdb/bin/activate;
    cd ~/src/tsdb/
    
    python setup.py develop;

Release Process
===============
Version Numbers
---------------

Version numbers have major.minor.patch parts. All are natural numbers.
For bug fixes please increment patch numbers.
For new features please increment major or minor versions as per [Semantic Versions] (http://semver.org)

Tag a new release
-----------------
1. Create a git tag with the version number. The format is major.minor.patch
2. Git Push to let everyone know.
3. Make profit!


    cd [quboletsdb checkout dir]  
    git tag -a 0.2.4 -m '0.2.4' #For e.g.  
    git push --tags 

4. If for some reason you see the string "dirty" in the version string even though 
   you are sure there are no uncommitted changes in your code, run:
   
    git update-index --refresh    