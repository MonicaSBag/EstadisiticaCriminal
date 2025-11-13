import pandas as pd
from peewee import *
import os

# MODELO ORM
sqlite_db = SqliteDatabase('data/estadistica_criminal.db')

def crear_db():
    """Crea el directorio data/ si no existe y conecta a la base de datos"""
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
    latitud = FloatField()
    longitud = FloatField()

def crear_tabla():
    """Crear tablas si no existen"""
    sqlite_db.create_tables([EstadisticasDelitos, Provincia], safe=True)
    print("Tablas creadas o ya existentes.")

def _buscar_archivo(nombre_archivo):
    """Busca el archivo en el directorio actual o en el directorio padre"""
    if os.path.exists(nombre_archivo):
        return nombre_archivo
    archivo_padre = f"../{nombre_archivo}"
    if os.path.exists(archivo_padre):
        return archivo_padre
    return None

def _cargar_delitos():
    """Carga datos de delitos desde archivo Excel"""
    cantidad_existente = EstadisticasDelitos.select().count()
    
    if cantidad_existente > 0:
        print(f"La tabla de delitos ya contiene {cantidad_existente} registros. No se cargarán datos.")
        return
    
    archivo = _buscar_archivo("snic-provincias.xlsx")
    if not archivo:
        print("No se encontró el archivo 'snic-provincias.xlsx'")
        return
    
    df = pd.read_excel(archivo)
    
    with sqlite_db.atomic():
        for _, row in df.iterrows():
            EstadisticasDelitos.create(**row.to_dict())
    
    print(f"{len(df)} registros de delitos cargados desde '{archivo}'.")

def _cargar_provincias():
    """Carga datos de provincias desde archivo Excel"""
    cantidad_existente = Provincia.select().count()
    
    if cantidad_existente > 0:
        print(f"La tabla de provincias ya contiene {cantidad_existente} registros. No se cargarán datos.")
        return
    
    archivo = _buscar_archivo("provincias_ubicacion.xlsx")
    if not archivo:
        print("No se encontró el archivo 'provincias_ubicacion.xlsx'")
        return
    
    df = pd.read_excel(archivo)
    
    columnas_requeridas = {'provincia_id', 'provincia_nombre', 'latitud', 'longitud'}
    if not columnas_requeridas.issubset(df.columns):
        print(f"Faltan columnas requeridas: {columnas_requeridas - set(df.columns)}")
        return

    df = df.dropna(subset=['latitud', 'longitud'])

    with sqlite_db.atomic():
        for _, row in df.iterrows():
            Provincia.create(
                provincia_id=int(row['provincia_id']),
                provincia_nombre=str(row['provincia_nombre']),
                latitud=float(row['latitud']),
                longitud=float(row['longitud'])
            )
    
    print(f"{len(df)} provincias cargadas correctamente.")

def cargar_archivo():
    """Carga todos los archivos de datos necesarios"""
    try:
        _cargar_delitos()
        _cargar_provincias()
    except Exception as e:
        print(f"Error al cargar archivos: {e}")
        raise