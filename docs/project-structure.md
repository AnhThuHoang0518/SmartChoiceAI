# Project structure

```text
smart-choice/
|-- frontend/                 # Web chatbot and product comparison UI
|   |-- public/               # Static assets
|   `-- src/
|       |-- components/       # Reusable UI components
|       |-- features/         # Chat and comparison feature modules
|       |-- hooks/            # Frontend state and data hooks
|       |-- pages/            # Routes or pages
|       |-- services/         # Backend API clients
|       `-- types/            # Shared frontend types
|-- backend/
|   `-- app/
|       |-- api/              # HTTP endpoints
|       |-- agents/           # Conversation and clarification flow
|       |-- core/             # Settings, logging and shared utilities
|       |-- guardrails/       # Grounding and anti-hallucination checks
|       |-- models/           # Domain models
|       |-- ranking/          # Product scoring and top-3 ranking
|       |-- retrieval/        # Catalog and policy retrieval/RAG
|       |-- schemas/          # Request and response schemas
|       `-- services/         # Catalog, price, promotion and stock adapters
|-- data/
|   |-- raw/                  # Source datasets; do not modify in place
|   |-- mock/                 # Safe demo data
|   |   |-- catalog/
|   |   |-- policies/
|   |   `-- scenarios/
|   `-- processed/            # Normalized/index-ready artifacts
|-- evaluations/
|   |-- datasets/             # Golden cases and judging scenarios
|   `-- results/              # Generated evaluation reports
|-- tests/
|   |-- unit/                 # Isolated ranking/retrieval/guardrail tests
|   |-- integration/          # API and service integration tests
|   |-- e2e/                  # Full chatbot user journeys
|   `-- fixtures/             # Deterministic test data
|-- configs/                  # Non-secret application and ranking config
|-- scripts/                  # Ingestion, indexing, evaluation and demo setup
|-- infra/                    # Docker and deployment definitions
|-- docs/
|   |-- architecture/         # AI/system architecture deliverable
|   `-- pilot/                # 1-2 page pilot roadmap deliverable
`-- logs/                     # Local masked runtime logs only
```

## Data rules

- Never commit real customer data, credentials, internal cost prices or NDA data.
- Keep raw input immutable; write cleaned data to `data/processed`.
- Store source identifiers with retrieved facts so recommendations can be audited.
- Mask sensitive values in logs and use anonymized/mock data for the demo.

