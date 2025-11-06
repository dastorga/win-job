# 🚀 Instrucciones de Lanzamiento - DevOps Job Scraper

## Métodos de Ejecución

### 1. Desarrollo Local (Recomendado para desarrollo)

#### Prerrequisitos
- Python 3.9+ instalado
- Node.js 14+ instalado
- Git instalado

#### Configuración Inicial
```bash
# 1. Clonar el repositorio (si aún no lo tienes)
git clone https://github.com/tu-usuario/win-job.git
cd win-job

# 2. Configurar Backend
cd backend
cp .env.example .env
# Editar .env con tus configuraciones locales
source venv/bin/activate  # El venv ya está creado
```

#### Lanzamiento Rápido
```bash
# En VS Code, usar las tareas creadas:
# 1. Cmd+Shift+P -> "Tasks: Run Task"
# 2. Seleccionar "Start Backend Server"
# 3. En otra terminal, seleccionar "Start Frontend Server"

# O manualmente:
# Terminal 1 - Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend && npm start
```

#### URLs de Desarrollo
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs
- **Redoc API**: http://localhost:8000/redoc

### 2. Con Docker Compose (Entorno completo)

```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Solo servicios específicos
docker-compose up backend frontend

# Con base de datos PostgreSQL
docker-compose up backend frontend db
```

#### URLs con Docker
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **PostgreSQL**: localhost:5432

### 3. Producción en Google Cloud

#### Configuración Inicial
```bash
# 1. Autenticarse en GCP
gcloud auth login
gcloud config set project TU-PROJECT-ID

# 2. Crear infraestructura
cd infrastructure
terraform init
terraform apply -var="project_id=TU-PROJECT-ID"

# 3. Configurar CI/CD
# Añadir secrets en GitHub:
# - GCP_PROJECT_ID
# - GCP_SA_KEY (JSON de service account)
```

#### Despliegue
```bash
# Push a main branch activa automáticamente:
git push origin main
# Esto ejecuta: tests → build → deploy a Cloud Run
```

## 🛠️ Comandos de Desarrollo

### Backend
```bash
cd backend && source venv/bin/activate

# Ejecutar servidor de desarrollo
uvicorn main:app --reload

# Ejecutar tests
pytest -v

# Crear migraciones (cuando agregues alembic)
alembic revision --autogenerate -m "Add new table"
alembic upgrade head

# Instalar nueva dependencia
pip install nueva-libreria
pip freeze > requirements.txt
```

### Frontend
```bash
cd frontend

# Ejecutar en desarrollo
npm start

# Ejecutar tests
npm test

# Build para producción
npm run build

# Instalar nueva dependencia
npm install nueva-libreria
```

### Docker
```bash
# Build solo backend
docker build -f docker/Dockerfile.backend -t devops-jobs-backend ./backend

# Build solo frontend
docker build -f docker/Dockerfile.frontend -t devops-jobs-frontend ./frontend

# Ver logs
docker-compose logs backend
docker-compose logs frontend
```

## 📊 Uso de la Aplicación

### Primera Ejecución
1. **Abrir**: http://localhost:3000
2. **Hacer clic en**: "Buscar Ofertas" 
3. **Configurar**:
   - Término: "DevOps" 
   - Ubicación: "España"
   - Máximo: 50 ofertas
4. **Ejecutar scraping**: El sistema extraerá ofertas de LinkedIn
5. **Ver resultados**: Las ofertas aparecerán filtradas automáticamente

### Funcionalidades Principales
- ✅ **Scraping automático** de LinkedIn
- ✅ **Filtrado inteligente** (sin inglés)
- ✅ **Dashboard interactivo** con estadísticas
- ✅ **Búsqueda y filtros** avanzados
- ✅ **Enlaces directos** a LinkedIn

## 🐛 Solución de Problemas

### Backend no arranca
```bash
# Verificar dependencias
cd backend && source venv/bin/activate && pip install -r requirements.txt

# Verificar puerto
lsof -i :8000
kill -9 PID_DEL_PROCESO

# Ver logs
cd backend && source venv/bin/activate && uvicorn main:app --reload --log-level debug
```

### Frontend no compila
```bash
cd frontend

# Limpiar caché
rm -rf node_modules package-lock.json
npm install

# Verificar versión Node
node --version  # Debe ser 14+
```

### Scraping no funciona
1. **Chrome no encontrado**: Instalar Google Chrome
2. **ChromeDriver**: Se instala automáticamente con Selenium 4+
3. **LinkedIn bloqueado**: Usar VPN o esperar (rate limiting)
4. **Sin resultados**: Cambiar términos de búsqueda

### Docker issues
```bash
# Limpiar todo
docker-compose down -v
docker system prune -a

# Reconstruir
docker-compose up --build --force-recreate
```

## 🔄 Desarrollo y Contribución

### Flujo de desarrollo
1. **Crear rama**: `git checkout -b feature/nueva-funcionalidad`
2. **Desarrollar**: Hacer cambios y tests
3. **Commit**: `git commit -m "Add nueva funcionalidad"`  
4. **Push**: `git push origin feature/nueva-funcionalidad`
5. **PR**: Crear Pull Request en GitHub

### Tests automáticos
```bash
# Backend tests
cd backend && source venv/bin/activate && pytest -v --cov=app

# Frontend tests
cd frontend && npm test -- --coverage
```

### Hot reloading
- **Backend**: FastAPI recarga automáticamente con `--reload`
- **Frontend**: React recarga automáticamente con `npm start`
- **Database**: Cambios en modelos requieren restart

## 📈 Monitoreo (Producción)

### Logs en Cloud Run
```bash
# Ver logs del backend
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=devops-jobs-backend" --limit 50 --format json

# Ver logs del frontend  
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=devops-jobs-frontend" --limit 50 --format json
```

### Métricas
- **Cloud Run**: CPU, Memoria, Requests en GCP Console
- **Base de datos**: Conexiones, Queries en Cloud SQL
- **Aplicación**: Ofertas extraídas, Errores de scraping

## 🚨 Importante

### LinkedIn Terms of Service
- Este proyecto es para **uso educativo** y personal
- **Respetar rate limits** de LinkedIn
- **No hacer scraping masivo** o comercial
- Considera las APIs oficiales de LinkedIn para uso comercial

### Seguridad
- **Cambiar SECRET_KEY** en producción
- **Usar HTTPS** en producción  
- **No commitear** credenciales reales
- **Actualizar dependencias** regularmente

---

## 🎉 ¡Listo para usar!

Tu sistema DevOps Job Scraper está configurado y listo. Para empezar:

1. **Ejecutar**: `cd backend && source venv/bin/activate && uvicorn main:app --reload`
2. **En otra terminal**: `cd frontend && npm start`
3. **Abrir**: http://localhost:3000
4. **¡Buscar ofertas DevOps sin inglés!** 🚀