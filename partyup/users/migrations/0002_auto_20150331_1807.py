# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'date published')),
                ('admin', models.ForeignKey(to='users.Person')),
                ('created_by', models.ForeignKey(related_name='event_creator', to='users.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_created', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'date published')),
                ('created_by', models.ForeignKey(related_name='group_creator', to='users.Person')),
                ('events', models.ManyToManyField(to='users.Event')),
                ('group_members', models.ManyToManyField(to='users.Person')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='user_profile',
            name='birthday',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
