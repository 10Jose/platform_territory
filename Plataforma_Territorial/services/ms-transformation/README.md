# ms-transformation (HU-07)

Microservicio FastAPI: sincroniza el último CSV desde **ms-ingestion**, transforma con **Pandas** y persiste en **db-transformation**.

**Python:** usa **3.11 o 3.12** (recomendado). Con **3.14** u otras versiones muy nuevas, `pip` puede intentar **compilar** `pandas` y fallar en Windows si no tienes Visual Studio Build Tools. Si ya tienes 3.14 instalado, instala también 3.12 desde [python.org](https://www.python.org/downloads/) y ejecuta el proyecto con `py -3.12` (ver abajo).

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/health` | Estado del servicio |
| POST | `/sync/zones` | Descarga último dataset, transforma y guarda en `transformed_zone_data` + `transformation_runs` |

## Variables de entorno

Ver `.env.example`. Destacadas: `DATABASE_URL`, `INGESTION_BASE_URL`, rutas `INGESTION_LATEST_PATH` y `INGESTION_DOWNLOAD_TEMPLATE`.

## Desarrollo local

```bash
cd ms-transformation
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8002
```

## Pruebas

### 1) Tests automáticos (transformación con Pandas)

Comprueban columnas obligatorias, densidad, índice, duplicados, etc. **No levantan** Postgres ni ingestion.

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

En **Windows**, si `python` no existe, prueba el launcher:

```powershell
py -3 -m pip install -r requirements-dev.txt
py -3 -m pytest
```

Si ninguno funciona, instala Python desde [python.org](https://www.python.org/downloads/) y marca **“Add python.exe to PATH”** en el instalador.

**Varias versiones de Python en Windows:** si instalaste 3.12 además de 3.14:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pytest
```

### Si `pip install` falla al instalar `pandas` (Windows)

Suele ser porque tu Python es **demasiado nuevo** y no hay paquete precompilado. Solución práctica: instala **Python 3.12**, crea un entorno virtual con `py -3.12` (como arriba) y vuelve a instalar dependencias. Alternativa: usar solo **Docker** (`docker compose up --build`) y olvidarte de `pip` en el PC.

### 2) Prueba manual end-to-end (recomendada para la demo)

Necesitas **Postgres**, el **mock de ingestion** (puerto 8001) y **ms-transformation** (puerto 8002).

**Opción A — Docker Compose (todo junto, incluye mock de ingestion)**

En la raíz del repositorio:

```bash
docker compose up --build
```

Cuando arranque, en otra terminal:

```bash
curl -s -X POST http://localhost:8002/sync/zones
```

En PowerShell (Windows):

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8002/sync/zones
```

Respuesta esperada: JSON con `transformation_run_id`, `rows_read`, `rows_inserted`, `rows_updated`, `rules_applied`, etc.

Comprobar datos en la base:

```bash
docker compose exec db-transformation psql -U postgres -d db_transformation -c "SELECT zone_key, zona, densidad_poblacional FROM transformed_zone_data;"
docker compose exec db-transformation psql -U postgres -d db_transformation -c "SELECT id, status, rows_read, rules_version FROM transformation_runs ORDER BY id DESC LIMIT 1;"
```

**Opción B — Sin Docker (tres procesos)**

1. Postgres local en el puerto que uses en `DATABASE_URL` (o solo `db-transformation` con `docker compose up db-transformation`).
2. Mock de ingestion:

   ```bash
   cd ms-transformation
   uvicorn mock_ingestion_server:app --host 127.0.0.1 --port 8001
   ```

3. En `.env`: `INGESTION_BASE_URL=http://127.0.0.1:8001`
4. Servicio de transformación:

   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8002
   ```

5. Mismo `curl` / `Invoke-RestMethod` a `POST http://127.0.0.1:8002/sync/zones`.

### 3) Contra el ms-ingestion real del equipo

Apaga o no uses `mock-ingestion` en compose; define `INGESTION_BASE_URL` (y rutas) al servicio real. Verifica con `GET {INGESTION_BASE_URL}/health` y que `/datasets/latest` + descarga de CSV coincidan con `.env`.

### Qué valida cada cosa

| Prueba | Qué demuestra |
|--------|----------------|
| `pytest` | Reglas Pandas, errores por columnas faltantes, sin duplicados en el CSV |
| `POST /sync/zones` con mock | Pipeline completo: HTTP → CSV → BD `transformed_zone_data` + `transformation_runs` |
| Consultas SQL | Filas guardadas y trazabilidad del run |

## Docker (desde la raíz del repo)

```bash
docker compose up --build
```

- **ms-transformation:** `http://localhost:8002`
- **mock-ingestion:** `http://localhost:8001` (solo para pruebas)
- **Postgres:** puerto host `5433`

Para usar **ms-ingestion** real en lugar del mock, elimina el servicio `mock-ingestion` del `docker-compose.yml` o sobrescribe `INGESTION_BASE_URL` al apuntar a otro host.

---

## Demostración para la evaluación (qué mostrar a la profesora)

**Antes de la clase:** tener **Docker Desktop** abierto y el repo en `spring1_corte2`.

### Guión rápido (5–8 minutos)

1. **Explicar el alcance (HU-07):** microservicio que **no modifica** ingestion; solo **lee** el último CSV, **transforma** con Pandas (densidad, índice) y **guarda** en `db-transformation` con **trazabilidad** (`transformation_runs`).
2. **Levantar el sistema** (terminal en la raíz del repo, donde está `docker-compose.yml`):

   ```powershell
   docker compose up --build
   ```

   Esperar a que los tres servicios arranquen (Postgres, mock-ingestion, ms-transformation).

3. **Swagger (muy visual):** en el navegador abrir [http://localhost:8002/docs](http://localhost:8002/docs). Ahí se ve la API documentada: probar **GET `/health`** y **POST `/sync/zones`** con “Try it out”.
4. **Script automático (opcional):** con el compose ya arriba, en **otra** terminal:

   ```powershell
   cd <carpeta-del-repo>   # donde está docker-compose.yml
   .\scripts\demo-profe.ps1
   ```

   Debe imprimir `status: ok` y un JSON con `transformation_run_id`, `rows_read`, `rows_inserted`, `rows_updated`, `rules_applied`.

5. **Probar lógica sin Docker (opcional):** si tienes Python **3.12** y el venv instalado:

   ```powershell
   cd ms-transformation
   python -m pytest
   ```

   Debe decir que los tests pasaron (reglas Pandas y validación de columnas).

6. **Base de datos (opcional, muy convincente):** en otra terminal:

   ```powershell
   docker compose exec db-transformation psql -U postgres -d db_transformation -c "SELECT zone_key, zona, densidad_poblacional FROM transformed_zone_data;"
   docker compose exec db-transformation psql -U postgres -d db_transformation -c "SELECT id, status, rows_read, rules_version, rules_applied::text FROM transformation_runs ORDER BY id DESC LIMIT 1;"
   ```

   Así se ve **persistencia real** y el **run** con reglas en JSON.

### Si algo falla en clase

- **Puerto ocupado:** cierra otras apps o cambia el mapeo de puertos en `docker-compose.yml`.
- **Docker no arranca:** usar la opción manual del README (mock en 8001 + `uvicorn` en 8002 + Postgres).
- **`pip` / `pytest`:** usar **Python 3.12** en un venv (ver sección anterior sobre 3.14 y `pandas`).
