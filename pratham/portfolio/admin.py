from django.contrib import admin
from portfolio.models import Transaction, TransactionCsv

# Register your models here.
admin.site.register(Transaction)
admin.site.register(TransactionCsv)
