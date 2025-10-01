import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
import urllib.parse as up

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

def get_db_connection():
    # Para Render PostgreSQL
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        # Parsear la URL para psycopg2
        up.uses_netloc.append("postgres")
        url = up.urlparse(database_url)
        
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port,
            sslmode='require'
        )
    else:
        # Conexión local (fallback)
        conn = psycopg2.connect(
            host='localhost',
            database='pokedex_db',
            user='postgres',
            password='tu_password_local'
        )
    
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS pokemones (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                tipo VARCHAR(50) NOT NULL,
                nivel INTEGER NOT NULL,
                fecha_captura DATE NOT NULL,
                evolucion VARCHAR(100),
                descripcion TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Tabla creada/existe correctamente")
    except Exception as e:
        print(f"❌ Error al crear tabla: {e}")

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM pokemones ORDER BY id;')
    pokemones = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('pokedex.html', pokemones=pokemones)

@app.route('/agregar', methods=('GET', 'POST'))
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        nivel = request.form['nivel']
        fecha_captura = request.form['fecha_captura']
        evolucion = request.form['evolucion']
        descripcion = request.form['descripcion']
        
        if not nombre or not tipo or not nivel or not fecha_captura:
            flash('Por favor completa todos los campos obligatorios', 'danger')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'INSERT INTO pokemones (nombre, tipo, nivel, fecha_captura, evolucion, descripcion)'
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (nombre, tipo, nivel, fecha_captura, evolucion, descripcion)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('¡Pokémon agregado exitosamente a tu Pokédex!', 'success')
            return redirect(url_for('index'))
    
    return render_template('agregar.html')

@app.route('/editar/<int:id>', methods=('GET', 'POST'))
def editar(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        tipo = request.form['tipo']
        nivel = request.form['nivel']
        fecha_captura = request.form['fecha_captura']
        evolucion = request.form['evolucion']
        descripcion = request.form['descripcion']
        
        if not nombre or not tipo or not nivel or not fecha_captura:
            flash('Por favor completa todos los campos obligatorios', 'danger')
        else:
            cur.execute(
                'UPDATE pokemones SET nombre = %s, tipo = %s, nivel = %s, fecha_captura = %s, evolucion = %s, descripcion = %s'
                ' WHERE id = %s',
                (nombre, tipo, nivel, fecha_captura, evolucion, descripcion, id)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('¡Pokémon actualizado exitosamente!', 'success')
            return redirect(url_for('index'))
    
    cur.execute('SELECT * FROM pokemones WHERE id = %s', (id,))
    pokemon = cur.fetchone()
    cur.close()
    conn.close()
    
    if pokemon is None:
        flash('Pokémon no encontrado', 'danger')
        return redirect(url_for('index'))
    
    return render_template('editar.html', pokemon=pokemon)

@app.route('/eliminar/<int:id>', methods=('POST',))
def eliminar(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM pokemones WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash('¡Pokémon liberado exitosamente!', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)