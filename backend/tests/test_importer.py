import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import date
from io import StringIO
from backend.importer.strategies import TwBrokerStrategy, TransactionDTO
from backend.importer.processor import TransactionProcessor
from backend.models import Transaction

# Mock CSV content mimicking the provided format
MOCK_CSV_CONTENT = """\t成交日期,\t類別,\t股票名稱,\t成交價,\t股數,\t金額,\t手續費,\t交易稅
2025/01/02,現股買進,元大美債20正2(00680L),10.5,1000,10500,20,0
2025/01/03,現股賣出,台積電(2330),600,100,60000,30,100
2025/01/04,融券買進,聯發科(2454),800,50,40000,40,200
2025/01/05,融券賣出,長榮(2603),150,200,30000,10,50
INVALID_DATE,現股買進,測試(9999),10,10,100,1,0
"""

@pytest.fixture
def strategy():
    return TwBrokerStrategy()

@pytest.fixture
def processor():
    return TransactionProcessor()

@pytest.fixture
def mock_db_session():
    session = MagicMock()
    # Mock query().scalar() to return False (no duplicate) by default
    session.query.return_value.scalar.return_value = False
    return session

def test_tw_broker_strategy_parse(strategy):
    # Create DataFrame before patching to use real pd.read_csv
    mock_df = pd.read_csv(StringIO(MOCK_CSV_CONTENT))
    
    # Mock pd.read_csv to return the pre-created DataFrame
    with patch('pandas.read_csv') as mock_read_csv:
        mock_read_csv.return_value = mock_df
        
        # Test parse method
        transactions = strategy.parse("dummy_path.csv")
        
        assert len(transactions) == 4 # Should skip the invalid date row
        
        # Check first transaction (BUY)
        t1 = transactions[0]
        assert t1.date == date(2025, 1, 2)
        assert t1.action == "BUY"
        assert t1.symbol == "00680L"
        assert t1.price == 10.5
        assert t1.quantity == 1000.0
        assert t1.fee == 20.0
        assert t1.tax == 0.0
        
        # Check second transaction (SELL)
        t2 = transactions[1]
        assert t2.action == "SELL"
        assert t2.symbol == "2330"

        # Check third transaction (BUY_CLOSE) - Short Cover
        t3 = transactions[2]
        assert t3.action == "BUY_CLOSE"
        
        # Check fourth transaction (SELL_OPEN) - Short Sell
        t4 = transactions[3]
        assert t4.action == "SELL_OPEN"

def test_processor_insert(processor, mock_db_session):
    transactions = [
        TransactionDTO(date=date(2025, 1, 1), asset_type="Stock", symbol="2330", action="BUY", price=500, quantity=1000),
        TransactionDTO(date=date(2025, 1, 2), asset_type="Stock", symbol="2330", action="SELL", price=550, quantity=1000)
    ]
    
    count = processor.process_transactions(transactions, mock_db_session)
    
    assert count == 2
    assert mock_db_session.add.call_count == 2
    mock_db_session.commit.assert_called_once()

def test_processor_duplicate_check(processor, mock_db_session):
    transactions = [
        TransactionDTO(date=date(2025, 1, 1), asset_type="Stock", symbol="2330", action="BUY", price=500, quantity=1000)
    ]
    
    # Mock duplicate check to return True
    mock_db_session.query.return_value.scalar.return_value = True
    
    count = processor.process_transactions(transactions, mock_db_session)
    
    assert count == 0
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_called_once()

