# Weav AI Developer Scripts

This repository contains scripts for interacting with the Weav AI platform, including managing agents, workflows, and forms.

## Setup


### 1. Clone the Repository

```bash
git clone https://github.com/weav-ai/weav-dev.git
```

### 2. Change to the `scripts` branch

```bash
git fetch
```

```bash
git checkout scripts
```

### 3. Move to the scripts folder

```bash
cd scripts
```

### 4. Install requirements

```bash
	pip3 install -r requirements.txt
```

### 5. Add variables to `.env` file

```bash
ENV = "https://<env_name>
AUTH_TOKEN = "eyJhbGci...."

```

For example

```bash
ENV = "https://dev2.copilot.weav.ai"
AUTH_TOKEN = "eyJhbGciOiJ..."
```

### Agents

1. Get Agent Types: Fetches all the agents present on the platform.

```bash
python3 agents/get_agent_types.py
```

Response

```bash
['Agent A', 'Agent B' ..... ,'Agent C']
```

1. Get Agent Response: Fetches the response of a selected agent from the platform.
    
    ```bash
    python3 agents/get_agent_response.py --user_input "Summarize the document" --chat_id "google-oauth2|117349365869611297391_Insurance Underwriting AI Agent" --agent_type "Insurance Underwriting AI Agent"
    ```
    
    Params
    
    | Parameter | Description | Required/Optional |
    | --- | --- | --- |
    | user_input | The question provided to the agent | Required |
    | agent_type | The Agent type to be used | Required |
    | chat_id | Chat ID in which the conversation takes place | Required |
    
    Response
    
    ```bash
    [GetAgentResponse(id=None, event=None, data='{"type": "assistant", "chat_id": "google-oauth2|117349365869611297391_Insurance Underwriting AI Agent", "vote": "no vote", "message_id": "d79c34f5-f4f3-4170-8baa-8baf2efea2a4", "search_results": [], "generate_button": null, "tags": [], "text": "**Analyzing request...<br><br>** ", "timestamp": "2024-09-25 19:12:20.178930+00:00"}', retry=None),...]
    ```
    
2. Get Chat History: Get all chat history with selected agent

```bash
python3 agents/get_chat_history.py --chat_id "google-oauth2|117349365869611297391_Insurance Underwriting AI Agent"
```

Params

| Parameter | Description | Required/Optional |
| --- | --- | --- |
| chat_id | Chat ID in which the conversation takes place | Required |

Response

```bash
{'messages': [Message(message_id='423a02c6-ad21-4438-b3cc-9be2ffa65197', chat_id='google-oauth2|117349365869611297391_Insurance Underwriting AI Agent', text='whatsup', timestamp=datetime.datetime(2024, 9, 24, 1, 5, 29, 775000), type='user', vote='no vote', search_results=[], generate_button=None, tags=[]), Message(message_id='f79bf3f7-3a52-47f8-8bf8-7e792c729b20', chat_id='google-oauth2|117349365869611297391_Insurance Underwriting AI Agent', text="Hello! How can I assist you today with your insurance underwriting needs? If you have any specific questions or requests, please let me know, and I'll be happy to help.<br><br>\n", timestamp=datetime.datetime(2024, 9, 24, 1, 5, 36, 20000), type='assistant', vote='no vote', search_results=[], generate_button=None, tags=[])..]}
```

Params

| Parameter | Description | Required/Optional |
| --- | --- | --- |
| chat_id | Chat ID in which the conversation takes place | Required |

### Workflows

1. Get all workflows

```bash
 python3 workflows/get_all_workflows.py --show_internal_steps false
```

Params

| Parameter | Description | Required/Optional | Allowed values |
| --- | --- | --- | --- |
| show_internal_steps | Set to true to show detailed internal steps | Optional (default : False) | false, f, False, true, t, True |

Response

```bash
{
   "workflows":[
      {
         "name":"dagtasktest",
         "params":[
            
         ],
         "tasks":[
            {
               "downstream_tasks":[
                  
               ],
               "is_active":true,
               "name":"only_if_failed"
            },
            {
               "downstream_tasks":[
                  
               ],
               "is_active":true,
               "name":"only_if_success"
            }
         ]
      }
   ]
}
```

1. Get Single workflow

```bash
python3 workflows/get_single_workflow.py --workflow_name dagtasktest --show_internal_steps false
```

Params

| Parameter | Description | Required/Optional | Allowed values |
| --- | --- | --- | --- |
| show_internal_steps | Set to true to show detailed internal steps | Optional (default : False) | false, f, False, true, t, True |
| workflow_name | The name of the worlflow to be fetched | Required |  |

Response

