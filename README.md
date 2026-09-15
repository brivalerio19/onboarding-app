\# Automated User Onboarding \& Access Orchestrator



\[!\[Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)

\[!\[Framework](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

\[!\[Validation](https://img.shields.io/badge/Validation-Pydantic%20v2-red.svg)](https://docs.pydantic.dev/)

\[!\[License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)



A RESTful API engine designed to automate employee digital identity provisioning and access orchestration across enterprise SaaS platforms (Google Workspace, Slack, GitHub, Okta, and AWS). 



Built to eliminate manual IT support overhead, prevent orphaned account creation, and enforce role-based access control (RBAC) through automated background tasks.



\---



\## Key Features



\* \*\*Automated Identity Creation:\*\* Accepts onboarding payloads and queues target SaaS provisioning workflows.

\* \*\*Strict Schema Validation:\*\* Powered by Pydantic v2 and `email-validator` for request payload sanitization and email verification.

\* \*\*Asynchronous Endpoint Architecture:\*\* Implements a decoupled `202 Accepted` response pattern for fast client execution and queued execution.

\* \*\*Granular Status Tracking:\*\* Exposes endpoints to check real-time state across individual SaaS provisioning steps.

\* \*\*Self-Documenting API:\*\* Built-in OpenAPI specification and interactive Swagger UI interface.



\---



\## System Architecture \& Data Flow



```text

&#x20; \[ Admin / HR Client ]

&#x20;          │

&#x20;          ▼

┌─────────────────────┐

│     FastAPI App     │ ◄── Validates request with Pydantic

└──────────┬──────────┘

&#x20;          │

&#x20;          ▼

┌─────────────────────┐

│  Service Dispatch   │ ◄── Assigns target SaaS provisioners

└──────────┬──────────┘

&#x20;          │

&#x20;┌─────────┼─────────┬─────────┐

&#x20;▼         ▼         ▼         ▼

\[Google] \[Slack]  \[GitHub]  \[AWS]

