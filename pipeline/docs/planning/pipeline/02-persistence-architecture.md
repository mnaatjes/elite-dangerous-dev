# Persistence Layer Architecture

The persistence architecture is designed to safely and efficiently handle data I/O by separating concerns into distinct layers of responsibility. This design allows for flexibility in storage mechanisms and provides robust, automatic safety checks.

## 1. Division of Responsibilities

The data flow from domain object to stored file involves three key stages, each with a clear owner.

| Stage       | Responsible Layer          | Core Responsibility                                                                                              |
|-------------|----------------------------|------------------------------------------------------------------------------------------------------------------|
| **Producer**  | **Repository** (Domain)    | **Owns the "What."** Provides the data to be persisted, either as a complete object or as an iterator/generator for large datasets. |
| **Transformer** | **Persistence** (Meso-Layer) | **Owns the "How and Safety."** Orchestrates the persistence process, serializes data, performs integrity checks, and monitors system resources. |
| **Consumer**  | **Infrastructure** (Adapter) | **Owns the "Where."** Manages the low-level I/O, writing bytes or strings to a specific destination like the local filesystem or a database. |

It is a requirement for the **Repository** to use generators when providing large datasets. This acts as a signal to the persistence layer: "I don't have this all in memory, so you shouldn't either."

## 2. The Role of the Persistence Orchestrator

The **Persistence Orchestrator** is the central conductor of the persistence process. Its primary responsibility is to manage the workflow and enforce safety rules, not to understand the details of data formats or storage media.

- **Data Type Detection**: It inspects the incoming data from the repository. If it receives a standard object (`dict`, `list`), it triggers an atomic save. If it receives a `generator`, it automatically switches to a streaming save logic.
- **Workflow Management**: It coordinates the other components, calling the serializer to transform the data and the adapter to write it.
- **Safety Enforcement**: It integrates with the `SystemMonitor` to check available resources (like RAM) before and during the operation, preventing the system from crashing due to memory exhaustion.

## 3. The Role of the Serializer Strategy

The **Serializer** is the "instrument" that performs the technical conversion of data. Its role is to translate a Python object into a specific string or byte representation.

- **Atomic Serialization**: A `serialize(data)` method that takes a complete Python object and returns a single string or blob of bytes. Used for small files.
- **Streaming Serialization**: A `serialize_item(item)` method that takes a single item from a collection and returns its serialized representation, typically followed by a newline for NDJSON. Used for large files.

By defining this dual capability in the strategy, the orchestrator can remain agnostic about the data format while handling both small and large payloads.

## 4. The "No Transformation" Rule

A core principle of the persistence layer is **"No Transformation."** This rule must be correctly interpreted:

- **Domain Transformation (Not Allowed)**: The persistence layer must not change the meaning or value of the data. For example, it should not convert star coordinates from one unit to another. Such logic belongs in the service/domain layer.
- **Representation Serialization (Required)**: The persistence layer is *required* to change the data's representation. It turns a Python dictionary in memory into a UTF-8 JSON string on disk. This is a technical conversion of the medium, not a modification of the domain value.
