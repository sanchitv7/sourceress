import asyncio
import os
from sourceress.agents.jd_ingestor import JDIngestor
from sourceress.agents.linkedin_sourcer import LinkedInSourcer

async def test_linkedin_sourcer():
    # Set up environment
    os.environ.setdefault("LLM_BACKEND", "openrouter")
    
    # First, parse a JD
    ingestor = JDIngestor()
    
    sample_jd = """
    Senior Python Developer - Remote
    
    We're looking for a talented Python developer to join our team:
    
    Must Have:
    - 3+ years of Python development experience
    - Experience with Django or FastAPI frameworks
    - Knowledge of SQL databases (PostgreSQL preferred)
    - Git version control experience
    
    Nice to Have:
    - AWS or cloud platform experience
    - Docker containerization
    - CI/CD pipeline experience
    - Machine learning basics
    
    Location: Remote (US-based)
    Seniority: Mid to Senior level
    """
    
    try:
        print("🔍 Step 1: Parsing job description...")
        jd_result = await ingestor.run(sample_jd)
        print(f"✅ JD parsed: {jd_result.job_description.title}")
        
        print("\n🔍 Step 2: Testing LinkedIn sourcing...")
        sourcer = LinkedInSourcer()
        sourcing_result = await sourcer.run(jd_result.job_description)
        
        print(f"✅ LinkedIn sourcing complete!")
        print(f"Found {len(sourcing_result.candidates)} candidates")
        
        if sourcing_result.candidates:
            print("\n📋 Sample candidates:")
            for i, candidate in enumerate(sourcing_result.candidates[:3]):  # Show first 3
                print(f"  {i+1}. {candidate.name} - {candidate.title}")
                print(f"     Location: {candidate.location}")
                print(f"     URL: {candidate.linkedin_url}")
                print()
        else:
            print("❌ No candidates found - LinkedIn sourcing may not be working")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_linkedin_sourcer())
