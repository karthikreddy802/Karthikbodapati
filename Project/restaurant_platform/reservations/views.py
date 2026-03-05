from django.shortcuts import render

# Create your views here.
def generate_bill(order):
    subtotal = sum([
        item.item.price * item.quantity
        for item in order.orderitem_set.all()
    ])
    tax = subtotal * 0.05
    total = subtotal + tax

    Bill.objects.create(
        order=order,
        subtotal=subtotal,
        tax=tax,
        total=total
    )
