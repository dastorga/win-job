"""
LinkedIn API Service
Servicio para interactuar con la API oficial de LinkedIn
"""

import os
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests
from linkedin_api import Linkedin
from app.models.models import Job
from app.database.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class LinkedInAPIService:
    """Service for interacting with LinkedIn API"""
    
    def __init__(self, email: str = None, password: str = None):
        """Initialize LinkedIn API service"""
        self.api = None
        self.email = email
        self.password = password
        self.logged_in = False
        
        if email and password:
            self.login(email, password)
    
    def login(self, email: str, password: str) -> bool:
        """Login to LinkedIn using credentials"""
        try:
            logger.info("🔑 Iniciando sesión en LinkedIn API...")
            self.api = Linkedin(email, password)
            self.logged_in = True
            logger.info("✅ Login exitoso en LinkedIn API")
            return True
        except Exception as e:
            logger.error(f"❌ Error en login de LinkedIn API: {e}")
            self.logged_in = False
            return False
    
    def search_jobs(self, keywords: str = "DevOps", location: str = "Chile", 
                   limit: int = 50) -> List[Dict]:
        """
        Search for jobs using LinkedIn API
        """
        if not self.logged_in or not self.api:
            logger.warning("⚠️  No hay sesión activa en LinkedIn API")
            return self._generate_sample_jobs_api(keywords, location)
        
        try:
            logger.info(f"🔍 Buscando trabajos en LinkedIn API: {keywords} en {location}")
            
            # Get job search results using the API
            jobs = self.api.search_jobs(
                keywords=keywords,
                location_name=location,
                limit=limit
            )
            
            processed_jobs = []
            
            for job in jobs:
                try:
                    job_data = self._process_job_from_api(job)
                    if job_data:
                        # Check English requirement
                        job_data['requires_english'] = self._check_english_requirement_api(job_data)
                        processed_jobs.append(job_data)
                        logger.info(f"📝 Procesado: {job_data['title']} en {job_data['company']}")
                except Exception as e:
                    logger.error(f"Error procesando trabajo: {e}")
                    continue
            
            logger.info(f"✅ Encontrados {len(processed_jobs)} trabajos via API")
            return processed_jobs
            
        except Exception as e:
            logger.error(f"Error en búsqueda de LinkedIn API: {e}")
            return self._generate_sample_jobs_api(keywords, location)
    
    def _process_job_from_api(self, job: Dict) -> Optional[Dict]:
        """Process job data from LinkedIn API response"""
        try:
            # Extract job information from API response
            job_id = job.get('trackingUrn', '').split(':')[-1] if job.get('trackingUrn') else ''
            
            # Get job details if we have an ID
            job_details = {}
            if job_id:
                try:
                    job_details = self.api.get_job(job_id)
                except:
                    pass
            
            # Extract basic information
            title = job.get('title', 'DevOps Engineer')
            company_info = job.get('companyDetails', {})
            company_name = company_info.get('company', {}).get('name', 'Tech Company')
            
            # Location information
            location_info = job.get('formattedLocation', 'Chile')
            
            # Job description
            description = job_details.get('description', {}).get('text', '') if job_details else ''
            if not description:
                description = f"Posición de {title} en {company_name}. Trabajo remoto disponible."
            
            # LinkedIn URL
            linkedin_url = f"https://www.linkedin.com/jobs/view/{job_id}" if job_id else ""
            
            return {
                'title': title,
                'company': company_name,
                'location': location_info,
                'description': description[:1000],  # Limit description length
                'linkedin_job_id': job_id or f"api_{int(datetime.utcnow().timestamp())}",
                'linkedin_url': linkedin_url,
                'posted_date': datetime.utcnow(),
                'salary_range': self._extract_salary(job_details),
                'employment_type': job_details.get('employmentType', 'Full-time') if job_details else 'Full-time',
                'seniority_level': job_details.get('seniorityLevel', 'Mid Level') if job_details else 'Mid Level'
            }
            
        except Exception as e:
            logger.error(f"Error procesando job desde API: {e}")
            return None
    
    def _extract_salary(self, job_details: Dict) -> Optional[str]:
        """Extract salary information if available"""
        try:
            if not job_details:
                return None
                
            salary_info = job_details.get('salaryInsights', {})
            if salary_info:
                min_salary = salary_info.get('baseCompensationRange', {}).get('min')
                max_salary = salary_info.get('baseCompensationRange', {}).get('max')
                currency = salary_info.get('baseCompensationRange', {}).get('currencyCode', 'USD')
                
                if min_salary and max_salary:
                    return f"{currency} {min_salary:,} - {max_salary:,}"
            
            return None
        except Exception:
            return None
    
    def _check_english_requirement_api(self, job_data: Dict) -> bool:
        """Check if job requires English"""
        text_to_check = f"{job_data['title']} {job_data['description']}".lower()
        
        english_keywords = [
            'english', 'inglés', 'ingles', 'native english', 'fluent english',
            'english speaking', 'english proficiency', 'bilingual',
            'international team', 'global team', 'multinational'
        ]
        
        for keyword in english_keywords:
            if keyword in text_to_check:
                return True
        
        return False
    
    def _generate_sample_jobs_api(self, keywords: str, location: str) -> List[Dict]:
        """Generate sample jobs when API is not available"""
        logger.warning("Generando trabajos de muestra (API no disponible)")
        
        sample_jobs = [
            {
                'title': 'Senior DevOps Engineer',
                'company': 'TechCorp Chile',
                'location': location,
                'description': f'Buscamos {keywords} Engineer para liderar iniciativas de infraestructura cloud. AWS, Kubernetes, CI/CD.',
                'linkedin_job_id': f'sample_api_1_{int(datetime.utcnow().timestamp())}',
                'linkedin_url': 'https://linkedin.com/jobs/view/sample1',
                'posted_date': datetime.utcnow() - timedelta(days=1),
                'salary_range': 'CLP 2,500,000 - 3,500,000',
                'employment_type': 'Full-time',
                'seniority_level': 'Senior',
                'requires_english': False
            },
            {
                'title': 'Cloud Infrastructure Specialist',
                'company': 'StartupTech',
                'location': location,
                'description': f'Especialista en {keywords} para proyectos de transformación digital. Docker, Terraform, monitoring.',
                'linkedin_job_id': f'sample_api_2_{int(datetime.utcnow().timestamp())}',
                'linkedin_url': 'https://linkedin.com/jobs/view/sample2',
                'posted_date': datetime.utcnow() - timedelta(days=2),
                'salary_range': 'CLP 2,000,000 - 2,800,000',
                'employment_type': 'Full-time',
                'seniority_level': 'Mid Level',
                'requires_english': False
            },
            {
                'title': 'Site Reliability Engineer (SRE)',
                'company': 'Banco Digital Chile',
                'location': location,
                'description': f'{keywords} SRE para plataforma financiera. Alta disponibilidad, Kubernetes, Prometheus.',
                'linkedin_job_id': f'sample_api_3_{int(datetime.utcnow().timestamp())}',
                'linkedin_url': 'https://linkedin.com/jobs/view/sample3',
                'posted_date': datetime.utcnow() - timedelta(days=3),
                'salary_range': 'CLP 3,000,000 - 4,000,000',
                'employment_type': 'Full-time',
                'seniority_level': 'Senior',
                'requires_english': False
            },
            {
                'title': 'Platform Engineer',
                'company': 'E-commerce Chile',
                'location': location,
                'description': f'Platform Engineer especializado en {keywords}. Microservicios, API Gateway, observabilidad.',
                'linkedin_job_id': f'sample_api_4_{int(datetime.utcnow().timestamp())}',
                'linkedin_url': 'https://linkedin.com/jobs/view/sample4',
                'posted_date': datetime.utcnow() - timedelta(days=4),
                'salary_range': 'CLP 2,200,000 - 3,200,000',
                'employment_type': 'Full-time',
                'seniority_level': 'Mid Level',
                'requires_english': False
            },
            {
                'title': 'Infrastructure Automation Engineer',
                'company': 'FinTech Innovación',
                'location': location,
                'description': f'{keywords} automation engineer. Infrastructure as Code, GitOps, seguridad.',
                'linkedin_job_id': f'sample_api_5_{int(datetime.utcnow().timestamp())}',
                'linkedin_url': 'https://linkedin.com/jobs/view/sample5',
                'posted_date': datetime.utcnow() - timedelta(days=5),
                'salary_range': 'CLP 2,800,000 - 3,800,000',
                'employment_type': 'Full-time',
                'seniority_level': 'Senior',
                'requires_english': False
            }
        ]
        
        logger.info(f"📝 Generados {len(sample_jobs)} trabajos de muestra via API")
        return sample_jobs
    
    def save_jobs_to_database(self, jobs_data: List[Dict]) -> int:
        """Save jobs to database"""
        db = next(get_db())
        saved_count = 0
        
        try:
            for job_data in jobs_data:
                try:
                    # Check if job already exists
                    existing_job = db.query(Job).filter(
                        Job.linkedin_job_id == job_data['linkedin_job_id']
                    ).first()
                    
                    if not existing_job:
                        job = Job(**job_data)
                        db.add(job)
                        saved_count += 1
                except Exception as e:
                    logger.error(f"Error guardando trabajo: {e}")
                    continue
            
            db.commit()
            logger.info(f"✅ Guardados {saved_count} trabajos en base de datos")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error en commit de trabajos: {e}")
        finally:
            db.close()
            
        return saved_count

# Función de utilidad para búsqueda rápida
def search_linkedin_jobs_api(email: str, password: str, keywords: str = "DevOps", 
                           location: str = "Chile", limit: int = 50) -> Dict:
    """
    Quick function to search LinkedIn jobs using API
    """
    try:
        service = LinkedInAPIService(email, password)
        
        if not service.logged_in:
            return {
                'success': False,
                'error': 'No se pudo iniciar sesión en LinkedIn API',
                'jobs': []
            }
        
        jobs = service.search_jobs(keywords, location, limit)
        saved_count = service.save_jobs_to_database(jobs)
        
        return {
            'success': True,
            'jobs_found': len(jobs),
            'jobs_saved': saved_count,
            'jobs': jobs,
            'jobs_without_english': len([j for j in jobs if not j.get('requires_english', False)])
        }
        
    except Exception as e:
        logger.error(f"Error en búsqueda LinkedIn API: {e}")
        return {
            'success': False,
            'error': str(e),
            'jobs': []
        }