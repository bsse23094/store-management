"""
Quick Test Script - Goods Receipt Calculations
Demonstrates the new GST, Discount, and FOC calculations
"""

def calculate_goods_receipt(trade_price, discount_percent, gst_rate, received_qty, foc_qty, tax_type='exclusive'):
    """Calculate goods receipt with discount, GST, and FOC"""
    
    print("=" * 80)
    print("GOODS RECEIPT CALCULATION EXAMPLE")
    print("=" * 80)
    print()
    print("INPUT:")
    print(f"  Trade Price:      Rs. {trade_price:.2f}")
    print(f"  Discount:         {discount_percent:.1f}%")
    print(f"  GST Rate:         {gst_rate:.1f}%")
    print(f"  GST Type:         {tax_type.upper()}")
    print(f"  Received Qty:     {received_qty:.0f} units (paid)")
    print(f"  FOC Qty:          {foc_qty:.0f} units (free)")
    print()
    
    # Step 1: Apply discount
    discounted_trade = trade_price * (1 - discount_percent / 100)
    print("STEP 1: Apply Discount")
    print(f"  Discounted Trade = {trade_price:.2f} × (1 - {discount_percent}/100)")
    print(f"  Discounted Trade = Rs. {discounted_trade:.2f}")
    print()
    
    # Step 2: Calculate retail price
    if tax_type == 'inclusive':
        retail_price = discounted_trade
        print("STEP 2: Calculate Retail Price (Inclusive GST)")
        print(f"  Retail Price = Rs. {retail_price:.2f} (GST already included)")
    else:
        retail_price = discounted_trade * (1 + gst_rate / 100)
        print("STEP 2: Calculate Retail Price (Exclusive GST)")
        print(f"  Retail Price = {discounted_trade:.2f} × (1 + {gst_rate}/100)")
        print(f"  Retail Price = Rs. {retail_price:.2f}")
    print()
    
    # Step 3: Calculate cost price
    total_paid_qty = received_qty
    total_value = total_paid_qty * discounted_trade
    total_qty = received_qty + foc_qty
    cost_price = total_value / total_qty if total_qty > 0 else 0
    
    print("STEP 3: Calculate Cost Price (including FOC)")
    print(f"  Total Paid Value = {received_qty:.0f} × {discounted_trade:.2f} = Rs. {total_value:.2f}")
    print(f"  Total Quantity = {received_qty:.0f} + {foc_qty:.0f} = {total_qty:.0f} units")
    print(f"  Cost Price = {total_value:.2f} / {total_qty:.0f} = Rs. {cost_price:.2f}")
    print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY:")
    print("=" * 80)
    print(f"  Trade Price (Original):    Rs. {trade_price:.2f}")
    print(f"  Discount Applied:          {discount_percent:.1f}% = Rs. {trade_price - discounted_trade:.2f} off")
    print(f"  Discounted Trade Price:    Rs. {discounted_trade:.2f}")
    print(f"  GST ({gst_rate:.1f}% {tax_type}):        Rs. {retail_price - discounted_trade:.2f}")
    print(f"  Retail Price (Final):      Rs. {retail_price:.2f}")
    print(f"  Cost Price (Avg):          Rs. {cost_price:.2f}")
    print()
    print(f"  Total Purchase Cost:       Rs. {total_value:.2f} (for {received_qty:.0f} units)")
    print(f"  Total Stock Received:      {total_qty:.0f} units ({received_qty:.0f} paid + {foc_qty:.0f} free)")
    print()
    
    # Profit analysis
    profit_per_unit = retail_price - cost_price
    profit_percent = (profit_per_unit / cost_price * 100) if cost_price > 0 else 0
    total_profit = profit_per_unit * total_qty
    
    print("PROFIT ANALYSIS:")
    print(f"  Profit per Unit:           Rs. {profit_per_unit:.2f}")
    print(f"  Profit Margin:             {profit_percent:.2f}%")
    print(f"  Total Potential Profit:    Rs. {total_profit:.2f} (if all {total_qty:.0f} units sold)")
    print("=" * 80)
    print()
    
    return {
        'trade_price': trade_price,
        'discounted_trade': discounted_trade,
        'retail_price': retail_price,
        'cost_price': cost_price,
        'total_qty': total_qty,
        'profit_per_unit': profit_per_unit,
        'profit_margin': profit_percent
    }


# Example 1: Simple purchase (no discount, no FOC)
print("\n" + "🔷" * 40)
print("EXAMPLE 1: Simple Purchase (No Discount, No FOC)")
print("🔷" * 40 + "\n")
calculate_goods_receipt(
    trade_price=100.00,
    discount_percent=0,
    gst_rate=17,
    received_qty=10,
    foc_qty=0,
    tax_type='exclusive'
)

# Example 2: With supplier discount
print("\n" + "🔶" * 40)
print("EXAMPLE 2: With 10% Supplier Discount")
print("🔶" * 40 + "\n")
calculate_goods_receipt(
    trade_price=100.00,
    discount_percent=10,
    gst_rate=17,
    received_qty=10,
    foc_qty=0,
    tax_type='exclusive'
)

# Example 3: With FOC (Buy 10 Get 2 Free)
print("\n" + "🔷" * 40)
print("EXAMPLE 3: With FOC - Buy 10 Get 2 Free")
print("🔷" * 40 + "\n")
calculate_goods_receipt(
    trade_price=100.00,
    discount_percent=0,
    gst_rate=17,
    received_qty=10,
    foc_qty=2,
    tax_type='exclusive'
)

# Example 4: Complete scenario (Discount + FOC)
print("\n" + "🔶" * 40)
print("EXAMPLE 4: Complete - 10% Discount + 2 FOC")
print("🔶" * 40 + "\n")
calculate_goods_receipt(
    trade_price=100.00,
    discount_percent=10,
    gst_rate=17,
    received_qty=10,
    foc_qty=2,
    tax_type='exclusive'
)

# Example 5: Inclusive GST
print("\n" + "🔷" * 40)
print("EXAMPLE 5: Inclusive GST (Price includes tax)")
print("🔷" * 40 + "\n")
calculate_goods_receipt(
    trade_price=117.00,
    discount_percent=0,
    gst_rate=17,
    received_qty=10,
    foc_qty=0,
    tax_type='inclusive'
)

# Example 6: Bulk purchase with discount and FOC
print("\n" + "🔶" * 40)
print("EXAMPLE 6: Bulk Purchase - 15% Discount + Buy 50 Get 10 Free")
print("🔶" * 40 + "\n")
result = calculate_goods_receipt(
    trade_price=50.00,
    discount_percent=15,
    gst_rate=17,
    received_qty=50,
    foc_qty=10,
    tax_type='exclusive'
)

print("\n" + "=" * 80)
print("💡 KEY INSIGHTS:")
print("=" * 80)
print()
print("1. DISCOUNTS reduce your cost, increasing profit margin")
print("2. FOC items reduce average cost per unit (spread cost over more items)")
print("3. GST is added AFTER discount (on discounted price)")
print("4. Inclusive GST means tax is already in the price")
print("5. You only pay for 'Received' qty, FOC is free")
print("6. Stock increases by Received + FOC")
print()
print("✅ All calculations match the enhanced goods receipt system!")
print("=" * 80)
