### Slice 1: Job Description Ingestion (Completed)

*   [x] **Define Data Contract:** `JobDescription` and `JDIngestResult` models are defined in `src/sourceress/models.py`.
*   [x] **Implement Agent:** `JDIngestor` is implemented in `src/sourceress/agents/jd_ingestor.py`.
*   [x] **Write Unit Test:** `tests/test_jd_ingestor.py` provides thorough tests.
*   [x] **Integrate into Workflow:** `JDIngestor` is integrated into the manual workflow in `src/sourceress/workflows.py`.
*   [x] **Create Entrypoint:** `main.py` can execute the workflow.

### Slice 2: LinkedIn Sourcing

*   [ ] **Implement `linkedin_api.py` `fetch_profiles` function:**
    *   [ ] Read the content of `src/sourceress/utils/scraping.py` to understand the `search_linkedin` function.
    *   [ ] Implement the logic to convert the raw data from `search_linkedin` into a list of `CandidateProfile` objects.
    *   [ ] Add error handling and logging.
*   [ ] **Implement `LinkedInSourcer` Agent:**
    *   [ ] In `src/sourceress/agents/linkedin_sourcer.py`, replace the dummy data with a call to the `fetch_profiles` function in `utils/linkedin_api.py`.
    *   [ ] Construct the search query from the input `JobDescription`.
    *   [ ] Return a `SourcingResult` with the fetched `CandidateProfile` objects.
*   [ ] **Write Integration Test for `LinkedInSourcer`:**
    *   [ ] In `tests/test_agents.py`, add a test for the `LinkedInSourcer` agent.
    *   [ ] Mock the `fetch_profiles` function to return sample data.
    *   [ ] Assert that the agent correctly processes the input and returns the expected `SourcingResult`.
*   [ ] **Verify End-to-End Workflow:**
    *   [ ] Run the existing `tests/test_workflow.py` to ensure the manual workflow still runs correctly with the new `LinkedInSourcer` implementation.
