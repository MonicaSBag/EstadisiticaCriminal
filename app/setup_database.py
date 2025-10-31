import pandas as pd
from peewee import *
import os
# MODELO ORM
sqlite_db = SqliteDatabase('data/estadistica_criminal.db')

# Se crea la base de datos o lee si ya existe
def crear_db():
    #Crea el directorio data/ si no existe y conecta a la base de datos
    os.makedirs('data', exist_ok=True)
    sqlite_db.connect(reuse_if_open=True)
    print("Base de datos conectada.")

# ESTRUCTURA DE LA BASE DE DATOS
class BaseModel(Model):
    class Meta:
        database = sqlite_db

class EstadisticasDelitos(BaseModel): 
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
    tasa_hechos = FloatField(null=True)
    tasa_victimas = FloatField(null=True)
    tasa_victimas_masc = FloatField(null=True)
    tasa_victimas_fem = FloatField(null=True)

class Provincia(BaseModel):
    class Meta:
        table_name = "provincias"
    id = AutoField()
    provincia_id = IntegerField()
    provincia_nombre = CharField(max_length=50)
    latitud = FloatField(null=False)
    longitud = FloatField(null=False)


@staticmethod
def crear_tabla():
    #Crear tabla si no existe
    ##safe=True evita error si la tabla ya existe
    sqlite_db.create_tables([EstadisticasDelitos], safe=True)
    sqlite_db.create_tables([Provincia], safe=True)

    print("Tablas creadas o ya existentes.")

@staticmethod
def cargar_archivo():
    #Se lee el archivo xlsx y se cargan los datos (solo si la tabla está vacía)
    try:
        # Verificar si ya hay datos para evitar duplicados
        cantidad_existente = EstadisticasDelitos.select().count()
        
        if cantidad_existente > 0:
            print(f"La tabla ya contiene {cantidad_existente} registros. No se cargarán datos.")
            return
    
        # Verificar que el archivo existe
        archivo = "snic-provincias.xlsx"
        if not os.path.exists(archivo):
            archivo = "../snic-provincias.xlsx"
        if not os.path.exists(archivo):
            print(f"No se encontró el archivo '{archivo}'")
            return
        
        # Leer el archivo xlsx
        df = pd.read_excel(archivo)
        
        # Cargar datos en la base de datos
        with sqlite_db.atomic():
            for _, row in df.iterrows():
                EstadisticasDelitos.create(**row.to_dict())
    
        print(f"{len(df)} registros cargados desde '{archivo}'.")
        
    except Exception as e:
        print(f"Error al cargar el archivo de delitos: {e}")
        raise
        # Verificar si ya hay datos para evitar duplicados
    cantidad_existente = Provincia.select().count()
    
    if cantidad_existente > 0:
        print(f"La tabla ya contiene {cantidad_existente} registros. No se cargarán datos.")
        return
    
    # Verificar que el archivo existe
    archivo = "provincias_ubicacion.xlsx"
    if not os.path.exists(archivo):
        archivo = "../provincias_ubicacion.xlsx"
    if not os.path.exists(archivo):
        print(f"No se encontró el archivo '{archivo}'")
        return
    
    # Leer el archivo xlsx
    df = pd.read_excel(archivo)
    
    # Validar que las columnas necesarias existen
    columnas_requeridas = {'provincia_id', 'provincia_nombre', 'latitud', 'longitud'}
    if not columnas_requeridas.issubset(df.columns):
        print(f"Faltan columnas requeridas: {columnas_requeridas - set(df.columns)}")
        return

    # Eliminar filas con latitud o longitud faltante
    df = df.dropna(subset=['latitud', 'longitud'])

    # Cargar en la base de datos
    with sqlite_db.atomic():
        for _, row in df.iterrows():
            Provincia.create(
                provincia_id=int(row['provincia_id']),
                provincia_nombre=str(row['provincia_nombre']),
                latitud=float(row['latitud']),
                longitud=float(row['longitud'])
            )
    print(f"{len(df)} provincias cargadas correctamente.")
