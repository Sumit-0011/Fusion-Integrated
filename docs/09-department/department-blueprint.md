# Department Module Blueprint

**Module Name:** Department (Online Academic Portal - Department / OAP Department)  
**Module Code:** `department`  
**Docs Directory:** `docs/09-department/`  
**Specification Reference:** `CFR-OAP-019` to `022`, `AFR-OAP-043` to `051`, `OA-UC-51`, `53`, `54`, `41`, `42`, `OA-BR-61`, `62`, `51`, `63`, `BW-OAP-09`  
**Student 1 (Builder):** Sumit Kumar (24BCS245)  
**Student 2 (Reviewer/Approver):** Sparsh Shukla (24BCS240)  
**Blueprint Approval:** Approved by Sparsh Shukla (Student 2) on 2026-11-01  

---

## 1. Domain Scope & Business Rules

1. **Graduate Seminar Scheduling (`BW-OAP-09`)**:
   - 4-state lifecycle: `NO_SUBMITTED_REQUEST` $\rightarrow$ `AWAITING_SCHEDULING` $\rightarrow$ `SCHEDULED` (or `REJECTED`, `CANCELLED`).
   - `OA-UC-51`: Request Graduate Seminar (PG Student).
   - `OA-UC-53`: Schedule Graduate Seminar (Department Administrator).
   - `OA-UC-54`: View Seminar Schedule (Public campus community).

2. **Business Rules**:
   - `OA-BR-61`: Postgraduate Scope Rule. Only postgraduate scholars (`M.Tech`, `Ph.D.`, `M.Des`, `PG`) may request graduate seminars. Undergraduates fail closed.
   - `OA-BR-62`: Administrator Audit Logging. Append-only history record in `SeminarSchedulingHistory` for every scheduling action.
   - `OA-BR-51`: Allocation Integrity. TA assignments must link to a course, a faculty member, or both.
   - `OA-BR-63`: Public Visibility. Only seminars in `SCHEDULED` status are published on the calendar.

3. **Allocations & Announcements**:
   - `AFR-OAP-043` / `OA-UC-41`: Thesis Supervisor Allocation.
   - `AFR-OAP-044` / `OA-UC-42`: Teaching Assistant Allocation.
   - `AFR-OAP-050` / `051`: Department Announcements and Notices.

---

## 2. Technical Architecture

- **Domain (`modules/department/domain/`)**: Pure Python business logic free of ORM dependencies:
  - `state_machine.py`: Deterministic state transitions for `BW-OAP-09`.
  - `eligibility.py`: Postgraduate eligibility checks and parameter validations.
- **Models (`modules/department/models/`)**: Decoupled relational persistence adhering to ADR-0013:
  - `SeminarSchedulingRequest`, `GraduateSeminar`, `SeminarSchedulingHistory`.
  - `ThesisSupervisorAllocation`, `TAAllocation`, `DepartmentAnnouncement`.
- **Services & Selectors (`services/`, `selectors/`)**: Domain orchestration and scoped queries.
- **Contracts (`contracts.py`)**: Inter-module DTOs (`DepartmentSeminarDTO`, `DepartmentNoDuesClearanceDTO`).
- **IAM Registry (`registry.py`)**: Standardized RBAC grants and permissions matching `registry/permissions.json`.
- **Frontend (`client/src/modules/department/`)**: React 18, Vite, Mantine UI, TanStack React Query pages registered under `/department`.
