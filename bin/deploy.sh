#!/usr/bin/env bash
PYTHON=~/.virtualenvs/shop/bin/python2.7
ssh jan@188.166.28.157 << EOF
cd /var/www/dshop/d_shop
git pull
#static files
printf 'yes' | $PYTHON manage.py collectstatic
#compress js and css
$PYTHON manage.py compress
touch shop/wsgi.py
$PYTHON manage.py migrate
EOF