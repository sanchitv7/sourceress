# Sourceress – MVP Implementation Plan

> Date: 2025-01-04 (Slice-Based Development)

A comprehensive slice-based development plan to build a working CrewAI-orchestrated talent acquisition system. Each slice delivers working end-to-end functionality.

---

## 🎯 MVP Goal

**Get a working CrewAI-orchestrated system**: JD text in → Excel file out, with proper Task-based agent coordination.

**Current State**: ✅ **Foundation Complete** - Models, CrewAI tasks, agent architecture, and orchestration are implemented  
**Next Step**: Implement real logic in agents through focused slices

---

## 📊 Current Foundation Status

### ✅ **COMPLETED Infrastructure**
- ✅ **Pydantic Models** - All data structures with validation (`models.py`)
- ✅ **CrewAI Tasks** - Task definitions with dependencies (`tasks.py`) 
- ✅ **Agent Architecture** - BaseAgent with retry logic, all agent roles/backstories defined
- ✅ **CrewAI Orchestration** - Crew coordination replacing manual chaining (`workflows.py`)
- ✅ **Utils Infrastructure** - LinkedIn auth, scraping utilities, LLM abstraction
- ✅ **Testing Framework** - Unit tests, integration tests, manual test scripts

### ⚠️ **NEEDS Implementation** (Real Logic)
- ⚠️ **LinkedIn Sourcer** - Connect to real scraping (currently dummy data)
- ⚠️ **Relevance Scorer** - Implement embedding-based scoring (currently dummy scores)
- ⚠️ **Key Matcher** - Add semantic similarity matching (currently dummy matches)
- ⚠️ **Pitch Generator** - LLM-powered personalization (currently templates)
- ⚠️ **Excel Writer** - Populate real data and formatting (basic structure done)

---

## 🎯 Slice-Based Development Plan

### **Slice 1: LinkedIn Sourcing Pipeline** 
**Goal**: JD text → Real LinkedIn profiles → Basic Excel output  
**Duration**: 3-4 days  
**Deliverable**: Demo real candidate sourcing from actual LinkedIn searches

#### Implementation Tasks:
- [ ] **Fix `fetch_profiles` in `linkedin_api.py`** (2-3 hours)
  - Connect to real `search_linkedin_async` from scraping utils
  - Convert raw scraping data to `CandidateProfile` objects  
  - Add proper error handling and logging
  - Test with sample job descriptions

- [ ] **Update `LinkedInSourcer` agent** (1-2 hours)
  - Replace dummy data with real `fetch_profiles` call
  - Build search query from `JobDescription` (title + must_haves)
  - Handle LinkedIn rate limiting and authentication
  - Return `SourcingResult` with real profiles

- [ ] **Complete basic Excel output** (1-2 hours)
  - Populate real candidate names, URLs, titles, locations
  - Basic formatting with headers and freeze panes
  - Handle empty results gracefully

- [ ] **End-to-end validation** (1 hour)
  - Test: Real JD → LinkedIn search → Excel with actual profiles
  - Verify CrewAI orchestration works with real data
  - Check LinkedIn authentication and scraping

#### Success Criteria:
- ✅ Input real job description → Output Excel with 5-15 real LinkedIn profiles
- ✅ CrewAI pipeline runs without dummy data
- ✅ LinkedIn scraping works reliably
- ✅ Demonstrable to others: "Look, it actually finds candidates!"

---

### **Slice 2: Candidate Relevance Scoring**
**Goal**: Add intelligent ranking to candidate results  
**Duration**: 4-5 days  
**Deliverable**: Excel output with scored and ranked candidates

#### Implementation Tasks:
- [ ] **Implement embedding-based scoring** (2-3 hours)
  - Add OpenAI `text-embedding-3-small` or sentence-transformers  
  - Encode JD requirements and candidate skills/summaries
  - Compute cosine similarity scores (0-100 range)
  - Weight must-haves vs nice-to-haves appropriately

- [ ] **Update `RelevanceScorer` agent** (1-2 hours)
  - Replace dummy scoring with real embedding logic
  - Populate `feature_weights` for transparency  
  - Return top candidates sorted by score
  - Add score confidence and reasoning

- [ ] **Enhance Excel output** (1-2 hours)
  - Add "Match Score" column with conditional formatting
  - Sort candidates by relevance score
  - Add "Match Reasons" column showing key factors
  - Color-code high/medium/low scores

