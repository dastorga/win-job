# DevOps Job Scraper 🚀

Sistema completo para extraer y analizar ofertas de trabajo DevOps desde LinkedIn, filtrando específicamente aquellas que **NO requieren inglés**. ✨ Sistema desplegado y operativo.

## 🎯 Características Principales

- **Web Scraping Inteligente**: Extrae ofertas de LinkedIn usando Selenium
- **Filtrado Automático**: Identifica y filtra ofertas sin requisitos de inglés
- **Dashboard Interactivo**: Interfaz React para visualizar y gestionar ofertas
- **API RESTful**: Backend FastAPI con documentación automática
- **Infraestructura como Código**: Despliegue automatizado con Terraform
- **CI/CD Completo**: Pipeline automatizado con GitHub Actions

## 🏗️ Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │────│   FastAPI       │────│  PostgreSQL     │
│   (Frontend)    │    │   (Backend)     │    │  (Database)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐             │
         └──────────────│  Google Cloud   │─────────────┘
                        │   Platform      │
                        └─────────────────┘
```

## 🛠️ Tecnologías

### Backend

- **Python 3.11** con FastAPI
- **PostgreSQL** como base de datos
- **Selenium** + BeautifulSoup para scraping
- **SQLAlchemy** para ORM
- **JWT** para autenticación
- **Redis** para tareas en segundo plano

### Frontend

- **React 18** con TypeScript
- **Material-UI** para componentes
- **Axios** para peticiones HTTP
- **React Router** para navegación

### Infraestructura

- **Google Cloud Platform**
  - Cloud Run (contenedores)
  - Cloud SQL (PostgreSQL)
  - Cloud Storage (archivos estáticos)
  - Artifact Registry (imágenes Docker)
- **Terraform** para Infrastructure as Code
- **Docker** para containerización

### DevOps

- **GitHub Actions** para CI/CD
- **Docker Compose** para desarrollo local
- **Pytest** para testing backend
- **Jest** para testing frontend

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.11+
- Node.js 18+
- Docker y Docker Compose
- Google Cloud SDK (para despliegue)
- Terraform (para infraestructura)

### Desarrollo Local

1. **Clonar el repositorio**

```bash
git clone https://github.com/tu-usuario/win-job.git
cd win-job
```

2. **Backend Setup**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Frontend Setup**

```bash
cd frontend
npm install
```

4. **Base de Datos Local**

```bash
# Usando Docker Compose
docker-compose up -d db redis
```

5. **Ejecutar la aplicación**

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

La aplicación estará disponible en:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentación API: http://localhost:8000/docs

### Usando Docker Compose

```bash
# Construir y ejecutar todos los servicios
docker-compose up --build

# Solo servicios de desarrollo (sin scraping)
docker-compose up backend frontend db redis
```

## 📊 Uso de la Aplicación

### Dashboard Principal

- **Visualización de ofertas**: Lista todas las ofertas encontradas
- **Filtros avanzados**: Por empresa, ubicación, sin inglés
- **Estadísticas**: Resumen de ofertas y tendencias
- **Búsqueda**: Buscar por título o descripción

### Scraping de Ofertas

1. Hacer clic en "Buscar Ofertas"
2. Configurar parámetros:
   - Término de búsqueda (ej: "DevOps", "SRE")
   - Ubicación (ej: "España", "Madrid")
   - Máximo de ofertas a extraer
3. El sistema automáticamente:
   - Extrae ofertas de LinkedIn
   - Analiza si requieren inglés
   - Las guarda en la base de datos
   - Actualiza el dashboard

### API Endpoints

#### Ofertas

- `GET /api/v1/jobs/` - Listar ofertas con filtros
- `GET /api/v1/jobs/{job_id}` - Obtener oferta específica
- `POST /api/v1/jobs/scrape` - Ejecutar scraping
- `GET /api/v1/jobs/stats/summary` - Estadísticas

#### Autenticación

- `POST /api/v1/auth/register` - Registro de usuario
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/users/me` - Perfil actual

## 🌐 Despliegue en Google Cloud

### 1. Configuración Inicial

```bash
# Autenticarse en GCP
gcloud auth login
gcloud config set project TU-PROJECT-ID

# Habilitar APIs necesarias
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### 2. Infraestructura con Terraform

```bash
cd infrastructure

# Inicializar Terraform
terraform init

# Planificar cambios
terraform plan -var="project_id=TU-PROJECT-ID"

# Aplicar infraestructura
terraform apply -var="project_id=TU-PROJECT-ID"
```

### 3. CI/CD con GitHub Actions

1. **Configurar Secrets en GitHub:**

   - `GCP_PROJECT_ID`: ID del proyecto en GCP
   - `GCP_SA_KEY`: Clave JSON de la cuenta de servicio

2. **Push a main branch** activará automáticamente:
   - Tests del backend y frontend
   - Análisis de seguridad
   - Build de imágenes Docker
   - Despliegue a Cloud Run

## 🔧 Configuración Avanzada

### Variables de Entorno

#### Backend (.env)

```env
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost:5432/devops_jobs

# Seguridad
SECRET_KEY=tu-clave-secreta-muy-segura
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LinkedIn (opcional)
LINKEDIN_EMAIL=tu-email@ejemplo.com
LINKEDIN_PASSWORD=tu-password

# Scraping
MAX_JOBS_PER_SCRAPE=50
SCRAPE_INTERVAL_HOURS=6

# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-key.json
GCP_PROJECT_ID=tu-project-id
```

#### Frontend (.env)

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

### Personalización del Scraping

El sistema permite personalizar la lógica de scraping:

1. **Filtros de inglés**: Modificar keywords en `linkedin_scraper.py`
2. **Selectores CSS**: Actualizar selectores si LinkedIn cambia su estructura
3. **Frecuencia**: Configurar intervalos de scraping automático

## 🧪 Testing

### Backend

```bash
cd backend
pytest -v --cov=app tests/
```

### Frontend

```bash
cd frontend
npm test -- --coverage
```

### Integración

```bash
# Con Docker Compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📈 Monitoreo y Logs

### Google Cloud Logging

```bash
# Ver logs de Cloud Run
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=devops-jobs-backend" --limit 50 --format json
```

### Métricas Disponibles

- Ofertas extraídas por día
- Tasa de éxito de scraping
- Ofertas sin requisitos de inglés
- Empresas más activas

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📝 Roadmap

- [ ] **Notificaciones**: Email/Slack para nuevas ofertas
- [ ] **Machine Learning**: Scoring automático de ofertas
- [ ] **Multi-plataforma**: Scraping de InfoJobs, Indeed, etc.
- [ ] **Móvil**: App React Native
- [ ] **Análisis avanzado**: Tendencias salariales, skills demandadas
- [ ] **Bot de Telegram**: Notificaciones en tiempo real

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🆘 Soporte

Si tienes problemas o preguntas:

1. **Issues**: Abre un issue en GitHub
2. **Documentación**: Revisa la doc de la API en `/docs`
3. **Logs**: Revisar logs de Cloud Run para errores

## 🙏 Agradecimientos

- LinkedIn por la plataforma (uso educativo)
- Comunidad Open Source de Python y React
- Google Cloud Platform por los recursos
- GitHub por Actions y hosting

---

**⭐ Si este proyecto te es útil, dale una estrella en GitHub!**

Hecho con ❤️ para la comunidad DevOps hispanohablante.
# Activar despliegue automático
