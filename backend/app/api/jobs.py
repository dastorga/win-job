from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.models.models import Job, JobApplication
from app.services.linkedin_scraper import scrape_linkedin_jobs
from app.services.linkedin_api_service import search_linkedin_jobs_api
from app.services.linkedin_oauth_service import LinkedInOAuthService, get_linkedin_auth_url
from pydantic import BaseModel
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class JobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    description: str
    employment_type: Optional[str]
    seniority_level: Optional[str]
    linkedin_url: str
    requires_english: bool
    match_score: float
    posted_date: Optional[datetime]
    scraped_at: datetime

    class Config:
        from_attributes = True

class JobSearchParams(BaseModel):
    search_term: str = "DevOps"
    location: str = "España" 
    max_jobs: int = 50

class ScrapeResponse(BaseModel):
    success: bool
    jobs_found: int
    jobs_saved: int
    jobs_without_english: int
    message: str

class LinkedInAPIParams(BaseModel):
    email: str
    password: str
    keywords: str = "DevOps"
    location: str = "Chile"
    limit: int = 50

class LinkedInAPIResponse(BaseModel):
    success: bool
    jobs_found: int
    jobs_saved: int
    jobs_without_english: int
    message: str
    error: Optional[str] = None

class OAuthURLResponse(BaseModel):
    authorization_url: Optional[str]
    state: Optional[str]
    instructions: List[str]
    error: Optional[str] = None

class OAuthTokenRequest(BaseModel):
    authorization_code: str
    state: str

class OAuthTokenResponse(BaseModel):
    success: bool
    access_token: Optional[str] = None
    expires_in: Optional[int] = None
    message: str
    error: Optional[str] = None

class OAuthJobSearchRequest(BaseModel):
    access_token: str
    keywords: str = "DevOps"
    location: str = "Chile"
    limit: int = 50

@router.post("/scrape", response_model=ScrapeResponse)
async def trigger_job_scrape(
    params: JobSearchParams,
    db: Session = Depends(get_db)
):
    """
    Trigger LinkedIn job scraping
    """
    try:
        logger.info(f"Starting job scrape: {params.search_term} in {params.location}")
        
        result = scrape_linkedin_jobs(
            search_term=params.search_term,
            location=params.location,
            max_jobs=params.max_jobs
        )
        
        if result['success']:
            return ScrapeResponse(
                success=True,
                jobs_found=result['jobs_found'],
                jobs_saved=result['jobs_saved'],
                jobs_without_english=result['jobs_without_english'],
                message=f"Successfully scraped {result['jobs_saved']} new jobs"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Scraping failed: {result['error']}"
            )
            
    except Exception as e:
        logger.error(f"Error in job scraping endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape-api", response_model=LinkedInAPIResponse)
async def trigger_linkedin_api_search(
    params: LinkedInAPIParams,
    db: Session = Depends(get_db)
):
    """
    Trigger LinkedIn API job search with user credentials
    """
    try:
        logger.info(f"Starting LinkedIn API search: {params.keywords} in {params.location}")
        
        result = search_linkedin_jobs_api(
            email=params.email,
            password=params.password,
            keywords=params.keywords,
            location=params.location,
            limit=params.limit
        )
        
        if result['success']:
            return LinkedInAPIResponse(
                success=True,
                jobs_found=result['jobs_found'],
                jobs_saved=result['jobs_saved'],
                jobs_without_english=result['jobs_without_english'],
                message=f"Successfully found {result['jobs_found']} jobs via LinkedIn API"
            )
        else:
            return LinkedInAPIResponse(
                success=False,
                jobs_found=0,
                jobs_saved=0,
                jobs_without_english=0,
                message="LinkedIn API search failed",
                error=result['error']
            )
            
    except Exception as e:
        logger.error(f"Error in LinkedIn API endpoint: {e}")
        return LinkedInAPIResponse(
            success=False,
            jobs_found=0,
            jobs_saved=0,
            jobs_without_english=0,
            message="Internal server error",
            error=str(e)
        )

@router.get("/oauth/auth-url", response_model=OAuthURLResponse)
async def get_oauth_authorization_url():
    """
    Get LinkedIn OAuth authorization URL
    """
    try:
        logger.info("Generating LinkedIn OAuth authorization URL")
        
        auth_data = get_linkedin_auth_url()
        
        if auth_data.get('authorization_url'):
            return OAuthURLResponse(
                authorization_url=auth_data['authorization_url'],
                state=auth_data['state'],
                instructions=auth_data.get('instructions', [])
            )
        else:
            return OAuthURLResponse(
                authorization_url=None,
                state=None,
                instructions=[],
                error=auth_data.get('error', 'Failed to generate authorization URL')
            )
            
    except Exception as e:
        logger.error(f"Error generating OAuth URL: {e}")
        return OAuthURLResponse(
            authorization_url=None,
            state=None,
            instructions=[],
            error=str(e)
        )

