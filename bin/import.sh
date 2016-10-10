#!/usr/bin/env bash
PYTHON=~/.virtualenvs/shop/bin/python2.7
TODAY=$(date +"%Y_%m_%d")
cd /var/www/dshop/d_shop/
$PYTHON manage.py import_catalogue --settings=production_settings > /var/www/dshop/d_shop/logs/import/import_$TODAY.log

