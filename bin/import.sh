#!/usr/bin/env bash
PYTHON=~/.virtualenvs/shop/bin/python2.7
TODAY=date+'%Y_%m_%d'
$PYTHON /var/www/dshop/d_shop/manage.py import_catalogue > /var/www/dshop/d_shop/logs/import_$TODAY.log