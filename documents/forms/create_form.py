import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from config_models import LoadConfigurations, ServiceType
from documents.service import FormOperations
from documents.models import CreateFormRequest
from pprint import pprint

if __name__ == "__main__":
    configs = LoadConfigurations().set_config(service=ServiceType.DOCUMENT)
    form_operation = FormOperations(configs=configs)
    parser = argparse.ArgumentParser(description="Provide parameters for the script.")

    parser.add_argument("--name", type=str, required=True, help="Form name")
    parser.add_argument("--category", type=str, required=True, help="Form category")
    parser.add_argument(
        "--description", type=bool, default=False, help="Form description"
    )
    parser.add_argument("--is_shared", type=str, required=True, help="Sharing mode")
    parser.add_argument(
        "--is_searchable", type=str, required=True, help="Visibilty mode"
    )

    args = parser.parse_args()

    body = CreateFormRequest(
        name=args.name,
        description=args.description,
        category=args.category,
        is_shared=args.is_shared,
        is_searchable=args.is_searchable,
    )
    form_create_response = form_operation.create_form(form_data=body)
    pprint(form_create_response.dict())
