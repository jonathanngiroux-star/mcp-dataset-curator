import pytest
import asyncio
import json
import secrets
from mcp_dataset_curator.server import (
    create_dataset, 
    create_curation_job, 
    update_quality,
    get_stats,
    list_datasets,
    list_tools_handler,
    call_tool_handler
)

@pytest.fixture
async def clean_db():
    import sqlite3
    from mcp_dataset_curator.server import DB_PATH
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM datasets")
        conn.execute("DELETE FROM curation_jobs")
    yield
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM datasets")
        conn.execute("DELETE FROM curation_jobs")

@pytest.mark.asyncio
async def test_list_tools():
    from mcp_dataset_curator.server import list_tools_handler
    from mcp.types import ListToolsResult
    result = await list_tools_handler()
    assert isinstance(result, ListToolsResult)
    assert len(result.tools) == 5

@pytest.mark.asyncio
async def test_create_dataset(clean_db):
    from mcp_dataset_curator.server import create_dataset
    result = await create_dataset({
        "name": "Test Dataset",
        "description": "Description",
        "task_type": "qa",
        "language": "en",
        "size": 1000,
        "format": "jsonl",
        "source": "github",
        "tags": ["test"]
    })
    assert len(result) > 0
    data = json.loads(result[0].text)
    assert data["status"] == "created"
    assert "dataset_id" in data

@pytest.mark.asyncio
async def test_create_curation_job(clean_db):
    from mcp_dataset_curator.server import create_dataset, create_curation_job
    ds = await create_dataset({
        "name": "Test", "description": "Desc", "task_type": "qa", "language": "en",
        "size": 100, "format": "jsonl", "source": "local"
    })
    ds_id = json.loads(ds[0].text)["dataset_id"]
    
    job = await create_curation_job({
        "dataset_id": ds_id,
        "job_type": "refresh",
        "config": {"incremental": True}
    })
    assert len(job) > 0
    data = json.loads(job[0].text)
    assert data["status"] == "pending"

@pytest.mark.asyncio
async def test_update_quality(clean_db):
    from mcp_dataset_curator.server import create_dataset, update_quality
    ds = await create_dataset({"name": "Test", "description": "Desc", "task_type": "qa", "language": "en", "size": 100, "format": "jsonl", "source": "local"})
    ds_id = json.loads(ds[0].text)["dataset_id"]
    
    result = await update_quality({"dataset_id": ds_id, "quality_score": 0.85})
    assert len(result) > 0
    data = json.loads(result[0].text)
    assert data["status"] == "updated"

@pytest.mark.asyncio
async def test_get_stats(clean_db):
    from mcp_dataset_curator.server import create_dataset, update_quality, get_stats
    ds = await create_dataset({"name": "DS1", "description": "Desc", "task_type": "qa", "language": "en", "size": 100, "format": "jsonl", "source": "src"})
    ds = await create_dataset({"name": "DS2", "description": "Desc", "task_type": "generation", "language": "fr", "size": 200, "format": "jsonl", "source": "src"})
    await update_quality({"dataset_id": json.loads(ds[0].text)["dataset_id"], "quality_score": 0.9})
    
    result = await get_stats({})
    data = json.loads(result[0].text)
    assert data["total_datasets"] >= 2
    assert data["total_samples"] >= 300
    assert "qa" in data["by_task_type"]

@pytest.mark.asyncio
async def test_list_datasets(clean_db):
    from mcp_dataset_curator.server import create_dataset, list_datasets
    await create_dataset({"name": "DS1", "description": "Desc", "task_type": "qa", "language": "en", "size": 100, "format": "jsonl", "source": "src"})
    await create_dataset({"name": "DS2", "description": "Desc", "task_type": "generation", "language": "fr", "size": 200, "format": "jsonl", "source": "src"})
    
    datasets = await list_datasets({})
    data = json.loads(datasets[0].text)
    assert len(data["datasets"]) >= 2
    
    qa_datasets = await list_datasets({"task_type": "qa"})
    qa_data = json.loads(qa_datasets[0].text)
    assert len(qa_data["datasets"]) >= 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])