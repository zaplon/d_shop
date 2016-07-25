# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogue', '0008_auto_20160304_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='external_category_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='video_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
