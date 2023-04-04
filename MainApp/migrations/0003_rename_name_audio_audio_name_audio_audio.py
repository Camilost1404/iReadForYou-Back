# Generated by Django 4.1.7 on 2023-04-04 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0002_audio_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='audio',
            old_name='name_audio',
            new_name='name',
        ),
        migrations.AddField(
            model_name='audio',
            name='audio',
            field=models.CharField(default='', max_length=150, verbose_name='Audio'),
            preserve_default=False,
        ),
    ]
