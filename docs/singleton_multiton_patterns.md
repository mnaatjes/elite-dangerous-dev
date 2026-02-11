# Singleton and Multiton Design Patterns in Python

Design patterns are reusable solutions to common problems in software design. The Singleton and Multiton patterns are creational patterns that control object instantiation, ensuring that a class has only one instance (Singleton) or a limited number of instances (Multiton) for specific keys or types.

## Singleton Pattern

The **Singleton pattern** restricts the instantiation of a class to a single object. This is useful when exactly one object is needed to coordinate actions across the system. Common use cases include logger objects, configuration managers, or objects that manage a single resource like a database connection pool.

In Python, the Singleton pattern is often implemented by overriding the `__new__` method. The `__new__` method is responsible for creating a new instance of a class, while `__init__` is responsible for initializing that instance. By controlling `__new__`, you can ensure that only one instance is ever created and returned. Subsequent calls to the class constructor will return the same instance.

## Multiton Pattern

The **Multiton pattern** is an extension of the Singleton pattern. Instead of ensuring only one instance of a class, it ensures that only a limited number of instances are created, typically managed by a key or name. This means that for each unique key, there will be a single instance of the class. It's useful when you need to manage a pool of objects where each object serves a specific purpose identified by a key. For example, managing multiple database connections, where each connection corresponds to a different database name.

Similar to Singleton, the Multiton pattern in Python is implemented by overriding `__new__` and maintaining a registry (usually a dictionary) within the class to store the created instances, keyed by their identifier. When a new instance is requested, `__new__` checks if an instance for that key already exists in the registry. If it does, the existing instance is returned; otherwise, a new one is created, stored in the registry, and then returned.

Both patterns emphasize controlled instantiation and can help in managing resources efficiently and preventing conflicts that might arise from multiple instances of certain types of objects.

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ValidationError
from typing import Literal, Dict, Type, Any, Optional

# --- Singleton is ALSO the Base Class ---
# --- Multiton is ALSO the Base Class (with mechanism for tracking different instances) ---
class Multiton:
    # For tracking multiton instances
    # Belongs to the cls
    _registry = {}

    # Allowable instance keys | schemas
    _definitions = {
        "circle": None,
        "square": None,
        "triangle": None
    }

    def __new__(cls, name, *args, **kwargs):
        """
        Static Method (not marked, but is) that MUST return a new instance of the class.
        - Needs parameters to decide how or if to create object
        - Checks _instance | Creates _instance
        - Controls creation: Singleton, Multiton, Immutables
        - MUST return a new instance
        
        Avoid explicit properties in __new__
        - __new__ passes arguments to __init__
        - If __init__ changes without __new__ having (*args, **kwargs) -> result TypeError | Missing parameters
        - *args and **kwargs makes __new__ Signature Agnostic | __new__ does NOT care what the parameters are

        In Multiton Design Pattern __new__ needs at least 1 explicit argument to determine WHICH instance (in the cls._registry = {...}) to return
        - __new__(<name>) -> searches cls._registry for the Singleton instance named <name> and returns it
        - Because Singleton(<name_one>) returns a different instance than 
        """
        # Multiton: Perform cls._definitions check for allowed instances
        if name not in cls._definitions:
            raise ValueError(f"The schema '{name}' is NOT Supported!")

        # Singleton: Check that _instance has been saved in Class
        # Multiton: Check that <name> [instance] is registered in container (cls._registry)
        if name not in cls._registry:
            # Create new instance
            # super() creates an instance of super class 
            #   - A proxy object holding context: class being defined, e.g. Singleton: cls._instance = super().__new__(cls)
            #   - The Target: the object or class being acted upon: cls as in @classmethod
            # super().__next__(cls) returns the instance of Singleton | Multiton
            instance = super().__new__(cls)

            # Store in registry
            cls._registry[name] = instance
            print(f"Instance of 'Multiton' name: {name} Created...")
        
        # Return instance for __init__
        return cls._registry[name]

    def __init__(self, name, size):
        """
        Initializer which receives the instances created by __new__() as self
        - Populates instance with data | Controls initial state | Fills memory with specific values

        """
        # Guard against re-initialization of either the Singleton or Multiton("<name>")
        # Check if Self (instance) has been initialized
        if not hasattr(self, "_initialized"):
            self._initialized   = True

            # Assign Properties
            self.name = name
            self.size = size

    @classmethod
    def list_instances(cls):
        """Returns list of instance names in cls._registry"""
        return list(cls._registry.keys())

    @classmethod
    def get_instances(cls):
        """Returns dict of instance names in cls._registry"""
        return cls._registry
    
# --- Implementing Tests ---
def test_registry():
    print(" --- Testing Registry...")
    circle = Multiton("circle", 2)
    square = Multiton("square", 6)
    #oval = Multiton("oval", 3)
    print(f"The following instances were created: {circle.list_instances()}")
```