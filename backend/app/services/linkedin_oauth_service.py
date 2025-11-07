"""
LinkedIn OAuth Service
Servicio para autenticación OAuth con LinkedIn usando Google OAuth
"""

import os
import logging
import secrets
import json
from typing import Dict, Optional
from datetime import datetime, timedelta
from authlib.integrations.requests_client import OAuth2Session
import requests

logger = logging.getLogger(__name__)

class LinkedInOAuthService:
    """Service for LinkedIn OAuth authentication"""
    
    def __init__(self):
        # LinkedIn OAuth endpoints
        self.authorization_base_url = 'https://www.linkedin.com/oauth/v2/authorization'
        self.token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        self.profile_url = 'https://api.linkedin.com/v2/userinfo'
        self.jobs_url = 'https://api.linkedin.com/rest/jobSearches'
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # OAuth credentials from environment
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI', 'http://localhost:3000/auth/linkedin/callback')
        
        # Check if credentials are configured
        self.credentials_configured = bool(self.client_id and self.client_secret and 
                                         self.client_id != 'your_linkedin_app_id')
        
        # OAuth scopes for job search
        self.scope = ['openid', 'profile', 'email', 'w_member_social']
        
        self.access_token = None
        self.token_expires_at = None
        
    def get_authorization_url(self) -> Dict[str, str]:
        """
        Get LinkedIn OAuth authorization URL
        """
        # Check if credentials are configured
        if not self.credentials_configured:
            return {
                'error': 'LinkedIn OAuth not configured. Please run setup_linkedin_oauth.py',
                'authorization_url': None,
                'state': None,
                'setup_instructions': [
                    "1. Ejecuta: python setup_linkedin_oauth.py",
                    "2. Sigue las instrucciones para crear una LinkedIn App",
                    "3. Configura las variables de entorno",
                    "4. Reinicia la aplicación"
                ]
            }
        
        try:
            # Generate state for CSRF protection
            state = secrets.token_urlsafe(32)
            
            # Create OAuth2 session
            linkedin = OAuth2Session(
                client_id=self.client_id,
                redirect_uri=self.redirect_uri,
                scope=self.scope
            )
            
            authorization_url, state = linkedin.create_authorization_url(
                self.authorization_base_url,
                state=state
            )
            
            logger.info("✅ Authorization URL generated successfully")
            
            return {
                'authorization_url': authorization_url,
                'state': state,
                'instructions': [
                    "1. Abre esta URL en tu navegador",
                    "2. Autoriza la aplicación en LinkedIn", 
                    "3. Copia el código de autorización de la URL de retorno",
                    "4. Usa el código para obtener el token de acceso"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating authorization URL: {e}")
            return {
                'error': str(e),
                'authorization_url': None,
                'state': None
            }
    
    def get_access_token_from_code(self, authorization_code: str, state: str) -> Dict:
        """
        Exchange authorization code for access token
        """
        try:
            # Create OAuth2 session
            linkedin = OAuth2Session(
                client_id=self.client_id,
                redirect_uri=self.redirect_uri
            )
            
            # Exchange code for token
            token = linkedin.fetch_token(
                self.token_url,
                authorization_response=f"{self.redirect_uri}?code={authorization_code}&state={state}",
                client_secret=self.client_secret
            )
            
            self.access_token = token['access_token']
            self.token_expires_at = datetime.utcnow() + timedelta(seconds=token.get('expires_in', 3600))
            
            logger.info("✅ Access token obtained successfully")
            
            return {
                'success': True,
                'access_token': self.access_token,
                'expires_in': token.get('expires_in', 3600),
                'message': 'Authentication successful'
            }
            
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to get access token'
            }
    
    def get_user_profile(self) -> Dict:
        """
        Get user profile information
        """
        if not self.access_token:
            return {
                'success': False,
                'error': 'No access token available',
                'profile': None
            }
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(self.profile_url, headers=headers)
            response.raise_for_status()
            
            profile_data = response.json()
            
            logger.info(f"✅ Profile retrieved: {profile_data.get('name', 'Unknown')}")
            
            return {
                'success': True,
                'profile': {
                    'name': profile_data.get('name', ''),
                    'email': profile_data.get('email', ''),
                    'picture': profile_data.get('picture', ''),
                    'linkedin_id': profile_data.get('sub', '')
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {
                'success': False,
                'error': str(e),
                'profile': None
            }
    
    def search_jobs_oauth(self, keywords: str = "DevOps", location: str = "Chile", limit: int = 50) -> Dict:
        """
        Search jobs using LinkedIn API with OAuth token
        """
        if not self.access_token:
            logger.warning("No access token available, using sample data")
            return self._generate_oauth_sample_jobs(keywords, location, limit)
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'LinkedIn-Version': '202304'
            }
            
            # LinkedIn Job Search API parameters
            params = {
                'keywords': keywords,
                'locationFallback': location,
                'count': min(limit, 50),  # LinkedIn API limit
                'start': 0
            }
            
            response = requests.get(self.jobs_url, headers=headers, params=params)
            
            if response.status_code == 200:
                jobs_data = response.json()
                processed_jobs = self._process_linkedin_jobs_oauth(jobs_data)
                
                logger.info(f"✅ Found {len(processed_jobs)} jobs via LinkedIn OAuth API")
                
                return {
                    'success': True,
                    'jobs_found': len(processed_jobs),
                    'jobs': processed_jobs,
                    'source': 'linkedin_oauth_api'
                }
            else:
                logger.warning(f"LinkedIn API returned status {response.status_code}")
                return self._generate_oauth_sample_jobs(keywords, location, limit)
                
        except Exception as e:
            logger.error(f"Error searching jobs via OAuth: {e}")
            return self._generate_oauth_sample_jobs(keywords, location, limit)
    
    def _process_linkedin_jobs_oauth(self, jobs_data: Dict) -> list:
        """Process job data from LinkedIn OAuth API response"""
        processed_jobs = []
        
        try:
            elements = jobs_data.get('elements', [])
            
            for job in elements:
                try:
                    job_info = {
                        'title': job.get('title', 'DevOps Engineer'),
                        'company': job.get('companyName', 'Tech Company'),
                        'location': job.get('location', 'Chile'),
                        'description': job.get('description', 'DevOps position with modern technologies')[:500],
                        'linkedin_job_id': str(job.get('jobPostingId', f"oauth_{int(datetime.utcnow().timestamp())}")),
                        'linkedin_url': job.get('jobPostingUrl', 'https://linkedin.com/jobs'),
                        'posted_date': datetime.utcnow(),
                        'salary_range': self._extract_salary_oauth(job),
                        'employment_type': job.get('employmentType', 'Full-time'),
                        'seniority_level': job.get('seniorityLevel', 'Mid Level'),
                        'requires_english': self._check_english_oauth(job)
                    }
                    
                    processed_jobs.append(job_info)
                    
                except Exception as e:
                    logger.error(f"Error processing individual job: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error processing jobs data: {e}")
            
        return processed_jobs
    
    def _extract_salary_oauth(self, job: Dict) -> Optional[str]:
        """Extract salary information from OAuth job data"""
        try:
            salary_info = job.get('salaryInsight', {})
            if salary_info:
                min_sal = salary_info.get('minSalary')
                max_sal = salary_info.get('maxSalary')
                currency = salary_info.get('currencyCode', 'CLP')
                
                if min_sal and max_sal:
                    return f"{currency} {min_sal:,} - {max_sal:,}"
            
            return None
        except Exception:
            return None
    
    def _check_english_oauth(self, job: Dict) -> bool:
        """Check if job requires English from OAuth data"""
        try:
            text_to_check = f"{job.get('title', '')} {job.get('description', '')}".lower()
            
            english_keywords = [
                'english', 'inglés', 'ingles', 'native english', 'fluent english',
                'english speaking', 'english proficiency', 'bilingual',
                'international team', 'global team', 'multinational'
            ]
            
            return any(keyword in text_to_check for keyword in english_keywords)
            
        except Exception:
            return False
    
    def _generate_oauth_sample_jobs(self, keywords: str, location: str, limit: int) -> Dict:
        """Generate sample jobs when OAuth API is not available"""
        logger.warning("Generating OAuth sample data (API not available)")
        
        sample_jobs = [
            {
                'title': 'Senior DevOps Engineer (OAuth)',
                'company': 'TechCorp OAuth',
                'location': location,
                'description': f'OAuth authenticated search for {keywords}. AWS, Kubernetes, CI/CD pipelines.',
                'linkedin_job_id': f'oauth_sample_1_{int(datetime.utcnow().timestamp())}',
                'linkedin_url': 'https://linkedin.com/jobs/view/oauth1',
                'posted_date': datetime.utcnow() - timedelta(days=1),
                'salary_range': 'CLP 3,000,000 - 4,200,000',
                'employment_type': 'Full-time',
                'seniority_level': 'Senior',
                'requires_english': False
            },
            {
                'title': 'Cloud Platform Engineer (OAuth)',
                'company': 'StartupTech OAuth',
                'location': location,
                'description': f'OAuth {keywords} position. Terraform, Docker, microservices architecture.',
                'linkedin_job_id': f'oauth_sample_2_{int(datetime.utcnow().timestamp())}',
                'linkedin_url': 'https://linkedin.com/jobs/view/oauth2',
                'posted_date': datetime.utcnow() - timedelta(days=2),
                'salary_range': 'CLP 2,500,000 - 3,500,000',
                'employment_type': 'Full-time',
                'seniority_level': 'Mid Level',
                'requires_english': False
            },
            {
                'title': 'Infrastructure Automation Specialist (OAuth)',
                'company': 'FinTech OAuth',
                'location': location,
                'description': f'OAuth authenticated {keywords} role. GitOps, monitoring, security.',
                'linkedin_job_id': f'oauth_sample_3_{int(datetime.utcnow().timestamp())}',
                'linkedin_url': 'https://linkedin.com/jobs/view/oauth3',
                'posted_date': datetime.utcnow() - timedelta(days=3),
                'salary_range': 'CLP 3,200,000 - 4,500,000',
                'employment_type': 'Full-time',
                'seniority_level': 'Senior',
                'requires_english': False
            }
        ]
        
        # Limit to requested number
        sample_jobs = sample_jobs[:limit]
        
        return {
            'success': True,
            'jobs_found': len(sample_jobs),
            'jobs': sample_jobs,
            'source': 'oauth_sample_data'
        }

# Utility functions
def create_oauth_service() -> LinkedInOAuthService:
    """Create and return LinkedIn OAuth service instance"""
    return LinkedInOAuthService()

def get_linkedin_auth_url() -> Dict:
    """Get LinkedIn authorization URL for OAuth flow"""
    service = create_oauth_service()
    return service.get_authorization_url()