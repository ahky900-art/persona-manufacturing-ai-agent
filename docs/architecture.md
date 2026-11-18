# Architecture

```mermaid
flowchart TD
  A[Persona / OCEAN data] --> B[Functional lens classifier]
  C[KOSHA accident cases] --> D[Accident knowledge layer]
  E[Process / equipment / work state] --> F[Scenario context]
  B --> G[Multi-agent reviewers]
  D --> G
  F --> G
  G --> H[Ontology graph]
  G --> I[Risk scoring and hard-control checks]
  H --> J[Safety dashboard]
  I --> J
```

## Design boundary
Persona changes the questions and review lens, not the worker's risk probability. Historical accident narratives provide hazard/control knowledge; real-time detection requires operational signals and validation.
