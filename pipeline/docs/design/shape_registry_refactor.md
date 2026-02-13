# Shape Registry Refactor: Diagnosis and Corrected Implementation

This document details the issues found in the provided `ShapeRegistry` code, explains the conflicts between class/instance properties and methods, and provides a corrected implementation adhering to the Singleton pattern, Pydantic schema validation, and attribute chaining.

---

## 1. Diagnosis of Original Code Issues

Below is a point-by-point breakdown of the errors and conflicts identified in your original `ShapeRegistry` implementation:

### Schema Definitions (`ShapeSchema`, `CircleSchema`)

*   **Issue:** `CircleSchema.sides: None` is incorrect. `None` is a value, not a type annotation. If a property is optional or not applicable, it should be type-hinted with `Optional[Type]` (e.g., `Optional[int] = None`).
*   **Issue:** The schemas (e.g., `ShapeSchema` and `CircleSchema`) did not consistently define all properties expected by the `Shape` class's constructor (like `version`). This created a mismatch between schema validation and object instantiation.
*   **Correction Principle:** Schemas should accurately reflect all data points needed to construct and describe a `Shape` instance, including constant, default, and dynamic properties.

### Generic `Shape` Class Issues

*   **Issue:** The `Shape` class was declared `ABC` (Abstract Base Class) but its `draw` method was not an `abstractmethod`. If `Shape` is truly abstract, it should have at least one abstract method. If not, it shouldn't inherit from `ABC`.
*   **Issue:** The `draw` method had a `-> str` type hint but used `print()`, which returns `None`. A method type-hinted `-> str` should return a string.
*   **Issue:** `Shape.__init__(self, name:str, sides:int, version:str)` was too rigid. To work seamlessly with Pydantic schemas, the `Shape` constructor should be more generic, accepting `**properties` and dynamically setting attributes based on the validated schema data.

### `ShapeRegistry` Constructor (`__new__` vs. `__init__`)

*   **Issue:** `def __new__(cls, sides:int, version:str)` and `def __init__(self, sides:int, version:str): pass` represented a parameter mismatch problem. Python passes the same arguments from the constructor call (`ShapeRegistry(...)`) to both `__new__` and then `__init__`. If `__init__` doesn't match the signature of the call, it will raise a `TypeError`.
*   **Issue (Major Design Flaw):** The `for` loop inside `__new__` that called `cls._register_shape(name, sides, version)` used the `sides` and `version` parameters passed to the `ShapeRegistry`'s constructor directly. This completely bypassed the intended Pydantic schema validation and used the *registry's* construction parameters for *all* shapes, rather than specific shape properties.

### Class vs. Instance Attributes (`_managed_shapes`)

*   **Issue:** `_managed_shapes: Dict[str, Shape] = {}` was defined as a class attribute. While `cls._managed_shapes = {}` inside `__new__` correctly initialized it as an *instance attribute* on the singleton object, subsequent `@classmethod`s (like `_register_shape`) would try to access `cls._managed_shapes`, which could ambiguously refer to the class attribute or lead to unexpected behavior if not handled precisely via `cls._instance._managed_shapes`.
*   **Correction Principle:** For singleton instance data, it's clearest to initialize it on the `self` (the instance) within a guarded `__init__` and then access it consistently via `self._managed_shapes`.

### Schema Validation Bypass

*   **Issue:** The `_register_shape` method directly called `Shape(name, sides, version)`. This bypassed the entire Pydantic schema validation system. The purpose of having schemas is to validate and normalize the data before creating the final `Shape` object.

### `_register_shape` Logic

*   **Issue:** The method was a `@classmethod` and was called from `__new__`. It should ideally be an *instance method* so it operates on the `self._managed_shapes` of the singleton instance.
*   **Issue:** It did not use the schemas for validation or proper `Shape` construction.

### `get_instance` Method Naming & Logic

