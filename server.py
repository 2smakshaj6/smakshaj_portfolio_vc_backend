from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime
from bson import ObjectId
from typing import List, Optional
import json

# Import models
from models.portfolio import Portfolio, PortfolioCreate, PortfolioUpdate, PersonalInfo, Stat
from models.experience import Experience, ExperienceCreate, ExperienceUpdate
from models.project import Project, ProjectCreate, ProjectUpdate
from models.skill import Skill, SkillCreate, SkillUpdate
from models.education import Education, EducationCreate, EducationUpdate
from models.certification import Certification, CertificationCreate, CertificationUpdate

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'portfolio_db')]

# Create the main app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Utility function to convert ObjectId to string in responses
def parse_json(data):
    return json.loads(json.dumps(data, default=str))

# Helper function to get portfolio by userId
async def get_portfolio_by_user_id(user_id: str):
    portfolio = await db.portfolios.find_one({"userId": user_id})
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

# ROOT ENDPOINT
@api_router.get("/")
async def root():
    return {"message": "Portfolio API is running"}

# PORTFOLIO ENDPOINTS
@api_router.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    """Get complete portfolio data for a user"""
    try:
        # Get main portfolio
        portfolio = await get_portfolio_by_user_id(user_id)
        portfolio_id = portfolio["_id"]
        
        # Get all related data
        experience = await db.experience.find({"portfolioId": portfolio_id}).sort("order", 1).to_list(100)
        projects = await db.projects.find({"portfolioId": portfolio_id}).sort("order", 1).to_list(100)
        skills = await db.skills.find({"portfolioId": portfolio_id}).sort("order", 1).to_list(100)
        education = await db.education.find({"portfolioId": portfolio_id}).sort("order", 1).to_list(100)
        certifications = await db.certifications.find({"portfolioId": portfolio_id}).sort("order", 1).to_list(100)
        
        result = {
            "portfolio": parse_json(portfolio),
            "experience": parse_json(experience),
            "projects": parse_json(projects),
            "skills": parse_json(skills),
            "education": parse_json(education),
            "certifications": parse_json(certifications)
        }
        
        return result
    except HTTPException:
        # Re-raise HTTPException to preserve status code
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/portfolio")
async def create_portfolio(portfolio_data: PortfolioCreate):
    """Create a new portfolio"""
    try:
        # Check if portfolio already exists
        existing = await db.portfolios.find_one({"userId": portfolio_data.userId})
        if existing:
            raise HTTPException(status_code=400, detail="Portfolio already exists for this user")
        
        portfolio = Portfolio(**portfolio_data.dict())
        result = await db.portfolios.insert_one(portfolio.dict(by_alias=True))
        
        created_portfolio = await db.portfolios.find_one({"_id": result.inserted_id})
        return parse_json(created_portfolio)
    except Exception as e:
        logger.error(f"Error creating portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/portfolio/{user_id}")
async def update_portfolio(user_id: str, update_data: PortfolioUpdate):
    """Update portfolio basic info"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updatedAt"] = datetime.utcnow()
        
        await db.portfolios.update_one(
            {"_id": portfolio["_id"]}, 
            {"$set": update_dict}
        )
        
        updated_portfolio = await db.portfolios.find_one({"_id": portfolio["_id"]})
        return parse_json(updated_portfolio)
    except Exception as e:
        logger.error(f"Error updating portfolio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# EXPERIENCE ENDPOINTS
@api_router.get("/portfolio/{user_id}/experience")
async def get_experience(user_id: str):
    """Get all experience for a user"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        experience = await db.experience.find({"portfolioId": portfolio["_id"]}).sort("order", 1).to_list(100)
        return parse_json(experience)
    except Exception as e:
        logger.error(f"Error getting experience: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/portfolio/{user_id}/experience")
