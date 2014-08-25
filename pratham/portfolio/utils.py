import pandas
import datetime
import logging

def handle_upload_file(file_path):
    status, msg = True, 'Upload of file `%s` successful'%file_path
    #status, msg = False, 'Upload failed'
    return (status, msg)

def calc_per_share_values(txndf):
    #txndf['trddatetime'] = txndf.apply(lambda r: datetime.datetime.strptime(r.ix['trddate']+r.ix['trdtime'], "%d-%b-%y%H:%M:%S"), axis=1)
    txndf['price'] = txndf.apply(lambda r: -1*r.ix['price'] if 'B' == r.ix['buysell'] else r.ix['price'], axis=1)
    txndf['netamt_ps_tbt'] = txndf.buysell.apply(lambda bs: -1 if 'B' == bs else 1)
    txndf['netamt_ps_tbt'] = txndf.apply(lambda r: (r.ix['netamt_ps_tbt']*r.ix['value']-r.ix['brokamt'])/r.ix['qty'], axis=1)
    txndf['netamt_ps_real'] = txndf.apply(lambda r: r.ix['netamt']/r.ix['qty'], axis=1)
    # round off to 3 decimals
    txndf['netamt_ps_tbt'] = txndf.netamt_ps_tbt.apply(lambda v: round(v,3))
    txndf['netamt_ps_real'] = txndf.netamt_ps_real.apply(lambda v: round(v,3))
    return txndf

def convert_to_dataframe(recent_txn):
    # txn = Transaction(order_dt=itxn.order_dt, trd_dt=itxn.trd_dt, buysell=itxn.buysell, scrip=itxn.scrip, quantity=itxn.quantity, price=itxn.price, value=itxn.value, brok=itxn.brok, other=itxn.servtax+itxn.stampduty+itxn.txnchg+itxn.stotc+itxn.stt+itxn.sebitt+itxn.higheducess+itxn.otherchg, netamt=itxn.netamt)
    txndf = pandas.DataFrame(columns=['trddatetime', 'scrip', 'buysell', 'qty', 'price', 'brokamt', 'value', 'netamt'])
    for txn in recent_txn:
        txn_id = txn.id
        tmp_txndf = pandas.DataFrame({'trddatetime': {txn_id: txn.trd_dt}, 'scrip':{txn_id: txn.scrip}, 'buysell':{txn_id: txn.buysell}, 'qty':{txn_id: txn.quantity}, 'price':{txn_id: txn.price}, 'brokamt':{txn_id: txn.brok}, 'value':{txn_id: txn.value}, 'netamt':{txn_id: txn.netamt}})
        txndf = txndf.append(tmp_txndf)
    txndf = calc_per_share_values(txndf)
    txndf = txndf.sort('trddatetime')
    print txndf.head(10)
    print txndf.scrip.count()
    return txndf

def match_buys_for_sells(recent_txn):
    txndf = convert_to_dataframe(recent_txn)
    gains_records = []
    sell_txndf = txndf[txndf.buysell=='S']
    sell_txndf = sell_txndf.sort('trddatetime')
    buy_txndf = txndf[txndf.buysell=='B']
    buy_txndf = buy_txndf.sort('trddatetime')
    print sell_txndf.count()
    print buy_txndf.count()
    for sell_irow, sell_txn in sell_txndf.iterrows():
        logging.info("Sell-record#%s time: %s qty: %s price: %s ps_tbt: %s ps_real: %s scrip: %s"%(sell_irow, sell_txn.trddatetime, sell_txn.qty, sell_txn.price, sell_txn.netamt_ps_tbt, sell_txn.netamt_ps_real, sell_txn.scrip))
        print("Sell-record#%s time: %s qty: %s price: %s ps_tbt: %s ps_real: %s scrip: %s"%(sell_irow, sell_txn.trddatetime, sell_txn.qty, sell_txn.price, sell_txn.netamt_ps_tbt, sell_txn.netamt_ps_real, sell_txn.scrip))
        for buy_irow, buy_txn in buy_txndf.iterrows():
            if buy_txn.scrip != sell_txn.scrip:
                continue
            if sell_txn.qty > 0 and buy_txn.qty > 0:
                logging.info("Buy-record#%s time: %s qty: %s price: %s ps_tbt: %s ps_real: %s scrip: %s"%(buy_irow, buy_txn.trddatetime, buy_txn.qty, buy_txn.price, buy_txn.netamt_ps_tbt, buy_txn.netamt_ps_real, buy_txn.scrip))
                print("Buy-record#%s time: %s qty: %s price: %s ps_tbt: %s ps_real: %s scrip: %s"%(buy_irow, buy_txn.trddatetime, buy_txn.qty, buy_txn.price, buy_txn.netamt_ps_tbt, buy_txn.netamt_ps_real, buy_txn.scrip))
                min_qty = min(buy_txn.qty, sell_txn.qty)
                gains_records.append((buy_txn.scrip, min_qty, \
                        buy_txn.price+sell_txn.price, buy_txn.netamt_ps_tbt+sell_txn.netamt_ps_tbt, buy_txn.netamt_ps_real+sell_txn.netamt_ps_real, \
                        sell_txn.trddatetime, sell_txn.price, sell_txn.netamt_ps_tbt, sell_txn.netamt_ps_real, \
                        buy_txn.trddatetime, buy_txn.price, buy_txn.netamt_ps_tbt, buy_txn.netamt_ps_real))
                # updating buy_txn.qty or sell_txn.qty does NOT effect itended record, just a local change
                buy_txndf.qty[buy_irow] -= min_qty
                sell_txndf.qty[sell_irow] -= min_qty
                buy_txn.qty -= min_qty
                sell_txn.qty -= min_qty
                logging.info("Settled for %d qty"%min_qty)
    #
    header = ['scrip', 'qty', 'gain_price_ps', 'gain_tbt_ps', 'ebt_ps', 'sell_datetime', 'sell_price_ps', 'sell_tbt_ps', 'sell_real_ps', 'buy_datetime', 'buy_price_ps', 'buy_tbt_ps', 'buy_real_ps']
    gains_df = pandas.DataFrame(gains_records)
    assert len(gains_df.columns) == len(header)
    gains_df.columns = header
    holding_df = buy_txndf[buy_txndf.qty>0]
    return (gains_df, holding_df)

