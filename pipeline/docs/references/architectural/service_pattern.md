# The Service Pattern

In Python and software architecture, a **Service** is a pattern used to encapsulate business logic. It acts as a middle layer that coordinates how data is moved and transformed, ensuring that your web framework (like FastAPI or Flask) or your database models don't get cluttered with "rules."

## 1. What is a "Service" Architecturally?

Architecturally, a Service lives in the **Domain** or **Application** layer. It sits between the entry point (the Controller/API) and the data storage (the Repository/Model).

*   **The Controller**: Handles HTTP requests and basic validation.
*   **The Service**: Handles the "Why" and "How" of the business process.
*   **The Repository/Model**: Handles the "Where" (saving to the database).

## 2. Can a Service be one or multiple classes?

A Service can be either, but it is usually defined by its boundary, not its class count.

*   **Single Class**: Most common. A `UserService` class might have methods like `create_user`, `deactivate_account`, and `reset_password`.
*   **Multiple Classes**: If a service becomes too large, it can be broken down into sub-services or "Helper" classes. For example, an `OrderService` might use a `TaxCalculator` class and a `ShippingRateService` class internally.
*   **Functional Approach**: In Python, it is also common to see services implemented as a module containing pure functions (e.g., `services/user_operations.py`) rather than a class, especially if there is no internal state to maintain.

## 3. What is the Scope of a "Service"?

The scope is typically defined by a Single Responsibility or a Bounded Context.

*   **Granularity**: A service should represent one cohesive piece of the business. You wouldn't put "Process Payment" and "Update User Bio" in the same service.
*   **Statelessness**: Generally, services should be stateless. They take an input, perform logic, and return an output (or update a database). They shouldn't "remember" previous calls within the object itself; that's what the database is for.

## 4. How does a "Service" relate to other patterns?

| Pattern | Relationship to Service |
| :--- | :--- |
| **Repository** | The Service calls the Repository to get/save data. The Service doesn't care how the SQL is written. |
| **Orchestrator** | "An Orchestrator is a ""High-Level Service."" It calls multiple smaller Services to complete a complex workflow." |
| **Facade** | A Service often acts as a Facade for the Domain. It provides one simple method (`place_order`) that hides 10 complex domain rules. |
| **Dependency Injection** | "In Python, we usually ""inject"" the Repository into the Service constructor so we can mock it during Linux-based CI/CD testing." |

### Example Implementation

```python
# app/services/order_service.py

class OrderService:
    def __init__(self, repo, email_provider):
        self.repo = repo
        self.email_provider = email_provider

    def place_order(self, user_id, items):
        # 1. Business Logic: Calculate total
        total = sum(item.price for item in items)
        
        # 2. Coordination: Save to DB via Repository
        order = self.repo.save_order(user_id, items, total)
        
        # 3. Side Effect: Send confirmation
        self.email_provider.send_receipt(user_id, order.id)
        
        return order
```
