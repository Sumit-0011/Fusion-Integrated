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
| Q2 | FR | 12 | 12 | 0 | 0 | 74.6% | 32.8% |
| Q2 | UC | 9 | 9 | 0 | 0 | 73.6% | 29.3% |
| Q2 | BR | 9 | 9 | 0 | 0 | 72.0% | 26.7% |
| Q2 | WF | 7 | 7 | 0 | 0 | 70.1% | 25.0% |

## Failures and skips
| Test id | Source id | Strategies | Category | Evidence | Outcome (fixing commit, covering test, or agreed reading with the spec sentence) | Open? |
|---------|-----------|------------|----------|----------|-----------------------------------------------------------------------------------|-------|
| FR-DEP-002 | CFR-OAP-019 / AFR-OAP-043 | FR | Confirmed implementation defect | Unauthorized student was permitted to create supervisor allocation (HTTP 201) | Fixed in commit b763b2d by enforcing permission check in create() | No |
| FR-DEP-005 | CFR-OAP-019 / AFR-OAP-044 | FR | Confirmed implementation defect | Faculty-only TA allocation rejected with 400 because course_code was mandatory | Fixed in commit b763b2d: allowed blank course_code and validated course or faculty presence | No |
| FR-DEP-008 | CFR-OAP-020 / AFR-OAP-046 | FR | Test-generation / test-implementation problem | Admin pending list endpoint returned 403 because stub_iam session was overwritten by student_client token | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| FR-DEP-009 | CFR-OAP-021 / AFR-OAP-047 | FR | Test-generation / test-implementation problem | Admin schedule endpoint returned 403 due to session overwrite in composite client test | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| FR-DEP-010 | CFR-OAP-021 / AFR-OAP-048 | FR | Test-generation / test-implementation problem | Admin schedule history audit check failed with 403 on schedule endpoint | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| FR-DEP-011 | CFR-OAP-022 / AFR-OAP-049 | FR | Test-generation / test-implementation problem | Calendar listing failed to show scheduled seminar because preceding admin scheduling call returned 403 | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| FR-DEP-012 | CFR-OAP-022 / AFR-OAP-050 | FR | Test-generation / test-implementation problem | Admin announcement publication returned 403 when executed alongside student client | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| UC-DEP-004 | OA-UC-53 Main Flow | UC | Test-generation / test-implementation problem | Admin scheduling call returned 403 due to session overwrite by student client | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| UC-DEP-005 | OA-UC-53 Alternative A1 | UC | Test-generation / test-implementation problem | Admin rejection call returned 403 due to session overwrite by student client | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| UC-DEP-007 | OA-UC-54 Main Flow | UC | Test-generation / test-implementation problem | Seminar schedule query did not find scheduled item because admin scheduling step was refused with 403 | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| BR-DEP-006 | OA-BR-62 audit-logging | BR | Test-generation / test-implementation problem | Schedule call returned 403 due to session overwrite; history log not generated | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| BR-DEP-007 | OA-BR-62 log-persistence | BR | Test-generation / test-implementation problem | Schedule call returned 403 due to session overwrite; history relation not verified | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| BR-DEP-009 | OA-BR-63 visibility-scheduled-only | BR | Test-generation / test-implementation problem | Duplicate pending request rejection due to shared student ID across test steps | Fixed in commit 53ddd7d: allocated separate student IDs for independent requests | No |
| WF-DEP-002 | BW-OAP-09 schedule-transition | WF | Test-generation / test-implementation problem | Admin schedule action returned 403 in composite workflow test | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| WF-DEP-003 | BW-OAP-09 reject-transition | WF | Test-generation / test-implementation problem | Admin reject action returned 403 in composite workflow test | Fixed in commit 53ddd7d: multi-session token dispatching in conftest.py | No |
| WF-DEP-005 | BW-OAP-09 invalid-transition-from-scheduled | WF | Test-generation / test-implementation problem | Token resolution caused 403 rather than reaching invalid transition refusal | Fixed in commit 53ddd7d: verified 400 Bad Request refusal on terminal transition | No |
| WF-DEP-006 | BW-OAP-09 invalid-transition-from-rejected | WF | Test-generation / test-implementation problem | Token resolution caused 403 rather than reaching invalid transition refusal | Fixed in commit 53ddd7d: verified 400 Bad Request refusal on terminal transition | No |
