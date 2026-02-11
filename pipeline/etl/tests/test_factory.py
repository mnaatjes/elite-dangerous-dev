from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ValidationError
from typing import Literal, Dict, Type, Any, Optional

class ShapeSchema(BaseModel):
    name: str
    sides:int

class CircleSchema(BaseModel):
    name: str
    sides: None
    version: str

# Const declaration with Typing
SCHEMA_MAP: Dict[str, Type[ShapeSchema]] = {
    "circle": CircleSchema,
    "square": ShapeSchema
}


# --- Codebase for Factory ---
class Shape(ABC):
    def __init__(self, name:str, sides:int, version:str):
        self.name = name
        self.sides = sides
        self.version = version

    def draw(self) -> str:
        print(f"I am a {self.name} and I have {self.sides} sides!")

class ShapeRegistry:
    _managed_shapes: Dict[str, Shape] = {}
    _instance = None

    def __new__(cls, sides:int, version:str):
        # Check that a Registry Instance doesn't already exist
        if cls._instance is None:
            # Create new Instance of Registry
            # Initialize _instances dict
            cls._instance = super(ShapeRegistry, cls).__new__(cls)
            cls._managed_shapes = {}

        # Register Declared Shapes
        for name, schema in SCHEMA_MAP.items():
            cls._register_shape(name, sides, version)

        # Return Registry Instance
        return cls._instance

    def __init__(self, sides:int, version:str):
        pass

    @classmethod
    def _register_shape(cls, name:str, sides:int, version:str):
        shape = Shape(name, sides, version)
        cls._managed_shapes[name] = shape

    @classmethod
    def get_instance(cls, name: str) -> Shape:
        if name.lower() in SCHEMA_MAP:
            if name in cls._managed_shapes:
                return cls._managed_shapes[name]
            
            # Shape was not registered and cannot be accessed
            raise KeyError(f"Shape {name} is NOT registered! It must be registered during Initialization!")
        # Not in Schema Map; Cannot Be Registered
        raise ValidationError(f"Shape name {name} has no schema and cannot be registered!")

    @classmethod
    def list_inventory(cls):
        return list(cls._instances.keys())

    def __getattr__(self, name):
        pass

# --- Implementing Tests ---
def test_registry():
    registry = ShapeRegistry(3, "1.0")
    print(registry)
    registry.get_instance("circle").draw()
    registry.square.draw()