# Generated by Django 3.1.7 on 2021-03-09 15:06

import courses.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_announcement_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('description', models.TextField(blank=True, verbose_name='Descrição')),
                ('order', models.IntegerField(blank=True, default=0, verbose_name='Ordem')),
                ('release_date', models.DateField(blank=True, null=True, verbose_name='Data de liberação')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Atualizado em')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='courses.course', verbose_name='Curso')),
            ],
            options={
                'verbose_name': 'aula',
                'verbose_name_plural': 'aulas',
                'ordering': ('order',),
            },
        ),
        migrations.AlterModelOptions(
            name='enrollment',
            options={'verbose_name': 'inscrição', 'verbose_name_plural': 'inscrições'},
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nome')),
                ('embedded', models.TextField(blank=True, verbose_name='Vídeo da aula')),
                ('resource', models.FileField(blank=True, null=True, upload_to=courses.utils.material_directory_path, verbose_name='Recurso')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='materials', to='courses.lesson', verbose_name='Aula')),
            ],
            options={
                'verbose_name': 'material',
                'verbose_name_plural': 'materiais',
            },
        ),
    ]
