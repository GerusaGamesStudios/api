users = [
    {"id":1,"psw":"hola"}
]

def auth(ide,psw):
    for i in users:
        if i["id"] == ide:
            return i

def identity(ide):
    for i in users:
        if i['id'] == ide:
            return i