*   **Issue:** The method was named `get_instance`, which is typically used to retrieve the *singleton registry itself*. Here, it was intended to retrieve a *shape*. This causes confusion. It should be renamed to `get_shape`.
*   **Issue:** The method contained validation-related checks and `ValidationError` raising, which belongs to the `register_shape` step. `get_shape` should only retrieve.
*   **Issue:** Inconsistent casing: `name.lower()` was used for `SCHEMA_MAP` lookup, but `name` (original case) was used for `_managed_shapes`. This can lead to `KeyError` if keys are not consistently cased.

### `list_inventory` Error

*   **Issue:** `return list(cls._instances.keys())` was incorrect. `_instances` is the `_instance` variable itself, not a dictionary of shapes. It should have accessed `_managed_shapes`.

### `__getattr__` Empty

*   **Issue:** The `__getattr__` method was empty (`pass`), meaning attribute-style access (e.g., `registry.square.draw()`) would not work as intended.

---

## 2. Corrected Code Implementation

Below is the complete, corrected code. Key changes include:
*   Refined Pydantic schemas with `Literal` types for constants and `Optional` for optional fields.
*   A generic `Shape` class that takes `**properties` to be flexible with schema data.
*   A `ShapeRegistry` implementing the Singleton pattern.
*   Guarded `__init__` to prevent re-initialization.
*   `register_shape` method that correctly uses `SCHEMA_MAP` for Pydantic validation and then constructs the `Shape`.
*   Consistent use of instance attributes (`self._managed_shapes`).
*   Renamed `get_instance` to `get_shape`.
*   Corrected `list_inventory` to return keys from `_managed_shapes`.
*   Proper implementation of `__getattr__` for attribute chaining.
*   Automatic registration of default shapes in `__init__` (optional, but demonstrates usage).

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, ValidationError
from typing import Literal, Dict, Type, Any, Optional

# --- 1. Pydantic Schemas ---
# Schemas define the structure and validation rules for each shape type.
# They also provide default values for constant properties.

class ShapeSchema(BaseModel):
    """Base schema for common shape properties."""
    shape_type: str # This field will dynamically hold "circle", "square", etc.
    name: str = Field(..., description="Unique name/ID for this shape instance")
    version: str # All shapes have a version

class CircleSchema(ShapeSchema):
    """Schema for a Circle shape."""
    shape_type: Literal["circle"] = "circle" # Constant/Literal field for the type
    sides: Optional[None] = None # Circle technically has no straight sides, or you might represent it as 0
    radius: float = Field(..., gt=0, description="Radius of the circle, required")

class SquareSchema(ShapeSchema):
    """Schema for a Square shape."""
    shape_type: Literal["square"] = "square" # Constant/Literal field for the type
    sides: Literal[4] = 4 # Constant: A square always has 4 sides
    side_length: float = Field(..., gt=0, description="Side length of the square, required")

class TriangleSchema(ShapeSchema):
    """Schema for a Triangle shape."""
    shape_type: Literal["triangle"] = "triangle"
    sides: Literal[3] = 3 # Constant: A triangle always has 3 sides
    base: float = Field(..., gt=0, description="Base length of the triangle")
    height: float = Field(..., gt=0, description="Height of the triangle")


# --- Global Map of Shape Type to its Pydantic Schema ---
# This dictionary serves as the source of truth for all creatable shape types
# and their validation rules.
SCHEMA_MAP: Dict[str, Type[ShapeSchema]] = {
    "circle": CircleSchema,
    "square": SquareSchema,
    "triangle": TriangleSchema,
}

# --- 2. Generic Shape Class ---
# This class is now generic and created from validated schema data.
# It does not need to be an ABC unless you plan to have truly abstract methods.
class Shape:
    """
    A generic Shape class whose properties are dynamically set from a validated schema.
    """
    def __init__(self, **properties: Any):
        # Store all validated properties from the schema directly on the instance
        for key, value in properties.items():
            setattr(self, key, value)

    def draw(self) -> str:
        """Draws the shape, returning a descriptive string."""
        # Access properties that are guaranteed to exist by the schema
        name = getattr(self, 'name', 'unknown')
        shape_type = getattr(self, 'shape_type', 'unknown')
        version = getattr(self, 'version', 'unknown')

        # Dynamically build property string, excluding standard ones
        display_props = {k: v for k, v in self.__dict__.items()
                         if k not in ['name', 'shape_type', 'version']}
        props_str = ", ".join(f"{k}={v}" for k, v in display_props.items())

        return f"I am a {shape_type.capitalize()} (named '{name}', version {version}) and my properties are: {props_str}!"

    def __repr__(self) -> str:
        return f"<Shape: {getattr(self, 'name', 'N/A')} (Type: {getattr(self, 'shape_type', 'N/A')})>"


