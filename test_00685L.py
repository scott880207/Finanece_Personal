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
    action = "BUY" if "買" in action_raw else "SELL"
    
    try:
        qty = float(str(row.get('股數', 0)).replace(',', ''))
        price = float(str(row.get('成交價', 0)).replace(',', ''))
        fee = float(str(row.get('手續費', 0)).replace(',', ''))
        tax = float(str(row.get('交易稅', 0)).replace(',', ''))
    except: continue
    transactions.append({'date': t_date, 'action': action, 'quantity': qty, 'price': price, 'fee': fee, 'tax': tax})
transactions.sort(key=lambda x: x['date'])

# Average Cost Logic
avg_cost_inventory = 0.0
total_cost = 0.0
avg_history = []

for t in transactions:
    if t['action'] == 'BUY':
        avg_cost_inventory += t['quantity']
        # Do we include fee in cost? Let's do both
        total_cost += (t['price'] * t['quantity'] + t['fee'])
    elif t['action'] == 'SELL':
        if avg_cost_inventory == 0:
            avg_cost = 0.0
        else:
            avg_cost = total_cost / avg_cost_inventory
        
        sell_qty = t['quantity']
        realized_pnl_gross = (t['price'] - avg_cost) * sell_qty
        realized_pnl_net = realized_pnl_gross - t['fee'] - t['tax']
        
        avg_history.append({'date': t['date'], 'qty': sell_qty, 'net_pnl': realized_pnl_net, 'gross_pnl': realized_pnl_gross})
        
        # reduce inventory and total_cost proportionally
        avg_cost_inventory -= sell_qty
        total_cost -= (avg_cost * sell_qty)

print(f"Average Cost Inventory: {avg_cost_inventory}")
recent_avg = [x for x in avg_history if x['date'] >= datetime(2025, 11, 20).date()]
print(f"Total Net PnL (Avg Cost, 3m): {sum(x['net_pnl'] for x in recent_avg):.2f}")
print(f"Total Gross PnL (Avg Cost, 3m): {sum(x['gross_pnl'] for x in recent_avg):.2f}")

RECENT_DATE = datetime(2025, 11, 20).date()
# What if we include the 2025-11-14 trade?
recent_avg_extended = [x for x in avg_history if x['date'] >= datetime(2025, 11, 1).date()]
print(f"Total Net PnL (Avg Cost, extended): {sum(x['net_pnl'] for x in recent_avg_extended):.2f}")
