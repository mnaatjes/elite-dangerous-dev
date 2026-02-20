# src/persistence/orchestrator.py

import inspect
from typing import Any, Optional, Iterable
from .models import ExecutionPlan
from .strategies.const import Capability, Category
from .strategies.serialization import AtomicSerializer, StreamingSerializer
from .strategies.integrity import AtomicIntegrity, StreamingIntegrity

class PersistenceOrchestrator:
    """
    Mission Control for Persistence.
    Dynamically resolves strategies based on data shape and policy.
    """
    def __init__(self, adapter, monitor, library) -> None:
        self._adapter = adapter
        self._monitor = monitor
        self._library = library

    def save(self, target: str, data: Any, policy: Optional[str] = None) -> Any:
        """
        The Universal Entry Point. 
        Detects if data should be Atomic or Streaming and resolves the plan.
        """
        # 1. Determine Shape (Hinting)
        is_stream = self._is_stream(data)
        required_cap = Capability.STREAM if is_stream else Capability.ATOMIC

        # 2. Resolve the Execution Plan
        plan = self._resolve_execution_plan(policy, required_cap)

        # 3. Resource Safety Check (Only for Atomic)
        if not is_stream:
            # Simple RAM check before we commit to an atomic encode
            if self._monitor.is_pressure_high():
                 # We could force-promote to stream here, but for now, we'll just guard
                 pass 

        # 4. Route Execution
        if is_stream:
            return self._execute_stream_save(target, data, plan)
        return self._execute_atomic_save(target, data, plan)

    def _resolve_execution_plan(self, policy: Optional[str], cap: Capability) -> ExecutionPlan:
        """The Internal Resolver Middleware."""
        # 1. Resolve Serializer using the policy name
        ser_manifest = self._library.find(Category.SERIALIZER, name=policy, required_capabilities=cap)
        
        # 2. RESOLVE INTEGRITY USING THE POLICY NAME
        # This was missing the 'name=policy' argument!
        int_manifest = self._library.find(Category.INTEGRITY, name=policy, required_capabilities=cap)

        # 3. Fallback: If policy didn't find a specific Integrity strategy, 
        # find the best match by capability (like we do for serializers)
        if not int_manifest:
            int_manifest = self._library.find(Category.INTEGRITY, required_capabilities=cap)

        if not ser_manifest:
            raise ValueError(f"No Serializer found for policy '{policy}' with capability {cap}")

        # Adaptive Mode Logic
        # If it's a stream, we check if we should use text or binary
        if cap == Capability.STREAM:
            # For now, default NDJSON to text mode. 
            # In a more advanced version, you could add 'is_binary' to the Manifest.
            mode = "w" if ser_manifest.name == "ndjson" else "wb"
        else:
            mode = "wb" # Default for atomic

        return ExecutionPlan(
            serializer=ser_manifest.strategy_class(),
            integrity=int_manifest.strategy_class() if int_manifest else None,
            is_stream=(cap == Capability.STREAM),
            target_mode=mode
        )

    def _execute_atomic_save(self, target: str, data: Any, plan: ExecutionPlan) -> str:
        # 1. Narrow the Serializer type
        if not isinstance(plan.serializer, AtomicSerializer):
            raise TypeError(f"ExecutionPlan for atomic save requires AtomicSerializer, got {type(plan.serializer)}")
        
        payload = plan.serializer.encode(data)
        
        # 2. Narrow the Integrity type
        checksum = ""
        if plan.integrity:
            if not isinstance(plan.integrity, AtomicIntegrity):
                raise TypeError(f"ExecutionPlan for atomic save requires AtomicIntegrity, got {type(plan.integrity)}")
            
            hash_input = payload.encode() if isinstance(payload, str) else payload
            checksum = plan.integrity.calculate(hash_input)

        self._adapter.write(target, payload)
        return checksum

    def _execute_stream_save(self, target: str, data: Iterable, plan: ExecutionPlan) -> str:
        if not isinstance(plan.serializer, StreamingSerializer):
            raise TypeError("Streaming save requires a StreamingSerializer.")

        # Use the plan's target_mode ('w' for NDJSON)
        with self._adapter.open_stream(target, mode=plan.target_mode) as stream:
            for item in data:
                chunk = plan.serializer.encode_item(item)
                
                # --- TYPE NARROWING FOR INTEGRITY ---
                if plan.integrity and isinstance(plan.integrity, StreamingIntegrity):
                    chunk_bytes = chunk.encode() if isinstance(chunk, str) else chunk
                    plan.integrity.update(chunk_bytes)
                
                stream.write(chunk)
            
            footer = plan.serializer.finalize()
            if footer: 
                stream.write(footer)

        # Finalize only if it's actually a streaming integrity object
        if plan.integrity and isinstance(plan.integrity, StreamingIntegrity):
            return plan.integrity.finalize()
            
        return "Success"
    
    def _is_stream(self, data: Any) -> bool:
        """
        Determines if the data shape requires a streaming approach.
        
        Returns True for:
        - Generators and Generator Expressions
        - Iterables that are NOT strings, bytes, or standard collections (dict/list).
        """
        # 1. Direct check for generators (e.g., yield)
        if inspect.isgenerator(data):
            return True
            
        # 2. Check for other iterables (like opened file handles or custom star-iterators)
        # We exclude dicts and lists because we usually want to save those atomically
        # and they are easily handled in memory.
        if hasattr(data, "__iter__") and not isinstance(data, (dict, list, str, bytes)):
            return True

        return False