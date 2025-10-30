from peewee import *
import os
from werkzeug.security import generate_password_hash, check_password_hash

#MODELO ORM
sqlite_db = SqliteDatabase('data/users.db')

def crear_user_db():
    #Crea el directorio data/ si no existe y conecta a la base de datos
    os.makedirs('data', exist_ok=True)
    sqlite_db.connect(reuse_if_open=True)
    print("Base de datos conectada.")

class BaseModel(Model):
    class Meta:
       database = sqlite_db
       table_name = 'user'
    id = AutoField()
    username = CharField(max_length=80, null=False, unique=True)
    provincia_nombre = CharField(max_length=50)
    password_hash = CharField(max_length=128, null=False)

    @staticmethod
    def crear_user_tabla():
        #Crear tabla si no existe
        ##safe=True evita error si la tabla ya existe
        sqlite_db.create_tables([BaseModel], safe=True)
        print("Tabla creada o ya existente.")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)