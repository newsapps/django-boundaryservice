# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BoundarySet'
        db.create_table('boundaries_boundaryset', (
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, primary_key=True, db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('singular', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('authority', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('last_updated', self.gf('django.db.models.fields.DateField')()),
            ('source_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('licence_url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('boundaries', ['BoundarySet'])

        # Adding model 'Boundary'
        db.create_table('boundaries_boundary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('set', self.gf('django.db.models.fields.related.ForeignKey')(related_name='boundaries', to=orm['boundaries.BoundarySet'])),
            ('set_name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=200, db_index=True)),
            ('external_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=192, db_index=True)),
            ('metadata', self.gf('jsonfield.fields.JSONField')(blank=True)),
            ('shape', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
            ('simple_shape', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')()),
            ('centroid', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True)),
        ))
        db.send_create_signal('boundaries', ['Boundary'])

        # Adding unique constraint on 'Boundary', fields ['slug', 'set']
        db.create_unique('boundaries_boundary', ['slug', 'set_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Boundary', fields ['slug', 'set']
        db.delete_unique('boundaries_boundary', ['slug', 'set_id'])

        # Deleting model 'BoundarySet'
        db.delete_table('boundaries_boundaryset')

        # Deleting model 'Boundary'
        db.delete_table('boundaries_boundary')


    models = {
        'boundaries.boundary': {
            'Meta': {'unique_together': "(('slug', 'set'),)", 'object_name': 'Boundary'},
            'centroid': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True'}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'metadata': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '192', 'db_index': 'True'}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'boundaries'", 'to': "orm['boundaries.BoundarySet']"}),
            'set_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'shape': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'simple_shape': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'db_index': 'True'})
        },
        'boundaries.boundaryset': {
            'Meta': {'ordering': "('name',)", 'object_name': 'BoundarySet'},
            'authority': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'last_updated': ('django.db.models.fields.DateField', [], {}),
            'licence_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'singular': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'primary_key': 'True', 'db_index': 'True'}),
            'source_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['boundaries']
