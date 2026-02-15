# Design Pattern: Strategy

The Strategy pattern is a behavioral design pattern that enables selecting an algorithm at runtime. Instead of implementing a single algorithm directly, code receives runtime instructions and selects an algorithm from a "family" of interchangeable algorithms.

## 1. Concept

The core idea of the Strategy pattern is to take a group of related algorithms, put each of them into its own separate class, and make their objects interchangeable. The main class, known as the **Context**, holds a reference to one of these **Strategy** objects. The Context doesn't know the concrete details of the strategy; it just knows that the strategy has a method that can be executed. When the Context needs to run the algorithm, it calls the execution method on its linked strategy object.

This allows the algorithm to be swapped out independently from the class that uses it.

## 2. Use Cases

-   **Multiple Variants of an Algorithm:** When you have many variations of the same algorithm (e.g., different ways to sample a file, different ways to compress a file, different ways to sort a list).
-   **Eliminating `if/elif/else` Chains:** When you have a single class with a large conditional statement that switches between different behaviors based on some property. The Strategy pattern allows you to replace this conditional with separate Strategy classes.
-   **Isolating Business Logic:** When you want to isolate the implementation details of different algorithms from the business logic that uses them.

## 3. Simple Code Example

Imagine a simple navigation app that can calculate routes for driving, walking, or public transit.

```python
from abc import ABC, abstractmethod

# The Strategy Interface
class RoutingStrategy(ABC):
    @abstractmethod
    def calculate_route(self, start: str, end: str) -> str:
        pass

# Concrete Strategies
class DrivingStrategy(RoutingStrategy):
    def calculate_route(self, start: str, end:str) -> str:
        return f"Calculating DRIVING route from {start} to {end}: Follow I-5 S..."

class WalkingStrategy(RoutingStrategy):
    def calculate_route(self, start: str, end:str) -> str:
        return f"Calculating WALKING route from {start} to {end}: Use pedestrian bridge..."

class TransitStrategy(RoutingStrategy):
    def calculate_route(self, start: str, end:str) -> str:
        return f"Calculating TRANSIT route from {start} to {end}: Take Bus #44..."

# The Context
class Navigator:
    def __init__(self, strategy: RoutingStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: RoutingStrategy):
        """Allows changing the strategy at runtime."""
        self._strategy = strategy

    def find_route(self, start_point: str, end_point: str):
        """The context delegates the work to its current strategy."""
        route_details = self._strategy.calculate_route(start_point, end_point)
        print(route_details)

# --- Main application logic ---
# The client decides which strategy to use
start_location = "City Hall"
destination = "Museum"

# Calculate a driving route
navigator = Navigator(DrivingStrategy())
print("Finding my driving route:")
navigator.find_route(start_location, destination)

print("-" * 20)

# The user changes their mind and wants to walk
print("Finding my walking route:")
navigator.set_strategy(WalkingStrategy())
navigator.find_route(start_location, destination)
```

## 4. Dos and Don'ts

-   **DO** ensure all concrete strategies implement the exact same interface (e.g., inherit from the same abstract base class).
-   **DO** use a Factory pattern in conjunction with the Strategy pattern to decide which strategy to instantiate. This keeps the client code clean, as seen in our pipeline's `SamplerFactory`.
-   **DON'T** use the Strategy pattern for algorithms that are not related or do not have the same goal. It's for variations of the *same* task.
-   **DON'T** over-engineer. If you only have two simple, rarely changing behaviors, a simple `if/else` statement might be more readable and maintainable.

## 5. Benefits and Drawbacks

### Benefits
-   **Flexibility and Extensibility:** You can introduce new strategies without changing the Context class or any other strategies.
-   **Single-Responsibility Principle:** Each strategy has a single responsibility: to implement one specific algorithm.
-   **Clean Code:** It helps to replace large conditional statements with cleaner, more organized code.
-   **Runtime Swapping:** You can switch algorithms at runtime.

### Drawbacks
-   **Increased Complexity:** It can increase the number of classes and objects in your application, which can be overkill for simple cases.
-   **Client Awareness:** The client often needs to be aware of the different strategies and decide which one to use (though this can be hidden behind a Factory).

## 6. Schema

-   **Purpose:** To define a family of interchangeable algorithms and allow a client to select one at runtime.
-   **Inputs:**
    -   The **Context** class is initialized with a concrete **Strategy** object.
    -   The client calls a method on the Context, providing the data needed for the algorithm (e.g., start and end points).
-   **Outputs:**
    -   The Context delegates the call to the Strategy object, which performs the algorithm and returns the result to the Context, which then passes it back to the client.