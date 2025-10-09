# 📊 GST CALCULATION METHODS - COMPLETE GUIDE

## ✨ NEW FEATURE: GST Calculation Method Selection

You now have **two methods** to calculate GST in the Goods Receipt system:

### Method 1: **Applicable on Trade Price** (Exclusive GST)
GST is added **on top** of the discounted trade price.

**Formula:**
```
Retail Price = Discounted Trade × (1 + GST% / 100)
GST Amount = Discounted Trade × (GST% / 100)
```

### Method 2: **Included in Retail Price** (Inclusive GST)
GST is **already included** in the retail price.

**Formula:**
```
Retail Price = Discounted Trade (GST already in it)
GST Amount = Retail Price × GST% / (100 + GST%)
Net Amount = Retail Price - GST Amount
```

---

## 📐 Calculation Examples

### 🔵 Method 1: Applicable on Trade Price

#### Example 1A: Simple Case
```
Trade Price:        Rs. 100.00
Discount:           0%
Discounted Trade:   Rs. 100.00
GST Rate:           17%

Calculation:
GST Amount = 100 × (17/100) = Rs. 17.00
Retail Price = 100 + 17 = Rs. 117.00

Result:
- You buy for: Rs. 100.00
- GST charged: Rs. 17.00
- Customer pays: Rs. 117.00
```

#### Example 1B: With Discount
```
Trade Price:        Rs. 100.00
Discount:           10%
Discounted Trade:   Rs. 90.00
GST Rate:           17%

Calculation:
GST Amount = 90 × (17/100) = Rs. 15.30
Retail Price = 90 + 15.30 = Rs. 105.30

Result:
- You buy for: Rs. 90.00 (saved Rs. 10)
- GST charged: Rs. 15.30
- Customer pays: Rs. 105.30
```

#### Example 1C: With Discount + FOC
```
Trade Price:        Rs. 100.00
Discount:           10%
Discounted Trade:   Rs. 90.00
GST Rate:           17%
Received:           10 units
FOC:                2 units

Calculation:
GST Amount = 90 × (17/100) = Rs. 15.30
Retail Price = 90 + 15.30 = Rs. 105.30
Total Paid = 10 × 90 = Rs. 900
Cost per Unit = 900 / 12 = Rs. 75.00

Result:
- You buy for: Rs. 75.00 per unit (average)
- Customer pays: Rs. 105.30 per unit
- Profit per unit: Rs. 30.30 (40.4% margin!)
```

---

### 🟢 Method 2: Included in Retail Price

#### Example 2A: Simple Case
```
Retail Price:       Rs. 117.00 (GST included)
GST Rate:           17%

Calculation:
GST Amount = 117 × 17 / (100 + 17) = Rs. 17.00
Net Amount = 117 - 17 = Rs. 100.00
Trade Price = Rs. 117.00 (displayed as retail)

Result:
- Customer pays: Rs. 117.00
- GST portion: Rs. 17.00
- Net amount: Rs. 100.00
```

#### Example 2B: With Discount
```
Trade Price:        Rs. 100.00
Discount:           10%
Discounted Trade:   Rs. 90.00
Retail Price:       Rs. 90.00 (GST included)
GST Rate:           17%

Calculation:
GST Amount = 90 × 17 / (100 + 17) = Rs. 13.08
Net Amount = 90 - 13.08 = Rs. 76.92

Result:
- Customer pays: Rs. 90.00
- GST portion: Rs. 13.08
- Net amount: Rs. 76.92
```

#### Example 2C: With Discount + FOC
```
Trade Price:        Rs. 100.00
Discount:           10%
Discounted Trade:   Rs. 90.00
Retail Price:       Rs. 90.00 (GST included)
GST Rate:           17%
Received:           10 units
FOC:                2 units

Calculation:
GST Amount = 90 × 17 / (100 + 17) = Rs. 13.08
Net Amount = 90 - 13.08 = Rs. 76.92
Total Paid = 10 × 90 = Rs. 900
Cost per Unit = 900 / 12 = Rs. 75.00

Result:
- You buy for: Rs. 75.00 per unit (average)
- Customer pays: Rs. 90.00 per unit (GST included)
- GST per unit: Rs. 13.08
- Profit per unit: Rs. 15.00
```

---

## 🔍 Comparison Chart

| Aspect | Method 1: On Trade Price | Method 2: In Retail Price |
|--------|-------------------------|--------------------------|
| **GST Position** | Added on top | Already included |
| **Retail Price** | Higher (trade + GST) | Same as trade (GST inside) |
| **GST Calculation** | Trade × GST% | Retail × GST% / (100 + GST%) |
| **Customer Pays** | Trade + GST | Retail (GST included) |
| **Best For** | Standard retail pricing | MRP pricing, fixed retail |
| **Tax Transparency** | GST shown separately | GST embedded in price |

---

## 🎯 When to Use Each Method

### ✅ Use Method 1 (On Trade Price) When:
- You want to show GST separately to customers
- Standard retail pricing model
- GST needs to be added on top of cost
- Clear tax transparency required
- Most common for grocery/retail stores

### ✅ Use Method 2 (In Retail Price) When:
- Retail price is fixed (MRP)
- GST is included in marked price
- Customer sees one final price
- Price tags already have GST included
- Common for electronics, packaged goods with MRP

---

## 💻 How to Use in the System

### Step 1: Select GST Method
At the top of the Goods Receipt screen, you'll see:

```
📊 GST Calculation Method:
○ Applicable on Trade Price (GST% × Trade Price)
○ Included in Retail Price (Retail × GST% / (100 + GST%))
```