# --- 3. ShapeRegistry (Singleton & Factory) ---
class ShapeRegistry:
    """
    A Singleton Registry for Shape objects.
    It acts as a Factory for creating shapes based on predefined Pydantic schemas.
    Allows attribute-style access to registered shapes.
    """
    _instance: Optional['ShapeRegistry'] = None
    # _managed_shapes will be an instance attribute initialized in __init__

    def __new__(cls, *args: Any, **kwargs: Any) -> 'ShapeRegistry':
        """Ensures only one instance of the ShapeRegistry is ever created."""
        if cls._instance is None:
            print("Creating the one and only instance of ShapeRegistry.")
            # Delegate to the parent class (object) to create the actual instance
            cls._instance = super(ShapeRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self, version: str):
        """
        Initializes the ShapeRegistry instance.
        This will be called every time ShapeRegistry(...) is invoked,
        but internal setup should only occur once for the singleton.
        """
        # Guard against re-initialization if __init__ is called multiple times on the same instance
        if not hasattr(self, '_managed_shapes'):
            print(f"Initializing ShapeRegistry (version: {version}).")
            self._managed_shapes: Dict[str, Shape] = {}
            self._registry_version = version # Store this on the instance

            # Automatically register all defined shapes from SCHEMA_MAP upon initialization
            # For this to work, schemas must define sufficient default properties
            # or the registry constructor needs to accept initial data for each.
            # Here, we assume a default `name` might not be in schema, so we pass one.
            print("Auto-registering default shapes from SCHEMA_MAP...")
            for shape_type_key, schema_class in SCHEMA_MAP.items():
                try:
                    # For demonstration, let's create a default name
                    default_shape_name = f"default_{shape_type_key}"
                    
                    # Pass the registry's version to the shape
                    self.register_shape(
                        name=default_shape_name,
                        shape_type=shape_type_key,
                        version=version # Pass the version from the registry
                    )
                    print(f"  - Auto-registered: {default_shape_name}")
                except Exception as e:
                    print(f"  - Failed to auto-register {shape_type_key}: {e}")
        else:
            print(f"ShapeRegistry already initialized. Version: {self._registry_version}")


    def register_shape(self, name: str, shape_type: str, **properties: Any) -> Shape:
        """
        Validates properties using the appropriate Pydantic schema
        and registers a new Shape object in the registry.

        :param name: A unique identifier for this specific shape instance (used for attribute access).
                         This should be a valid Python identifier.
        :param shape_type: The type of shape (e.g., "circle", "square") to look up in SCHEMA_MAP.
        :param properties: Keyword arguments for properties specific to this shape instance.
        :return: The validated and registered Shape object.
        :raises ValueError: If the shape_type is unknown or validation fails.
        """
        # --- Input Validation (for name used as attribute) ---
        if not isinstance(name, str) or not name.isidentifier():
             raise ValueError(f"'{name}' is not a valid Python identifier. "
                              f"Cannot be used as an attribute name for shape access.")
        if name in self._managed_shapes:
            print(f"Warning: Shape '{name}' already registered. Overwriting.")

        # --- Schema Lookup ---
        if shape_type not in SCHEMA_MAP:
            raise ValueError(f"Unknown shape type: '{shape_type}'. Available types: {list(SCHEMA_MAP.keys())}")
        ShapePydanticSchema = SCHEMA_MAP[shape_type]

        # --- Property Merging and Validation ---
        # Merge provided properties with the name, then validate with Pydantic
        all_properties = {"name": name, "shape_type": shape_type, **properties}
        
        try:
            validated_model = ShapePydanticSchema(**all_properties)
        except ValidationError as e:
            raise ValueError(
                f"Validation error for shape '{name}' (type: '{shape_type}'): {e.errors()}"
            ) from e

        # --- Shape Instance Creation ---
        # Create the generic Shape instance from the validated model's data
        shape_instance = Shape(**validated_model.model_dump())
        self._managed_shapes[name] = shape_instance
        return shape_instance

    def get_shape(self, name: str) -> Optional[Shape]:
        """Retrieves a registered Shape object by its unique name."""
        return self._managed_shapes.get(name)

    def list_registered_shapes(self) -> Dict[str, Shape]:
        """Returns a dictionary of all registered shapes."""
        return self._managed_shapes

    def __getattr__(self, name: str) -> Shape:
        """
        Enables attribute-style access to registered shapes (e.g., registry.my_circle).
        """
        if name in self._managed_shapes:
            return self._managed_shapes[name]
        # Standard Python behavior: raise AttributeError if not found
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


