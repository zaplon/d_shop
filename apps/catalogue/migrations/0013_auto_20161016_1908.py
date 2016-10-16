# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-16 19:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0012_auto_20160919_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='productcategory',
            name='filters',
            field=models.CharField(default=b'', max_length=100),
        ),
        migrations.AlterField(
            model_name='productattributevalue',
            name='slug',
            field=models.CharField(max_length=50, unique=False),
        ),
    ]
