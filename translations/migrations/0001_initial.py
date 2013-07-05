# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Language'
        db.create_table(u'translations_language', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=7, primary_key=True)),
            ('image', self.gf('elfinder.fields.ElfinderField')(max_length=100, null=True, blank=True)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'translations', ['Language'])


    def backwards(self, orm):
        # Deleting model 'Language'
        db.delete_table(u'translations_language')


    models = {
        u'translations.language': {
            'Meta': {'ordering': "['name']", 'object_name': 'Language'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'image': ('elfinder.fields.ElfinderField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '7', 'primary_key': 'True'})
        }
    }

    complete_apps = ['translations']