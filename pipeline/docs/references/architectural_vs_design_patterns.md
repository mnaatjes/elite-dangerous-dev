# Architectural vs. Design Patterns

Design patterns are typically applied at different "altitudes" of a software system. Using a pattern at the wrong altitude is a common source of "over-engineering."

## The Hierarchy of Scope

1.  **Architectural Patterns (The System "City Map")**
    These define the highest level of your application. They dictate how major components interact across the entire project or network.
    *   **Examples**: Microservices, Model-View-Controller (MVC), Layered Architecture, Orchestrator.
    *   **Scope**: The entire application or multi-service ecosystem.
    *   **Python Context**: Using FastAPI or Django usually forces you into an MVC or MVT architectural pattern.

2.  **Design Patterns (The "Building Blueprints")**
    These are the Gang of Four patterns. They solve specific problems within a single module or a group of related classes.
    *   **Examples**: Strategy, Observer, Factory, Adapter.
    *   **Scope**: A single functional component or "subsystem" (e.g., the payment processing module).
    *   **Python Context**: Implementing a PaymentProcessor class that can swap between Stripe and PayPal using the Strategy pattern.

3.  **Idioms / Coding Patterns (The "Interior Design")**
    These are language-specific ways of solving small-scale problems. They are often "low-level" patterns that might be a single line of code.
    *   **Examples**: List comprehensions, Context Managers (`with` statements), Decorators.
    *   **Scope**: A single function or class method.
    *   **Python Context**: Using a `@property` decorator is a Pythonic idiom that implements the Getter/Setter pattern without the boilerplate.

### Pattern Interdependence

Patterns often "nest" within each other to solve a complete problem. A common "Pattern Stack" looks like this:

*   **Macro Level (Architectural)**: You use an Orchestrator to manage a data pipeline.
*   **Meso Level (Structural)**: Inside that Orchestrator, you use a Facade to hide the complexity of the 3rd party APIs you are calling.
*   **Micro Level (Creational)**: The Facade uses a Factory to decide which API client object to create based on the input data.

---

## The Orchestrator Pattern

The "Orchestrator" pattern is often missing from classic Object-Oriented Programming (OOP) lists because it isn't one of the original 23 Gang of Four (GoF) patterns. While those 23 patterns focus on the internal structure of a single application, the Orchestrator is a more modern, high-level pattern typically found in Distributed Systems and Microservices.

Here is why it occupies a different space:

1.  **Scope**: System-Level vs. Object-Level
    Classic OOP patterns (like Factory or Strategy) deal with how classes and objects interact within a codebase. The Orchestrator pattern deals with how independent services or workflows interact to complete a business process.

2.  **The "Mediator" Connection**
    In pure OOP, the Mediator pattern is the closest relative to an Orchestrator.
    *   **Mediator**: Prevents objects from referring to each other explicitly, forcing them to communicate through a central point.
    *   **Orchestrator**: Acts as the "brain" for a complex workflow, calling Service A, waiting for a response, and then deciding whether to call Service B or Service C.

3.  **Common Contexts for Orchestrators**
    Since you are likely working in a Linux/Python environment, you probably encounter "Orchestration" in these specific forms:
    *   **Cloud/Infrastructure**: Tools like Kubernetes orchestrate the deployment and scaling of containers.
    *   **Workflow Automation**: Python libraries like Airflow, Prefect, or Temporal use an Orchestrator to manage task dependencies and retries.
    *   **Microservices (Saga Pattern)**: An Orchestrator manages distributed transactions, ensuring that if Step 2 fails, Step 1 is rolled back (compensation).

| Pattern | Category | Key Difference |
| :--- | :--- | :--- |
| **Mediator** | Behavioral (OOP) | Coordinates communication between objects to reduce coupling. |
| **Facade** | Structural (OOP) | Provides a simple interface to a complex subsystem (static). |
| **Orchestrator** | Architectural (System) | Manages the state and logic of a multi-step business process (dynamic). |

---

## Pattern Altitude Explained

In software design, **Altitude** refers to the level of abstraction at which a pattern operates. It is a way to measure the "blast radius" of a design decision. If you change a Micro pattern, you usually only touch one file; if you change a Macro pattern, you might have to rewrite how entire modules communicate.

| Range | Level | Focus | Primary Goal | Python Tooling |
| :--- | :--- | :--- | :--- | :--- |
| **Micro** | Internal | Logic within a class | "Clean, readable code" | `self`, `@decorators` |
| **Meso** | Relationship | Interaction between classes | Low coupling (flexibility) | `abc`, Type Hinting |
| **Macro** | Subsystem | Interaction between modules | Reduced complexity (usability) | Modules, Facades, Packages |

