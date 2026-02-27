# Granite AI Platform Architecture

## Purpose
This document describes the high-level architecture of the Granite AI Platform, including core components, data flow, deployment model, and operational concerns.

## System Overview
- **Clients**: Web, CLI, or API consumers.
- **Gateway/API Layer**: Entry point for authentication, routing, and rate limiting.
- **Application Services**: Domain logic and orchestration.
- **Model Runtime Layer**: Inference, prompt processing, and model/tool integrations.
- **Data Layer**: Primary database, cache, and object storage.
- **Observability**: Logging, metrics, tracing, and alerting.

## High-Level Component Diagram
```text
[Clients]
    |
    v
[API Gateway]
    |
    v
[Application Services] ---> [Model Runtime]
    |                             |
    v                             v
[Primary DB] <--------------> [Cache]
    |
    v
[Object Storage]

[Observability] collects signals from all layers
```

## Core Components

### Agentic Architecture Extension

#### Agent Orchestrator Layer

Implements deterministic workflow graphs using LangGraph.

Enforces separation between LLM reasoning and system state mutation.

All database mutations must occur through tool endpoints.

Supports guardrails and policy enforcement before tool execution.

#### Tooling Layer (MCP + REST)

All actionable operations are exposed as tools.

Tools are:

Strictly schema-validated (Pydantic)

RBAC-protected

Logged and auditable

LLM cannot call database or services directly.

Tools include:

search_inventory

create_hold

generate_quote_draft

approve_quote

track_shipment

draft_purchase_order

#### RAG Design (Pinecone)

Separate indexes or namespaces per corpus:

inventory_knowledge

pricing_policies

sops_playbooks

supplier_docs

Metadata-first filtering strategy.

Prompts and retrieval configuration versioned and auditable.

#### Guardrails

Prompt injection detection.

Tool allowlist enforcement per role.

Deterministic pricing enforcement.

PII redaction.

Human approval triggers for high-risk actions.

#### Human-in-the-Loop

Discount > threshold requires Manager approval.

Purchase orders require Procurement approval.

Shipment rerouting requires Operations approval.

### API Gateway
- Handles authn/authz, request validation, traffic controls, and routing.

### Application Services
- Implements business workflows and integrates with model/runtime services.

### Model Runtime
- Manages inference requests, prompt templates, model selection, and tool calling.

### Data Stores
- **Primary DB**: System of record for platform entities.
- **Cache**: Low-latency reads and short-lived state.
- **Object Storage**: Large artifacts, model outputs, and documents.

### Observability Stack
- Centralized logs, service metrics, distributed tracing, and incident alerts.

## Request Lifecycle
1. Client sends request to the API gateway.
2. Gateway authenticates user/service and forwards request.
3. Application service validates inputs and executes workflow.
4. If needed, runtime invokes models/tools.
5. Results are persisted and returned to client.
6. Telemetry is emitted throughout the path.

## Agent Execution Flow
1. Intent Classification
2. Context Retrieval (RAG)
3. Tool Planning
4. Policy Validation
5. Tool Execution
6. Response Composition
7. Audit Logging

## Data Flow and Boundaries
- Clearly separate public API contracts from internal service contracts.
- Keep model prompts/configs versioned and auditable.
- Restrict sensitive data to least-privilege access paths.

## Security Model
- Authentication via tokens/identity provider.
- Authorization using role- or policy-based access control.
- Encryption in transit and at rest.
- Audit logging for privileged and data-sensitive actions.

## Reliability and Scalability
- Horizontal scaling for stateless services.
- Retry and timeout policies for downstream dependencies.
- Circuit breakers and graceful degradation for runtime failures.
- Backups and recovery plans for stateful systems.

## Deployment Architecture
- Environments: local, staging, production.
- Containerized services with orchestration.
- CI/CD pipeline for build, test, security checks, and deployment.

## Configuration and Secrets
- Environment-specific config management.
- Secrets provided via a secure secret manager, never committed to source control.

## Open Questions
- Which model providers and fallback strategy are required?
- What are the latency and cost SLO targets?
- Which tenancy model (single vs multi-tenant) is needed?

## Decisions Log
Track key architecture decisions here or link to ADRs.

- **Date**: YYYY-MM-DD
- **Decision**: _TBD_
- **Context**: _TBD_
- **Status**: Proposed | Accepted | Superseded