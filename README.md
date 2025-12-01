# 🌐 Turbo-Librarian: Arquitectura Distribuida

Este proyecto implementa una arquitectura **Cliente-Servidor desacoplada**.

* **Backend (Puerto 5001):** API RESTful que maneja KeyDB.
* **Frontend (Puerto 5000):** Cliente Flask que consume la API.

## ⚙️ Instalación

1. **Instalar dependencias:**

   ```bash
   pip install -r requirements.txt
```

2.  **Configurar Base de Datos (Docker):**

    ```bash
    docker run -d -p 6379:6379 --name keydb eqalpha/keydb
    ```

3.  **Crear archivos `.env`** en las carpetas correspondientes (o uno en la raíz si ejecutas desde ahí, pero se recomienda orden):

    **api/.env**

    ```ini
    KEYDB_HOST=localhost
    KEYDB_PORT=6379
    ```

    **client/.env**

    ```ini
    API_URL=[http://127.0.0.1:5001](http://127.0.0.1:5001)
    SECRET_KEY=secreto_cliente
    ```

## 🚀 Ejecución (Requiere 2 Terminales)

Debes mantener ambos procesos corriendo simultáneamente.

### Terminal 1: La API (Backend)

```bash
python api/app.py
# Verás: Running on [http://127.0.0.1:5001](http://127.0.0.1:5001)
```

### Terminal 2: El Cliente Web (Frontend)

```bash
python client/app.py
# Verás: Running on [http://127.0.0.1:5000](http://127.0.0.1:5000)
```

## 🧪 Uso

Abre tu navegador en **http://127.0.0.1:5000**.

La web funcionará igual que antes, pero internamente estará haciendo peticiones HTTP a `localhost:5001` para cada acción. Si apagas la Terminal 1, el frontend mostrará alertas de "Error de conexión".

## 🏭 Producción (Gunicorn + Nginx)

En un entorno real, no usarías `python app.py`. Usarías un gestor de procesos como Gunicorn.

**Ejemplo de comando Gunicorn para la API:**

```bash
gunicorn -w 4 -b 0.0.0.0:5001 api.app:app
```

**Ejemplo de comando Gunicorn para el Cliente:**

```bash
gunicorn -w 4 -b 0.0.0.0:5000 client.app:app
```
