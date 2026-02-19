
## 0. Overall Data Flow
1. **Bootstrap** Load ALL `PersistenceProfiles` into `PolicyRegistry`
    1. Instantiate all Strategy Classes
    2. Register their manifests
    3. Inject the `StrategyLibrary`, `Adapter`, `SystemMonitor`, `CoreCounter` into *Universal Orchestrator*
    - [x] Remove `Resolution` from Bootstrap process
    - [ ] Loads **Library of Strategies** organized by **Capability and Constraint**
    - [ ] Handles **Instantiation**
2. **Request** `Repository` calls `orchestrator.save()`
    - [ ] Centralized `save()` method 
        1. Routes `_open_stream()` or `_save_atomic()`
3. **Resolver**
    * **Middleware** Executed inside `orchestrator.save()` at runtime
    - [x] Identify `How` we will Resolve the PersistenceProfile, using:
    - [ ] Utilizes **ExecutionPlan**
    - [ ] Determine Criteria for Resolution
    - [ ] Implement default Safe-Guard pattern
    * **Properties as Selection Criteria**
        - [ ] **Data Shape** i.e. is_generator() --> SerializeStrategies()
        - [ ] **Environment** i.e. is_env_production() --> HighIntegrityCheck(); For later maybe
        - [ ] **Security** i.e. is_sensative() --> EncryptionDecorator()
    * **Resources from which to make Selection***
        - [ ] **Cross-Cutting Concerns** Checksum integrity, security, etc - does this include decorators?
            - [ ] What are `decorators`?
        - [ ] **Properties and Settings** as Filtering criterion; e.g. mode="wb" output binary

---

## 1. Orchestrator
- [ ] Implement "Logic Gate" Design from `05_implementation_plan...md`
* **Questions**
    - [ ] Do we need a **RollingIntegrity** strategy / check to update hash
        - [ ] Ensure hash implementation strategy is content based for stream
    - [ ] What **Authorities** should the Orchestrator have?
        - [ ] `gc.collect()`
* **Build Decisions**
- [x] Is there `middleware` in the Orchestrator `save()` routing method which would perform Resolve() or are we making it Explicit from Repo?
- [x] Using **Late-Bound** / **Universal Orchestrator** model
* **Workflow**
    - [ ] **Intercept** data and a `policy_key` or the *Hints*
    - [ ] **Resolve** from the `StrategyLibrary` to build a `PersistenceProfile`
    - [ ] **Execute** Route the corrected internal method `_save_atomic()` or `_open_stream()`

--- 

# 2. Serializer Changes
- [x] Ensure serialize_item() is able to handle json objects correctly
- [ ] Check for other edge cases when serializing in chunks
- [x] Check about deserialize() methods for refactored AbstractSerializer
- [ ] `deserialize()` changed to `finalize()` for streaming methods

<del>
# 3. Resolver
- [x] Identify what we are doing with Resolver
    - [x] Currently: Used in bootstrapping to **Select PersistenceProfile** based on **file extension** i.e. `target` param
    - [x] Use `03-strategy-selection.md` and `04-cross-cutting...md` to **Implement New Resolution Scheme**
    - [x] Determine if Resolver is necessary - **Explicit vs Inferred** strategy selection
- [x] **Resolver Necessary** as a **Validator and Fetcher**
</del>

---

# 4. Adapter
- [ ] Changing from `save_stream()` to `open_stream()`
- [ ] Should `open_stream()` implement **Write-to-tmp-then-move**

---

# 5. Bootstrap Process 
- [ ] **Library of Strategies** Using filters - instead of a static map - for Resolver actions
- [x] Handles **Instantiation**

---

# 6. Library of Strategies
- [ ] Organize by **Capability** and **Constraint**
- [ ] `Keyed` by combination of **Category** (serialization, integrity, compression) and **Behavior** (atomic vs streaming)
- [ ] Enforce **Mutual Exclusivity**

# 7. Resolver Middleware
- [ ] Move Resolver to middleware action inside `orchestrator.save()` routing method
- [ ] Add: `selected_integrity = library.get_integrity(policy_key) or NoOpIntegrity()`

# 8. ExecutionPlan - i.e. StrategyProfile Refactor
- [x] Replace PersistenceProfile named tuple
- [x] Alter `Union[str, dict]` logic
- [x] Must be able to *know* contents are compatible with **Data Shape**
- [x] Refactor into a Data Class
- [x] Add type for Strategies abstract Serializer and abstract Integrity

# 9. StrategyManifest
- [ ] Contains Metadata about the Profile
- [ ] Allows the **Library of Strategies** to exist WITHOUT having to instantiate ALL Strategies
