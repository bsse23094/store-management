
# Entity classes representing database tables

class User:
    def __init__(self, id, username, password, role, full_name=None):
        self.id = id
        self.username = username
        self.password = password
        self.role = role
        self.full_name = full_name

class Product:
    def __init__(self, id, name, price, stock=0, barcode=None):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
        self.barcode = barcode

class Sale:
    def __init__(self, id, invoice_no, customer_name, total, discount=0, payment_method=None,
                 is_held=False, is_return=False, original_invoice=None, cashier_id=None, created_at=None):
        self.id = id
        self.invoice_no = invoice_no
        self.customer_name = customer_name
        self.total = total
        self.discount = discount
        self.payment_method = payment_method
        self.is_held = is_held
        self.is_return = is_return
        self.original_invoice = original_invoice
        self.cashier_id = cashier_id
        self.created_at = created_at

class SaleItem:
    def __init__(self, id, sale_id, product_id, quantity, unit_price, total_price):
        self.id = id
        self.sale_id = sale_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.total_price = total_price