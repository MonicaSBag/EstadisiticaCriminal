from peewee import *
import os
from werkzeug.security import generate_password_hash

# MODELO ORM
sqlite_db = SqliteDatabase('data/users.db')

def crear_user_db():
    """Crea el directorio data/ si no existe y conecta a la base de datos"""
    os.makedirs('data', exist_ok=True)
    sqlite_db.connect(reuse_if_open=True)
    print("Base de datos de usuarios conectada.")

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
    username = CharField(max_length=80, unique=True)
    provincia_nombre = CharField(max_length=50)
    password_hash = CharField(max_length=128)
    tipo_usuario = ForeignKeyField(TipoUsuario)
    debe_cambiar_password = BooleanField(default=False)

def crear_user_tabla():
    """Crear tablas y usuarios iniciales si no existen"""
    sqlite_db.create_tables([TipoUsuario, User], safe=True)
    
    # Crear tipos de usuario
    for tipo in ["superAdmin", "admin"]:
        TipoUsuario.get_or_create(tipo_usuario=tipo)
    
    # Crear usuarios de prueba
    usuarios_prueba = [
        {
            "username": "superAdmin",
            "provincia_nombre": "Todos",
            "password": "superAdmin123",
            "tipo_usuario": 1
        },
        {
            "username": "admin",
            "provincia_nombre": "Buenos Aires",
            "password": "admin123",
            "tipo_usuario": 2
        }
    ]
    
    for usuario_data in usuarios_prueba:
        try:
            User.get(User.username == usuario_data["username"])
        except User.DoesNotExist:
            User.create(
                username=usuario_data["username"],
                provincia_nombre=usuario_data["provincia_nombre"],
                password_hash=generate_password_hash(usuario_data["password"]),
                tipo_usuario=usuario_data["tipo_usuario"]
            )
            print(f"Usuario '{usuario_data['username']}' creado correctamente.")
    
    print("Tablas de usuarios creadas o ya existentes.")

def verificar_o_agregar_campo():
    """Agrega el campo 'debe_cambiar_password' a la tabla user si no existe"""
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