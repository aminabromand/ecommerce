# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-09-02 08:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_auto_20180901_2353'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productpurchase',
            old_name='Refunded',
            new_name='refunded',
        ),
    ]
