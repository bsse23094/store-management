"""
GST Calculation Methods - Comparison Test
Demonstrates both GST calculation methods side by side
"""

def calculate_method_1(trade_price, discount_percent, gst_rate, received_qty, foc_qty):
    """Method 1: GST Applicable on Trade Price (Exclusive)"""
    print("\n" + "="*80)
    print("METHOD 1: GST APPLICABLE ON TRADE PRICE (EXCLUSIVE)")
    print("="*80)
    print("\nFormula: Retail = Discounted Trade × (1 + GST%/100)")
    print("-"*80)
    
    # Step 1: Apply discount
    discounted_trade = trade_price * (1 - discount_percent / 100)
    print(f"\nStep 1: Apply Discount")
    print(f"  Discounted Trade = {trade_price:.2f} × (1 - {discount_percent}/100)")
    print(f"  Discounted Trade = Rs. {discounted_trade:.2f}")
    
    # Step 2: Calculate GST
    gst_amount = discounted_trade * (gst_rate / 100)
    retail_price = discounted_trade + gst_amount
    print(f"\nStep 2: Add GST on Top")
    print(f"  GST Amount = {discounted_trade:.2f} × ({gst_rate}/100)")
    print(f"  GST Amount = Rs. {gst_amount:.2f}")
    print(f"  Retail Price = {discounted_trade:.2f} + {gst_amount:.2f}")
    print(f"  Retail Price = Rs. {retail_price:.2f}")
    
    # Step 3: Calculate cost
    total_paid = received_qty * discounted_trade
    total_qty = received_qty + foc_qty
    cost_price = total_paid / total_qty if total_qty > 0 else 0
    
    print(f"\nStep 3: Calculate Cost (with FOC)")
    print(f"  Total Paid = {received_qty} × {discounted_trade:.2f} = Rs. {total_paid:.2f}")
    print(f"  Total Quantity = {received_qty} + {foc_qty} = {total_qty} units")
    print(f"  Cost per Unit = {total_paid:.2f} / {total_qty} = Rs. {cost_price:.2f}")
    
    # Profit analysis
    profit_per_unit = retail_price - cost_price
    profit_percent = (profit_per_unit / cost_price * 100) if cost_price > 0 else 0
    
    print(f"\n{'='*80}")
    print("RESULTS - METHOD 1:")
    print(f"{'='*80}")
    print(f"  Trade Price:           Rs. {trade_price:.2f}")
    print(f"  Discount:              {discount_percent}% = Rs. {trade_price - discounted_trade:.2f} off")
    print(f"  Discounted Trade:      Rs. {discounted_trade:.2f}")
    print(f"  GST ({gst_rate}%):             Rs. {gst_amount:.2f} (ADDED ON TOP)")
    print(f"  RETAIL PRICE:          Rs. {retail_price:.2f}")
    print(f"  Cost per Unit:         Rs. {cost_price:.2f}")
    print(f"  Profit per Unit:       Rs. {profit_per_unit:.2f}")
    print(f"  Profit Margin:         {profit_percent:.2f}%")
    print(f"  Total Stock:           {total_qty} units")
    print(f"{'='*80}")
    
    return {
        'retail': retail_price,
        'cost': cost_price,
        'profit': profit_per_unit,
        'margin': profit_percent,
        'gst': gst_amount
    }


def calculate_method_2(trade_price, discount_percent, gst_rate, received_qty, foc_qty):
    """Method 2: GST Included in Retail Price"""
    print("\n" + "="*80)
    print("METHOD 2: GST INCLUDED IN RETAIL PRICE (INCLUSIVE)")
    print("="*80)
    print("\nFormula: GST Amount = Retail × GST% / (100 + GST%)")
    print("-"*80)
    
    # Step 1: Apply discount
    discounted_trade = trade_price * (1 - discount_percent / 100)
    print(f"\nStep 1: Apply Discount")
    print(f"  Discounted Trade = {trade_price:.2f} × (1 - {discount_percent}/100)")
    print(f"  Discounted Trade = Rs. {discounted_trade:.2f}")
    
    # Step 2: Retail = Discounted (GST included)
    retail_price = discounted_trade
    gst_amount = retail_price * gst_rate / (100 + gst_rate)
    net_amount = retail_price - gst_amount
    
    print(f"\nStep 2: GST Already Included")
    print(f"  Retail Price = Rs. {retail_price:.2f} (GST included)")
    print(f"  GST Amount = {retail_price:.2f} × {gst_rate} / (100 + {gst_rate})")
    print(f"  GST Amount = Rs. {gst_amount:.2f}")
    print(f"  Net Amount = {retail_price:.2f} - {gst_amount:.2f}")
    print(f"  Net Amount = Rs. {net_amount:.2f}")
    
    # Step 3: Calculate cost
    total_paid = received_qty * discounted_trade
    total_qty = received_qty + foc_qty
    cost_price = total_paid / total_qty if total_qty > 0 else 0
    
    print(f"\nStep 3: Calculate Cost (with FOC)")
    print(f"  Total Paid = {received_qty} × {discounted_trade:.2f} = Rs. {total_paid:.2f}")
    print(f"  Total Quantity = {received_qty} + {foc_qty} = {total_qty} units")
    print(f"  Cost per Unit = {total_paid:.2f} / {total_qty} = Rs. {cost_price:.2f}")
    
    # Profit analysis
    profit_per_unit = retail_price - cost_price
    profit_percent = (profit_per_unit / cost_price * 100) if cost_price > 0 else 0
    
    print(f"\n{'='*80}")
    print("RESULTS - METHOD 2:")
    print(f"{'='*80}")
    print(f"  Trade Price:           Rs. {trade_price:.2f}")
    print(f"  Discount:              {discount_percent}% = Rs. {trade_price - discounted_trade:.2f} off")
    print(f"  Discounted Trade:      Rs. {discounted_trade:.2f}")
    print(f"  GST ({gst_rate}%):             Rs. {gst_amount:.2f} (INCLUDED IN RETAIL)")
    print(f"  RETAIL PRICE:          Rs. {retail_price:.2f}")
    print(f"  Net Amount:            Rs. {net_amount:.2f}")
    print(f"  Cost per Unit:         Rs. {cost_price:.2f}")
    print(f"  Profit per Unit:       Rs. {profit_per_unit:.2f}")
    print(f"  Profit Margin:         {profit_percent:.2f}%")
    print(f"  Total Stock:           {total_qty} units")
    print(f"{'='*80}")
    
    return {
        'retail': retail_price,
        'cost': cost_price,
        'profit': profit_per_unit,
        'margin': profit_percent,
        'gst': gst_amount
    }