@router.post("/oauth/token", response_model=OAuthTokenResponse)
async def exchange_oauth_code_for_token(request: OAuthTokenRequest):
    """
    Exchange OAuth authorization code for access token
    """
    try:
        logger.info("Exchanging OAuth code for access token")
        
        oauth_service = LinkedInOAuthService()
        result = oauth_service.get_access_token_from_code(
            request.authorization_code, 
            request.state
        )
        
        if result['success']:
            return OAuthTokenResponse(
                success=True,
                access_token=result['access_token'],
                expires_in=result.get('expires_in'),
                message=result['message']
            )
        else:
            return OAuthTokenResponse(
                success=False,
                message=result['message'],
                error=result['error']
            )
            
    except Exception as e:
        logger.error(f"Error exchanging OAuth code: {e}")
        return OAuthTokenResponse(
            success=False,
            message="Internal server error",
            error=str(e)
        )

@router.post("/oauth/search", response_model=LinkedInAPIResponse)
async def search_jobs_with_oauth(request: OAuthJobSearchRequest):
    """
    Search LinkedIn jobs using OAuth access token
    """
    try:
        logger.info(f"OAuth job search: {request.keywords} in {request.location}")
        
        oauth_service = LinkedInOAuthService()
        oauth_service.access_token = request.access_token
        
        result = oauth_service.search_jobs_oauth(
            request.keywords,
            request.location,
            request.limit
        )
        
        if result['success']:
            jobs = result['jobs']
            jobs_without_english = len([j for j in jobs if not j.get('requires_english', False)])
            
            return LinkedInAPIResponse(
                success=True,
                jobs_found=result['jobs_found'],
                jobs_saved=0,  # OAuth endpoint doesn't save to DB automatically
                jobs_without_english=jobs_without_english,
                message=f"Found {result['jobs_found']} jobs via OAuth"
            )
        else:
            return LinkedInAPIResponse(
                success=False,
                jobs_found=0,
                jobs_saved=0,
                jobs_without_english=0,
                message="OAuth job search failed",
                error="Search failed"
            )
            
    except Exception as e:
        logger.error(f"Error in OAuth job search: {e}")
        return LinkedInAPIResponse(
            success=False,
            jobs_found=0,
            jobs_saved=0,
            jobs_without_english=0,
            message="Internal server error",
            error=str(e)
        )

