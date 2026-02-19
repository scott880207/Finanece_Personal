import requests
import json

BASE_URL = "http://localhost:8000"

def test_add_future_transaction():
    print("Testing Add Future Transaction...")
    
    # 1. Add first transaction (New - Buy)
    tx1 = {
        "date": "2025-11-24",
        "asset_type": "TW_FUTURE",
        "symbol": "TEST_FUTURE",
        "action": "OPEN_LONG",
        "price": 1345,
        "quantity": 1,
        "contract_month": "202512",
        "multiplier": 100,
        "fee": 50,
        "tax": 2,
        "assigned_margin": 10000
    }
    
    response = requests.post(f"{BASE_URL}/transactions/future", json=tx1)
    if response.status_code != 200:
        print(f"Failed to add tx1: {response.text}")
        return
    print("Tx1 added successfully.")
    
    # Verify Asset created
    response = requests.get(f"{BASE_URL}/assets/")
    assets = response.json()
    asset = next((a for a in assets if a['symbol'] == "TEST_FUTURE" and a['contract_month'] == "202512"), None)
    
    if not asset:
        print("Asset not found!")
        return
        
    print(f"Asset found: Qty={asset['quantity']}, Cost={asset['cost']}")
    assert asset['quantity'] == 1
    assert asset['cost'] == 1345
    
    # 2. Add second transaction (New - Buy, Aggregation)
    tx2 = {
        "date": "2025-11-24",
        "asset_type": "TW_FUTURE",
        "symbol": "TEST_FUTURE",
        "action": "OPEN_LONG",
        "price": 1075,
        "quantity": 1,
        "contract_month": "202512",
        "multiplier": 100,
        "fee": 50,
        "tax": 2,
        "assigned_margin": 0 # Using remaining margin
    }
    
    response = requests.post(f"{BASE_URL}/transactions/future", json=tx2)
    if response.status_code != 200:
        print(f"Failed to add tx2: {response.text}")
        return
    print("Tx2 added successfully.")
    
    # Verify Asset updated
    response = requests.get(f"{BASE_URL}/assets/")
    assets = response.json()
    asset = next((a for a in assets if a['symbol'] == "TEST_FUTURE" and a['contract_month'] == "202512"), None)
    
    print(f"Asset updated: Qty={asset['quantity']}, Cost={asset['cost']}")
    
    # Expected Cost: ((1345 * 1) + (1075 * 1)) / 2 = 1210
    assert asset['quantity'] == 2
    assert asset['cost'] == 1210
    
    print("Verification Passed!")

if __name__ == "__main__":
    try:
        test_add_future_transaction()
    except Exception as e:
        print(f"Test failed with error: {e}")
