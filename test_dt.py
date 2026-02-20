import pandas as pd
from datetime import datetime

df = pd.read_csv('d:/Finanece_Personal/csv_for_import/20250219_20260219_record.csv', encoding='big5')
df.columns = df.columns.str.strip().str.replace('\t', '')
df = df[df['股票名稱'].astype(str).str.contains('00685L')].copy()

records = df.to_dict('records')
transactions = []
for row in records:
    date_str = str(row.get('成交日期', '')).strip()
    try:
        t_date = datetime.strptime(date_str, "%Y/%m/%d").date()
    except: continue
    
    action_raw = str(row.get('類別', '')).strip()
    
    try:
        qty = float(str(row.get('股數', 0)).replace(',', ''))
        price = float(str(row.get('成交價', 0)).replace(',', ''))
        fee = float(str(row.get('手續費', 0)).replace(',', ''))
        tax = float(str(row.get('交易稅', 0)).replace(',', ''))
    except: continue
    
    # flag day trade
    is_day_trade = '沖' in action_raw
    action = "BUY" if "買" in action_raw else "SELL"
    
    transactions.append({
        'date': t_date, 'action': action, 'quantity': qty, 
        'price': price, 'fee': fee, 'tax': tax, 'is_dt': is_day_trade
    })

transactions.sort(key=lambda x: x['date'])

buy_queue = []
realized_pnl_history = []
inventory = 0

# Process normal vs DT
# We assume DT buys and sells match on the same day. 
# They don't go into buy_queue.
for t in transactions:
    if t['is_dt']:
        # We can just record their PnL without affecting inventory.
        # But wait! A DT sell and DT buy must be paired.
        # They cancel out in inventory. So we just compute their net cashflow as PnL.
        pass
    else:
        if t['action'] == 'BUY':
            unit_fee = t['fee'] / t['quantity'] if t['quantity'] > 0 else 0
            buy_queue.append({'qty': t['quantity'], 'price': t['price'], 'unit_fee': unit_fee})
            inventory += t['quantity']
        elif t['action'] == 'SELL':
            sell_qty = t['quantity']
            sell_price = t['price']
            inventory -= sell_qty
            
            realized_pnl = 0.0
            matched_buy_fees = 0.0
            while sell_qty > 0 and buy_queue:
                buy_lot = buy_queue[0]
                if buy_lot['qty'] <= sell_qty:
                    qty_to_match = buy_lot['qty']
                    realized_pnl += (sell_price - buy_lot['price']) * qty_to_match
                    matched_buy_fees += qty_to_match * buy_lot['unit_fee']
                    sell_qty -= qty_to_match
                    buy_queue.pop(0)
                else:
                    qty_to_match = sell_qty
                    realized_pnl += (sell_price - buy_lot['price']) * qty_to_match
                    matched_buy_fees += qty_to_match * buy_lot['unit_fee']
                    buy_lot['qty'] -= qty_to_match
                    sell_qty = 0
            
            net_pnl = realized_pnl - t['fee'] - t['tax'] - matched_buy_fees
            realized_pnl_history.append({
                'date': t['date'], 'pnl': net_pnl, 'gross_pnl': realized_pnl, 
                'qty': t['quantity'], 'sell_fee': t['fee'], 'sell_tax': t['tax'], 'buy_fee': matched_buy_fees
            })

print(f"Inventory remaining: {inventory}")

recent_pnls = [x for x in realized_pnl_history if x['date'] >= datetime(2025, 11, 20).date()]
for p in recent_pnls:
    print(f"{p['date']} - Sold {p['qty']}: Net {p['pnl']:.0f} | Gross {p['gross_pnl']:.0f} | Fees/Tax: {p['sell_fee']}+{p['sell_tax']}+{p['buy_fee']:.0f}")

net_pnl_3m = sum(x['pnl'] for x in recent_pnls)
gross_pnl_3m = sum(x['gross_pnl'] for x in recent_pnls)
print(f"\nTotal Net PnL (3m): +{net_pnl_3m:.0f}")
print(f"Total Gross PnL (3m): +{gross_pnl_3m:.0f}")
