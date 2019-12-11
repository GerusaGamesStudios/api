from flask import Flask,request,jsonify
from flask_restful import Api,Resource,reqparse
import jwt
import datetime
from functools import wraps
import mysql.connector

app = Flask(__name__)
api = Api(app)
mydb = mysql.connector.connect(
  host="localhost",
  port=8080,
  user="root",
  passwd="",
  database="python"
)
cursor = mydb.cursor(dictionary=True)




private = "snoopy"
items = [{
    "id":1,"name":"silla","price":20
}]
users = [
    {"username":"nando","password":"hola"}
]
def tokenRequired(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        data = request.get_json()
        if data:
            token = data["token"]
            try:
                jwt.decode(token,private)
            except:
                return {"message":"Invalid key"}
            return f(*args,**kwargs)
        else:
            return {"message":"No arguments supplied"},400
    return decorated

def userAuth(u,p):
    for a in users:
        if a['username'] == u:
            if a['password'] == p:
                return True
    return False

class Register(Resource):
    def post(self):
        data = request.get_json()
        username = data['user']
        psw = data['psw']

        cursor.execute('SELECT * FROM users WHERE username = %s AND pass = %s',(username,psw))
        result = cursor.fetchall()
        if result:
            return{"msg":"Usuario ya registrado"}
        else:
            cursor.execute('INSERT INTO users VALUES(%s,%s)',(username,psw))
            mydb.commit()
            return{"Columnas Modificadas":cursor.rowcount}
        

class auth(Resource):
    def post(self):
        data = request.get_json()
        user = data["user"]
        psw = data["psw"]

        cursor.execute('SELECT * FROM users WHERE username = %s AND pass = %s',(user,psw))
        result = cursor.fetchall()
        if result:
            token = jwt.encode({"user":user,"date": str(datetime.datetime.utcnow()) },private)
            return {"token":token.decode("UTF-8")}
        else:
            return {"message":"user not found"}


class Item(Resource):
    @tokenRequired
    def get(self,name):
        cursor.execute('SELECT * FROM items WHERE nombre = %s',(name,))
        result = cursor.fetchall()
        if result:
            return {"item":result}
        else:
            return {"message":"no se encontró el elemento"},404

    def post(self,name):
        cursor.execute('SELECT * FROM items WHERE nombre = %s',(name,))
        result = cursor.fetchall()
        if result:
            return {"message":"El elemento ya existe"},400
        else:
            data = request.get_json()
            price = data['price']
            cursor.execute('INSERT INTO items VALUES(NULL,%s,%s)',(name,price))
            mydb.commit()
            return {"message":"ElementoCreado","ElementosAfectados":cursor.rowcount}

    @tokenRequired
    def put(self,name):
        data = request.get_json()
        cursor.execute('SELECT * FROM items WHERE nombre = %s',(name,))
        result = cursor.fetchall()
        if(result):
            cursor.execute('UPDATE items SET precio = %s WHERE nombre = %s',(data['precio'],name))
            mydb.commit()
            return{"ElementosModificados":cursor.rowcount,"tipo":"Modificado"},200
        else:
            cursor.execute('INSERT INTO items VALUES(NULL, %s,%s)',(name,data['precio']))
            mydb.commit()
            return{"ElementosModificados":cursor.rowcount,"tipo":"Creado"},201
            

    @tokenRequired
    def delete(self,name):
        cursor.execute("DELETE FROM items WHERE nombre = %s ",(name,))
        mydb.commit()
        return {"ElementosAfectados":cursor.rowcount}

class ItemList(Resource):
    def get(self):
        cursor.execute('SELECT * FROM items')
        result = cursor.fetchall()
        return {"items":result},200



api.add_resource(Item,'/item/<string:name>')
api.add_resource(ItemList,'/items')
api.add_resource(auth,'/login')
api.add_resource(Register,'/register')
app.run(port=5000,debug=True)