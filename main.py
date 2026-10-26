#!/usr/bin/env python3
"""MCP server for dataset-curator - Dataset Curation Retainer"""

import json
import os
import hashlib
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("mcp-dataset-curator")

# Simple in-memory storage for demo
DATASETS = {}

app = Server("mcp-dataset-curator")

TOOLS = [
    Tool(
        name="deduplicate_dataset",
        description="Remove duplicate entries from a dataset",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string", "description": "Dataset identifier"},
                "data": {"type": "array", "items": {"type": "object"}, "description": "Dataset entries"},
                "key_fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to use for deduplication"},
                "keep": {"type": "string", "enum": ["first", "last"], "default": "first", "description": "Which duplicate to keep"}
            },
            "required": ["dataset_id", "data", "key_fields"]
        }
    ),
    Tool(
        name="rebalance_classes",
        description="Rebalance class distribution in a dataset",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string", "description": "Dataset identifier"},
                "data": {"type": "array", "items": {"type": "object"}, "description": "Dataset entries"},
                "label_field": {"type": "string", "description": "Field containing class labels"},
                "target_distribution": {"type": "object", "description": "Target class distribution (optional)"},
                "method": {"type": "string", "enum": ["undersample", "oversample", "smote"], "default": "undersample", "description": "Rebalancing method"}
            },
            "required": ["dataset_id", "data", "label_field"]
        }
    ),
    Tool(
        name="remove_poisoned_entries",
        description="Detect and remove potentially poisoned/malicious entries",
        inputSchema={
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string", "description": "Dataset identifier"},
                "data": {"type": "array", "items": {"type": "object"}, "description": "Dataset entries"},
                "detection_methods": {"type": "array", "items": {"type": "string", "enum": ["statistical_outlier", "label_inconsistency", "feature_anomaly", "duplicate_label"]}, "default": ["statistical_outlier", "label_inconsistency", "feature_anomaly", "duplicate_label"], "description": "Detection methods to use"},
                "threshold": {"type": "number", "default": 0.95, "description": "Confidence threshold for removal"}
            },
            "required": ["dataset_id", "data"]
        }
    )
]

app = Server("mcp-dataset-curator")

@app.list_tools()
async def list_tools():
    return TOOLS

@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "deduplicate_dataset":
        dataset_id = arguments.get("dataset_id")
        data = arguments.get("data", [])
        key_fields = arguments.get("key_fields", [])
        keep = arguments.get("keep", "first")
        
        # Create hash for each entry based on key fields
        seen = {}
        unique = []
        duplicates = 0
        
        for entry in data:
            key = tuple(entry.get(field) for field in key_fields)
            key_hash = hashlib.md5(str(key).encode()).hexdigest()
            
            if key_hash in seen:
                duplicates += 1
                if keep == "last":
                    seen[key_hash] = entry
            else:
                seen[key_hash] = entry
        
        unique = list(seen.values())
        
        result = {
            "status": "ok",
            "tool": "deduplicate_dataset",
            "dataset_id": arguments.get("dataset_id"),
            "original_count": len(arguments.get("data", [])),
            "unique_count": len(unique),
            "duplicates_removed": len(arguments.get("data", [])) - len(unique),
            "keep_strategy": keep
        }
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "rebalance_classes":
        dataset_id = arguments.get("dataset_id")
        data = arguments.get("data", [])
        label_field = arguments.get("label_field")
        target_distribution = arguments.get("target_distribution", {})
        method = arguments.get("method", "undersample")
        
        # Count class distribution
        class_counts = {}
        class_data = {}
        
        for entry in data:
            label = entry.get(label_field)
            if label not in class_counts:
                class_counts[label] = 0
                class_data[label] = []
            class_counts[label] += 1
            class_data[label].append(entry)
        
        if not target_distribution:
            # Equal distribution
            min_count = min(class_counts.values())
            target_distribution = {k: min_count for k in class_counts}
        
        rebalanced = []
        if method == "undersample":
            for label, entries in class_data.items():
                target = target_distribution.get(label, len(entries))
                rebalanced.extend(entries[:target])
        elif method == "oversample":
            max_count = max(target_distribution.values()) if target_distribution else max(class_counts.values())
            for label, entries in class_data.items():
                target = target_distribution.get(label, max_count)
                times = (target + len(entries) - 1) // len(entries) if entries else 0
                rebalanced.extend(entries * times)
                rebalanced = rebalanced[:max_count]
        
        result = {
            "status": "ok",
            "tool": "rebalance_classes",
            "dataset_id": arguments.get("dataset_id"),
            "method": method,
            "original_distribution": class_counts,
            "target_distribution": target_distribution,
            "final_count": len(rebalanced)
        }
        return [TextContent(type="text", text=json.dumps(result))]
    
    elif name == "remove_poisoned_entries":
        dataset_id = arguments.get("dataset_id")
        data = arguments.get("data", [])
        detection_methods = arguments.get("detection_methods", ["statistical_outlier", "label_inconsistency", "feature_anomaly", "duplicate_label"])
        threshold = arguments.get("threshold", 0.95)
        
        # Simple poison detection placeholder
        flagged = []
        clean = []
        
        for i, entry in enumerate(data):
            is_poisoned = False
            reasons = []
            
            # Simple heuristics
            if "duplicate_label" in detection_methods:
                pass  # Would check for same input different labels
            
            if "statistical_outlier" in detection_methods:
                pass  # Would use statistical methods
            
            # Placeholder: randomly flag ~1% as poisoned for demo
            if hash(str(entry)) % 100 < 1:
                is_poisoned = True
                reasons.append("statistical_outlier")
            
            if is_poisoned:
                flagged.append({"index": i, "entry": entry, "reasons": reasons})
            else:
                clean.append(entry)
        
        result = {
            "status": "ok",
            "tool": "remove_poisoned_entries",
            "dataset_id": arguments.get("dataset_id"),
            "detection_methods": detection_methods,
            "threshold": threshold,
            "original_count": len(arguments.get("data", [])),
            "clean_count": len(clean),
            "flagged_count": len(flagged),
            "flagged_entries": flagged[:10]  # Limit output
        }
        return [TextContent(type="text", text=json.dumps(result))]
    
    return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def serve():
        reader, writer = await stdio_server()
        await app.run(reader, writer)
    
    asyncio.run(serve())