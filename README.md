
## Prerequisites
* Python 3.10.14
* Postgres 16.3
* ViratualWrapper

## Setup instructions
* Update your system using the command :
```sh
  sudo apt update
```
* Install essentials given below:
```sh
  sudo apt install python3-pip
  sudo apt install git
```

* Create virtualenv and activate
```sh
  sudo pip install virtualenv
  sudo pip install virtualenvwrapper
  source /usr/local/bin/virtualenvwrapper.sh
```
* Setup gitlab ssh:

Just create key and go to gitlab. in user settings their we can add ssh public key.
```sh
ssh-keygen -t rsa -b 4096
```
* Create the navigate environment using the following command:
```sh
mkproject -p python3 navigate
```
* clone the project
```sh
$ git clone git@git.cied.in:fairfood/trace-v2/backend/navigate.git .
```
* After cloning:
```sh
* git fetch origin <enviroment>
* git checkout <enviroment>
* git pull origin <enviroment>
```
* Next to create .env:
```sh
touch .env
```
Copy the file .env.sample to .env and update the varialbes if necessary.

* Install Postgres and related libraries:
```sh
* sudo apt-get install postgresql postgresql-contrib libpq-dev gdal-bin postgis
```
* Create the database user and the database:

First, switch to the postgres system user account and run the psql command as follows:

```sh
$ sudo su - postgres
$ psql
postgres=#
```
Now create a new database and a user using the following commands.

```sh
postgres=# CREATE USER navigate WITH PASSWORD 'navigate';
postgres=# CREATE DATABASE navigate;
postgres=# GRANT ALL PRIVILEGES ON DATABASE navigate to navigate;
postgres=# \q
```

* Installing pgAdmin4
```sh
  * curl https://www.pgadmin.org/static/packages_pgadmin_org.pub
  * sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'
  * sudo apt install pgadmin4
```

* Install requirements
```sh
$ pip install requirements/<enviroment>.txt
```
If there is an error occur when install pillow library. Then install pillow as:
```sh
python3 -m pip install Pillow
```
After that complete the requirement installation.