@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    no_english: bool = Query(False),
    company: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get filtered job listings
    """
    try:
        query = db.query(Job).filter(Job.is_active == True)
        
        # Apply filters
        if no_english:
            query = query.filter(Job.requires_english == False)
            
        if search:
            query = query.filter(
                Job.title.contains(search) | 
                Job.description.contains(search)
            )
            
        if company:
            query = query.filter(Job.company.contains(company))
            
        if location:
            query = query.filter(Job.location.contains(location))
        
        # Order by posted date (newest first)
        query = query.order_by(Job.posted_date.desc())
        
        # Pagination
        jobs = query.offset(skip).limit(limit).all()
        
        return jobs
        
    except Exception as e:
        logger.error(f"Error fetching jobs: {e}")
        raise HTTPException(status_code=500, detail="Error fetching jobs")

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    Get specific job by ID
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@router.get("/stats/summary")
async def get_job_stats(db: Session = Depends(get_db)):
    """
    Get job statistics summary
    """
    try:
        total_jobs = db.query(Job).filter(Job.is_active == True).count()
        jobs_without_english = db.query(Job).filter(
            Job.is_active == True, 
            Job.requires_english == False
        ).count()
        
        # Top companies
        top_companies = db.query(Job.company, db.func.count(Job.id).label('count'))\
            .filter(Job.is_active == True)\
            .group_by(Job.company)\
            .order_by(db.text('count DESC'))\
            .limit(5).all()
        
        # Top locations
        top_locations = db.query(Job.location, db.func.count(Job.id).label('count'))\
            .filter(Job.is_active == True)\
            .group_by(Job.location)\
            .order_by(db.text('count DESC'))\
            .limit(5).all()
        
        return {
            "total_jobs": total_jobs,
            "jobs_without_english": jobs_without_english,
            "english_percentage": round((total_jobs - jobs_without_english) / total_jobs * 100, 2) if total_jobs > 0 else 0,
            "top_companies": [{"name": company, "count": count} for company, count in top_companies],
            "top_locations": [{"name": location, "count": count} for location, count in top_locations]
        }
        
    except Exception as e:
        logger.error(f"Error getting job stats: {e}")
        raise HTTPException(status_code=500, detail="Error getting statistics")

@router.post("/seed-test-data")
def create_test_data(db: Session = Depends(get_db)):
    """Create test data for frontend development and testing"""
    try:
        # Check if test data already exists
        existing_jobs = db.query(Job).filter(Job.title.like('%TEST%')).count()
        if existing_jobs > 0:
            return {"message": f"Test data already exists ({existing_jobs} test jobs found)"}
        
        # Sample test jobs
        test_jobs = [
            {
                "title": "DevOps Engineer - TEST",
                "company": "TechCorp Chile",
                "location": "Santiago, Chile",
                "description": "Buscamos un DevOps Engineer con experiencia en AWS, Docker y Kubernetes. Trabajo remoto disponible.",
                "requirements": "3+ años experiencia, Docker, Kubernetes, CI/CD",
                "employment_type": "Full-time",
                "seniority_level": "Mid-level",
                "linkedin_job_id": "test-job-001",
                "linkedin_url": "https://linkedin.com/jobs/test-001",
                "requires_english": False,
                "match_score": 0.95,
                "posted_date": datetime.now(),
                "is_active": True
            },
            {
                "title": "Senior DevOps Engineer - TEST",
                "company": "InnovaTech",
                "location": "Valparaíso, Chile",
                "description": "Empresa chilena busca Senior DevOps para liderar transformación digital. Excelente ambiente laboral.",
                "requirements": "5+ años experiencia, AWS, Terraform, Python",
                "employment_type": "Full-time",
                "seniority_level": "Senior",
                "linkedin_job_id": "test-job-002",
                "linkedin_url": "https://linkedin.com/jobs/test-002",
                "requires_english": False,
                "match_score": 0.88,
                "posted_date": datetime.now(),
                "is_active": True
            },
            {
                "title": "DevOps Specialist - TEST",
                "company": "StartupChile",
                "location": "Concepción, Chile", 
                "description": "Startup innovadora busca DevOps para implementar infraestructura escalable. Sin requisito de inglés.",
                "requirements": "2+ años experiencia, Git, Jenkins, Linux",
                "employment_type": "Full-time",
                "seniority_level": "Junior",
                "linkedin_job_id": "test-job-003",
                "linkedin_url": "https://linkedin.com/jobs/test-003",
                "requires_english": False,
                "match_score": 0.78,
                "posted_date": datetime.now(),
                "is_active": True
            },
            {
                "title": "Platform Engineer - TEST",
                "company": "CloudSolutions",
                "location": "La Serena, Chile",
                "description": "Ingeniero de plataforma para arquitectura cloud. Trabajo 100% en español.",
                "requirements": "3+ años experiencia, GCP, Docker, Monitoring",
                "employment_type": "Contract",
                "seniority_level": "Mid-level",
                "linkedin_job_id": "test-job-004",
                "linkedin_url": "https://linkedin.com/jobs/test-004",
                "requires_english": False,
                "match_score": 0.82,
                "posted_date": datetime.now(),
                "is_active": True
            },
            {
                "title": "Infrastructure Engineer - TEST",
                "company": "DigitalChile",
                "location": "Temuco, Chile",
                "description": "Ingeniero de infraestructura para modernización tecnológica. Comunicación en español.",
                "requirements": "4+ años experiencia, VMware, Ansible, Networking",
                "employment_type": "Full-time", 
                "seniority_level": "Senior",
                "linkedin_job_id": "test-job-005",
                "linkedin_url": "https://linkedin.com/jobs/test-005",
                "requires_english": False,
                "match_score": 0.75,
                "posted_date": datetime.now(),
                "is_active": True
            }
        ]
        
        # Add test jobs to database
        created_jobs = []
        for job_data in test_jobs:
            job = Job(**job_data)
            db.add(job)
            created_jobs.append(job_data["title"])
        
        db.commit()
        
        return {
            "message": "Test data created successfully",
            "jobs_created": len(created_jobs),
            "job_titles": created_jobs
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating test data: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating test data: {str(e)}")