# 📊 Sistema de Estadísticas Criminales SNIC

Sistema web para la gestión, visualización y análisis de estadísticas delictivas basado en datos del Sistema Nacional de Información Criminal (SNIC) de Argentina.

## 🚀 Características

### 📈 Visualización de Datos
- **Dashboards interactivos** con gráficos dinámicos (Google Charts)
- **Filtros avanzados** por provincia, año y tipo de delito
- **Tablas paginadas** con búsqueda en tiempo real
- **Exportación a CSV** de registros filtrados

### 👥 Gestión de Usuarios
- **Dos niveles de acceso:**
  - **SuperAdmin**: Acceso total a todas las provincias y gestión de usuarios
  - **Admin**: Acceso limitado a su provincia asignada
- **Sistema de autenticación** con hash de contraseñas
- **Cambio obligatorio de contraseña** en primer inicio de sesión
- **Panel de administración** para ABM de usuarios

### 🗄️ Gestión de Datos
- **CRUD completo** de registros estadísticos
- **Autocompletado inteligente** de totales por género
- **Validaciones** de integridad de datos
- **Cálculo automático** de tasas delictivas

### 🌐 Acceso Público y Privado
- **Dashboard público**: Visualización de datos generales sin autenticación
- **Dashboard privado**: Gestión completa para usuarios autenticados

---

## 🛠️ Tecnologías

### Backend
- **Python 3.x**
- **Flask** - Framework web
- **Peewee ORM** - Mapeo objeto-relacional
- **SQLite** - Base de datos
- **Pandas** - Procesamiento de datos Excel
- **Werkzeug** - Seguridad (hashing de contraseñas)

### Frontend
- **HTML5 / CSS3**
- **Bootstrap 5.3** - Framework CSS
- **JavaScript ES6+**
- **Google Charts** - Visualización de datos
- **Jinja2** - Motor de plantillas

---

## 📦 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/estadisticas-snic.git
cd estadisticas-snic
```

2. **Crear entorno virtual:**
```bash
python -m venv venv

# Activar en Windows:
venv\Scripts\activate

# Activar en Linux/Mac:
source venv/bin/activate
```

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Preparar archivos de datos:**
   - Colocar `snic-provincias.xlsx` en la raíz del proyecto
   - Colocar `provincias_ubicacion.xlsx` en la raíz del proyecto

5. **Ejecutar la aplicación:**
```bash
cd main
python app.py
```

6. **Acceder a la aplicación:**
   - Abrir navegador en: `http://localhost:5000`

---

## 📂 Estructura del Proyecto

```
estadisticas-snic/
│
├── main/
│   ├── app.py                          # Aplicación principal Flask
│   ├── setup_database.py               # Configuración BD de estadísticas
│   ├── user_database.py                # Configuración BD de usuarios
│   │
│   ├── templates/
│   │   ├── index.html                  # Página de inicio
│   │   ├── login.html                  # Login de usuarios
│   │   ├── usuarios.html               # Gestión de usuarios
│   │   ├── PortalAdmin.html            # Panel de administración
│   │   ├── cambiar_password_primera_vez.html
│   │   └── components/
│   │       ├── iFrame_filtros_prueba1.html  # Dashboard público
│   │       └── iFrame_filtros_prueba2.html  # Dashboard privado
│   │
│   └── data/
│       ├── estadistica_criminal.db     # BD de estadísticas (auto-generada)
│       └── users.db                    # BD de usuarios (auto-generada)
│
├── snic-provincias.xlsx                # Datos estadísticos
├── provincias_ubicacion.xlsx           # Datos de ubicación
├── requirements.txt                    # Dependencias Python
├── .gitignore
└── README.md
```

---

## 👤 Usuarios Predeterminados

Al iniciar por primera vez, se crean automáticamente:

| Usuario      | Contraseña     | Tipo        | Provincia    |
|--------------|----------------|-------------|--------------|
| `superAdmin` | `superAdmin123`| SuperAdmin  | Todas        |
| `admin`      | `admin123`     | Admin       | Buenos Aires |

> ⚠️ **Importante:** Se solicitará cambiar la contraseña en el primer inicio de sesión.

---

## 🔐 Configuración de Seguridad

### Cambiar la Clave Secreta

En `app.py`, modificar:
```python
app.config['SECRET_KEY'] = 'tu_clave_secreta_muy_larga_y_segura'
```

### Recomendaciones:
- Usar una clave de al menos 32 caracteres aleatorios
- Nunca compartir la clave en repositorios públicos
- Considerar variables de entorno para producción

---

## 📊 Uso del Sistema

### Dashboard Público
1. Acceder a `/dashboard-public`
2. Seleccionar filtros (provincia, año, tipo de delito)
3. Hacer clic en "🔍 Buscar Datos"
4. Visualizar tablas y gráficos
5. Exportar datos con "📥 Exportar CSV"

