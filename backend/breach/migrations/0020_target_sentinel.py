# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-08-02 18:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('breach', '0019_auto_20160729_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='target',
            name='sentinel',
            field=models.CharField(default='^', help_text='Character used to seperate the complementary huffman characters, in order to avoid unwanted compression.', max_length=1),
        ),
    ]
