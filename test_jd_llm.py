import asyncio
import os
from sourceress.agents.jd_ingestor import JDIngestor


async def test_jd_with_llm():
    # Set up environment
    os.environ.setdefault("LLM_BACKEND", "openrouter")

    ingestor = JDIngestor()

    sample_jd = """
    About the job
    Isomorphic Labs is applying frontier AI to help unlock deeper scientific insights, faster breakthroughs, and life-changing medicines with an ambition to solve all disease.
    
    The future is coming. A future enabled and enriched by the incredible power of machine learning. A future in which diseases are curtailed or cured starting with better and faster drug discovery.

    Come and be part of an interdisciplinary team driving groundbreaking innovation and play a meaningful role in contributing towards us achieving our ambitious goals, while being a part of an inspiring and collaborative culture.

    The world we want tomorrow is the one we’re building today. It starts with the culture at this company. It starts with you.

    About Iso

    Isomorphic Labs (IsoLabs) was launched in 2021 to advance human health by building on and beyond the Nobel-winning AlphaFold system. Since then, our interdisciplinary team of drug discovery experts and machine learning specialists has built powerful new predictive and generative AI models that accelerate scientific discovery at digital speed.

    Our name comes from the belief that there is an underlying symmetry between biology and information science. By harnessing AI’s powerful capabilities, we can use it to model complex biological phenomena to help design novel molecules, anticipate how drugs will perform and develop innovative medicines to treat and cure some of the world’s most devastating diseases.

    We have built a world-leading drug design engine comprising AI models that are capable of working across multiple therapeutic areas and drug modalities. We are continually innovating on model architecture and developing cutting-edge capabilities to advance rational drug design.

    Every day, and with each new breakthrough, we’re getting closer to the promise of digital biology, and achieving our ambitious mission to one day solve all disease with the help of AI.

    Software Engineer (ML Research Engineering)

    We are looking for engineers with different levels of experience - Mid through to Senior, Principal, Staff or equivalent levels.

    Your impact 

    This is an exciting opportunity for you to work on a greenfield ML-based software platform that will transform the biopharmaceutical world as we know it.

    Working in a highly creative, iterative environment, you will be partnering with leading engineers, scientists and ML researchers to build the critical platform driving that transformation. This is a newly created role and you will need to use your previous experience and show initiative in order to fully carve out your contribution.

    What You Will Do

    Partner with the ML Research, Drug Design, and Data Engineering teams to design, develop, train, and evaluate a variety of cutting edge ML models at unprecedented scale. 
    Build a world-class ML drug design research environment with scalable software and libraries. 
    Develop tools and libraries to enable large-scale machine learning experiments across thousands of accelerators. 
    Maximise model performance, scalability, and robustness for production use within our computational platform. 
    Create novel instrumental drug discovery tools in partnership with domain experts. Take end-to-end ownership from rapid prototyping to production-quality code. 
    Iterate collaboratively with scientists and domain experts to deeply understand feature requirements and user feedback. 

    Essential

    Skills and qualifications 

    Strong experience with developing large-scale machine learning models. 
    Extensive programming experience using any mainstream programming languages, including strong Python experience. 
    Experience with modern ML frameworks including at least one of JAX, PyTorch or TensorFlow. 
    Experience with the full ML research and development lifecycle. 
    Experience partnering with research and product teams to prototype and ideally productionise ML models. 
    Strong software engineering experience with software design / architecture skills. 
    Strong understanding of ML theory and applications. 
    Strong understanding of data structures and algorithms. 
    Either a Bachelor’s degree in Computer Science, a related technical field, or equivalent practical experience. 

    Nice to have

    Interest in chemistry and biology. 
    Experience working with biomedical data. 
    Knowledge of the pharmaceutical industry, ideally with a focus on drug discovery. 
    Experience developing user facing production code. 

    Culture and values

    We are guided by our shared values. It's not about finding people who think and act in the same way. These values help to guide our work and will continue to strengthen it.

    Thoughtful

    Thoughtful at Iso is about curiosity, creativity and care. It is about good people doing good, rigorous and future-making science every single day.

    Brave

    Brave at Iso is about fearlessness, but it’s also about initiative and integrity. The scale of the challenge demands nothing less.

    Determined

    Determined at Iso is the way we pursue our goal. It’s a confidence in our hypothesis, as well as the urgency and agility needed to deliver on it. Because disease won’t wait, so neither should we.

    Together

    Together at Iso is about connection, collaboration across fields and catalytic relationships. It’s knowing that transformation is a group project, and remembering that what we’re doing will have a real impact on real people everywhere.

    Creating An Extraordinary Company

    We believe that to be successful we need a team with a range of skills and talents. We're building an environment where collaboration is fundamental, learning is shared and every employee feels supported and able to thrive. We value unique experiences, knowledge, backgrounds, and perspectives, and harness these qualities to create extraordinary impact.

    We are committed to equal employment opportunities regardless of sex, race, religion or belief, ethnic or national origin, disability, age, citizenship, marital, domestic or civil partnership status, sexual orientation, gender identity, pregnancy or related condition (including breastfeeding) or any other basis protected by applicable law. If you have a disability or additional need that requires accommodation, please do not hesitate to let us know.

    Hybrid working

    It’s hugely important for us to share knowledge and build strong relationships with each other, and we find it easier to do this if we spend time together in person. This is why we follow a hybrid model, and would require you to be able to come into the office 3 days a week (currently Tuesday, Wednesday, and one other day depending on which team you’re in). If you have additional needs that would prevent you from following this hybrid approach, we’d be happy to talk through these if you’re selected for an initial screening call.
    """

    try:
        print("🔍 Parsing job description with LLM...")
        result = await ingestor.run(sample_jd)

        print("\n✅ JD Ingestor Results:")
        print(f"Title: {result.job_description.title}")
        print(f"Must Haves: {result.job_description.must_haves}")
        print(f"Nice to Haves: {result.job_description.nice_to_haves}")
        print(f"Seniority: {result.job_description.seniority}")
        print(f"Location: {result.job_description.location}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_jd_with_llm())