def compare_methods(trade_price, discount_percent, gst_rate, received_qty, foc_qty):
    """Compare both methods side by side"""
    
    print("\n" + "="*80)
    print(f"COMPARISON: Trade Rs.{trade_price}, Discount {discount_percent}%, GST {gst_rate}%")
    print(f"Quantity: {received_qty} received + {foc_qty} FOC = {received_qty + foc_qty} total")
    print("="*80)
    
    method1 = calculate_method_1(trade_price, discount_percent, gst_rate, received_qty, foc_qty)
    method2 = calculate_method_2(trade_price, discount_percent, gst_rate, received_qty, foc_qty)
    
    print("\n" + "="*80)
    print("SIDE-BY-SIDE COMPARISON")
    print("="*80)
    print(f"{'Metric':<30} {'Method 1 (On Trade)':<25} {'Method 2 (In Retail)':<25}")
    print("-"*80)
    print(f"{'Retail Price':<30} Rs. {method1['retail']:>8.2f}              Rs. {method2['retail']:>8.2f}")
    print(f"{'GST Amount':<30} Rs. {method1['gst']:>8.2f}              Rs. {method2['gst']:>8.2f}")
    print(f"{'Cost per Unit':<30} Rs. {method1['cost']:>8.2f}              Rs. {method2['cost']:>8.2f}")
    print(f"{'Profit per Unit':<30} Rs. {method1['profit']:>8.2f}              Rs. {method2['profit']:>8.2f}")
    print(f"{'Profit Margin':<30} {method1['margin']:>8.2f}%              {method2['margin']:>8.2f}%")
    print("-"*80)
    
    # Calculate differences
    retail_diff = method1['retail'] - method2['retail']
    profit_diff = method1['profit'] - method2['profit']
    margin_diff = method1['margin'] - method2['margin']
    
    print(f"{'DIFFERENCE':<30} Rs. {retail_diff:>8.2f}              Rs. {profit_diff:>8.2f}  ({margin_diff:+.2f}%)")
    print("="*80)
    
    print("\nKEY INSIGHTS:")
    print(f"  • Method 1 retail is Rs. {retail_diff:.2f} HIGHER than Method 2")
    print(f"  • Method 1 profit is Rs. {profit_diff:.2f} MORE per unit")
    print(f"  • Method 1 margin is {margin_diff:.2f}% BETTER")
    print(f"  • Method 1: Better margins, higher prices")
    print(f"  • Method 2: Competitive prices, lower margins")
    print()


# Run comparison tests
print("\n" + "="*80)
print("GST CALCULATION METHODS - COMPARISON TESTS")
print("="*80)

# Test 1: Standard case
print("\n\n" + "TEST 1: Standard Purchase")
print("-"*80)
compare_methods(
    trade_price=100.00,
    discount_percent=0,
    gst_rate=17,
    received_qty=10,
    foc_qty=0
)

# Test 2: With discount
print("\n\n" + "TEST 2: With 10% Discount")
print("-"*80)
compare_methods(
    trade_price=100.00,
    discount_percent=10,
    gst_rate=17,
    received_qty=10,
    foc_qty=0
)

# Test 3: With FOC
print("\n\n" + "TEST 3: With FOC (Buy 10 Get 2 Free)")
print("-"*80)
compare_methods(
    trade_price=100.00,
    discount_percent=0,
    gst_rate=17,
    received_qty=10,
    foc_qty=2
)

# Test 4: Complete scenario
print("\n\n" + "TEST 4: Complete - Discount + FOC")
print("-"*80)
compare_methods(
    trade_price=100.00,
    discount_percent=10,
    gst_rate=17,
    received_qty=10,
    foc_qty=2
)

# Test 5: Higher GST rate
print("\n\n" + "TEST 5: Higher GST (25%)")
print("-"*80)
compare_methods(
    trade_price=100.00,
    discount_percent=10,
    gst_rate=25,
    received_qty=10,
    foc_qty=2
)

# Final summary
print("\n\n" + "="*80)
print("CONCLUSION")
print("="*80)
print("""
METHOD 1 (GST on Trade Price):
   • GST added on top of discounted trade price
   • Higher retail prices
   • Better profit margins
   • Clear tax visibility for customers
   • Best for: Standard retail, grocery stores

METHOD 2 (GST in Retail Price):
   • GST embedded in the retail price
   • Lower retail prices (competitive)
   • Lower profit margins
   • Customer sees one final price
   • Best for: MRP items, fixed pricing, electronics

RECOMMENDATION:
   Choose the method that matches your pricing strategy and customer expectations.
   You can switch between methods anytime in the system!
""")
print("="*80)
