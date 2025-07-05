# Sourceress – MVP Implementation Plan

> Date: 2025-01-04 (Simplified MVP Version)

A streamlined todo list to get the basic CrewAI system working quickly. Focus on core functionality first, advanced features later.

---

## 🎯 MVP Goal

**Get a working CrewAI-orchestrated system**: JD text in → Excel file out, with proper Task-based agent coordination.

**MVP Focus (Option A)**: Task definitions, Crew orchestration, agent collaboration, context passing.  
**What's NOT in MVP**: Advanced tools, memory, parallel processing, quality verification agents.

**Current Progress**: ✅ SourcingResult model fixed (no more Dict[str, Any] complexity)  
**Next Step**: Complete utils for LinkedIn scraping, then focus on CrewAI Task definitions

---

## 📋 MVP Tasks (11 Total) - Option A → Option B Progression

### Phase 1: Foundation (2 tasks)
- [x] **1. Basic Models** (`models.py`) ✅ COMPLETED
  - ✅ Replace `List[Dict[str, Any]]` with `List[CandidateProfile]` in `SourcingResult`
  - [ ] Add basic validation (optional validators for URLs, score ranges)
  - [ ] Test: All models validate correctly

- [ ] **2. Complete Utils** (`utils/scraping.py`, `utils/linkedin_api.py`)
  - Basic Playwright scraping (search + parse profiles)
  - Convert scraping results to `CandidateProfile` objects
  - Simple error handling

### Phase 2: Agents + Task Definitions (6 tasks)
- [ ] **3. JD Ingestor** (`agents/jd_ingestor.py`)
  - Add CrewAI role definition and backstory
  - Improve JSON extraction (keep existing fallback)
  - Return structured `JobDescription`

- [ ] **4. LinkedIn Sourcer** (`agents/linkedin_sourcer.py`)
  - Add CrewAI role definition and backstory
  - Use Playwright to scrape 10-20 profiles (not 50+)
  - Return `List[CandidateProfile]`

- [ ] **5. Relevance Scorer** (`agents/relevance_scorer.py`)
  - Add CrewAI role definition and backstory
  - Simple embedding-based scoring (OpenAI or sentence-transformers)
  - Return top 10 candidates with scores

- [ ] **6. Key Matcher** (`agents/key_matcher.py`)
  - Add CrewAI role definition and backstory
  - Basic requirement-to-evidence matching
  - Simple string matching with confidence scores

- [ ] **7. Pitch Generator** (`agents/pitch_generator.py`)
  - Add CrewAI role definition and backstory
  - Simple template-based messaging (3 channels)
  - Basic personalization with candidate name/skills

- [ ] **8. Task Definitions** (`tasks.py`) 🆕
  - Define CrewAI Task objects for each agent
  - Set up task dependencies and context passing
  - Define expected outputs and validation schemas

### Phase 3: CrewAI Orchestration (2 tasks)
- [ ] **9. Excel Writer** (`agents/excel_writer.py`)
  - Add CrewAI role definition and backstory
  - Complete workbook formatting with all columns
  - Basic conditional formatting for scores

- [ ] **10. CrewAI Integration** (`workflows.py`)
  - Replace manual chaining with `Crew` orchestration
  - Implement Task-based execution with context passing
  - Remove all manual `await agent.run()` calls
  - Add basic error handling and logging

### Phase 4: Validation (1 task)
- [ ] **11. Basic Testing** (`tests/`)
  - Unit tests for each agent (`test_agents.py`)
  - End-to-end CrewAI integration test (`test_workflow.py`)
  - Mock LLM responses for consistent testing

---

## 🚀 Future Enhancements (Option B Features)

### After MVP is Working:
- [ ] **Agent Tools** - Specialized tools for each agent type
- [ ] **Memory & Context** - Cross-agent learning and pattern storage  
- [ ] **Advanced Orchestration** - Parallel processing, worker pools
- [ ] **Quality Verification** - Review agents and consistency checking
- [ ] **Human-in-the-Loop** - Review points and feedback integration
- [ ] **Performance Optimization** - Caching, monitoring, analytics

---

## 🚀 Implementation Order

### Week 1: Foundation
```bash
# Get the basics working
✅ Task 1: Update models.py (SourcingResult fixed ✅, validation pending)
⏳ Task 2: Complete utils (scraping, linkedin_api)
⏳ Test: Can scrape LinkedIn and create CandidateProfile objects
```

