apt-get -qqy update
apt-get -qqy install postgresql
apt-get -qqy install python-psycopg2
apt-get -qqy install python-flask
apt-get -qqy install python-sqlalchemy
apt-get -qqy install python-pip
pip install bleach
pip install flask-seasurf
pip install github-flask
pip install httplib2
pip install oauth2client
pip install requests
pip install gunicorn
su postgres -c 'createuser -dRS vagrant'
su vagrant -c 'createdb'
su vagrant -c 'createdb catalog'