- [ ] **Scoring validation** (1 hour)
  - Test with diverse job descriptions
  - Verify senior developers score higher than junior
  - Check that required skills boost scores appropriately

#### Success Criteria:
- ✅ Candidates ranked by actual relevance to job requirements
- ✅ Scores make intuitive sense (Python experts score high for Python roles)
- ✅ Excel shows scores with visual formatting
- ✅ Demonstrable: "Look how it ranks the best candidates first!"

---

### **Slice 3: Requirement Matching & Evidence**
**Goal**: Show specific matches between job requirements and candidate qualifications  
**Duration**: 3-4 days  
**Deliverable**: Excel with detailed requirement-evidence matching

#### Implementation Tasks:
- [ ] **Implement semantic matching** (2-3 hours)
  - Add spaCy (`en_core_web_lg`) for tokenization
  - Use Sentence-Transformers (`all-miniLM-L6-v2`) for similarity
  - Match JD requirements to candidate evidence above threshold (0.75)
  - Extract most representative candidate sentences as evidence

- [ ] **Update `KeyMatcher` agent** (1-2 hours)
  - Replace dummy matching with real similarity logic
  - Process each requirement against candidate profiles
  - Return structured `KeyMatchResult` with evidence
  - Handle cases where no good matches found

- [ ] **Enhanced Excel formatting** (1-2 hours)
  - Add "Key Matches" column with requirement → evidence pairs
  - Format as bullet points or structured text
  - Highlight strong matches vs weak matches
  - Add match confidence scores

- [ ] **Matching validation** (1 hour)
  - Test requirement matching accuracy
  - Verify evidence sentences are relevant
  - Check for false positives/negatives

#### Success Criteria:
- ✅ Clear mapping from job requirements to candidate evidence
- ✅ Evidence sentences are relevant and specific
- ✅ Excel shows why each candidate matches the role
- ✅ Demonstrable: "See exactly why this candidate fits each requirement!"

---

### **Slice 4: Personalized Pitch Generation**
**Goal**: Generate personalized outreach messages for each candidate  
**Duration**: 4-5 days  
**Deliverable**: Complete Excel with personalized cold call, LinkedIn DM, and WhatsApp messages

#### Implementation Tasks:
- [ ] **Design message templates** (1-2 hours)
  - Create Jinja2 templates for each channel (cold call, LinkedIn DM, WhatsApp)
  - Include placeholders for name, skills, company, role specifics
  - Different tone/length for each channel
  - A/B test template variations

- [ ] **Implement LLM-powered personalization** (2-3 hours)
  - Feed filled templates to GPT-4 via `async_chat`
  - Use temperature 0.3-0.7 for variation
  - Include candidate key matches in prompt context
  - Polish tone and add personal touches

- [ ] **Update `PitchGenerator` agent** (1-2 hours)
  - Replace template messages with LLM-generated content
  - Use key matches to personalize messaging
  - Track token usage and optimize costs
  - Handle LLM failures gracefully

- [ ] **Complete Excel output** (1-2 hours)
  - Add columns for all three message types
  - Format messages for readability
  - Add character counts for each channel
  - Implement copy-paste friendly formatting

#### Success Criteria:
- ✅ Personalized messages that mention specific candidate skills/experience
- ✅ Different tone/style for each communication channel
- ✅ Messages sound natural and recruiter-like
- ✅ Demonstrable: "These messages are better than what I write manually!"

---

### **Slice 5: Polish & Production Ready**
**Goal**: Production-ready system with performance optimization and advanced features  
**Duration**: 3-4 days  
**Deliverable**: Polished system ready for daily use

#### Implementation Tasks:
- [ ] **Performance optimization** (1-2 hours)
  - Optimize to meet <5 minute pipeline target
  - Add caching for expensive operations (embeddings, LLM calls)
  - Implement parallel processing where safe
  - Monitor and log performance metrics

- [ ] **Advanced Excel formatting** (1-2 hours)
  - Add hidden sheet with raw résumé text for reference
  - Implement conditional formatting for scores (green gradient)
  - Auto-fit column widths and professional styling
  - Add filters and sorting capabilities

- [ ] **Error handling & reliability** (1-2 hours)
  - Robust handling of LinkedIn rate limits
  - Graceful degradation when LLM APIs fail
  - Better error messages and user guidance
  - Resume capability for interrupted pipelines

