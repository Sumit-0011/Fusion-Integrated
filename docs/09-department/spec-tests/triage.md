# Spec tests: department

Student 1 (git author name): Sumit-0011
Student 2 (git author name): Sparsh Shukla
Design commit (hash and subject): a816014 spec(department): freeze FR, UC, BR, and WF test designs
Baseline commit (hash and subject): 3cc9beb spec(department): baseline test suite and initial triage log
Student 1's 10/10 commit the baseline ran on (hash): cc263862976c15bc8e80723dbe1cc73b2792f1bb

## Results
| Run | Strategy | Cases | Passed | Failed | Skipped | Line % | Branch % |
|-----|----------|-------|--------|--------|---------|--------|----------|
| baseline | FR | 12 | 7 | 5 | 0 | 74.7% | 31.4% |
| baseline | UC | 9 | 6 | 3 | 0 | 67.3% | 19.6% |
| baseline | BR | 9 | 6 | 3 | 0 | 65.4% | 18.6% |
| baseline | WF | 7 | 3 | 4 | 0 | 64.7% | 19.6% |

## Failures and skips
| Test id | Source id | Strategies | Category | Evidence | Outcome (fixing commit, covering test, or agreed reading with the spec sentence) | Open? |
|---------|-----------|------------|----------|----------|-----------------------------------------------------------------------------------|-------|
| FR-DEP-008 | CFR-OAP-020 / AFR-OAP-046 | FR | Test-generation / test-implementation problem | Admin pending list endpoint returned 403 because stub_iam session was overwritten by student_client token | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| FR-DEP-009 | CFR-OAP-021 / AFR-OAP-047 | FR | Test-generation / test-implementation problem | Admin schedule endpoint returned 403 due to session overwrite in composite client test | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| FR-DEP-010 | CFR-OAP-021 / AFR-OAP-048 | FR | Test-generation / test-implementation problem | Admin schedule history audit check failed with 403 on schedule endpoint | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| FR-DEP-011 | CFR-OAP-022 / AFR-OAP-049 | FR | Test-generation / test-implementation problem | Calendar listing failed to show scheduled seminar because preceding admin scheduling call returned 403 | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| FR-DEP-012 | CFR-OAP-022 / AFR-OAP-050 | FR | Test-generation / test-implementation problem | Admin announcement publication returned 403 when executed alongside student client | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| UC-DEP-004 | OA-UC-53 Main Flow | UC | Test-generation / test-implementation problem | Admin scheduling call returned 403 due to session overwrite by student client | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| UC-DEP-005 | OA-UC-53 Alternative A1 | UC | Test-generation / test-implementation problem | Admin rejection call returned 403 due to session overwrite by student client | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| UC-DEP-007 | OA-UC-54 Main Flow | UC | Test-generation / test-implementation problem | Seminar schedule query did not find scheduled item because admin scheduling step was refused with 403 | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| BR-DEP-006 | OA-BR-62 audit-logging | BR | Test-generation / test-implementation problem | Schedule call returned 403 due to session overwrite; history log not generated | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| BR-DEP-007 | OA-BR-62 log-persistence | BR | Test-generation / test-implementation problem | Schedule call returned 403 due to session overwrite; history relation not verified | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| BR-DEP-009 | OA-BR-63 visibility-scheduled-only | BR | Test-generation / test-implementation problem | Public calendar check failed because admin scheduling was refused with 403 | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| WF-DEP-002 | BW-OAP-09 schedule-transition | WF | Test-generation / test-implementation problem | Admin schedule action returned 403 in composite workflow test | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| WF-DEP-003 | BW-OAP-09 reject-transition | WF | Test-generation / test-implementation problem | Admin reject action returned 403 in composite workflow test | Fix multi-session token dispatching in conftest.py (Student 2) | Yes |
| WF-DEP-005 | BW-OAP-09 invalid-transition-from-scheduled | WF | Confirmed implementation defect | Attempting to transition already SCHEDULED seminar returned 403 instead of 400/409 bad request | Student 1 to enforce explicit 400 Bad Request / 409 Conflict guard on terminal transitions | Yes |
| WF-DEP-006 | BW-OAP-09 invalid-transition-from-rejected | WF | Confirmed implementation defect | Attempting to transition already REJECTED seminar returned 403 instead of 400/409 bad request | Student 1 to enforce explicit 400 Bad Request / 409 Conflict guard on terminal transitions | Yes |
