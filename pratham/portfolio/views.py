from django.shortcuts import render, get_object_or_404
from portfolio.models import Transaction, TransactionForm, TransactionCsvForm, TransactionCsv

from utils import handle_upload_file, match_buys_for_sells, update_gains_df_for_summary

# Create your views here.
def index(request):
    print "Index.."
    error_message = success_message = ''
    recent_txn = Transaction.objects.all()
    buy_txn = [ txn for txn in recent_txn if 'B' == txn.buysell ]
    sell_txn = [ txn for txn in recent_txn if 'S' == txn.buysell ]
    num_buy_txn = len(buy_txn)
    num_sell_txn = len(sell_txn)
    sum_buy_netamt = sum( [txn.netamt for txn in buy_txn] )
    sum_sell_netamt = sum( [txn.netamt for txn in sell_txn] )
    return render(request, 'portfolio/index.html', {'num_buy_txn': num_buy_txn, 'num_sell_txn': num_sell_txn, 'sum_buy_netamt': sum_buy_netamt, 'sum_sell_netamt': sum_sell_netamt, 'error_message':error_message, 'success_message':success_message})

def detail(request, txn_id):
    print "Detail.."
    txn = get_object_or_404(Transaction, pk=txn_id)
    error_message = success_message = ''
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=txn)
        if form.is_valid():
            form.save()
            success_message = 'Transaction updated successfully!'
        else:
            error_message = 'Form input not valid!'
    else:
        form = TransactionForm(instance=txn)
    return render(request, 'portfolio/detail.html', {'txn':txn, 'form':form, 'error_message':error_message, 'success_message':success_message})

def upload(request):
    print "Upload"
    error_message = ''
    success_message = ''
    if 'POST' == request.method:
        print request.POST['title']
        upload_form = TransactionCsvForm(request.POST, request.FILES)
        if upload_form.is_valid():
            file_path = request.FILES['file']
            tcsv = TransactionCsv(title=request.POST['title'], file=file_path)
            tcsv.save()
            success_message = 'Saved `%s` successfully'%file_path
            tcsv.import_txn()
        else:
            error_message = 'Upload form not valid! %s'%upload_form.errors
        prev_csv = TransactionCsv.objects.all()
        print success_message, error_message
    else:
        prev_csv = TransactionCsv.objects.all()
        upload_form = TransactionCsvForm()
    return render(request, 'portfolio/upload.html', {'prev_csv':prev_csv, 'upload_form':upload_form, 'error_message':error_message, 'success_message':success_message})

def home(request):
    print "Home"
    return render(request, 'portfolio/home.html')

def dashboard(request):
    print "Dashboard"
    return render(request, 'portfolio/dashboard.html')


def history(request):
    print "History"
    error_message = ''
    success_message = ''
    recent_txn = Transaction.objects.order_by('-trd_dt')
    buy_txn = [ txn for txn in recent_txn if 'B' == txn.buysell ]
    sell_txn = [ txn for txn in recent_txn if 'S' == txn.buysell ]
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            error_message = 'Form input not valid!'
    else:
        form = TransactionForm()
    return render(request, 'portfolio/history.html', {'buy_txn':buy_txn, 'sell_txn':sell_txn, 'form':form, 'error_message':error_message, 'success_message':success_message})

def gains(request):
    print "Gains"
    error_message = success_message = ''
    recent_txn = Transaction.objects.order_by('trd_dt')
    gains_df, holding_df = match_buys_for_sells(recent_txn)
    gains_df = update_gains_df_for_summary(gains_df)
    gains_dict = gains_df.groupby('fy')['gain_price', 'gain_tbt', 'stcg_tax'].sum().to_dict()
    sum_gain_price = gains_df.gain_price.sum()
    sum_gain_tbt = gains_df.gain_tbt.sum()
    sum_stcg_tax = gains_df.stcg_tax.sum()
    return render(request, 'portfolio/gains.html', {'gains_df':gains_df, 'holding_df':holding_df, 'sum_gain_price':sum_gain_price, 'sum_gain_tbt':sum_gain_tbt, 'sum_stcg_tax':sum_stcg_tax, 'gains_dict':gains_dict, 'error_message':error_message, 'success_message':success_message})

def portfolio(request):
    print "Portfolio"
    error_message = success_message = ''
    recent_txn = Transaction.objects.order_by('trd_dt')
    gains_df, holding_df = match_buys_for_sells(recent_txn)
    return render(request, 'portfolio/portfolio.html', {'gains_df':gains_df, 'holding_df':holding_df, 'error_message':error_message, 'success_message':success_message})
