# Layered Architecture

Most professional Python architectures use a four-layer approach to keep code manageable. In a Linux-based backend environment, these layers help you separate the "How" (Infrastructure) from the "What" (Domain) and the "Who" (Interface).

This is often referred to as **Clean Architecture** or **Hexagonal Architecture**.

## The Standard Four-Layer Architecture

| Layer | Responsibility | Typical Python Content |
| :--- | :--- | :--- |
| **1. Interface** | Entry points to the system. | "FastAPI/Flask routes, CLI commands, Celery task definitions." |
| **2. Application**| "The ""Orchestrator."" Coordinates the workflow." | Services that call the Domain and Infrastructure. |
| **3. Domain** | "The ""Heart."" Pure business rules and logic." | "Entities, Value Objects, and Domain exceptions." |
| **4. Infrastructure**| External tools and technical details. | "SQLAlchemy models, Redis clients, S3 storage wrappers." |

### Why the Middle Layers Matter
If you only had Domain and Infrastructure, your code would be hard to test. The additional layers act as buffers:

*   **The Application Layer (The Glue)**
    This is where the [Service Pattern](./service_pattern.md) and [Orchestrator Pattern](./orchestrator_pattern.md) usually live.
    *   **The Rule**: This layer shouldn't contain complex business logic (that belongs in the Domain) or SQL queries (that belongs in Infrastructure).
    *   **The Job**: It says: *"First, get the User from the Database (Infra). Then, check if they are allowed to buy this (Domain). If yes, save the Order (Infra) and send a Slack alert (Infra)."*

*   **The Interface Layer (The Boundary)**
    This is the outermost shell. It translates "Computer Speak" (JSON, CLI arguments, Environment Variables) into "Domain Speak."
    *   **Example**: On a Linux server, you might have a cron job that triggers a Python script. The script is an Interface. It parses the command-line flags and then hands the data to an Application Service.

### Mapping "Rules" to the Layers

| Rule Type | Layer |
| :--- | :--- |
| **Business Rules** | Strictly in the **Domain**. |
| **Orchestration/Workflow Rules** | In the **Application** (Services). |
| **Technical/Validation Rules** | In the **Interface** (e.g., Pydantic models for API validation). |
| **Persistence Rules** | In the **Infrastructure** (e.g., Database constraints). |

## Directory Structure Example

The best way to visualize these layers is through a standard project directory structure. This layout (often called a "Screaming Architecture") makes it immediately obvious what the business does.

```
my_python_project/
├── app/                        # The Application Layer (Orchestration/Services)
│   ├── services/               # Orchestrates Domain and Infra
│   │   └── order_service.py    # (e.g., "Place Order" workflow)
│   └── use_cases/              # Specific business actions
├── domain/                     # The Domain Layer (The "Heart")
│   ├── models.py               # Pure Business Entities (Dataclasses)
│   ├── logic.py                # Business Rules & Calculations
│   └── exceptions.py           # Domain-specific errors (e.g. InsufficientFunds)
├── infra/                      # The Infrastructure Layer (The "Tools")
│   ├── db/                     # Database implementations (SQLAlchemy/Tortoise)
│   ├── clients/                # External API clients (Stripe, Twilio)
│   └── repositories.py         # Data access logic (CRUD)
├── interface/                  # The Interface Layer (The "Entry Points")
│   ├── api/                    # FastAPI/Flask routes
│   ├── cli/                    # Typer/Click command line tools
│   └── workers/                # Celery or Dramatiq task handlers
├── tests/                      # Testing suite (mirrors the app structure)
├── config.py                   # Environment variable management
└── main.py                     # Entry point to start the application
```

## Visualization of Data Flow

Imagine a user placing an order via an API on a Linux-based backend:

1.  **Interface Layer (`interface/api/routes.py`)**
    *   **Action**: Receives a JSON `POST` request.
    *   **Role**: Validates the format (using Pydantic).
    *   **Handoff**: Calls a function in the Application Layer.

2.  **Application Layer (`app/services/order_service.py`)**
    *   **Action**: The Orchestrator.
    *   **Role**: Tells the Infrastructure to fetch a user, tells the Domain to validate the price, then tells the Infrastructure to save the result.
    *   **Handoff**: Coordinates the move between Domain and Infra.

3.  **Domain Layer (`domain/logic.py`)**
    *   **Action**: Executes the Business Rule.
    *   **Role**: Calculates: `if user.is_vip: apply_discount(order)`.
    *   **Handoff**: Returns a calculated object back to the Application Layer.

4.  **Infrastructure Layer (`infra/db/repositories.py`)**
    *   **Action**: Talks to the Linux System/Database.
    *   **Role**: Executes the actual SQL: `INSERT INTO orders ...`.
    *   **Handoff**: Returns confirmation of the save.

### Why this is powerful in Linux/DevOps
*   **Testing**: You can test your Domain logic (the rules) without ever starting a database or a web server. It's just pure Python.
*   **Swappability**: If you decide to move from an API-driven system to a CLI-driven tool, you only change the Interface layer. The Domain and Application logic remains untouched.
*   **Deployment**: You can easily wrap the Interface in a Docker container, while keeping the logic clean and decoupled.