# --- Implementing Tests ---
def test_registry():
    print("
--- Initializing Registry ---")
    # First call creates and initializes the singleton
    registry1 = ShapeRegistry(version="1.0")
    print(f"Registry 1 ID: {id(registry1)}")
    
    # Second call returns the same instance, __init__ is guarded
    registry2 = ShapeRegistry(version="2.0") # Version passed here is ignored by guarded __init__
    print(f"Registry 2 ID: {id(registry2)}")
    print(f"Are registry1 and registry2 the same instance? {registry1 is registry2}")
    
    print("
--- Registering Custom Shapes ---")
    try:
        # Register a custom circle (name must be a valid identifier)
        custom_circle = registry1.register_shape("my_custom_circle", "circle", radius=7.5, version="1.1")
        print(f"Registered: {custom_circle}")

        # Register a custom square
        custom_square = registry1.register_shape("my_custom_square", "square", side_length=10.0, version="1.2")
        print(f"Registered: {custom_square}")

    except ValueError as e:
        print(f"Error registering custom shape: {e}")

    print("
--- Accessing Shapes via Attribute Chaining ---")
    # Access the auto-registered default circle
    print(registry1.default_circle.draw())

    # Access the custom square
    print(registry2.my_custom_square.draw()) # Works via registry2 because it's the same instance

    print("
--- Accessing Shapes via get_shape Method ---")
    retrieved_triangle = registry1.get_shape("default_triangle")
    if retrieved_triangle:
        print(retrieved_triangle.draw())
    
    print("
--- Listing All Registered Shapes ---")
    print("Registered Shapes:")
    for name, shape in registry1.list_registered_shapes().items():
        print(f"  - {name}: {shape}")

    print("
--- Testing Non-Existent Shape Access ---")
    try:
        print(registry1.non_existent_shape.draw())
    except AttributeError as e:
        print(f"Caught expected error: {e}")

    print("
--- Testing Schema Validation Error ---")
    try:
        registry1.register_shape("bad_circle", "circle", radius=-5.0, version="1.0") # radius must be > 0
    except ValueError as e:
        print(f"Caught expected validation error: {e}")

```
---

## 3. Todo List for Your Original Code

Based on the diagnosis, here's a structured todo list to correct your original code:

### Task: Refactor Schema Definitions

-   **Why:** Ensure schemas accurately reflect properties needed for `Shape` and use correct type hints.
-   **What to do:**
    1.  **Correct `CircleSchema.sides`:** Change `sides: None` to `sides: Optional[None] = None` or simply remove `sides` from `CircleSchema` if it's not applicable (and `ShapeSchema` doesn't enforce it as required).
    2.  **Add `version` to schemas:** Ensure all schemas (`ShapeSchema`, `CircleSchema`, etc.) include a `version: str` field if `Shape` expects it.
    3.  **Refine `ShapeSchema`:** Make `shape_type: str` a common field, and use `Literal["circle"]`, `Literal["square"]` in subclasses.
    4.  **Add all relevant properties:** Ensure schemas cover all properties that will be part of the `Shape` object.

### Task: Refactor Generic `Shape` Class

-   **Why:** Make `Shape` flexible to accept properties from any validated schema and fix `ABC`/`draw` issues.
-   **What to do:**
    1.  **Remove `ABC` inheritance** if `draw` is not abstract.
    2.  **Modify `Shape.__init__`:** Change its signature to `def __init__(self, **properties: Any):` to dynamically accept and store all validated properties from the schema.
    3.  **Correct `draw` method:** Change `print()` to `return f"..."` to match the `-> str` type hint. Ensure it accesses properties dynamically (e.g., `getattr(self, 'name', 'unknown')`).

### Task: Refactor `ShapeRegistry` Constructor and Initialization

-   **Why:** Ensure proper Singleton initialization, consistent argument handling, and prevent schema bypass.
-   **What to do:**
    1.  **Simplify `__new__`:** It should primarily be responsible for ensuring only one instance is created and returned. Do *not* put shape registration logic here. Accept `*args: Any, **kwargs: Any` to pass arguments to `__init__`.
    2.  **Guard `__init__`:** Add a `if not hasattr(self, '_managed_shapes'):` check at the beginning of `__init__` to ensure the registry's internal state (`_managed_shapes`, `_registry_version`) is initialized only once.
    3.  **Pass `version` to `__init__` only:** The `ShapeRegistry` constructor should primarily take arguments relevant to the *registry itself* (like its `version`).

### Task: Implement Correct Shape Registration Logic

-   **Why:** Utilize Pydantic schemas for validation and correct `Shape` object creation.
-   **What to do:**
    1.  **Create a `register_shape` instance method:** This method (not a class method) will take `name: str`, `shape_type: str`, and `**properties: Any`.
    2.  **Enforce valid `name`:** Add a check `name.isidentifier()` if `name` is to be used for attribute access.
    3.  **Schema Lookup:** Use `SCHEMA_MAP` to get the correct Pydantic schema for `shape_type`.
    4.  **Merge and Validate:** Combine all passed properties (including `name`, `shape_type`) and validate them using the retrieved Pydantic schema (`ShapePydanticSchema(**all_properties)`).
    5.  **Create `Shape`:** Construct the `Shape` object using `Shape(**validated_model.model_dump())`, passing all validated data.
    6.  **Store in `_managed_shapes`:** Store the created `Shape` instance in `self._managed_shapes`.
    7.  **Remove registration logic from `__new__`:** Move any shape registration (e.g., auto-registration of defaults) into the *guarded part* of `__init__` or a separate method.

### Task: Refactor `get_instance` Method

-   **Why:** Improve clarity and separation of concerns.
-   **What to do:**
    1.  **Rename `get_instance` to `get_shape`:** This more accurately reflects its purpose.
    2.  **Change to instance method:** Make it `def get_shape(self, name: str)`.
    3.  **Simplify logic:** It should simply retrieve the shape from `self._managed_shapes.get(name)` and *not* perform validation or raise `ValidationError`.

### Task: Refactor `list_inventory` Method

-   **Why:** Correctly access the stored shapes.
-   **What to do:**
    1.  **Change to instance method:** Make it `def list_registered_shapes(self)`.
    2.  **Correct access:** Return `list(self._managed_shapes.keys())` or `list(self._managed_shapes.values())` depending on whether you want names or shape objects.

### Task: Implement `__getattr__`

-   **Why:** Enable attribute-style access for registered shapes.
-   **What to do:**
    1.  **Implement `def __getattr__(self, name: str):`**
    2.  **Lookup in `_managed_shapes`:** If `name` is in `self._managed_shapes`, return the corresponding `Shape` object.
    3.  **Raise `AttributeError`:** If not found, `raise AttributeError(...)` to maintain standard Python behavior.

This comprehensive refactoring will result in a robust, clear, and functional `ShapeRegistry`.
