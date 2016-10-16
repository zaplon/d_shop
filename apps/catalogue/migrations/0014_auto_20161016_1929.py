# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-16 19:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0013_auto_20161016_1908'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productcategory',
            name='filters',
        ),
        migrations.AddField(
            model_name='category',
            name='filters',
            field=models.CharField(default=b'', max_length=100, verbose_name='Filtry'),
        ),
    ]
