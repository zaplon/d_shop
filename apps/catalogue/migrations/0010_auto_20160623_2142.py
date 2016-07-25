# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0009_auto_20160622_1125'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='external_category_id',
            new_name='external_id',
        ),
        migrations.AddField(
            model_name='productclass',
            name='external_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
