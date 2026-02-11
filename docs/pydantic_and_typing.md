# Schemas with Pydantic and Type Reinforcement

Pydantic is a powerful Python library that provides data validation and settings management using Python type hints. It allows developers to define how data should be structured and validated, ensuring data integrity and making code more robust and easier to maintain. By leveraging standard Python type hints, Pydantic offers a developer-friendly way to enforce data contracts, both at runtime and compile time, especially when working with external data sources like APIs, databases, or configuration files.

Python's built-in `typing` module is fundamental to Pydantic, as Pydantic uses these type hints to perform its validation. This combination is particularly useful in modern data-driven applications where strong data guarantees are crucial.

```python
"""Schemas with Pydantic and Type Reinforcement"""
from datetime import datetime
from pydantic import BaseModel, Field, ValidationError, PrivateAttr, ConfigDict
from typing import Dict, Final, Any, Optional, List

# --- Helper ---
class Box:
    def __init__(self):
        self.name = "box"
        self.sides = 6

    def hello(self):
        print("Hello, I am a box!")

# --- Shape Schema --- 
class Schema(BaseModel):
    # This config tells Pydantic: "If you don't recognize the class, 
    # just check if the object is an instance of it."
    # So that List[Box] will validate
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    sides: int = Field (ge=0)
    registry: List[Box] #PrivateAttr(default_factory=list) # Defined as private
    ts: datetime = Field(description="A datetime object")


# --- Base Class --- 
class Shape:
    """
    DO NOT use schema as a direct argument of __init__!
    - This avoids Tight Coupling between data's structure and object's behavior
    - Schema cares about the delivery rules (validation)
    - Class cares about the content (logic of the message)
    """
    
    def __init__(self, name:str, sides:int, arr, ts:datetime):
        # Enforce Validation Here:
        try:
            # Create temporary schema instance
            # Pydantic logic will perform validation
            data = Schema(
                name=name,
                sides=sides,
                registry=arr,
                ts=ts
            )

            # Pass validated arguments to instance
            self.name = data.name
            self.sides = data.sides
            self.registry = data.registry
            self.ts = data.ts
        except ValidationError as e:
            raise ValueError(f"Invalid Schema data! {e}")

    def hello(self):
        print(f"Hello! I am a {self.name} I have {self.sides} sides!")

    def list_all(self):
        for b in self.registry:
            b.hello()


def test_schemas():
    b1 = Box()
    b2 = Box()
    b3 = Box()
    circle = Shape("circle", 0, [b1, b2, b3], datetime.now())
    circle.hello()
    circle.list_all()
```