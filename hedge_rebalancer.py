# hedge_rebalancer.py
import pandas as pd
import os
from constants import HEDGABLE_TOKENS, METEORA_LATEST_CSV, KRYSTAL_LATEST_CSV, HEDGE_LATEST_CSV

def calculate_hedge_quantities():
    """Calculate total hedged (short) quantities from Bitget positions by symbol."""
    hedge_quantities = {symbol: 0.0 for symbol in HEDGABLE_TOKENS}
    if os.path.exists(HEDGE_LATEST_CSV):
        try:
            hedge_df = pd.read_csv(HEDGE_LATEST_CSV)
            for _, row in hedge_df.iterrows():
                symbol = row["symbol"]
                qty = float(row["quantity"] or 0)  # Negative for short positions
                if symbol in HEDGABLE_TOKENS:
                    hedge_quantities[symbol] += qty  # Accumulate negative quantities
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
    """Compare LP quantities with absolute hedge quantities (short) and signal directional rebalance."""
    print("Starting hedge-rebalancer...")

    # Calculate quantities
    hedge_quantities = calculate_hedge_quantities()  # Negative values
    lp_quantities = calculate_lp_quantities()        # Positive values

    # Compare and signal rebalance
    for symbol in HEDGABLE_TOKENS:
        hedge_qty = hedge_quantities[symbol]  # Negative (short)
        lp_qty = lp_quantities[symbol]        # Positive (long)
        abs_hedge_qty = abs(hedge_qty)       # Absolute value of short position

        # Calculate directional difference: LP vs absolute hedge qty
        difference = lp_qty - abs_hedge_qty  # Positive: under-hedged, Negative: over-hedged
        abs_difference = abs(difference)
        percentage_diff = (abs_difference / lp_qty) * 100 if lp_qty > 0 else 0

        # Skip if no LP exposure and no hedge
        if lp_qty == 0 and hedge_qty == 0:
            continue

        print(f"Token: {symbol}")
        print(f"  LP Qty: {lp_qty}, Hedged Qty: {hedge_qty} (Short: {abs_hedge_qty})")
        print(f"  Difference: {difference} ({percentage_diff:.2f}% of LP)")

        # Signal rebalance if difference > 10% of LP qty (only if LP qty > 0)
        if lp_qty > 0 and abs_difference > 0.1 * lp_qty:
            if difference > 0:
                print(f"  *** REBALANCE SIGNAL: Increase short hedge by {abs_difference:.2f} for {symbol} ***")
            else:
                print(f"  *** REBALANCE SIGNAL: Decrease short hedge by {abs_difference:.2f} for {symbol} ***")
        elif lp_qty == 0 and hedge_qty != 0:
            # Special case: No LP exposure but hedged
            print(f"  *** REBALANCE SIGNAL: Close short hedge of {abs_hedge_qty:.2f} for {symbol} (no LP exposure) ***")
        else:
            print(f"  No rebalance needed for {symbol}")

    print("Hedge rebalance check completed.")

if __name__ == "__main__":
    check_hedge_rebalance()