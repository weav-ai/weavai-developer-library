# python3 documents/forms/download_query_result.py --form_id 66f45d0db1d0dfb13c9974c3 --query "Test query"

# {\n    'pymongo_pipeline': [\n        {\n            '$match': {\n                'Cost of revenue': {\n                    '$gt': 65000\n                }\n            }\n        },\n        {\n            '$project': {\n                'Cost of revenue': 1,\n                'metadata': 1\n            }\n        }\n    ]\n}

import sys
import os
import argparse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from documents.models import DownloadQueryResultRequest
from config_models import LoadConfigurations, ServiceType
from documents.service import FormOperations
from pprint import pprint

if __name__ == "__main__":
    configs = LoadConfigurations().set_config(service=ServiceType.DOCUMENT)
    form_operation = FormOperations(configs=configs)
    parser = argparse.ArgumentParser(description="Provide parameters for the script.")

    parser.add_argument("--form_id", type=str, required=True, help="Form ID")
    parser.add_argument(
        "--download_format",
        type=str,
        default="JSON",
        choices=["JSON", "CSV"],
        required=False,
        help="Download format",
    )
    parser.add_argument(
        "--query",
        default="",
        type=str,
        required=False,
        help="This string is matched in category and description",
    )

    args = parser.parse_args()

    if args.query:
        data = DownloadQueryResultRequest(query=args.query)
    else:
        data = DownloadQueryResultRequest()

    download_query_response = form_operation.download_query_result(
        form_id=args.form_id, download_format=args.download_format, form_data=data
    )
    if args.download_format == "CSV":
        print(download_query_response)
    else:
        pprint(download_query_response.model_dump())
