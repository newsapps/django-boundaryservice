# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BoundarySet'
        db.create_table('boundaryservice_boundaryset', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=256)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=64)),
            ('singular', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('kind_first', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('authority', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('last_updated', self.gf('django.db.models.fields.DateField')()),
            ('href', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('metadata_fields', self.gf('boundaryservice.fields.ListField')(separator='|', blank=True)),
        ))
        db.send_create_signal('boundaryservice', ['BoundarySet'])

        # Adding model 'Boundary'
        db.create_table('boundaryservice_boundary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=256)),
            ('set', self.gf('django.db.models.fields.related.ForeignKey')(related_name='boundaries', to=orm['boundaryservice.BoundarySet'])),
            ('kind', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('external_id', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=192, db_index=True)),
            ('display_name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('metadata', self.gf('boundaryservice.fields.JSONField')(blank=True)),
            ('shape', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=4269)),
            ('simple_shape', self.gf('django.contrib.gis.db.models.fields.MultiPolygonField')(srid=4269)),
            ('centroid', self.gf('django.contrib.gis.db.models.fields.PointField')(srid=4269, null=True)),
        ))
        db.send_create_signal('boundaryservice', ['Boundary'])

        # Adding model 'Shapefile'
        db.create_table('boundaryservice_shapefile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('singular', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('kind_first', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ider_namer', self.gf('django.db.models.fields.CharField')(default='simple', max_length=10)),
            ('ider_fields', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('name_namer', self.gf('django.db.models.fields.CharField')(default='simple', max_length=10)),
            ('name_fields', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('authority', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('domain', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('last_updated', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('href', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('encoding', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('srid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('simplification', self.gf('django.db.models.fields.DecimalField')(default=0.0001, null=True, max_digits=10, decimal_places=8, blank=True)),
        ))
        db.send_create_signal('boundaryservice', ['Shapefile'])

    def backwards(self, orm):
        # Deleting model 'BoundarySet'
        db.delete_table('boundaryservice_boundaryset')

        # Deleting model 'Boundary'
        db.delete_table('boundaryservice_boundary')

        # Deleting model 'Shapefile'
        db.delete_table('boundaryservice_shapefile')

    models = {
        'boundaryservice.boundary': {
            'Meta': {'ordering': "('kind', 'display_name')", 'object_name': 'Boundary'},
            'centroid': ('django.contrib.gis.db.models.fields.PointField', [], {'srid': '4269', 'null': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'external_id': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'metadata': ('boundaryservice.fields.JSONField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '192', 'db_index': 'True'}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'boundaries'", 'to': "orm['boundaryservice.BoundarySet']"}),
            'shape': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            'simple_shape': ('django.contrib.gis.db.models.fields.MultiPolygonField', [], {'srid': '4269'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256'})
        },
        'boundaryservice.boundaryset': {
            'Meta': {'ordering': "('name',)", 'object_name': 'BoundarySet'},
            'authority': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'href': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kind_first': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_updated': ('django.db.models.fields.DateField', [], {}),
            'metadata_fields': ('boundaryservice.fields.ListField', [], {'separator': "'|'", 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'singular': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '256'})
        },
        'boundaryservice.shapefile': {
            'Meta': {'object_name': 'Shapefile'},
            'authority': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'encoding': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'href': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ider_fields': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'ider_namer': ('django.db.models.fields.CharField', [], {'default': "'simple'", 'max_length': '10'}),
            'kind_first': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_updated': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'name_fields': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'name_namer': ('django.db.models.fields.CharField', [], {'default': "'simple'", 'max_length': '10'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'simplification': ('django.db.models.fields.DecimalField', [], {'default': '0.0001', 'null': 'True', 'max_digits': '10', 'decimal_places': '8', 'blank': 'True'}),
            'singular': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'srid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['boundaryservice']