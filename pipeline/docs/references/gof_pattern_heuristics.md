# GoF Pattern Heuristics

Navigating the 23 Gang of Four (GoF) patterns can feel like a maze, but they generally fall into three buckets: Creational (how you make objects), Structural (how you fit them together), and Behavioral (how they talk to each other).

In a Python/Linux context, we often favor simple functions, but these patterns emerge once complexity scales. Use these heuristics to quickly identify which pattern might fit your problem.

## Creational Patterns

| Pattern | Scenario | The Heuristic / Test |
| :--- | :--- | :--- |
| **Factory Method** | A logging library where you need a `FileLogger` for production and a `ConsoleLogger` for local dev. | """I know what I need, but I don't know the exact class name yet.""" |
| **Abstract Factory** | "Building a UI that needs to look like GNOME on Linux and Aqua on macOS (Buttons, Windows, Menus)." | """I need a family of related objects that must work together.""" |
| **Builder** | "Constructing a complex `HttpRequest` with 20 optional headers, auth, and body types." | """The constructor has too many arguments and needs a step-by-step setup.""" |
| **Prototype** | Spawning a complex Game NPC that takes 5 seconds to load from a DB; you just clone an existing one. | """It's cheaper to copy an existing object than to create a new one from scratch.""" |
| **Singleton** | A shared Connection Pool to a database that must be unique across the app. | """There must be exactly one instance, and everyone needs access to it.""" |

## Structural Patterns

| Pattern | Scenario | The Heuristic / Test |
| :--- | :--- | :--- |
| **Adapter** | Using a modern JSON-based API client where your legacy system expects XML. | """Two existing interfaces don't match, but I need them to work together.""" |
| **Bridge** | "An `OperatingSystem` class that needs to support multiple `Filesystems` (Ext4, NTFS) independently." | """I want to vary the implementation and the abstraction separately.""" |
| **Composite** | A Linux File System where a Folder can contain both Files and other Folders. | """I want to treat a single object and a group of objects the same way.""" |
| **Decorator** | "Adding ""Compression"" or ""Encryption"" to a standard `FileWriter` without changing the class." | """I want to add responsibilities to an object dynamically without subclassing.""" |
| **Facade** | "A single `Startup()` method that initializes the DB, Cache, and Auth services behind the scenes." | """The subsystem is too complex; I need a 'Simplified Front Door'.""" |
| **Flyweight** | "Rendering a forest with 10,000 trees where they all share the same `TreeModel` data." | """I have thousands of small objects that share mostly the same data.""" |
| **Proxy** | "A ""Lazy Loading"" image object that only fetches data from a remote Linux server when accessed." | """I need to control or 'gatekeep' access to an expensive or sensitive object.""" |

## Behavioral Patterns

| Pattern | Scenario | The Heuristic / Test |
| :--- | :--- | :--- |
| **Chain of Responsibility**| "A middleware stack where an HTTP request passes through Auth, then Logging, then Caching." | """More than one object might handle the request; pass it down the line.""" |
| **Command** | "Implementing an ""Undo"" button by turning every user action into a `Command` object." | """I need to turn a 'request' into a standalone object (to queue, log, or undo it).""" |
| **Interpreter** | "Creating a mini-language for users to write custom search queries (e.g., `name=""bob"" AND age > 20`)." | """I have a specific grammar or language I need to evaluate.""" |
| **Iterator** | Looping through a custom linked list or database cursor without knowing how it's stored. | """I want to traverse a collection without exposing its internal structure.""" |
| **Mediator** | An Air Traffic Control tower coordinating between 50 airplanes so they don't hit each other. | """A group of objects are talking too much; I need a 'Central Hub'.""" |
| **Memento** | "Saving the state of a text editor before a major change so the user can ""Restore"" later." | """I need to capture and restore an object's internal state without breaking encapsulation.""" |
| **Observer** | "A ""YouTube Channel"" (Subject) notifying all its ""Subscribers"" (Observers) when a video drops." | """When one object changes, a bunch of others need to know immediately.""" |
| **State** | A `VendingMachine` that behaves differently if it's in the `HasCoin` state vs `OutOfStock` state. | """An object’s behavior changes fundamentally based on its internal status.""" |
| **Strategy** | "A Navigator app that switches between `WalkStrategy`, `DriveStrategy`, and `BikeStrategy`." | """I have multiple ways to do a task and want to swap them at runtime.""" |
| **Template Method** | "A `DataMiner` that always Opens, Processes, then Closes, but let's subclasses define `Process`." | """The 'Skeleton' of the algorithm is fixed, but some steps vary.""" |
| **Visitor** | "A tool that ""Visits"" every node in a code tree to check for syntax errors vs. calculating metrics." | """I want to add new operations to a class structure without changing the classes.""" |

---

### Pro-Tip for Pythonistas
In Python, many of these are "built-in."

*   **Decorators** are a first-class language feature (`@decorator`).
*   **Iterators** are used every time you write `for x in y:`.
*   **Strategy** is often just passing a function as an argument.
