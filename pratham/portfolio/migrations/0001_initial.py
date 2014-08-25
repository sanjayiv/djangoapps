# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Transaction'
        db.create_table(u'portfolio_transaction', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('trd_dt', self.gf('django.db.models.fields.DateTimeField')()),
            ('buysell', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('scrip', self.gf('django.db.models.fields.CharField')(max_length=500)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('price', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('value', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('brok', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('other', self.gf('django.db.models.fields.FloatField')(default=0.0)),
            ('netamt', self.gf('django.db.models.fields.FloatField')(default=0.0)),
        ))
        db.send_create_signal(u'portfolio', ['Transaction'])

        # Adding model 'TransactionCsv'
        db.create_table(u'portfolio_transactioncsv', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'portfolio', ['TransactionCsv'])


    def backwards(self, orm):
        # Deleting model 'Transaction'
        db.delete_table(u'portfolio_transaction')

        # Deleting model 'TransactionCsv'
        db.delete_table(u'portfolio_transactioncsv')


    models = {
        u'portfolio.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'brok': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'buysell': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'netamt': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'order_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'other': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'price': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'scrip': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'trd_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0.0'})
        },
        u'portfolio.transactioncsv': {
            'Meta': {'object_name': 'TransactionCsv'},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['portfolio']