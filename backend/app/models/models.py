from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with job applications
    job_applications = relationship("JobApplication", back_populates="user")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)
    location = Column(String)
    description = Column(Text)
    requirements = Column(Text)
    salary_range = Column(String)
    employment_type = Column(String)  # Full-time, Part-time, Contract, etc.
    seniority_level = Column(String)  # Entry, Mid, Senior, etc.
    
    # LinkedIn specific fields
    linkedin_job_id = Column(String, unique=True, index=True)
    linkedin_url = Column(String)
    
    # Analysis fields
    requires_english = Column(Boolean, default=False)
    match_score = Column(Float, default=0.0)
    
    # Metadata
    posted_date = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    job_applications = relationship("JobApplication", back_populates="job")

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    status = Column(String, default="interested")  # interested, applied, rejected, etc.
    notes = Column(Text)
    applied_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="job_applications")
    job = relationship("Job", back_populates="job_applications")

class ScrapeLog(Base):
    __tablename__ = "scrape_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    search_term = Column(String, nullable=False)
    location = Column(String)
    jobs_found = Column(Integer, default=0)
    jobs_saved = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)