```bash
{
   "name":"dagtasktest",
   "params":[
      
   ],
   "tasks":[
      {
         "downstream_tasks":[
            
         ],
         "is_active":true,
         "name":"only_if_failed"
      },
      {
         "downstream_tasks":[
            
         ],
         "is_active":true,
         "name":"only_if_success"
      },
      {
         "downstream_tasks":[
            "second"
         ],
         "is_active":true,
         "name":"first"
      },
      {
         "downstream_tasks":[
            "third"
         ],
         "is_active":true,
         "name":"second"
      },
      {
         "downstream_tasks":[
            "only_if_success",
            "only_if_failed"
         ],
         "is_active":true,
         "name":"third"
      },
      {
         "downstream_tasks":[
            "second",
            "third",
            "first"
         ],
         "is_active":true,
         "name":"split"
      }
   ]
}
```

1. Run Workflow

```bash
python3 workflows/run_workflow.py --doc_id 66e0fba3089fbd21c4dd80c3 --workflow_name dagtest
```

Params

| Parameter | Description | Required/Optional |
| --- | --- | --- |
| workflow_name | Name of the workflow to be run | Required |
| doc_id | Document for which the workflow has to be run | Required |

Response

```bash
{'created_at': '2024-09-25T19:33:32.000000+00:00',
 'document_id': '66e0fba3089fbd21c4dd80c3',
 'document_name': 'AAPL_10Q.pdf',
 'end_date': None,
 'in_folders': ['66e0f93093798ee1c937e39a'],
 'run_id': '66e0fba3089fbd21c4dd80c3_3df1b127-9ea5-4714-9bf5-b1a5653859f6',
 'start_date': None,
 'state': None,
 'workflow_id': 'dagtest'}
```

1. Get Workflow status

```bash
python3 workflows/get_workflow_status.py --workflow_id "dagtasktest" --workflow_run_id "66df87ec2b1edfc0dc3b556f_2461160a-117f-45ac-9fa0-f5590d977882"
```

Params

| Parameter | Description | Required/Optional | Allowed values |
| --- | --- | --- | --- |
| show_internal_steps | Set to true to show detailed internal steps | Optional (default : False) | false, f, False, true, t, True |
| workflow_id | Document identifier for which the workflow has to be run | Required |  |
| workflow_run_id | The run ID of the workflow | Required |  |
1. Rerun workflow

```bash
python3 workflows/rerun_workflow.py --doc_id 66df87ec2b1edfc0dc3b556f --workflow_name "process_form_workflow"
```

Param

| Parameter | Description | Required/Optional |
| --- | --- | --- |
| workflow_name | Name of the workflow to be run | Required |
| doc_id | Document for which the workflow has to be run | Required |
1. Skip steps in workflow

```bash
python3 workflows/skip_tasks.py --workflow_name "dagtest" --tasks task_1 task_2
```

Params

| Parameter | Description | Required/Optional |
| --- | --- | --- |
| workflow_name | Name of the workflow to be run | Required |
| tasks | A list of tasks to be skipped | Required |

### Forms

1. Create form

```bash
python3 documents/forms/create_form.py --name "new form" --category "new" --description "test" --is_shared true --is_searchable true
```

Params

| Parameter | Description | Required/Optional | Allowed values |
| --- | --- | --- | --- |
| name | The form name | Required |  |
| category | A category name for the form | Required |  |
| description | The description of the form | Required |  |
| is_shared | A flag to decide sharing permissions | Optional (default : False) | false, f, False, true, t, True |
| is_searchable | A flag to decide visibility | Optional (default : False) | false, f, False, true, t, True |

Response

```bash
{'category': 'new',
 'created_at': datetime.datetime(2024, 9, 25, 20, 12, 11, tzinfo=datetime.timezone.utc),
 'description': 'True',
 'fields': [],
 'id': '66f46e9b70dd6d497d9b8a37',
 'is_searchable': True,
 'is_shared': True,
 'name': 'new form',
 'user_id': 'google-oauth2|117349365869611297391'}
```

1. Delete Form definition

```bash
python3 documents/forms/delete_form_definition.py --form_id 66ea66d547fff0950cba17e
```

Params

| Parameter | Description | Required/Optional |
| --- | --- | --- |
| form_id | The unique identifier of the form | Required |

Response

```bash
{'category': 'new',
 'created_at': datetime.datetime(2024, 9, 25, 20, 12, 11, tzinfo=datetime.timezone.utc),
 'description': 'True',
 'fields': [],
 'id': '66f46e9b70dd6d497d9b8a37',
 'is_searchable': True,
 'is_shared': True,
 'name': 'new form',
 'user_id': 'google-oauth2|117349365869611297391'}
```

1. Filter form

```bash
python3 documents/forms/filter_form.py --query "SECURITIES AND EXCHANGE COMMISSION" --scope "all_forms
```

