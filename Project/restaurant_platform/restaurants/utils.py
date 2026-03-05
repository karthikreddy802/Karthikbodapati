import qrcode

def generate_table_qr(table):
    data = f"restaurant/{table.restaurant.id}/table/{table.id}"
    qr = qrcode.make(data)
    qr.save(f"media/qr/table_{table.id}.png")
