import pandas as pd
from peewee import *
#MODELO ORM
#se crea la base de datos o lee si ya existe
def crear_db():
    sqlite_db = SqliteDatabase('../database/estadistica_criminal.db')
    sqlite_db.connect()
#b47fe25d952c1df94b8270651d426d976deafa494098fb3f8e96ee54461d5c30
# ESTRUCTURA DE LA BASE DE DATOS
class BaseModel(Model):
    class Meta:
        database = sqlite_db
        table_name = 'estadisticas_delitos'
    id = AutoField()
    provincia_id = IntegerField()
    provincia_nombre = CharField(max_length=50)
    anio = IntegerField()
    codigo_delito_snic_id = IntegerField()
    codigo_delito_snic_nombre = CharField(max_length=100)
    cantidad_hechos = IntegerField()
    cantidad_victimas = IntegerField()
    cantidad_victimas_masc = IntegerField()
    cantidad_victimas_fem = IntegerField()
    cantidad_victimas_sd = IntegerField()
    tasa_hechos = FloatField()
    tasa_victimas = FloatField()
    tasa_victimas_masc = FloatField()
    tasa_victimas_fem = FloatField()
    def crear_tabla():
        # Crear tabla si no existe
        #sqlite_db.connect()
        sqlite_db.create_tables([BaseModel])
        print("Tabla creada o ya existente.")
    def cargar_archivo():
        # Se lee el archivo xlsx y se carga los datos
        df = pd.read_excel("../snic-provincias.xlsx")
        with sqlite_db.atomic():
            for _, row in df.iterrows():
                BaseModel.create(**row.to_dict())
         print(f"{len(df)} registros cargados desde 'snic-provincias.xlsx'.")