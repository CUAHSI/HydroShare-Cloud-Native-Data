import json
import os

import typer

from api.models.schema import DatasetMetadata


def main(output_name: str = "api/models/schemas/schema.json"):
    schema = DatasetMetadata.schema()
    json_schema = DatasetMetadata.schema_json()#indent=2)
    # Have to run it a few times for the definitions to get updated before inserted into another model
    while "#/definitions/" in json_schema:
        for definition in schema["definitions"]:
            class_definition = schema["definitions"][definition]
            # replace allOf with a single definition
            json_schema = json_schema.replace(
                f'"allOf": [{{"$ref": "#/definitions/{definition}"}}]',
                json.dumps(class_definition)[1:-1]
            )
            #replace definition directly
            json_schema = json_schema.replace(
                f'"$ref": "#/definitions/{definition}"',
                json.dumps(class_definition)[1:-1]
            )
    embedded_schema = json.loads(json_schema)
    current_directory = absolute_directory(output_name)
    with open(current_directory, "w") as f:
        f.write(json.dumps(embedded_schema, indent=2))


def absolute_directory(output_name):
    current_directory = os.getcwd()
    current_directory = os.path.join(current_directory, output_name)
    return "/" + current_directory


if __name__ == "__main__":
    typer.run(main)
