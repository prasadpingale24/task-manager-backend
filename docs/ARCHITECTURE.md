# System Architecture Overview

## Classification: Modular Monolith
The Team Tasks Manager follows a **Modular Monolith** architecture.

### Why Modular Monolith?
- **Logical Separation**: The system is organized into distinct domain modules (`auth`, `projects`, `tasks`), each with its own routes, models, and business logic.
- **Single Deployment Unit**: Despite the logical separation, the backend is deployed as a single FastAPI service. This simplifies orchestration and reduces operational overhead while the project is in its growth phase.
- **Scale-Ready**: Because the modules are loosely coupled through services, individual components can be extracted into independent microservices in the future with minimal refactoring.

---

## Technical N-Tier Layer Structure
The system is organized into 5 primary layers, following a strict top-to-bottom data flow.

![System Architecture](./Team_Task_Manager_System_Architecture.png)

### Layer 1: Presentation Layer (Frontend)
- **Technology**: React (Vite), TypeScript, Tailwind CSS.
- **Client-Side State**: **Zustand**. Use of `persist` middleware ensures the session survives page refreshes by syncing to `localStorage`.
- **Responsibility**: Rendering the UI, handling user interactions, and maintaining client-side session state.

### Layer 2: Security & Interface Layer
- **Interface**: REST API powered by **FastAPI**.
- **Network Client**: **Axios** with Interceptors (to automatically inject JWT Bearer tokens).
- **Security**: **JWT (JSON Web Tokens)** with OAuth2 Password Flow. Tokens are signed with HS256.
- **Responsibility**: Defining the API contract, authenticating requests, and protecting endpoints.

### Layer 3: Business Logic Layer
- **Design**: Actions are decoupled from the API layer into **Services**.
- **Domain Modules**:
    - **Auth Service**: Handles registration and login.
    - **Project Service**: Manages team project lifecycles.
    - **Task Service**: Handles granular task creation and updates.
- **Authorization**: Role-based access control (RBAC) verifies if a user has permission to access specific data.

### Layer 4: Persistence Layer (The Bridge)
- **ORM**: **SQLAlchemy 2.0**. Provides high-level mapping from Python objects to Relational tables.
- **Driver**: **asyncpg**. An asynchronous PostgreSQL driver for non-blocking I/O operations.
- **Responsibility**: Managing database sessions, transactions, and data integrity.

### Layer 5: Data Store
- **Technology**: **PostgreSQL** (Production).
- **Storage**: Docker volumes are used to ensure data persistence across container restarts.

---

## Infrastructure & DevOps
The entire N-tier stack is wrapped in an automation layer:
- **Orchestration**: Docker & Docker Compose.
- **Automation**: Jenkins Pipelines with Shared Libraries.
- **Deployment**: Automatic build-test-deploy flow triggered by git commits.
