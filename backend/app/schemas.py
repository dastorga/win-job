from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Job-related schemas
class JobBase(BaseModel):
    title: str
    company: str
    location: str
    description: str
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    seniority_level: Optional[str] = None
    linkedin_job_id: Optional[str] = None
    linkedin_url: Optional[str] = None
    requires_english: bool = False
    match_score: float = 0.0

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_range: Optional[str] = None
    employment_type: Optional[str] = None
    seniority_level: Optional[str] = None
    requires_english: Optional[bool] = None
    match_score: Optional[float] = None
    is_active: Optional[bool] = None

class JobResponse(JobBase):
    id: int
    posted_date: Optional[datetime]
    scraped_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# User-related schemas
class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Job Application schemas
class JobApplicationBase(BaseModel):
    job_id: int
    status: str = "interested"
    notes: Optional[str] = None

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class JobApplicationResponse(JobApplicationBase):
    id: int
    user_id: int
    applied_at: datetime
    job: JobResponse

    class Config:
        from_attributes = True

# Scraping schemas
class ScrapeJobsRequest(BaseModel):
    search_term: str = "DevOps"
    location: str = "España"
    max_jobs: int = 50

class ScrapeJobsResponse(BaseModel):
    success: bool
    jobs_found: int
    jobs_saved: int
    jobs_without_english: int
    message: str

# Statistics schemas
class JobStats(BaseModel):
    total_jobs: int
    jobs_without_english: int
    english_percentage: float
    top_companies: List[dict]
    top_locations: List[dict]

# Pagination
class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 20

# Search and filter schemas
class JobSearchParams(PaginationParams):
    search: Optional[str] = None
    no_english: Optional[bool] = None
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    seniority_level: Optional[str] = None