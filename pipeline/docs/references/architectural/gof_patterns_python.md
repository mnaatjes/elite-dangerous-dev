# Gang of Four (GoF) Patterns in Python

The Gang of Four (GoF) patterns, introduced in the 1994 book *Design Patterns: Elements of Reusable Object-Oriented Software*, are divided into three categories. In Python, many of these are simplified or even built-in (like Iterators or Decorators).

## Creational Patterns

| Pattern | Purpose | Python Simple Example |
| :--- | :--- | :--- |
| **Abstract Factory** | Creates families of related objects. | "A UI factory creating a ""LinuxButton"" and ""LinuxCheckbox.""" |
| **Builder** | Constructs complex objects step-by-step. | "A HouseBuilder adding walls, roof, and windows separately." |
| **Factory Method** | "Provides an interface for creating objects, but lets subclasses decide which class to instantiate." | A Logistics class where subclasses return either a Truck or Ship object. |
| **Prototype** | Creates new objects by cloning an existing one. | Using `copy.deepcopy(existing_object)` to create a pre-configured instance. |
| **Singleton** | Ensures a class has only one instance. | A DatabaseConnection class that returns the same instance every time it's called. |

## Structural Patterns

| Pattern | Purpose | Python Simple Example |
| :--- | :--- | :--- |
| **Adapter** | Allows incompatible interfaces to work together. | A wrapper that makes a 3rd-party XML API look like JSON to your app. |
| **Bridge** | Splits a large class into two hierarchies: abstraction and implementation. | A RemoteControl class (abstraction) linked to a TV or Radio (implementation). |
| **Composite** | Treats individual objects and compositions of objects uniformly (Tree structure). | A Folder containing Files; calling `delete()` on the folder deletes everything inside. |
| **Decorator** | Adds responsibilities to objects dynamically. | A Coffee object wrapped in a MilkDecorator and SugarDecorator. |
| **Facade** | Provides a simplified interface to a complex system. | "A HomeTheater class with a `watch_movie()` method that turns on the TV, dim lights, and starts DVD." |
| **Flyweight** | Shares common parts of state between multiple objects to save memory. | "A forest of 10,000 Tree objects sharing one TreeModel (texture/mesh) but having unique positions." |
| **Proxy** | Provides a placeholder for another object to control access. | A CachedImage that only loads the real image from disk when first displayed. |

## Behavioral Patterns

| Pattern | Purpose | Python Simple Example |
| :--- | :--- | :--- |
| **Chain of Responsibility** | Passes a request along a chain of handlers. | "An ATM dispensing bills: $50 handler passes remainder to $20 handler, etc." |
| **Command** | Encapsulates a request as an object. | A Button object that stores a SaveCommand to be executed later. |
| **Interpreter** | Evaluates a language grammar or expression. | "A class that parses and executes a specific string format like ""SELECT * FROM table""." |
| **Iterator** | Accesses elements of a collection sequentially. | Python’s `__iter__` and `__next__` methods used in a `for` loop. |
| **Mediator** | Restricts direct communications between objects and forces them to collaborate via a mediator. | An AirTrafficControl tower coordinating planes so they don't talk to each other directly. |
| **Memento** | Saves and restores the previous state of an object (Undo). | "A TextEditor saving a ""snapshot"" of its text to a History list." |
| **Observer** | Notifies multiple objects about any events that happen to the object they’re observing. | A YouTubeChannel notifying all subscribed Users when a video is posted. |
| **State** | Lets an object change its behavior when its internal state changes. | A VendingMachine behaving differently if it is in HasMoney vs OutOfStock state. |
| **Strategy** | Defines a family of algorithms and makes them interchangeable. | A ShoppingCart that can use a PaypalStrategy or CreditCardStrategy at runtime. |
| **Template Method** | "Defines the skeleton of an algorithm, letting subclasses override specific steps." | A DataMiner class with a fixed `run()` method but custom `parse_file()` steps for CSV/JSON. |
| **Visitor** | Separates an algorithm from the object structure on which it operates. | An ExportVisitor that visits Circle and Square shapes to save them as XML. |
