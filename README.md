# Club Deportivo Encuentro

API REST para gestionar canchas, socios, disponibilidad y reservas del Club Deportivo Encuentro.

Proyecto Backend - FIUBA - Trabajo Practico 1

## Que resuelve

La API permite:

- consultar los deportes precargados;
- crear, consultar, actualizar y eliminar canchas;
- filtrar canchas por deporte, nombre, si son techadas y estado;
- consultar disponibilidad por fecha y horario;
- registrar y desactivar socios;
- crear reservas sin superposiciones;
- impedir reservas sobre una cancha o socio inactivo;
- calcular el importe en centavos y conservar la tarifa historica;
- cancelar y finalizar reservas respetando las reglas temporales;
- consultar listados con filtros, paginacion y enlaces HATEOAS;
- administrar bloqueos de mantenimiento y reservas recurrentes como extensiones opcionales.

## Tecnologias

- Python 3.12
- Flask 3.1
- MySQL 8.0
- Docker Compose
- OpenAPI 3.0

## Estructura del proyecto

```text
.
├── app.py                         # Punto de entrada de Flask
├── docker-compose.yml             # API + MySQL
├── requirements.txt               # Dependencias Python
├── .env.example                   # Configuracion de ejemplo
├── db/
│   └── init_db.sql                # Tablas e informacion inicial
├── docs/
│   └── swagger.yaml               # Contrato OpenAPI, no modificar
└── src/
    ├── routes/                    # HTTP, status codes y JSON
    ├── services/                  # Consultas y reglas del negocio
    ├── validators/                # Validaciones de cuerpos y fechas
    ├── constants.py               # Constantes del dominio
    ├── db.py                      # Conexion y operaciones MySQL
    └── utils.py                   # Errores, paginacion y serializacion
```

## Opcion recomendada: Docker en Linux

### Requisitos

Instalar solamente:

- Git
- Docker Engine
- Docker Compose v2, normalmente incluido como `docker compose`

En Ubuntu, Docker se puede instalar siguiendo la documentacion oficial de Docker. No hace falta instalar Python ni MySQL en el host si se usa Compose.

### Ejecutar desde una copia nueva

```bash
git clone URL_DE_TU_REPOSITORIO
cd NOMBRE_DEL_REPOSITORIO
cp .env.example .env
docker compose up --build
```

La API queda disponible en `http://localhost:5000`.

Probar que responde:

```bash
curl http://localhost:5000/deportes
```

La base de datos utiliza el volumen `mysql_data`, por lo que reiniciar los contenedores no borra la informacion.

El script `db/init_db.sql` se ejecuta automaticamente cuando MySQL crea el volumen por primera vez. Para borrar completamente la base y volver a cargar los datos iniciales:

```bash
docker compose down -v
docker compose up --build
```

El comando `down -v` es destructivo: elimina el volumen y todos los datos guardados.

Detener los servicios sin borrar datos:

```bash
docker compose down
```

## Ejecucion local en Linux

Esta opcion requiere tener un servidor MySQL 8 accesible y una base llamada `club_deportivo`.

```bash
git clone URL_DE_TU_REPOSITORIO
cd NOMBRE_DEL_REPOSITORIO
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

Si MySQL no esta en Docker, ajustar en `.env` al menos `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` y `DB_NAME`. Luego ejecutar `db/init_db.sql` una sola vez desde MySQL.

Para salir del entorno virtual:

```bash
deactivate
```

## Configuracion

La aplicacion lee estas variables:

| Variable | Valor de ejemplo | Uso |
| --- | --- | --- |
| `PORT` | `5000` | Puerto HTTP de Flask |
| `DB_HOST` | `db` | Host de MySQL en Docker |
| `DB_PORT` | `3306` | Puerto de MySQL |
| `DB_NAME` | `club_deportivo` | Base utilizada por el script inicial |
| `DB_USER` | `club_user` | Usuario de la API |
| `DB_PASSWORD` | `club_password` | Password de la API |
| `MYSQL_ROOT_PASSWORD` | `root_password` | Password root de MySQL |
No subir `.env` a GitHub. El archivo versionado es `.env.example`, que no contiene credenciales reales.

## Ejemplos de uso

Listar deportes:

```bash
curl http://localhost:5000/deportes
```

Listar canchas con filtros y paginacion:

```bash
curl "http://localhost:5000/canchas?id_deporte=1&activa=true&_limit=10&_offset=0"
```

Crear un socio:

```bash
curl -X POST http://localhost:5000/socios \
  -H 'Content-Type: application/json' \
  -d '{"nombre":"Nuevo Socio","email":"nuevo@example.com"}'
```

Crear una reserva futura:

```bash
curl -X POST http://localhost:5000/reservas \
  -H 'Content-Type: application/json' \
  -d '{
    "id_socio": 1,
    "id_cancha": 2,
    "fecha_hora_inicio": "2026-10-15T18:00:00.000000-03:00",
    "fecha_hora_fin": "2026-10-15T20:00:00.000000-03:00"
  }'
```

Consultar disponibilidad:

```bash
curl "http://localhost:5000/canchas/disponibles?fecha=2026-10-15&hora_inicio=18:00:00&hora_fin=20:00:00"
```

Cambiar el estado de una reserva:

```bash
curl -X PUT http://localhost:5000/reservas/1/estado \
  -H 'Content-Type: application/json' \
  -d '{"estado":"cancelada"}'
```

Todas las fechas de reservas se reciben en formato ISO 8601 con GMT-3 y seis digitos de fraccion: `YYYY-MM-DDTHH:MM:SS.ffffff-03:00`.

## Reglas principales

- El club funciona todos los dias de 08:00 a 23:00.
- Una reserva dura entre una y tres horas completas.
- Inicio y fin deben ser horas en punto y no se puede atravesar la medianoche.
- El intervalo debe ser futuro al crear la reserva.
- Las reservas consecutivas son validas: 18:00-20:00 y 20:00-21:00.
- Las reservas canceladas liberan el horario, pero conservan su registro.
- Los importes se expresan en centavos.
- Cambiar el precio de una cancha no modifica reservas anteriores.
- Los campos desconocidos, filtros invalidos y cuerpos vacios se rechazan.

## Contrato de la API

El contrato oficial se encuentra en [docs/swagger.yaml](docs/swagger.yaml). La implementacion debe seguir ese archivo. No se requiere autenticacion ni una interfaz grafica.

## `__init__.py`

Los archivos `__init__.py` vacios se conservan intencionalmente. Indican que `src`, `routes`, `services` y `validators` son paquetes Python y hacen mas clara la estructura para quienes recien empiezan. No es necesario poner codigo dentro de ellos ni borrarlos.

## Subir el proyecto a GitHub

Desde la carpeta raiz:

```bash
git init
git add .
git commit -m "Implementar API de reservas del club"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
git push -u origin main
```

Antes de hacer `git add .`, revisar que `.env` no aparezca en la lista:

```bash
git status
```

El repositorio debe incluir `README.md`, `requirements.txt`, `docker-compose.yml`, `db/init_db.sql`, `docs/swagger.yaml` y el codigo de `src`.

## Verificaciones rapidas

```bash
python -m compileall -q app.py src
python -c "from app import app; print(app.url_map)"
```

Para una entrega completa tambien conviene probar creaciones validas, superposiciones, horarios invalidos, cancelaciones, filtros y paginacion contra MySQL levantado.
