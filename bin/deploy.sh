#!/usr/bin/env bash
$ ssh zapalj@188.166.28.157 << EOF
cd /var/www/dshop/
git pull
workon shop
./manage.py collectstatic
./manage.py compress
EOF