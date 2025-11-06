# DevOps Job Scraper - Copilot Instructions

## Proyecto Completado ✅

Sistema completo para extraer y analizar ofertas de trabajo DevOps desde LinkedIn, filtrando aquellas que NO requieren inglés.

## Arquitectura Implementada

- **Backend**: FastAPI con Python 3.9+, SQLAlchemy, Selenium
- **Frontend**: React 18 con TypeScript, Material-UI
- **Base de datos**: PostgreSQL (producción) / SQLite (desarrollo)
- **Infraestructura**: Google Cloud Platform con Terraform
- **CI/CD**: GitHub Actions con despliegue automático
- **Scraping**: Selenium + BeautifulSoup para LinkedIn

## Estructura del Proyecto

```
win-job/
├── backend/              # API Python/FastAPI
│   ├── app/
│   │   ├── api/         # Endpoints REST
│   │   ├── models/      # Modelos SQLAlchemy
│   │   ├── services/    # Lógica de negocio
│   │   └── database/    # Configuración DB
│   ├── tests/           # Tests backend
│   └── requirements.txt # Dependencias Python
├── frontend/            # React TypeScript app
│   ├── src/
│   │   ├── components/  # Componentes React
│   │   ├── pages/       # Páginas principales
│   │   ├── services/    # API client
│   │   └── types/       # Tipos TypeScript
│   └── package.json     # Dependencias Node
├── infrastructure/      # Terraform IaC
│   ├── main.tf         # Configuración principal
│   ├── resources.tf    # Recursos GCP
│   └── cloud_run.tf    # Cloud Run services
├── .github/workflows/   # CI/CD pipelines
├── docker/             # Dockerfiles
└── docs/               # Documentación
```

## Funcionalidades Implementadas

- ✅ Web scraping inteligente de LinkedIn
- ✅ Filtrado automático de ofertas sin inglés
- ✅ Dashboard interactivo con estadísticas
- ✅ API REST completa con autenticación JWT
- ✅ Sistema de usuarios y aplicaciones
- ✅ Despliegue automatizado en Google Cloud
- ✅ CI/CD pipeline con GitHub Actions
- ✅ Docker containers para desarrollo y producción
- ✅ Terraform para infraestructura como código

## Comandos de Desarrollo

```bash
# Backend
cd backend && source venv/bin/activate && uvicorn main:app --reload

# Frontend
cd frontend && npm start

# Docker Compose
docker-compose up --build

# Tests
cd backend && pytest -v
cd frontend && npm test
```

## URLs de Desarrollo

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Estado: ✅ PROYECTO COMPLETADO

- Todos los componentes implementados
- Dependencias instaladas correctamente
- Tareas de VS Code configuradas
- Documentación completa en README.md y LAUNCH.md
- Listo para desarrollo y despliegue
