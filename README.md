# mcp-dataset-curator

MCP server for dataset curation retainer - deduplication, rebalancing, and poison detection.

## Tools

### deduplicate_dataset
Remove duplicate entries from a dataset.

**Parameters:**
- `dataset_id` (string, required): Dataset identifier
- `data` (array, required): Dataset entries
- `key_fields` (array, required): Fields to use for deduplication
- `keep` (string, optional): "first" or "last" (default: "first")

### rebalance_classes
Rebalance class distribution in a dataset.

**Parameters:**
- `dataset_id` (string, required): Dataset identifier
- `data` (array, required): Dataset entries
- `label_field` (string, required): Field containing class labels
- `target_distribution` (object, optional): Target class distribution
- `method` (string, optional): "undersample", "oversample", or "smote" (default: "undersample")

### remove_poisoned_entries
Detect and remove potentially poisoned/malicious entries.

**Parameters:**
- `dataset_id` (string, required): Dataset identifier
- `data` (array, required): Dataset entries
- `detection_methods` (array, optional): Detection methods - statistical_outlier, label_inconsistency, feature_anomaly, duplicate_label (default: all)
- `threshold` (number, optional): Confidence threshold for removal (default: 0.95)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Connecting to Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "dataset-curator": {
      "command": "python",
      "args": ["/path/to/mcp-dataset-curator/main.py"],
      "cwd": "/path/to/mcp-dataset-curator"
    }
  }
}
```

## License

MIT