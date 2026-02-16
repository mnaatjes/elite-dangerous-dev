# GoF Pattern Comparisons ("Battles")

This is the best way to understand the "gray areas" of design. Often, two patterns look identical in code, but their **intent** is what sets them apart. In a Linux-based Python environment, these "battles" usually happen when deciding how to structure your Services or Domain logic.

---

## Battle 1: Strategy vs. State
The code looks the same (delegating to another class), but the logic's intent is different.

| Feature | Strategy (The Tool) | State (The Mood) |
| :--- | :--- | :--- |
| **Intent** | Swapping *how* a task is done. | Swapping *how the object behaves* based on status. |
| **Who Switches?**| Usually the Client (the caller). | Usually the Object itself (internal transition). |
| **Example** | Choosing a compression algorithm (ZIP vs. GZIP).| A `Connection` object (Disconnected -> Connecting -> Connected). |

**The Heuristic:**
*   Use **Strategy** if you are choosing an algorithm at the start and sticking with it.
*   Use **State** if the object needs to "evolve" and change its behavior as variables change.

---

## Battle 2: Facade vs. Proxy
Both wrap a complex object, but for very different reasons.

| Feature | Facade (The Front Door) | Proxy (The Guard) |
| :--- | :--- | :--- |
| **Intent** | **Simplification**. Hiding 10 classes behind 1. | **Access Control**. Adding logic before the real call. |
| **Interface**| "Usually provides a new, simpler interface." | Usually provides the exact same interface. |
| **Example** | A `StartSystem()` call that hides DB and Cache setup. | A `SecureDatabase` that checks permissions before calling `Query()`. |

**The Heuristic:**
*   Use **Facade** when you want to make a messy subsystem easier to use.
*   Use **Proxy** when you want to add "extra stuff" (logging, caching, security) without the caller knowing.

---

## Battle 3: Factory Method vs. Abstract Factory
The most common point of confusion in creational patterns.

| Feature | Factory Method (The Item Maker) | Abstract Factory (The Theme Maker) |
| :--- | :--- | :--- |
| **Focus** | "Making *one type* of thing (e.g., a Document)." | "Making a *family* of things (e.g., a UI Theme)." |
| **Mechanism** | Uses **Inheritance** (subclasses decide). | Uses **Composition** (you pass in a factory object). |
| **Example** | `CSVExporter` vs `PDFExporter`. | "A `LinuxTheme` (makes `LinuxButton`, `LinuxWindow`, `LinuxMenu`)." |

**The Heuristic:**
*   Use **Factory Method** if you just need to create an object but want to delay the choice of class to a subclass.
*   Use **Abstract Factory** if you have multiple related objects that must match (e.g., you can't mix a Windows Button with a Linux Window).

---

## Battle 4: Decorator vs. Adapter
Both are "Wrappers," but they solve different compatibility problems.

| Feature | Decorator (The Upgrade) | Adapter (The Translator) |
| :--- | :--- | :--- |
| **Intent** | Adding features without changing the class. | Fixing a mismatch between two interfaces. |
| **Relationship**| The wrapper and the wrapped have the *same interface*. | The wrapper *changes the interface* to match a target. |
| **Example** | Adding Encryption to a `FileStream`. | Making a `LegacyUser` class work with a `NewAuthSystem` interface. |

**The Heuristic:**
*   Use **Decorator** when you want to add behavior (like logging) to an object at runtime.
*   Use **Adapter** when you have a library that works perfectly, but its method names don't match what your code expects.

---

## Summary Checklist

If you are looking at a requirement and aren't sure which pattern to pick, run this mental "Test":

1.  Is it about **creating an object**?
    *   Look at **Factories** or **Builder**.
2.  Is it about **connecting two existing things**?
    *   Look at **Adapter** or **Mediator**.
3.  Is it about **adding "if/then" logic**?
    *   Look at **Strategy** or **State**.
4.  Is it about **hiding complexity**?
    *   Look at **Facade**.
