import os
import json
import uuid
import redis
from flask import Flask, jsonify, request
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

app = Flask(__name__)

REDIS_HOST = os.getenv('KEYDB_HOST', 'localhost')
REDIS_PORT = int(os.getenv('KEYDB_PORT', 6379))
REDIS_PASS = os.getenv('KEYDB_PASSWORD', None)

try:
    db = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASS,
        decode_responses=True
    )
    db.ping()
except redis.ConnectionError:
    print("❌ API Error: No se pudo conectar a KeyDB.")

@app.route('/books', methods=['GET'])
def get_books():
    """Obtener todos los libros"""
    query = request.args.get('q', '').lower()
    libros = []

    # Scan es más eficiente que keys()
    for key in db.scan_iter("libro:*"):
        data = db.get(key)
        if data:
            libro = json.loads(data)
            # Filtro básico en el backend
            if query:
                if (query in libro['titulo'].lower() or
                        query in libro['autor'].lower()):
                    libros.append(libro)
            else:
                libros.append(libro)

    return jsonify(libros), 200


@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """Obtener un libro específico"""
    key = f"libro:{book_id}"
    if not db.exists(key):
        return jsonify({"error": "Libro no encontrado"}), 404

    data = db.get(key)
    return jsonify(json.loads(data)), 200


@app.route('/books', methods=['POST'])
def create_book():
    """Crear nuevo libro"""
    if not request.is_json:
        return jsonify({"error": "El cuerpo debe ser JSON"}), 400

    data = request.get_json()

    # Validaciones básicas
    if 'titulo' not in data or 'autor' not in data:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    book_id = str(uuid.uuid4())
    libro = {
        "id": book_id,
        "titulo": data['titulo'],
        "autor": data['autor'],
        "genero": data.get('genero', ''),
        "estado": data.get('estado', 'No leído')
    }

    db.set(f"libro:{book_id}", json.dumps(libro))

    return jsonify(libro), 201


@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """Actualizar libro existente"""
    key = f"libro:{book_id}"
    if not db.exists(key):
        return jsonify({"error": "Libro no encontrado"}), 404

    if not request.is_json:
        return jsonify({"error": "El cuerpo debe ser JSON"}), 400

    data = request.get_json()

    # Recuperamos el actual para mantener el ID y sobreescribir campos
    actual_json = db.get(key)
    libro = json.loads(actual_json)

    # Actualizamos campos
    libro['titulo'] = data.get('titulo', libro['titulo'])
    libro['autor'] = data.get('autor', libro['autor'])
    libro['genero'] = data.get('genero', libro['genero'])
    libro['estado'] = data.get('estado', libro['estado'])

    db.set(key, json.dumps(libro))

    return jsonify(libro), 200


@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Eliminar libro"""
    key = f"libro:{book_id}"
    if not db.exists(key):
        return jsonify({"error": "Libro no encontrado"}), 404

    db.delete(key)
    return jsonify({"message": "Libro eliminado"}), 200


if __name__ == '__main__':
    # Ejecutamos la API en el puerto 5001 para no chocar con el cliente
    app.run(port=5001, debug=True)