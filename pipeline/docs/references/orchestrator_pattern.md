# Design Pattern: Orchestrator / Facade

The Orchestrator pattern, often used interchangeably with the Facade pattern in this context, provides a simplified, high-level interface to a more complex subsystem of components. It acts as a single point of entry that coordinates the work of multiple specialized services to accomplish a larger task.

## 1. Concept

An Orchestrator class encapsulates a complex workflow. Instead of having the main application logic call a dozen different objects in a specific sequence, it calls a single method on the Orchestrator. The Orchestrator, in turn, knows the correct sequence and logic to call its internal "worker" components to get the job done. It acts as a "traffic controller" or the "brain" of a specific operation.

A **Facade** is a similar concept that emphasizes providing a *simpler* interface to a complex library or system, hiding its complexity. In our use case, the terms are nearly interchangeable because our `SamplerOrchestrator` both coordinates a workflow (Orchestrator) and hides the complexity of sniffing, factories, and artifact creation (Facade).

## 2. Use Cases

This pattern is ideal for:
-   **Simplifying Complex Workflows:** When a single user action (like "sample a file") requires multiple steps involving different components.
-   **Decoupling Subsystems:** It provides a clean boundary between the main application logic and a specialized subsystem (like the sampling module). Changes to the internal implementation of the subsystem don't affect the main application, as long as the Orchestrator's public interface remains the same.
-   **Centralizing Business Logic:** The sequence of operations is a form of business logic. The Orchestrator centralizes this, making it easier to understand, modify, and debug.

## 3. Simple Code Example

Imagine a simple system for processing an online order.

```python
# The complex, specialized "worker" classes
class InventoryService:
    def check_stock(self, item_id: str, quantity: int) -> bool:
        print(f"Checking stock for {quantity} of {item_id}...")
        return True # Simplified

class PaymentGateway:
    def process_payment(self, amount: float, card_details: dict) -> bool:
        print(f"Processing payment of ${amount}...")
        return True # Simplified

class ShippingService:
    def arrange_delivery(self, address: str, item_id: str):
        print(f"Shipping {item_id} to {address}...")

# The Orchestrator / Facade
class OrderFacade:
    def __init__(self, inventory: InventoryService, payment: PaymentGateway, shipping: ShippingService):
        # Dependencies are injected
        self.inventory = inventory
        self.payment = payment
        self.shipping = shipping

    def place_order(self, item: str, quantity: int, amount: float, card: dict, address: str) -> bool:
        """A single, simple method to handle the entire workflow."""
        print("--- Placing new order ---")
        if not self.inventory.check_stock(item, quantity):
            print("Order failed: Item out of stock.")
            return False
        
        if not self.payment.process_payment(amount, card):
            print("Order failed: Payment declined.")
            return False
            
        self.shipping.arrange_delivery(address, item)
        print("--- Order placed successfully! ---")
        return True

# --- Main application logic ---
# Composition Root
inventory_svc = InventoryService()
payment_svc = PaymentGateway()
shipping_svc = ShippingService()

# Inject dependencies
order_placer = OrderFacade(inventory_svc, payment_svc, shipping_svc)

# The main logic is now incredibly simple
order_placer.place_order(item="123", quantity=1, amount=99.99, card={}, address="123 Main St")
```

## 4. Dos and Don'ts

-   **DO** keep the Orchestrator focused on a single, high-level responsibility (e.g., "sampling" or "placing an order").
-   **DO** use dependency injection to provide the Orchestrator with its worker components. This is critical for testability.
-   **DON'T** let the Orchestrator become a "God Object." It should not contain the implementation logic of the workers themselves. It should only *delegate* tasks. If the Orchestrator's methods become very long and complex, it's a sign that some logic should be extracted into a new, specialized service.
-   **DON'T** create circular dependencies where a worker component needs to call back to the Orchestrator. The flow of control should be one-way: from the Orchestrator down to the workers.

## 5. Benefits and Drawbacks

### Benefits
-   **Simplicity:** Hides complexity from the client/main application.
-   **Decoupling:** Reduces dependencies between the client and the internal subsystem.
-   **Centralization:** Provides a single place to manage a specific workflow.
-   **Readability:** The main application logic becomes much cleaner and easier to follow.

### Drawbacks
-   **Risk of "God Object":** If not managed carefully, the Orchestrator can grow too large and start violating the Single-Responsibility Principle.
-   **Hides Components:** While usually a benefit, hiding the subsystem can sometimes make it harder for developers to access the specific functionality of a worker component if needed (though this can be mitigated with good design).

## 6. Schema

-   **Purpose:** To provide a single, simplified entry point to a complex subsystem, coordinating the interactions between multiple components to perform a high-level task.
-   **Inputs:**
    -   Dependencies (worker components) are provided via the constructor (Dependency Injection).
    -   Method arguments are the high-level data needed to start the workflow (e.g., `FileMetadata`).
-   **Outputs:**
    -   Typically returns a final result or a summary object that represents the outcome of the entire workflow (e.g., `SampleArtifact` or a boolean success flag).
    -   It manages the side effects of the operation (e.g., creating files, updating databases) by delegating to the appropriate workers.