import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

# Crear instancia de Flask
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de la base de datos para Pokémon
class Pokemon(db.Model):
    __tablename__ = 'pokemones'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    nivel = db.Column(db.Integer, nullable=False)
    fecha_captura = db.Column(db.String(50), nullable=False)  # Usamos String para simplificar
    evolucion = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'tipo': self.tipo,
            'nivel': self.nivel,
            'fecha_captura': self.fecha_captura,
            'evolucion': self.evolucion,
            'descripcion': self.descripcion
        }

# Crear las tablas
@app.before_first_request
def create_tables():
    db.create_all()

# Ruta principal - Lista todos los Pokémon
@app.route('/')
def index():
    pokemones = Pokemon.query.order_by(Pokemon.id).all()
    return render_template('pokedex.html', pokemones=pokemones)

# Ruta para agregar nuevo Pokémon
@app.route('/agregar', methods=['GET', 'POST'])
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
            # Crear nuevo Pokémon
            nuevo_pokemon = Pokemon(
                nombre=nombre,
                tipo=tipo,
                nivel=nivel,
                fecha_captura=fecha_captura,
                evolucion=evolucion,
                descripcion=descripcion
            )
            
            db.session.add(nuevo_pokemon)
            db.session.commit()
            flash('¡Pokémon agregado exitosamente a tu Pokédex!', 'success')
            return redirect(url_for('index'))
    
    return render_template('agregar.html')

# Ruta para editar Pokémon
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    pokemon = Pokemon.query.get_or_404(id)
    
    if request.method == 'POST':
        pokemon.nombre = request.form['nombre']
        pokemon.tipo = request.form['tipo']
        pokemon.nivel = request.form['nivel']
        pokemon.fecha_captura = request.form['fecha_captura']
        pokemon.evolucion = request.form['evolucion']
        pokemon.descripcion = request.form['descripcion']
        
        if not pokemon.nombre or not pokemon.tipo or not pokemon.nivel or not pokemon.fecha_captura:
            flash('Por favor completa todos los campos obligatorios', 'danger')
        else:
            db.session.commit()
            flash('¡Pokémon actualizado exitosamente!', 'success')
            return redirect(url_for('index'))
    
    return render_template('editar.html', pokemon=pokemon)

# Ruta para eliminar Pokémon
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    pokemon = Pokemon.query.get_or_404(id)
    db.session.delete(pokemon)
    db.session.commit()
    flash('¡Pokémon liberado exitosamente!', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)