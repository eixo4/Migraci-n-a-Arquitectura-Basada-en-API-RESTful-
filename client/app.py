import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'client_secret')

API_BASE_URL = os.getenv('API_URL', 'http://127.0.0.1:5001')


@app.route('/')
def index():
    """Listado de libros (Consumiendo API)"""
    query = request.args.get('q', '')
    try:
        # Petición GET a la API
        response = requests.get(f"{API_BASE_URL}/books", params={'q': query})

        if response.status_code == 200:
            libros = response.json()
        else:
            libros = []
            flash('Error al obtener libros de la API', 'danger')

    except requests.exceptions.RequestException:
        libros = []
        flash('❌ Error de conexión: La API no responde.', 'danger')

    return render_template('index.html', libros=libros, query=query)


@app.route('/add', methods=['GET', 'POST'])
def add_libro():
    """Agregar libro (Enviando POST a API)"""
    if request.method == 'POST':
        datos_libro = {
            "titulo": request.form['titulo'],
            "autor": request.form['autor'],
            "genero": request.form['genero'],
            "estado": request.form['estado']
        }

        try:
            response = requests.post(f"{API_BASE_URL}/books", json=datos_libro)

            if response.status_code == 201:
                flash('¡Libro agregado exitosamente!', 'success')
                return redirect(url_for('index'))
            else:
                flash(f'Error de la API: {response.text}', 'warning')

        except requests.exceptions.RequestException:
            flash('No se pudo conectar con la API para guardar.', 'danger')

    return render_template('add.html')


@app.route('/edit/<book_id>', methods=['GET', 'POST'])
def edit_libro(book_id):
    """Editar libro (GET para datos, PUT para actualizar)"""

    if request.method == 'POST':
        datos_actualizados = {
            "titulo": request.form['titulo'],
            "autor": request.form['autor'],
            "genero": request.form['genero'],
            "estado": request.form['estado']
        }
        try:
            response = requests.put(f"{API_BASE_URL}/books/{book_id}", json=datos_actualizados)
            if response.status_code == 200:
                flash('Libro actualizado.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Error al actualizar.', 'danger')
        except requests.exceptions.RequestException:
            flash('API caída.', 'danger')

    try:
        response = requests.get(f"{API_BASE_URL}/books/{book_id}")
        if response.status_code == 200:
            libro = response.json()
            return render_template('edit.html', libro=libro)
        else:
            flash('Libro no encontrado en la API.', 'warning')
            return redirect(url_for('index'))
    except requests.exceptions.RequestException:
        flash('Error conectando a la API.', 'danger')
        return redirect(url_for('index'))


@app.route('/delete/<book_id>', methods=['GET', 'POST'])
def delete_libro(book_id):
    """Eliminar libro (GET confirma, POST elimina en API)"""

    # Confirmación visual (GET)
    if request.method == 'GET':
        try:
            response = requests.get(f"{API_BASE_URL}/books/{book_id}")
            if response.status_code == 200:
                libro = response.json()
                return render_template('delete.html', libro=libro)
            return redirect(url_for('index'))
        except:
            return redirect(url_for('index'))

    # Eliminación real (POST)
    try:
        response = requests.delete(f"{API_BASE_URL}/books/{book_id}")
        if response.status_code == 200:
            flash('Libro eliminado.', 'info')
        else:
            flash('No se pudo eliminar.', 'warning')
    except requests.exceptions.RequestException:
        flash('API no disponible.', 'danger')

    return redirect(url_for('index'))


if __name__ == '__main__':
    # El cliente corre en el puerto 5000
    app.run(port=5000, debug=True)