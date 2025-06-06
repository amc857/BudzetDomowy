# Generated by Django 5.1.4 on 2025-05-14 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budzetApp', '0009_alter_userbudget_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='category',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userbudget',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterUniqueTogether(
            name='userbudget',
            unique_together={('user', 'budget')},
        ),
    ]