### Week 2: Individual Agents + Tasks
```bash
# Build each agent with CrewAI roles
⏳ Task 3: JD Ingestor with CrewAI role/backstory
⏳ Task 4: LinkedIn Sourcer with CrewAI role/backstory
⏳ Task 5: Relevance Scorer with CrewAI role/backstory
⏳ Test: Each agent works independently
```

### Week 3: Complete Agents + Task Definitions
```bash
# Complete remaining agents and define CrewAI Tasks
⏳ Task 6: Key Matcher with CrewAI role/backstory
⏳ Task 7: Pitch Generator with CrewAI role/backstory
⏳ Task 8: Task Definitions (tasks.py) 🎯 KEY MILESTONE
⏳ Test: All agents + Task definitions ready for orchestration
```

### Week 4: CrewAI Integration & Testing
```bash
# Replace manual chaining with CrewAI orchestration
⏳ Task 9: Excel Writer with CrewAI role/backstory
⏳ Task 10: CrewAI Integration (workflows.py) 🎯 MAJOR MILESTONE
⏳ Task 11: Basic Testing
⏳ Test: Full CrewAI-orchestrated pipeline works
```

### Future: Option B Features
```bash
# After MVP is stable, add advanced features
🔮 Agent Tools (specialized tools for each agent)
🔮 Memory & Context (cross-agent learning)
🔮 Advanced Orchestration (parallel processing)
🔮 Quality Verification (review agents)
```

---

## 💡 Option A vs Option B: What's Different

### **Option A (MVP) - Core CrewAI Orchestration:**
- ✅ **Task Definitions** - Proper CrewAI Task objects with dependencies
- ✅ **Crew Orchestration** - Replace manual chaining with `crew.kickoff()`
- ✅ **Agent Roles** - Proper role/goal/backstory definitions
- ✅ **Context Passing** - Tasks automatically pass results to next tasks
- ✅ **Sequential Processing** - One task after another with dependencies

### **Current Manual Approach (BAD):**
```python
# workflows.py - Manual chaining (what we're replacing)
jd_result = await jd_ingestor.run(jd_text)
sourcing_result = await linkedin_sourcer.run(jd_result.job_description)
scoring_result = await relevance_scorer.run(jd_result.job_description, sourcing_result)
# This is NOT CrewAI orchestration!
```

### **Option A Target (GOOD):**
```python
# workflows.py - CrewAI orchestration (what we're building)
crew = Crew(agents=[...], tasks=[...], verbose=True)
result = crew.kickoff(inputs={"jd_text": jd_text})
# CrewAI handles task dependencies and context passing!
```

### **Option B (Future) - Advanced Features:**
- 🔮 **Agent Tools** - Specialized tools for each agent type
- 🔮 **Memory & Context** - Cross-agent learning and pattern storage
- 🔮 **Parallel Processing** - Worker pools and concurrent execution
- 🔮 **Quality Verification** - Review agents and consistency checking
- 🔮 **Human-in-the-Loop** - Review points and feedback integration

---

## 🎯 Success Criteria

**MVP is complete when:**
- ✅ JD text → structured JobDescription
- ✅ LinkedIn search → 10+ CandidateProfile objects
- ✅ Candidates scored and ranked
- ✅ Key matches identified
- ✅ Personalized pitches generated
- ✅ Excel file created with all data
- ✅ Basic tests pass

**Performance targets:**
- Complete pipeline in <5 minutes
- Process 10+ candidates successfully
- Generate readable Excel output
- 80%+ test coverage

---

## 🔧 Technical Decisions for MVP

### Simple Tech Choices:
- **Embeddings**: OpenAI `text-embedding-3-small` (simple API)
- **Scraping**: Basic Playwright without proxies
- **Matching**: String similarity + keyword matching
- **Templates**: Simple f-strings for now
- **Storage**: No database, just in-memory processing

### Environment Setup:
```bash
# Required environment variables
OPENAI_API_KEY=your_key_here
LINKEDIN_COOKIE=your_cookie_here
LLM_BACKEND=openrouter  # or huggingface
```

This MVP approach gets you a working system quickly without overwhelming complexity. Once it's working, you can add parallel processing, verification agents, and advanced features incrementally.
