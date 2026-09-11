import json
from src.dataset import ScientificDataset, EditableScientificDataset

js_schema = EditableScientificDataset.model_json_schema()
with open("schema/dataset_schema.json", "w") as f:
    f.write(json.dumps(js_schema, indent=2))