# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-07-19 16:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('order', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Choice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('value', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='CustomService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('address', models.GenericIPAddressField()),
                ('local_id', models.IntegerField()),
                ('active', models.BooleanField(default=True)),
                ('last_access', models.DateTimeField(auto_now_add=True)),
                ('timeout', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='DeviceType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='EnumValueType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='LogAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('CREATE', 'CREATE'), ('UPDATE', 'UPDATE'), ('READ', 'READ'), ('DELETE', 'DELETE'), ('ERROR', 'ERROR'), ('STATUS DOWN', 'STATUS DOWN'), ('STATUS UP', 'STATUS UP')], max_length=15)),
                ('description', models.TextField()),
                ('instance_class', models.CharField(choices=[('HOUSE', 'HOUSE'), ('AREA', 'AREA'), ('DIVISION', 'DIVISION'), ('SERVER', 'SERVER'), ('DEVICE', 'DEVICE'), ('SERVICE', 'SERVICE')], max_length=10)),
                ('instance_id', models.IntegerField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('value', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='PropertyChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('new_state_text', models.TextField()),
                ('source', models.CharField(choices=[('CLOUD', 'CLOUD'), ('DEVICE', 'DEVICE')], max_length=6)),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('access_mode', models.CharField(choices=[('RO', 'RO'), ('WO', 'WO'), ('RW', 'RW')], default='RO', max_length=2)),
                ('value_type_class', models.CharField(choices=[('SCALAR', 'Scalar'), ('ENUM', 'Enumerated')], max_length=4)),
                ('value_type_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='ScalarValueType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('units', models.CharField(max_length=10)),
                ('default_value', models.FloatField(default=0)),
                ('min_value', models.FloatField(default=0)),
                ('max_value', models.FloatField(default=0)),
                ('step', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('coap_address', models.GenericIPAddressField()),
                ('coap_port', models.IntegerField()),
                ('proxy_address', models.GenericIPAddressField()),
                ('proxy_port', models.IntegerField()),
                ('multicast', models.BooleanField()),
                ('active', models.BooleanField(default=True)),
                ('last_access', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
    ]
