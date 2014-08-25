from django.db import models
from django.forms import ModelForm

import os
import pandas
import datetime

# Create your models here.
class Transaction(models.Model):
    order_dt = models.DateTimeField('Order DateTime')
    trd_dt = models.DateTimeField('Order DateTime')
    buysell = models.CharField('Buy/Sell', max_length=1, choices=(('B','Buy'),('S','Sell')))
    scrip = models.CharField('Scrip name', max_length=500)
    quantity = models.IntegerField('Quantity', default=0)
    price = models.FloatField('Price per share', default=0.0)
    value = models.FloatField('Value of trade', default=0.0)
    brok = models.FloatField('Brokerage value of trade', default=0.0)
    other = models.FloatField('Other charges of trade, including stt, educess etc', default=0.0)
    netamt = models.FloatField('Net amount of trade', default=0.0)

    def __str__(self):
        if 'B' == self.buysell:
            return "Bought %s shares of %s @%s on %s"%(self.quantity, self.scrip, self.price, self.trd_dt.date())
        else:
            return "Sold %s shares of %s @%s on %s"%(self.quantity, self.scrip, self.price, self.trd_dt.date())

    def print_pretty(self):
        if 'B' == self.buysell:
            return "Bought %s shares of %s @%s on %s"%(self.quantity, self.scrip, self.price, self.trd_dt.date())
        else:
            return "Sold %s shares of %s @%s on %s"%(self.quantity, self.scrip, self.price, self.trd_dt.date())

class TransactionForm(ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

class TransactionCsv(models.Model):
    title = models.CharField(max_length=256)
    file = models.FileField('Transaction CSV', upload_to='./tmp/')

    def __str__(self):
        return self.file

    def print_pretty(self):
        return "File for `%s` saved as `%s`"%(self.title, self.file)

    def import_txn(self):
        file_path = str(self.file)
        if os.path.exists(file_path):
            print "File exists"
            txndf = pandas.read_csv(file_path, header=None)
            columns = [ 'trddate', 'trdno', 'orderno', 'exchange', 'settno', 'setttype', 'trdtime', 'ordertime',
                'scrip', 'buysell', 'quantity', 'price', 'value', 'squpdel', 'brok', 'servtax', 'stampduty', 
                'txnchg', 'stotc', 'stt', 'sebitt', 'educess', 'higheducess', 'otherchg', 'netamt',
                'product', 'sipflag', 'siprefno']
            assert len(columns) == len(txndf.columns)
            txndf.columns = columns
            assert set(txndf.buysell) == set(['S','B'])
            txndf.drop_duplicates(inplace=True)
            txndf['trd_dt'] = txndf.apply(lambda r: datetime.datetime.strptime(r.ix['trddate']+r.ix['trdtime'], "%d-%b-%y%H:%M:%S"), axis=1)
            txndf['order_dt'] = txndf.apply(lambda r: datetime.datetime.strptime(r.ix['trddate']+r.ix['ordertime'], "%d-%b-%y%H:%M:%S"), axis=1)
            last_id = -1
            for irow, itxn in txndf.iterrows():
                txn = Transaction(order_dt=itxn.order_dt, trd_dt=itxn.trd_dt, buysell=itxn.buysell, scrip=itxn.scrip, quantity=itxn.quantity, price=itxn.price, value=itxn.value, brok=itxn.brok, other=itxn.servtax+itxn.stampduty+itxn.txnchg+itxn.stotc+itxn.stt+itxn.sebitt+itxn.higheducess+itxn.otherchg, netamt=itxn.netamt)
                txn.save()
                last_id = txn.id
            print "Saved up to %d id"%last_id
        else:
            print "File does not exist"

class TransactionCsvForm(ModelForm):
    class Meta:
        model = TransactionCsv
        fields = '__all__'