def fy_from_sell_datetime(sell_date):
    if sell_date.month <= 3:
        return "FY-%d"%sell_date.year
    else:
        return "FY-%d"%(sell_date.year+1)

STCG_NUM_DAYS = 365
STCG_TAX_PCT = 15.0

def update_gains_df_for_summary(gains_df):
    gains_df['fy'] = gains_df.sell_datetime.apply(lambda dt: fy_from_sell_datetime(dt))
    gains_df['sell_date'] = gains_df.sell_datetime.apply(lambda dt: dt.date())
    gains_df['buy_date'] = gains_df.buy_datetime.apply(lambda dt: dt.date())
    gains_df['hold_days'] = gains_df.apply(lambda r: (r.ix['sell_datetime']-r.ix['buy_datetime']).days, axis=1)
    gains_df['sell_price'] = gains_df.apply(lambda r: r.ix['qty']*r.ix['sell_price_ps'], axis=1)
    gains_df['buy_price'] = gains_df.apply(lambda r: r.ix['qty']*r.ix['buy_price_ps'], axis=1)
    gains_df['gain_price'] = gains_df.apply(lambda r: r.ix['qty']*r.ix['gain_price_ps'], axis=1)
    gains_df['gain_tbt'] = gains_df.apply(lambda r: r.ix['qty']*r.ix['gain_tbt_ps'], axis=1)
    gains_df['ebt'] = gains_df.apply(lambda r: r.ix['qty']*r.ix['ebt_ps'], axis=1)
    gains_df['is_stcg'] = gains_df.apply(lambda r: True if (r.ix['hold_days'] <= STCG_NUM_DAYS) else False, axis=1)
    gains_df['stcg_tax'] = gains_df.apply(lambda r: STCG_TAX_PCT*r.ix['gain_tbt']/100.0 if r.ix['is_stcg'] else 0.0, axis=1)
    gains_df['pat'] = gains_df.apply(lambda r: r.ix['ebt']-r.ix['stcg_tax'], axis=1)
    #
    gains_df['gain_price_pct'] = gains_df.apply(lambda r: -100.0*r.ix['gain_price']/r.ix['buy_price'], axis=1)
    gains_df['gain_tbt_pct'] = gains_df.apply(lambda r: -100.0*r.ix['gain_tbt']/r.ix['buy_price'], axis=1)
    gains_df['ebt_pct'] = gains_df.apply(lambda r: -100.0*r.ix['ebt']/r.ix['buy_price'], axis=1)
    gains_df['pat_pct'] = gains_df.apply(lambda r: -100.0*r.ix['pat']/r.ix['buy_price'], axis=1)
    gains_df['cagr_price'] = gains_df.apply(lambda r: STCG_NUM_DAYS*r.ix['gain_price_pct']/max(1,r.ix['hold_days']), axis=1)
    gains_df['cagr_tbt'] = gains_df.apply(lambda r: STCG_NUM_DAYS*r.ix['gain_tbt_pct']/max(1,r.ix['hold_days']), axis=1)
    gains_df['cagr_ebt'] = gains_df.apply(lambda r: STCG_NUM_DAYS*r.ix['ebt_pct']/max(1,r.ix['hold_days']), axis=1)
    gains_df['cagr_pat'] = gains_df.apply(lambda r: STCG_NUM_DAYS*r.ix['pat_pct']/max(1,r.ix['hold_days']), axis=1)
    return gains_df

