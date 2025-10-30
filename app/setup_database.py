import pandas as pd
from peewee import *
import os
# MODELO ORM
sqlite_db = SqliteDatabase('data/estadistica_criminal.db')

# Se crea la base de datos o lee si ya existe
def crear_db():
    """Crea el directorio data/ si no existe y conecta a la base de datos"""
    os.makedirs('data', exist_ok=True)
    sqlite_db.connect(reuse_if_open=True)
    print("Base de datos conectada.")

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
    
    @staticmethod
    def crear_tabla():
        #Crear tabla si no existe
        ##safe=True evita error si la tabla ya existe
        sqlite_db.create_tables([BaseModel], safe=True)
        print("Tabla creada o ya existente.")
    
    @staticmethod
    def cargar_archivo():
        #Se lee el archivo xlsx y se cargan los datos (solo si la tabla está vacía)
        try:
            # Verificar si ya hay datos para evitar duplicados
            cantidad_existente = BaseModel.select().count()
            
            if cantidad_existente > 0:
                print(f"La tabla ya contiene {cantidad_existente} registros. No se cargarán datos.")
                return
            
            # Verificar que el archivo existe
            archivo = "snic-provincias.xlsx"
            if not os.path.exists(archivo):
                print(f"Advertencia: No se encontró el archivo '{archivo}'")
                return
            
            # Leer el archivo xlsx
            df = pd.read_excel(archivo)
            
            # Cargar datos en la base de datos
            with sqlite_db.atomic():
                for _, row in df.iterrows():
                    BaseModel.create(**row.to_dict())
            
            print(f"{len(df)} registros cargados desde '{archivo}'.")
            
        except Exception as e:
            print(f"Error al cargar el archivo: {e}")
            raise