### Dashboard Privado (Requiere Login)
1. Iniciar sesión en `/login`
2. Acceder a `/dashboard-private`
3. **Consultar datos** con filtros avanzados
4. **Agregar registros** nuevos:
   - Clic en "➕ Agregar Registro"
   - Completar formulario (autocompletado de totales)
   - Confirmar y guardar
5. **Eliminar registros**:
   - Clic en "🗑️ Eliminar Registro"
   - Buscar registro específico
   - Seleccionar y confirmar eliminación

### Gestión de Usuarios (Solo SuperAdmin)
1. Acceder a `/portal_admin`
2. Ir a "Gestión de Usuarios"
3. **Agregar usuario**: Asignar provincia y tipo
4. **Editar usuario**: Modificar datos
5. **Cambiar contraseña**: Restablecer acceso
6. **Eliminar usuario**: Remover del sistema

---

## 🗃️ Base de Datos

### Tablas Principales

#### `estadisticasdelitos`
- `id`: ID único
- `provincia_id`, `provincia_nombre`: Identificación de provincia
- `anio`: Año del registro
- `codigo_delito_snic_id`, `codigo_delito_snic_nombre`: Tipo de delito
- `cantidad_hechos`: Total de hechos
- `cantidad_victimas`: Total de víctimas
- `cantidad_victimas_masc/fem/sd`: Víctimas por género
- `tasa_hechos`, `tasa_victimas`, etc.: Tasas calculadas

#### `provincias`
- `provincia_id`, `provincia_nombre`
- `latitud`, `longitud`: Coordenadas geográficas

#### `user`
- `username`: Nombre de usuario
- `password_hash`: Contraseña hasheada
- `provincia_nombre`: Provincia asignada
- `tipo_usuario`: Tipo de usuario (1=SuperAdmin, 2=Admin)
- `debe_cambiar_password`: Flag de cambio obligatorio

---

## 🔄 API Endpoints

### Públicos
- `GET /` - Página de inicio
- `GET /dashboard-public` - Dashboard público
- `POST /filtrar` - Filtrar datos
- `POST /estadisticas` - Obtener estadísticas agregadas
- `GET /filtros2` - Obtener opciones de filtros

### Autenticados
- `POST /login` - Inicio de sesión
- `GET /logout` - Cerrar sesión
- `GET /dashboard-private` - Dashboard privado
- `GET /filtros` - Filtros según usuario

### ABM de Datos (Requiere autenticación)
- `POST /abm/consultar` - Consultar registros
- `POST /abm/agregar` - Agregar registro
- `DELETE /abm/eliminar/<id>` - Eliminar registro

### Administración (Solo SuperAdmin)
- `GET /portal_admin` - Portal de administración
- `GET /usuarios` - Lista de usuarios
- `POST /usuarios/agregar` - Crear usuario
- `POST /usuarios/editar/<id>` - Editar usuario
- `POST /usuarios/eliminar/<id>` - Eliminar usuario
- `POST /usuarios/set_password/<id>` - Cambiar contraseña

---

## 🐛 Solución de Problemas

### La aplicación no inicia
```bash
# Verificar que el entorno virtual esté activado
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error: "No se encontró el archivo Excel"
- Verificar que `snic-provincias.xlsx` y `provincias_ubicacion.xlsx` estén en la raíz
- Revisar que los nombres de archivo coincidan exactamente

### No puedo iniciar sesión
- Verificar credenciales predeterminadas
- Revisar logs en consola para errores de BD
- Eliminar `data/users.db` y reiniciar (recrea usuarios por defecto)

### Los datos no se muestran
- Verificar que `data/estadistica_criminal.db` exista
- Revisar logs de carga de datos al iniciar
- Comprobar que el Excel tenga el formato correcto

---

## 🚀 Despliegue en Producción

### Consideraciones Importantes:

1. **Cambiar `debug=False`** en `app.py`:
```python
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0')
```

2. **Usar servidor WSGI** (Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 main.app:app
```

3. **Variables de entorno** para configuración sensible

4. **Base de datos más robusta** (PostgreSQL, MySQL) para producción

5. **HTTPS** obligatorio para proteger credenciales


## 🙏 Agradecimientos

- Datos proporcionados por el Sistema Nacional de Información Criminal (SNIC)
- Bootstrap por el framework CSS
- Google Charts por las herramientas de visualización
- Comunidad de Flask y Python

---

## 📅 Historial de Versiones

### v1.0.0 (2025-01-XX)
- ✅ Lanzamiento inicial
- ✅ Dashboard público y privado
- ✅ Sistema de autenticación
- ✅ CRUD completo de registros
- ✅ Gestión de usuarios
- ✅ Exportación a CSV
- ✅ Visualizaciones con Google Charts