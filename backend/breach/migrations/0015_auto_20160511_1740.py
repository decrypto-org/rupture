# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-05-11 17:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('breach', '0014_auto_20160504_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='victim',
            name='realtimeurl',
            field=models.CharField(default='http://localhost:3031', help_text="The realtime module URL that the client should communicate with. This URL must include the 'http://' prefix.", max_length=255),
        ),
        migrations.AlterField(
            model_name='victim',
            name='method',
            field=models.IntegerField(choices=[(1, 'serial'), (2, 'divide&conquer')], default=1, help_text='Method of building candidate samplesets.'),
        ),
    ]
