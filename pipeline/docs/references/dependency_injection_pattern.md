# Design Pattern: Dependency Injection

Dependency Injection (DI) is not a standalone pattern in the same way as Factory or Strategy, but rather a fundamental principle and a set of patterns that enable loose coupling and high testability in modern software. It is the "glue" that holds the other patterns in our pipeline's architecture together.

## 1. Concept

The core principle of Dependency Injection is **Inversion of Control (IoC)**.

-   **Without DI:** A class is responsible for creating its own dependencies (the other objects it needs to do its work). This creates tight coupling.
    ```python
    class OrderProcessor:
        def __init__(self):
            # The class creates its own dependency
            self.payment_gateway = PaymentGateway()
        
        def process(self):
            self.payment_gateway.charge(...)
    ```
-   **With DI:** A class is **given** its dependencies from an external source. It is no longer responsible for creating them.
    ```python
    class OrderProcessor:
        def __init__(self, payment_gateway: PaymentGateway):
            # The dependency is "injected" from the outside
            self.payment_gateway = payment_gateway
        
        def process(self):
            self.payment_gateway.charge(...)
    ```
The control of providing the `PaymentGateway` has been inverted—it's now the responsibility of the code that *creates* `OrderProcessor`.

## 2. Use Cases

-   **Building Testable Code:** This is the primary driver for using DI. It allows you to "inject" mock or fake versions of dependencies during unit tests, isolating the class under test.
-   **Decoupling Components:** It breaks the hard-coded link between a class and its dependencies. The class only needs to know about the dependency's interface, not its concrete implementation.
-   **Creating Flexible and Pluggable Systems:** Since dependencies are injected, you can easily swap one implementation for another without changing the class that uses it (e.g., swapping a `MySqlDatabase` for a `PostgresDatabase`).

## 3. Simple Code Example (Constructor Injection)

This example shows **Constructor Injection**, the most common form of DI, which is what we use in our pipeline's `SamplerOrchestrator`.

```python
# The dependency (an abstraction and its implementation)
from abc import ABC, abstractmethod

class MessageService(ABC):
    @abstractmethod
    def send_message(self, recipient: str, message: str):
        pass

class EmailService(MessageService):
    def send_message(self, recipient: str, message: str):
        print(f"Sending email to {recipient}: {message}")

class SmsService(MessageService):
    def send_message(self, recipient: str, message: str):
        print(f"Sending SMS to {recipient}: {message}")

# The dependent class (the client)
class NotificationManager:
    def __init__(self, service: MessageService):
        """
        The dependency (a MessageService) is injected via the constructor.
        """
        self._service = service

    def notify(self, user: str, alert: str):
        self._service.send_message(user, alert)

# --- The Composition Root (in your main application script) ---
# This is where the concrete dependencies are chosen and created.

# Create a manager that uses email
email_sender = EmailService()
email_notifier = NotificationManager(service=email_sender)
email_notifier.notify("test@example.com", "Your order is confirmed.")

# Create another manager that uses SMS, without changing NotificationManager
sms_sender = SmsService()
sms_notifier = NotificationManager(service=sms_sender)
sms_notifier.notify("+1234567890", "Your order has shipped.")

# --- In a test file ---
# You can easily inject a mock service to test the manager in isolation.
class MockMessageService(MessageService):
    def send_message(self, recipient: str, message: str):
        print("MOCK: Message would be sent.")
        self.was_called = True

mock_svc = MockMessageService()
test_notifier = NotificationManager(service=mock_svc)
test_notifier.notify("user", "test alert")
assert mock_svc.was_called # The test passes
```

## 4. Dos and Don'ts

-   **DO** use constructor injection as your default method. It makes dependencies explicit and ensures the object is in a valid state immediately upon creation.
-   **DO** depend on abstractions (like an Abstract Base Class), not on concrete implementations. `NotificationManager` depends on `MessageService` (the ABC), not `EmailService` (the concrete class).
-   **DON'T** have your application logic be aware of multiple concrete implementations. The choice of which concrete class to inject should happen at the highest level of your application—the "Composition Root."
-   **DON'T** confuse DI with a DI "Framework." You can implement DI perfectly well by manually creating and "wiring" your objects together, as shown above. Frameworks (like `FastAPI's Depends` or `python-dependency-injector`) can automate this process but are not required to use the pattern.

## 5. Benefits and Drawbacks

### Benefits
-   **Dramatically Improved Testability:** Makes unit testing easier and more reliable by allowing mock dependencies.
-   **Loose Coupling:** Reduces the dependencies between components, making the codebase easier to maintain, refactor, and extend.
-   **Increased Flexibility:** Allows for different implementations of a service to be swapped out easily.
-   **Clearer API Contracts:** A class's constructor clearly lists everything it needs to function.

### Drawbacks
-   **Increased Upfront Complexity:** It can feel more complex at first because you have to "wire up" your objects at the start of the application (the Composition Root).
-   **Can Lead to Long Constructor Signatures:** If a class has many dependencies, its constructor can become very long. This is often a sign that the class is doing too much and should be broken down further (violating the Single-Responsibility Principle).

## 6. Schema

-   **Purpose:** To invert the control of dependency creation, making a class receive its dependencies from an external source rather than creating them itself.
-   **Inputs:**
    -   An **Abstraction** (an Abstract Base Class or Protocol) that defines the contract for the dependency.
    -   A **Concrete Implementation** of that abstraction.
    -   A **Client** class that depends on the abstraction and receives a concrete implementation in its constructor.
    -   A **Composition Root** (the main script) that creates the concrete implementation and "injects" it into the client.
-   **Outputs:**
    -   A highly decoupled and testable system where components are linked together at runtime.