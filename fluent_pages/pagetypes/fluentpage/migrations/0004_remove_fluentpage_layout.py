# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fluentpage', '0003_migrate_translatable_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fluentpage',
            name='layout',
        ),
    ]