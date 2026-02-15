# Design Pattern: Factory

The Factory pattern is a creational design pattern that provides an interface for creating objects in a superclass, but allows subclasses or a separate class to alter the type of objects that will be created. It encapsulates the logic of object instantiation.

## 1. Concept

Instead of calling a class constructor directly (e.g., `my_object = MyClass(a, b)`), you call a "factory" method. This factory method contains the logic (often a conditional `if/elif/else` block) to determine which specific class to instantiate based on the provided inputs. It then creates an instance of that class and returns it.

This decouples the client code (which needs an object) from the concrete classes that are being instantiated. The client only needs to know about the factory and the common interface that the created objects share.

## 2. Use Cases

-   **Complex Object Creation:** When the process of creating an object is complex and involves conditional logic.
-   **Decoupling:** When you want to decouple your client code from specific implementations. The client code can work with a generic interface, and the factory provides the concrete object that implements it.
-   **Centralizing Creation Logic:** When you need a single, centralized place to manage the creation of a family of related objects. This is exactly how it's used in our `SamplerFactory` to choose a `SamplingStrategy`.

## 3. Simple Code Example

Imagine a system that needs to create different types of notification objects (Email, SMS, Push Notification).

```python
from abc import ABC, abstractmethod

# The common interface for all products the factory can create
class Notification(ABC):
    @abstractmethod
    def send(self, message: str):
        pass

# Concrete product classes
class EmailNotification(Notification):
    def send(self, message: str):
        print(f"Sending EMAIL: {message}")

class SmsNotification(Notification):
    def send(self, message: str):
        print(f"Sending SMS: {message}")

class PushNotification(Notification):
    def send(self, message: str):
        print(f"Sending PUSH: {message}")

# The Factory class
class NotificationFactory:
    def get_notification(self, channel: str) -> Notification:
        """
        The factory method. It contains the logic to select
        and instantiate the correct class.
        """
        if channel == "email":
            return EmailNotification()
        if channel == "sms":
            return SmsNotification()
        if channel == "push":
            return PushNotification()
        
        raise ValueError(f"Unknown notification channel: {channel}")

# --- Main application logic ---
# The client doesn't know about EmailNotification or SmsNotification.
# It only knows about the factory and the Notification interface.
factory = NotificationFactory()

def send_alert(alert_message: str, preferred_channel: str):
    # Ask the factory for the appropriate notification object
    notification_sender = factory.get_notification(preferred_channel)
    
    # Use the object via its common interface
    notification_sender.send(alert_message)

# Send notifications using different channels
send_alert("Your order has shipped!", "email")
send_alert("Your driver is arriving.", "sms")
```

## 4. Dos and Don'ts

-   **DO** ensure all objects created by the factory share a common interface (or base class). This is essential for the client to use them interchangeably.
-   **DO** use the Factory pattern to encapsulate complex `if/elif/else` chains related to object creation.
-   **DON'T** make the factory responsible for more than just object creation. It shouldn't contain business logic related to *using* the objects.
-   **DON'T** use a factory if the object creation is simple and there is only one type of object to create. In that case, direct instantiation (`MyClass()`) is simpler.

## 5. Benefits and Drawbacks

### Benefits
-   **Abstraction:** Hides the complexity of object creation from the client.
-   **Decoupling:** The client code is not tied to concrete classes, making the system more flexible.
-   **Centralization:** All object creation logic is in one place, making it easier to manage and modify.
-   **Single-Responsibility Principle:** The factory has one responsibility: creating objects.

### Drawbacks
-   **Increased Complexity:** Introduces another class (the factory itself), which can be overkill for simple scenarios.
-   **Can Require Subclassing:** In some variations of the pattern (Abstract Factory), you may need to create a whole hierarchy of factory classes, which can add complexity.

## 6. Schema

-   **Purpose:** To encapsulate the logic of object instantiation, decoupling the client from the concrete classes being created.
-   **Inputs:**
    -   The factory method takes one or more parameters that determine which concrete object to create (e.g., a string, an enum, a configuration object).
-   **Outputs:**
    -   The factory method returns an **instance** of a concrete class, but it is typed as the common abstract interface. This allows the client to treat all created objects the same way.