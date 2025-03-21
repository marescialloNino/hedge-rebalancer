# hedge_rebalancer.py
import pandas as pd
import os
from constants import HEDGABLE_TOKENS, METEORA_LATEST_CSV, KRYSTAL_LATEST_CSV, HEDGE_LATEST_CSV

def calculate_hedge_quantities():
    """Calculate total hedged quantities from Bitget positions by symbol."""
    hedge_quantities = {symbol: 0.0 for symbol in HEDGABLE_TOKENS}

    if os.path.exists(HEDGE_LATEST_CSV):
        try:
            hedge_df = pd.read_csv(HEDGE_LATEST_CSV)
            for _, row in hedge_df.iterrows():
                symbol = row["symbol"]  # Bitget symbol
                qty = float(row["quantity"] or 0)
                if symbol in HEDGABLE_TOKENS:
                    hedge_quantities[symbol] += qty
        except Exception as e:
            print(f"Error reading {HEDGE_LATEST_CSV}: {e}")
    else:
        print(f"{HEDGE_LATEST_CSV} not found.")

    return hedge_quantities

def calculate_lp_quantities():
    """Calculate total LP quantities by Bitget symbol, searching by token address."""
    lp_quantities = {symbol: 0.0 for symbol in HEDGABLE_TOKENS}

    # Read Meteora LP positions
    if os.path.exists(METEORA_LATEST_CSV):
        try:
            meteora_df = pd.read_csv(METEORA_LATEST_CSV)
            for _, row in meteora_df.iterrows():
                token_x = row["Token X Address"]
                token_y = row["Token Y Address"]
                qty_x = float(row["Token X Qty"] or 0)
                qty_y = float(row["Token Y Qty"] or 0)

                # Map token addresses to Bitget symbols
                for symbol, info in HEDGABLE_TOKENS.items():
                    if token_x in info["addresses"]:
                        lp_quantities[symbol] += qty_x
                    if token_y in info["addresses"]:
                        lp_quantities[symbol] += qty_y
        except Exception as e:
            print(f"Error reading {METEORA_LATEST_CSV}: {e}")
    else:
        print(f"{METEORA_LATEST_CSV} not found.")

    # Read Krystal LP positions
    if os.path.exists(KRYSTAL_LATEST_CSV):
        try:
            krystal_df = pd.read_csv(KRYSTAL_LATEST_CSV)
            for _, row in krystal_df.iterrows():
                token_x = row["Token X Address"]
                token_y = row["Token Y Address"]
                qty_x = float(row["Token X Qty"] or 0)
                qty_y = float(row["Token Y Qty"] or 0)

                # Map token addresses to Bitget symbols
                for symbol, info in HEDGABLE_TOKENS.items():
                    if token_x in info["addresses"]:
                        lp_quantities[symbol] += qty_x
                    if token_y in info["addresses"]:
                        lp_quantities[symbol] += qty_y
        except Exception as e:
            print(f"Error reading {KRYSTAL_LATEST_CSV}: {e}")
    else:
        print(f"{KRYSTAL_LATEST_CSV} not found.")

    return lp_quantities

def check_hedge_rebalance():
    """Compare hedged quantities with LP quantities and signal rebalance if >10% difference."""
    print("Starting hedge-rebalancer...")

    hedge_quantities = calculate_hedge_quantities()
    lp_quantities = calculate_lp_quantities()

    for symbol in HEDGABLE_TOKENS:
        hedge_qty = hedge_quantities[symbol]
        lp_qty = lp_quantities[symbol]
        if lp_qty == 0 and hedge_qty == 0:
            continue  

        difference = lp_qty + hedge_qty
        max_qty = max(lp_qty, hedge_qty)
        percentage_diff = (difference / max_qty) * 100 if max_qty > 0 else 0

        print(f"Token: {symbol}")
        print(f"  LP Qty: {lp_qty}, Hedged Qty: {hedge_qty}")
        print(f"  Difference: {difference} ({percentage_diff:.2f}%)")

        if percentage_diff > 10:
            print(f"  *** REBALANCE SIGNAL: {symbol} hedge differs by more than 10% ***")
        else:
            print(f"  No rebalance needed for {symbol}")

    print("Hedge rebalance check completed.")

if __name__ == "__main__":
    check_hedge_rebalance()