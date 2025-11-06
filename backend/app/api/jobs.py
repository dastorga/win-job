from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.database import get_db
from app.models.models import Job, JobApplication
from app.services.linkedin_scraper import scrape_linkedin_jobs
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