- [ ] **Advanced testing & validation** (1 hour)
  - End-to-end tests with real data
  - Performance testing with 20+ candidates
  - Edge case testing (empty results, API failures)
  - 80%+ test coverage verification

#### Success Criteria:
- ✅ Complete pipeline in <5 minutes for 10-20 candidates
- ✅ Professional Excel output ready for client presentation
- ✅ Reliable operation even with API issues
- ✅ Ready for daily production use

---

## 🚀 Implementation Timeline

### **Week 1: Foundation → Working Sourcer**
```bash
Day 1-2: Slice 1 implementation (LinkedIn sourcing)
Day 3: End-to-end testing and bug fixes
Day 4-5: Slice 2 setup (embedding infrastructure)
```

### **Week 2: Intelligent Ranking**  
```bash
Day 1-2: Slice 2 completion (relevance scoring)
Day 3: Testing and score validation
Day 4-5: Slice 3 setup (semantic matching)
```

### **Week 3: Smart Matching**
```bash
Day 1-2: Slice 3 completion (requirement matching)
Day 3: Testing and validation
Day 4-5: Slice 4 setup (LLM templates)
```

### **Week 4: Personalized Messaging**
```bash
Day 1-3: Slice 4 completion (pitch generation)
Day 4-5: Slice 5 (polish and optimization)
```

---

## 🎯 Success Criteria & KPIs

### **Per-Slice Validation**
- **Slice 1**: Can demo real LinkedIn candidates from job description
- **Slice 2**: Rankings make intuitive sense to domain experts
- **Slice 3**: Evidence clearly supports each match claim
- **Slice 4**: Messages sound natural and personalized
- **Slice 5**: System runs reliably in production conditions

### **Final MVP Targets**
- ✅ Complete pipeline: JD text → Excel file in <5 minutes
- ✅ Process 10-20 candidates successfully per run
- ✅ Generate readable, professional Excel output
- ✅ 80%+ test coverage with both unit and integration tests
- ✅ Reliable LinkedIn scraping without rate limit issues
- ✅ LLM-generated content quality acceptable for recruiter use

---

## 🔧 Technical Implementation Details

### **Core Tech Stack** 
- **Python 3.11+** with modern async/await patterns
- **CrewAI** for multi-agent orchestration (foundation complete ✅)
- **OpenAI API** for embeddings (`text-embedding-3-small`) and LLM (`gpt-4`)
- **undetected-chromedriver** for LinkedIn scraping (authentication complete ✅)
- **Pandas + OpenPyXL** for Excel generation and formatting
- **sentence-transformers** for semantic similarity (alternative to OpenAI)
- **spaCy** for natural language processing and tokenization
- **Jinja2** for templating personalized messages

### **Environment Setup**
```bash
# Required environment variables
OPENAI_API_KEY=your_key_here              # For embeddings and LLM
LLM_BACKEND=openai                        # or huggingface/openrouter  
LINKEDIN_SESSION_FILE=.linkedin_session   # Session persistence
```

### **Development Workflow Per Slice**
1. **Implement** core logic for the slice
2. **Test** with real data and edge cases  
3. **Validate** output quality and performance
4. **Demo** functionality to stakeholders
5. **Refactor** based on learnings before next slice

---

## 🚀 Future Enhancements (Post-MVP)

### **Advanced Features**
- [ ] **Agent Tools** - Specialized tools for each agent type
- [ ] **Memory & Context** - Cross-agent learning and pattern storage  
- [ ] **Advanced Orchestration** - Parallel processing, worker pools
- [ ] **Quality Verification** - Review agents and consistency checking
- [ ] **Human-in-the-Loop** - Review points and feedback integration
- [ ] **Performance Analytics** - Success rate tracking, A/B testing
- [ ] **Multi-Platform Sourcing** - GitHub, Stack Overflow, company websites
- [ ] **CRM Integration** - Export to ATS systems, lead tracking
- [ ] **Advanced ML Models** - Custom relevance models, candidate scoring

### **Scaling Considerations**
- [ ] **Database Storage** - Replace in-memory processing
- [ ] **API Rate Management** - LinkedIn, OpenAI quota optimization
- [ ] **Distributed Processing** - Handle larger candidate volumes
- [ ] **UI/UX Interface** - Web dashboard for non-technical users
- [ ] **Enterprise Features** - Team collaboration, approval workflows
