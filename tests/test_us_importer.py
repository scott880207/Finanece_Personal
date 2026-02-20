import pytest
import os
import io
from datetime import date
from backend.importer.us_strategies import UsBrokerStrategy
from backend.importer.base import TransactionDTO

def test_us_broker_strategy_parse(tmp_path):
    # Create a dummy CSV that mimics the multi-section format
    csv_content = """商品代號,	商品名稱,	交易市場,	交易所,	持有股數
AMDG,Leverage Shares,美國,NASDAQ,100
交易日期,	商品代號,	商品名稱,	交易市場,	交易種類,	交易幣別,	交割幣別,	股數,	價格,	匯率,	成交金額,	手續費,	其他費用,	應收/付(-)金額
2026/01/07,AMDG,Leverage Shares 2X Long AMD Da,美國,買進,美金,美金,48.000000,24.7050,1.00,1185.840000,3.00,0.00,-1188.84
2026/01/12,QQQ,Invesco QQQ Trust Series 1,美國,賣出,美金,美金,2.257500,626.7000,1.00,1414.790000,3.00,0.00,1411.79
"""
    file_path = tmp_path / "dummy_us.csv"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(csv_content)

    strategy = UsBrokerStrategy()
    transactions = strategy.parse(str(file_path))

    assert len(transactions) == 2

    # Check first transaction
    t1 = transactions[0]
    assert t1.date == date(2026, 1, 7)
    assert t1.symbol == "AMDG"
    assert t1.action == "BUY"
    assert t1.quantity == 48.0
    assert t1.price == 24.705
    assert t1.fee == 3.0
    assert t1.asset_type == "US_STOCK"

    # Check second transaction
    t2 = transactions[1]
    assert t2.date == date(2026, 1, 12)
    assert t2.symbol == "QQQ"
    assert t2.action == "SELL"
    assert t2.quantity == 2.2575
    assert t2.price == 626.7
    assert t2.fee == 3.0
