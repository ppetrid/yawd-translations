# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Language.order'
        db.add_column(u'translations_language', 'order',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Language.order'
        db.delete_column(u'translations_language', 'order')


    models = {
        u'translations.language': {
            'Meta': {'ordering': "['name']", 'object_name': 'Language'},
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'image': ('elfinder.fields.ElfinderField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '7', 'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['translations']