# Se importa el componente Flask
from flask import Flask
from flask import render_template, request, redirect, url_for,flash
from flask_mysqldb import MySQL
from datetime import datetime
import os
from flask import send_from_directory

# Se implementa el uso de Flask y se crea la aplicación
app =  Flask(__name__)

app.secret_key = 'mysecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'sistema'

mysql = MySQL(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)


# Creamos nuestra aplicación la cual recibe solicitudes mediante route
@app.route('/')
def index():
    sql= "SELECT * FROM empleados;"
    cursor = mysql.connection.cursor()
    cursor.execute(sql)
    data = cursor.fetchall()
    
    #print(data)
    return render_template('empleados/index.html', empleados = data)

@app.route('/destroy/<id>')
def destroy(id):
    
    cursor = mysql.connection.cursor()

    cursor.execute('SELECT foto FROM empleados WHERE id=%s;',(id))
    fila=cursor.fetchall()
    os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

    cursor.execute("DELETE FROM empleados WHERE id=%s;",(id))
    mysql.connection.commit()

    return redirect(url_for('index'))

@app.route('/edit/<id>')
def edit(id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM empleados WHERE id=%s;",(id))
    data = cursor.fetchall()
    #print(data)
    return render_template('empleados/edit.html',empleados = data)

@app.route('/update', methods=['POST'])
def update():
    _id = request.form['txtId']
    _nombre =  request.form['txtNombre']
    _correo =  request.form['txtCorreo']
    _foto =  request.files['txtFoto']

    sql= "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s;"
    datos = (_nombre,_correo,_id)
    cursor = mysql.connection.cursor()

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
       nuevoNombreFoto = tiempo + "_" + _foto.filename
       _foto.save("uploads/"+nuevoNombreFoto)

       cursor.execute('SELECT foto FROM empleados WHERE id=%s',(_id))
       fila=cursor.fetchall()

       os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
       cursor.execute('UPDATE empleados SET foto=%s WHERE id=%s',(nuevoNombreFoto,_id))
       mysql.connection.commit()

    cursor.execute(sql,datos)
    mysql.connection.commit()

    return redirect(url_for('index'))

@app.route('/create')
def create():

    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
  if request.method == 'POST':
    _nombre =  request.form['txtNombre']
    _correo =  request.form['txtCorreo']
    _foto =  request.files['txtFoto']

    if _nombre=='' or _correo == '' or _foto == '':
       flash('Debe llenar todos los campos')
       return redirect(url_for('create'))

    now = datetime.now()
    tiempo = now.strftime("%Y%H%M%S")

    if _foto.filename != '':
       nuevoNombreFoto = tiempo + "_" + _foto.filename
       _foto.save("uploads/"+nuevoNombreFoto)

    sql= "INSERT INTO empleados(nombre, correo, foto) VALUES(%s,%s,%s);"
    datos = (_nombre,_correo,nuevoNombreFoto)
    cursor = mysql.connection.cursor()
    cursor.execute(sql,datos)
    mysql.connection.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=3000,debug=True)
