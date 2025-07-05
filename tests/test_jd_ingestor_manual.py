import asyncio
from sourceress.agents.jd_ingestor import JDIngestor

async def test_manual():
    ingestor = JDIngestor()
    
    sample_jd = """
    Senior Data Scientist - San Francisco
    
    We need a data scientist with:
    - Python, pandas, scikit-learn
    - 5+ years experience
    - PhD preferred
    
    Location: San Francisco, CA
    """
    
    try:
        result = await ingestor.run(sample_jd)
        print(f"Title: {result.job_description.title}")
        print(f"Must haves: {result.job_description.must_haves}")
        print(f"Nice to haves: {result.job_description.nice_to_haves}")
        print(f"Location: {result.job_description.location}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_manual())
