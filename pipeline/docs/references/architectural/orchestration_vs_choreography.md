# Orchestration vs. Choreography

In distributed systems, Orchestration and Choreography are two patterns for how services can collaborate.

*   **Orchestration**: A conductor directing an orchestra. Everyone follows the conductor's lead.
*   **Choreography**: Dancers in a performance. Each dancer reacts to the moves of the dancer next to them without a central leader.

When comparing them, the fundamental difference lies in who is responsible for the workflow and recovery logic. In a Linux-based microservices environment, this choice significantly impacts how you debug logs and trace failures across containers.

## Error Handling Compared

### 1. Orchestration (The Conductor)
In this model, the Orchestrator acts as a centralized controller. If a step fails, the Orchestrator is the only component that needs to know the "Plan B."

*   **Error Handling**: The Orchestrator receives a failure signal (e.g., a 500 error or a timeout) and explicitly calls the "rollback" or "compensating" actions on the previous services.
*   **Visibility**: You can look at one set of logs (the Orchestrator's) to see exactly why a workflow died.
*   **Complexity**: The logic for "what happens if X fails" is all in one place.

### 2. Choreography (The Dancers)
In a choreographed system, there is no central "brain." Services communicate via events (often using a message broker like RabbitMQ or Kafka).

*   **Error Handling**: If Service B fails, it emits a `PaymentFailed` event. Service A (Inventory) must be "listening" for that specific failure event to know it needs to release the reserved items.
*   **Visibility**: Harder to trace. You have to follow the trail of events across multiple services to understand the state of a single order.
*   **Complexity**: Each service must know how to react to failures from other services, leading to distributed logic.

## Summary Table

| Feature | Orchestration | Choreography |
| :--- | :--- | :--- |
| **Control** | Centralized | Decentralized |
| **Coupling** | Services are low-coupled; Orchestrator is high-coupled. | Services are coupled to events/contracts. |
| **Failure Recovery** | Explicitly managed by Orchestrator. | Implicitly managed by event listeners. |
| **Best For** | "Complex, multi-step business transactions." | "High-throughput, simple, decoupled tasks." |

### The "Saga" Pattern Reality
In practice, many developers use a **Stateful Orchestrator** (like Temporal or AWS Step Functions) because it provides a "visual" workflow of where an error occurred. In a Linux environment, this makes monitoring via tools like Prometheus or Grafana much more straightforward because you have a single source of truth for the process state.
