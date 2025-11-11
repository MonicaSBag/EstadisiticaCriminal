from peewee import *
import os
from werkzeug.security import generate_password_hash, check_password_hash

# MODELO ORM
sqlite_db = SqliteDatabase('data/users.db')

def crear_user_db():
    # Crea el directorio data/ si no existe y conecta a la base de datos
    os.makedirs('data', exist_ok=True)
    sqlite_db.connect(reuse_if_open=True)
    print("Base de datos conectada.")

class BaseModel(Model):
    class Meta:
        database = sqlite_db
       
class TipoUsuario(BaseModel):
    class Meta:
        table_name = "tipo_usuario"
    id = AutoField()
    tipo_usuario = CharField(unique=True)

class User(BaseModel):
    class Meta:
        table_name = 'user'
    id = AutoField()
    username = CharField(max_length=80, null=False, unique=True)
    provincia_nombre = CharField(max_length=50, null=False)
    password_hash = CharField(max_length=128, null=False)
    tipo_usuario = ForeignKeyField(TipoUsuario)
    debe_cambiar_password = BooleanField(default=False)  # 🔹 Campo nuevo

def crear_user_tabla():
    # Crear tabla si no existe
    sqlite_db.create_tables([TipoUsuario, User], safe=True)
    for tipo in ["superAdmin", "admin"]:
        TipoUsuario.get_or_create(tipo_usuario=tipo)
    try:
        User.create(
            username="superAdmin",
            provincia_nombre="Todos",
            password_hash=generate_password_hash("superAdmin123"),
            tipo_usuario=1,
        )
        User.create(
            username="admin",
            provincia_nombre="Buenos Aires",
            password_hash=generate_password_hash("admin123"),
            tipo_usuario=2,
        )
    except:
        print("Usuarios de prueba ya existentes o error al crearlos.")
    print("Tabla creada o ya existente.")

def check_password(password):
    return check_password_hash(generate_password_hash(password), password)

# 🔹 Agrega automáticamente el campo 'debe_cambiar_password' si no existe
def verificar_o_agregar_campo():
    """Agrega el campo 'debe_cambiar_password' a la tabla user si no existe."""
    sqlite_db.connect(reuse_if_open=True)
    cursor = sqlite_db.execute_sql("PRAGMA table_info(user);")
    columnas = [row[1] for row in cursor.fetchall()]

    if "debe_cambiar_password" not in columnas:
        print("🟡 Campo 'debe_cambiar_password' no encontrado. Creando...")
        sqlite_db.execute_sql("ALTER TABLE user ADD COLUMN debe_cambiar_password BOOLEAN DEFAULT 0;")
        print("✅ Campo 'debe_cambiar_password' agregado correctamente.")
    else:
        print("✅ El campo 'debe_cambiar_password' ya existe.")

    sqlite_db.close()
