# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0010_auto_20160623_2142'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productclass',
            name='external_id',
        ),
        migrations.AddField(
            model_name='productclass',
            name='external_type',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