async def create_experience(user_id: str, experience_data: ExperienceCreate):
    """Add new experience"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        experience = Experience(
            portfolioId=portfolio["_id"],
            **experience_data.dict()
        )
        
        result = await db.experience.insert_one(experience.dict(by_alias=True))
        created_experience = await db.experience.find_one({"_id": result.inserted_id})
        return parse_json(created_experience)
    except Exception as e:
        logger.error(f"Error creating experience: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/portfolio/{user_id}/experience/{experience_id}")
async def update_experience(user_id: str, experience_id: str, update_data: ExperienceUpdate):
    """Update experience"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updatedAt"] = datetime.utcnow()
        
        result = await db.experience.update_one(
            {"_id": ObjectId(experience_id), "portfolioId": portfolio["_id"]},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Experience not found")
        
        updated_experience = await db.experience.find_one({"_id": ObjectId(experience_id)})
        return parse_json(updated_experience)
    except Exception as e:
        logger.error(f"Error updating experience: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/portfolio/{user_id}/experience/{experience_id}")
async def delete_experience(user_id: str, experience_id: str):
    """Delete experience"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        result = await db.experience.delete_one(
            {"_id": ObjectId(experience_id), "portfolioId": portfolio["_id"]}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Experience not found")
        
        return {"message": "Experience deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting experience: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# PROJECT ENDPOINTS
@api_router.get("/portfolio/{user_id}/projects")
async def get_projects(user_id: str):
    """Get all projects for a user"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        projects = await db.projects.find({"portfolioId": portfolio["_id"]}).sort("order", 1).to_list(100)
        return parse_json(projects)
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/portfolio/{user_id}/projects")
async def create_project(user_id: str, project_data: ProjectCreate):
    """Add new project"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        project = Project(
            portfolioId=portfolio["_id"],
            **project_data.dict()
        )
        
        result = await db.projects.insert_one(project.dict(by_alias=True))
        created_project = await db.projects.find_one({"_id": result.inserted_id})
        return parse_json(created_project)
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/portfolio/{user_id}/projects/{project_id}")
async def update_project(user_id: str, project_id: str, update_data: ProjectUpdate):
    """Update project"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updatedAt"] = datetime.utcnow()
        
        result = await db.projects.update_one(
            {"_id": ObjectId(project_id), "portfolioId": portfolio["_id"]},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        updated_project = await db.projects.find_one({"_id": ObjectId(project_id)})
        return parse_json(updated_project)
    except Exception as e:
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/portfolio/{user_id}/projects/{project_id}")
async def delete_project(user_id: str, project_id: str):
    """Delete project"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        result = await db.projects.delete_one(
            {"_id": ObjectId(project_id), "portfolioId": portfolio["_id"]}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {"message": "Project deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# SKILL ENDPOINTS
@api_router.get("/portfolio/{user_id}/skills")
async def get_skills(user_id: str):
    """Get all skills for a user"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        skills = await db.skills.find({"portfolioId": portfolio["_id"]}).sort("order", 1).to_list(100)
        return parse_json(skills)
    except Exception as e:
        logger.error(f"Error getting skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/portfolio/{user_id}/skills")
async def create_skill(user_id: str, skill_data: SkillCreate):
    """Add new skill category"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        skill = Skill(
            portfolioId=portfolio["_id"],
            **skill_data.dict()
        )
        
        result = await db.skills.insert_one(skill.dict(by_alias=True))
        created_skill = await db.skills.find_one({"_id": result.inserted_id})
        return parse_json(created_skill)
    except Exception as e:
        logger.error(f"Error creating skill: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/portfolio/{user_id}/skills/{skill_id}")
async def update_skill(user_id: str, skill_id: str, update_data: SkillUpdate):
    """Update skill category"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        update_dict["updatedAt"] = datetime.utcnow()
        
        result = await db.skills.update_one(
            {"_id": ObjectId(skill_id), "portfolioId": portfolio["_id"]},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        updated_skill = await db.skills.find_one({"_id": ObjectId(skill_id)})
        return parse_json(updated_skill)
    except Exception as e:
        logger.error(f"Error updating skill: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/portfolio/{user_id}/skills/{skill_id}")
async def delete_skill(user_id: str, skill_id: str):
    """Delete skill category"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        result = await db.skills.delete_one(
            {"_id": ObjectId(skill_id), "portfolioId": portfolio["_id"]}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Skill not found")
        
        return {"message": "Skill deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting skill: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# EDUCATION ENDPOINTS
@api_router.get("/portfolio/{user_id}/education")
async def get_education(user_id: str):
    """Get all education for a user"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        education = await db.education.find({"portfolioId": portfolio["_id"]}).sort("order", 1).to_list(100)
        return parse_json(education)
    except Exception as e:
        logger.error(f"Error getting education: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/portfolio/{user_id}/education")
async def create_education(user_id: str, education_data: EducationCreate):
    """Add new education"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        education = Education(
            portfolioId=portfolio["_id"],
            **education_data.dict()
        )
        
        result = await db.education.insert_one(education.dict(by_alias=True))
        created_education = await db.education.find_one({"_id": result.inserted_id})
        return parse_json(created_education)
    except Exception as e:
        logger.error(f"Error creating education: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# CERTIFICATION ENDPOINTS
@api_router.get("/portfolio/{user_id}/certifications")
async def get_certifications(user_id: str):
    """Get all certifications for a user"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        certifications = await db.certifications.find({"portfolioId": portfolio["_id"]}).sort("order", 1).to_list(100)
        return parse_json(certifications)
    except Exception as e:
        logger.error(f"Error getting certifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/portfolio/{user_id}/certifications")
async def create_certification(user_id: str, certification_data: CertificationCreate):
    """Add new certification"""
    try:
        portfolio = await get_portfolio_by_user_id(user_id)
        
        certification = Certification(
            portfolioId=portfolio["_id"],
            **certification_data.dict()
        )
        
        result = await db.certifications.insert_one(certification.dict(by_alias=True))
        created_certification = await db.certifications.find_one({"_id": result.inserted_id})
        return parse_json(created_certification)
    except Exception as e:
        logger.error(f"Error creating certification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# SEED DATA ENDPOINT (for initial setup)
@api_router.post("/seed-data")
async def seed_data():
    """Seed database with initial data from mock.js"""
    try:
        # Check if data already exists
        existing_portfolio = await db.portfolios.find_one({"userId": "akshaj"})
        if existing_portfolio:
            return {"message": "Data already exists", "portfolioId": str(existing_portfolio["_id"])}
        
        # Create main portfolio
        personal_info = PersonalInfo(
            name="Akshaj Shivara Madhusudhan",
            title="Building Safer Systems at the Intersection of Cybersecurity & AI",
            bio="I'm a cybersecurity professional passionate about building safer digital ecosystems through the strategic integration of AI and traditional security practices.",
            location="Buffalo, NY",
            email="akshaj@example.com",
            linkedin="https://linkedin.com/in/akshaj",
            github="https://github.com/akshaj"
        )
        
        stats = [
            Stat(value="3+", label="Years Experience", order=1),
            Stat(value="15+", label="Security Projects", order=2),
            Stat(value="8+", label="Certifications", order=3),
            Stat(value="2", label="Research Papers", order=4)
        ]
        
        portfolio = Portfolio(
            userId="akshaj",
            personalInfo=personal_info,
            stats=stats
        )
        
        portfolio_result = await db.portfolios.insert_one(portfolio.dict(by_alias=True))
        portfolio_id = portfolio_result.inserted_id
        
        # Add experience data
        experience_data = [
            {
                "role": "Cybersecurity Intern",
                "company": "Catenactio Inc",
                "location": "Los Angeles, CA",
                "period": "May 2024 – Present",
                "current": True,
                "highlights": [
                    "Tuned SIEM rules (Wazuh) to reduce false positives and improve threat detection across enterprise clients",
                    "Managed IAM (Okta) policies, automated provisioning/deprovisioning, and led user access reviews",
                    "Applied system hardening and patch management practices on Linux endpoints",
                    "Authored IR plans, playbooks, and security policy documents aligned with SOC 2, NIST 800-53, and CIS Controls",
                    "Researched integration of AI models for alert triage, contributing to early-stage automation"
                ],
                "skills": ["SIEM", "Wazuh", "IAM", "Okta", "Linux Hardening", "Incident Response", "SOC 2", "NIST 800-53"],
                "order": 1
            },
            {
                "role": "Research Assistant – AI Safety & Security",
                "company": "University at Buffalo",
                "location": "Buffalo, NY",
                "period": "Aug 2024 – Dec 2024",
                "current": False,
                "highlights": [
                    "Fine-tuned LLMs to detect adversarial prompts, hate speech, and toxic content",
                    "Prompt-engineered secure inputs and outputs to reduce hallucinations",
                    "Drafted internal guidelines for secure AI deployment and usage policies",
                    "Contributed to cutting-edge research on adversarial machine learning"
                ],
                "skills": ["LLM Fine-tuning", "Prompt Engineering", "AI Safety", "Python", "Machine Learning"],
                "order": 2
            },
            {
                "role": "Associate Software Engineer",
                "company": "Bosch Global Software Technologies",
                "location": "Bengaluru, IN",
                "period": "Jan 2023 – Jun 2023",
                "current": False,
                "highlights": [
                    "Developed and tested embedded automotive software in compliance with MISRA C standards",
                    "Supported integration of functional safety protocols with vehicle cybersecurity measures",
                    "Implemented secure coding practices for automotive control systems",
                    "Collaborated on automotive cybersecurity frameworks and security validation processes"
                ],
                "skills": ["Embedded Systems", "MISRA C", "Automotive Security", "Functional Safety"],
                "order": 3
            }
        ]
        
        for exp_data in experience_data:
            experience = Experience(portfolioId=portfolio_id, **exp_data)
            await db.experience.insert_one(experience.dict(by_alias=True))
        
        return {"message": "Database seeded successfully", "portfolioId": str(portfolio_id)}
        
    except Exception as e:
        logger.error(f"Error seeding data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)