Click the radio button to select your preferred method.

### Step 2: Enter Product Details
- Enter Received Qty and FOC Qty
- Right-click to edit Trade Price, Discount%, GST%

### Step 3: System Auto-calculates
Based on your selected method:
- **Method 1:** Retail = Discounted Trade + GST
- **Method 2:** Retail = Discounted Trade (GST included)

### Step 4: Verify Calculations
Check that the Retail Price matches your expectations:
- Method 1 will show higher retail (GST added)
- Method 2 will show same as discounted trade (GST inside)

### Step 5: Switch Methods Anytime
- Change the radio button selection
- All items recalculate automatically!
- Compare both methods to see the difference

---

## 🧪 Test Scenarios

### Test Case 1: Compare Both Methods
```
Input:
- Trade Price: Rs. 100
- Discount: 10%
- GST: 17%

Method 1 Result:
- Retail: Rs. 105.30 (90 + 15.30 GST)

Method 2 Result:
- Retail: Rs. 90.00 (GST included)
- GST Amount: Rs. 13.08
```

### Test Case 2: With FOC
```
Input:
- Trade Price: Rs. 100
- Discount: 10%
- GST: 17%
- Received: 10
- FOC: 2

Method 1:
- Cost: Rs. 75/unit
- Retail: Rs. 105.30/unit
- Profit: Rs. 30.30/unit (40.4%)

Method 2:
- Cost: Rs. 75/unit
- Retail: Rs. 90/unit
- Profit: Rs. 15/unit (20%)
```

---

## 📊 Visual Example

### Method 1: Applicable on Trade Price
```
┌─────────────────────────────────────┐
│ Trade Price: Rs. 100                │
│    ↓ (minus 10% discount)           │
│ Discounted: Rs. 90                  │
│    ↓ (add 17% GST)                  │
│ GST Amount: Rs. 15.30               │
│    ↓                                │
│ RETAIL PRICE: Rs. 105.30            │
└─────────────────────────────────────┘
```

### Method 2: Included in Retail Price
```
┌─────────────────────────────────────┐
│ Trade Price: Rs. 100                │
│    ↓ (minus 10% discount)           │
│ Discounted: Rs. 90                  │
│    ↓ (GST already in it)            │
│ RETAIL PRICE: Rs. 90.00             │
│                                     │
│ (GST inside: Rs. 13.08)            │
│ (Net: Rs. 76.92)                   │
└─────────────────────────────────────┘
```

---

## 🔢 Formulas Reference

### Method 1: Applicable on Trade Price
```python
discounted_trade = trade_price × (1 - discount% / 100)
gst_amount = discounted_trade × (gst_rate / 100)
retail_price = discounted_trade + gst_amount
# OR simplified:
retail_price = discounted_trade × (1 + gst_rate / 100)
```

### Method 2: Included in Retail Price
```python
discounted_trade = trade_price × (1 - discount% / 100)
retail_price = discounted_trade  # GST already in it
gst_amount = retail_price × gst_rate / (100 + gst_rate)
net_amount = retail_price - gst_amount
```

### Cost Price (Both Methods)
```python
total_paid_value = received_qty × discounted_trade
total_qty = received_qty + foc_qty
cost_price = total_paid_value / total_qty
```

---

## ⚠️ Important Notes

1. **Switching Methods:** You can switch between methods anytime, and all items will recalculate automatically.

2. **Discount First:** Discount is ALWAYS applied before GST calculation in both methods.

3. **FOC Impact:** FOC items reduce cost per unit but don't change GST calculations.

4. **Database Storage:** The selected method affects how retail price is calculated and stored.

5. **Customer Invoice:** Choose the method that matches how you want to show prices to customers.

---

## 🎯 Best Practices

### For Grocery Stores:
- **Use Method 1** (On Trade Price)
- Show GST separately on receipts
- Clear tax transparency

### For Electronics/MRP Items:
- **Use Method 2** (In Retail Price)
- Price tag shows final price
- GST embedded in MRP

### For Mixed Inventory:
- Set method per receipt
- Use Method 1 for most items
- Switch to Method 2 for MRP items

---

## 📈 Profit Impact Analysis

### Scenario: Trade Rs. 100, Discount 10%, GST 17%, Buy 10 Get 2 Free

| Aspect | Method 1 | Method 2 | Difference |
|--------|----------|----------|------------|
| Cost per unit | Rs. 75.00 | Rs. 75.00 | Same |
| Retail per unit | Rs. 105.30 | Rs. 90.00 | Rs. 15.30 |
| Profit per unit | Rs. 30.30 | Rs. 15.00 | Rs. 15.30 |
| Profit % | 40.4% | 20.0% | 20.4% |
| Customer pays | Higher | Lower | - |

**Key Insight:** Method 1 gives higher profit margins but higher customer prices. Method 2 has lower margins but competitive pricing.

---

## ✅ Summary

### Method 1: Applicable on Trade Price
- ✅ GST added on top
- ✅ Higher retail price
- ✅ Clear tax visibility
- ✅ Better profit margins
- ✅ Standard retail model

### Method 2: Included in Retail Price
- ✅ GST embedded inside
- ✅ Lower retail price
- ✅ Fixed MRP pricing
- ✅ Customer sees one price
- ✅ Competitive pricing

**Choose the method that best fits your business model and customer expectations!**

---

**Last Updated:** October 8, 2025  
**Status:** ✅ Fully Implemented and Tested  
**Version:** 3.0 (GST Method Selection Added)