### 1. Micro-Altitude: Internal Logic
*   **Definition**: Micro patterns focus on the internal mechanics of a single class or a specific function. They are "low-altitude" because they are invisible to the rest of the system.
*   **Articulated by**: Encapsulation and implementation details.
*   **Appraised by**: How readable and maintainable the internal code is. Does it follow the DRY (Don't Repeat Yourself) principle?
*   **Python Context**: Often involves Python-specific features like decorators, context managers, or magic methods.

**Python Example: Template Method**
This pattern defines the skeleton of an algorithm in a base class but lets subclasses override specific steps without changing the algorithm's structure.
```python
class DataProcessor:
    def run(self):
        """The 'Skeleton' - Micro-level control flow."""
        self.read_data()
        self.process_data()
        self.save_data()

    def read_data(self):
        raise NotImplementedError()

    def process_data(self):
        print("Standard processing applied")

    def save_data(self):
        print("Saving to database")

class CSVProcessor(DataProcessor):
    def read_data(self):
        print("Reading from CSV file")
```

### 2. Meso-Altitude: Relationships
*   **Definition**: Meso patterns manage the "contract" between a small group of related objects (usually 2–5). They define how these objects collaborate to achieve a single feature.
*   **Articulated by**: Interfaces, abstract base classes (ABCs), and dependency injection.
*   **Appraised by**: Coupling. Can I swap one object for another without breaking the collaborator?
*   **Python Context**: Often uses the `abc` module or "Duck Typing" to ensure different classes can work together.

**Python Example: Strategy Pattern**
This pattern allows you to switch between different algorithms (strategies) at runtime.
```python
from abc import ABC, abstractmethod

# The Interface (The Relationship Contract)
class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

class CreditCard(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid {amount} using Credit Card")

class PayPal(PaymentStrategy):
    def pay(self, amount):
        print(f"Paid {amount} using PayPal")

class ShoppingCart:
    def __init__(self, strategy: PaymentStrategy):
        self._strategy = strategy # The Meso Relationship

    def checkout(self, total):
        self._strategy.pay(total)
```
**Appraisal**: The Altitude is "Mid" because we are defining how `ShoppingCart` and `PaymentStrategy` talk to each other. We can add a `CryptoPayment` strategy without touching the `ShoppingCart` code.

### 3. Macro-Altitude: Subsystem Architecture
*   **Definition**: Macro patterns provide a unified interface or a communication protocol for an entire subsystem or a collection of modules. They sit at the "High-Altitude" entry points of your library.
*   **Articulated by**: API design, "Gateways," and "Managers."
*   **Appraised by**: Complexity reduction. Does this pattern hide the "spaghetti" of the underlying modules from the end user?
*   **Python Context**: Often implemented as a top-level package `__init__.py` or a main "Engine" class.

**Python Example: Facade Pattern**
A Facade provides a simple interface to a complex set of classes (a subsystem).
```python
class AudioSystem:
    def turn_on(self): print("Audio on")

class VideoSystem:
    def turn_on(self): print("Video on")

class LightSystem:
    def dim(self): print("Lights dimmed")

# The Macro Facade
class HomeTheaterFacade:
    def __init__(self):
        self.audio = AudioSystem()
        self.video = VideoSystem()
        self.lights = LightSystem()

    def watch_movie(self):
        """One simple call manages the entire subsystem."""
        self.lights.dim()
        self.audio.turn_on()
        self.video.turn_on()
```

## GoF Patterns by Altitude

| Pattern | Category | Hierarchy of Scope | Ideal Altitude | Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **Singleton** | Creational | Micro | Low (Method/Class) | "Managing a single global resource (e.g., a Config loader)." |
| **Factory Method** | Creational | Meso | Mid (Module) | Creating objects without knowing the exact class until runtime. |
| **Abstract Factory** | Creational | Macro | High (Subsystem) | "Providing a suite of related objects (e.g., a ""Theme"" factory)." |
| **Builder** | Creational | Meso | Mid (Module) | Constructing a complex object with many optional parts. |
| **Prototype** | Creational | Micro | Low (Method) | "Creating a new object by ""cloning"" a pre-configured state." |
| **Adapter** | Structural | Meso | Mid (Module) | Translating a 3rd party API into your internal interface. |
| **Bridge** | Structural | Macro | High (Subsystem) | "Decoupling an abstraction from its implementation (e.g., UI vs OS)." |
| **Composite** | Structural | Meso/Macro | Mid-High | "Representing tree structures (e.g., file systems or UI elements)." |
| **Decorator** | Structural | Micro/Meso | Low-Mid | "Adding behavior to an object without subclassing (e.g., Logging)." |
| **Facade** | Structural | Macro | High (Subsystem) | "Providing a ""single entry point"" to a messy complex library." |
| **Flyweight** | Structural | Micro | Low (Class) | Optimizing memory by sharing data across thousands of objects. |
| **Proxy** | Structural | Meso | Mid (Module) | "Controlling access to an object (e.g., Lazy loading or Auth)." |
| **Chain of Responsibility**| Behavioral | Macro | High (Subsystem) | Passing a request through a series of filters or handlers. |
| **Command** | Behavioral | Meso | Mid (Module) | "Turning an action into an object to support ""Undo"" or ""Redo.""" |
| **Interpreter** | Behavioral | Macro | High (Subsystem) | Defining a grammar for a simple language or search query. |
| **Iterator** | Behavioral | Micro | Low (Method) | Sequentially accessing elements of a collection (standard in Python). |
| **Mediator** | Behavioral | Macro | High (Subsystem) | "Centralizing communication to stop objects from ""talking"" to each other." |
| **Memento** | Behavioral | Micro/Meso | Low-Mid | Capturing and restoring an object's internal state (Snapshots). |
| **Observer** | Behavioral | Meso/Macro | Mid-High | "Notifying multiple ""subscribers"" when a state changes." |
| **State** | Behavioral | Meso | Mid (Module) | Changing an object's behavior as its internal state changes. |
| **Strategy** | Behavioral | Meso | Mid (Module) | "Swapping algorithms at runtime (e.g., sorting or payment logic)." |
| **Template Method** | Behavioral | Micro | Low (Class) | Defining a base algorithm but letting subclasses fill in the blanks. |
| **Visitor** | Behavioral | Meso | Mid (Module) | Adding new operations to a class without modifying the class. |