Params

| Parameter | Description | Required/Optional | Allowed values |
| --- | --- | --- | --- |
| scope | The scope of search | Required | all_forms, my_forms |
| is_searchable | Filter for visibility | Optional (default : False) | false, f, False, true, t, True |
| query | When applied, string matches category | Required |  |

Response

```bash
{'forms': [{'category': 'SECURITIES AND EXCHANGE COMMISSION',
            'created_at': '2024-09-25T09:13:50Z',
            'description': '',
            'fields': [{'description': '',
                        'field_type': 'Date',
                        'fill_by_search': False,
                        'is_array': False,
                        'name': 'testEnitity1'}],
            'is_searchable': False,
            'is_shared': False,
            'name': 'test',
            'user_id': 'google-oauth2|117349365869611297391'}]}
```

1. Get form definitions

```bash
python3 documents/forms/get_form_definition.py --form_id "66f46e9b70dd6d497d9b8a37
```

Params

| Parameter | Description | Required/Optional |
| --- | --- | --- |
| form_id | Form ID | Required |

Response

```bash
{'category': 'new',
 'created_at': '2024-09-25T20:12:11Z',
 'description': 'True',
 'fields': [],
 'id': '66f46e9b70dd6d497d9b8a37',
 'is_searchable': True,
 'is_shared': True,
 'name': 'new form',
 'user_id': 'google-oauth2|117349365869611297391'}
```

1. Update form definition 

```bash
python3 documents/forms/update_form_definition.py --form_id 66f46e9b70dd6d497d9b8a37 --name "update" --category "new" --description "Test desc" --is_shared false --is_searchable false
```

Params

| Parameter | Description | Required/Optional | Allowed values |
| --- | --- | --- | --- |
| form_id | Form identifier | Required |  |
| name | Form name | Required |  |
| category | Form category | Required |  |
| description  | Form description | Required |  |
| is_shared | Filter for sharing permissions | Required | false, f, False, true, t, True |
| is_searchable | Filter for visibility | Required | false, f, False, true, t, True |

Response

```bash
{
 'category': 'new',
 'created_at': '2024-09-25T20:12:11Z',
 'description': 'Test desc',
 'fields': [],
 'id': '66f46e9b70dd6d497d9b8a37',
 'is_searchable': False,
 'is_shared': False,
 'name': 'update',
 'user_id': 'google-oauth2|117349365869611297391'
}
```

1. Filter form instances

```bash
python3 documents/forms/filter_form_instances.py --scope all_documents --status "DONE" --category "SECURITIES AND EXCHANGE COMMISSION"
```

Params

| Parameter | Description | Required/Optional | Allowed values |
| --- | --- | --- | --- |
| scope | The scope of search | Required |  "all_documents",
"current_document",
"my_documents",
"shared_documents" |
| status | Status of workflow | Optional | "NOT_STARTED", "IN_PROGRESS", "DONE", "FAILED” |
| category | Category of  | Required |  |
| query | When applied, string matches category | Required |  |
| form_id | Form identifier | Optional |  |
| doc_id | Document identifier | Required |  |
| only_latest | Fetches only latest | Optional (default True) |  |
| skip | Number of documents to skip | Optional (default 0) |  |
| limit | Max number of documents | Optional (default 25) |  |

Response

```bash
{
   "total":1,
   "form_instances":[
      {
         "form_instance":{
            "Name":"",
            "weav_metadata":""
         },
         "doc_id":"66e0fba3089fbd21c4dd80c3",
         "form_id":"66f3d44eeb87303bc52bb9b4",
         "file_name":"AAPL_10Q.pdf",
         "status":"AI_READY",
         "category":"SECURITIES AND EXCHANGE COMMISSION",
         "in_folders":[
            "66e0f93093798ee1c937e39a"
         ],
         "owner_id":"google-oauth2|117349365869611297391"
      }
   ]
}
```

1. Execute form analytics

```bash
python3 documents/forms/execute_form_analytics.py --form_id 66f3d44eeb87303bc52bb9b4 --skip 0 --limit 25
```

Params

| Parameters | Description | Required/Optional |
| --- | --- | --- |
| skip | Number of documents to skip | Optional (default 0) |
| limit | Total number of documents to consider | Optional (default 25) |
| form_id | Form Identifier | Required |

Response

```bash
{
   "columns":[
      "testEnitity1"
   ],
   "results":[
      {
         "metadata":{
            "file_name":"AAPL_10Q.pdf",
            "in_folders":[
               "66e0f93093798ee1c937e39a"
            ]
         },
         "testEnitity1":"datetime.datetime(2023, 8, 3, 0, 0)"
      }
   ],
   "summary":"",
   "total_count":1
}
```