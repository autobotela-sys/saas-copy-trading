import json, urllib.request, secrets, sys

token = "rw_Fe26.2**69e77d4e9a7e4b79d98a8c31301d334cefe64f95964a6ec9737239ebb1e1a044*XPgjIlCZzrc2uR10MgFYxA*dDZLCv5aOfEOfgXboSaEhd2-eGgzWwph8ukcHO88sLrOTuGNNkszE0PqqMsGw5VyIGrXGkNKER9kn5WwwzMsqw*1772275391705*6d6cc6b10705ba4087e9bdf89985ca1d658b49c52e303bba28323d0518f1ece4*p5aioY74HdZ0_iVpwDEAp9LZnfz7a8AK39bSZ2deefQ"
project_id = "5fad707a-bcd2-4fb6-805f-282da19a459a"
env_id = "6a3e066a-0a24-49af-a509-737c33ee1c4b"
backend_id = "c42ad436-b755-4abd-b017-1f7e6264dca8"
frontend_id = "0897eded-6dc0-445d-996e-8e7e4779fe55"
graphql = "https://backboard.railway.com/graphql/v2"

def graphql_req(query, variables):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    body = {'query': query, 'variables': variables}
    req = urllib.request.Request(graphql, data=json.dumps(body).encode(), headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

q = 'mutation($input: VariableUpsertInput!) { variableUpsert(input: $input) }'

# Backend vars
backend_vars = [
    ('JWT_SECRET_KEY', secrets.token_urlsafe(32)),
    ('ENCRYPTION_KEY', secrets.token_urlsafe(32)),
    ('ENVIRONMENT', 'production'),
    ('LOG_LEVEL', 'INFO'),
    ('PORT', '3445'),
    ('ALLOWED_ORIGINS', '*')
]

for name, value in backend_vars:
    try:
        graphql_req(q, {
            'input': {
                'projectId': project_id,
                'environmentId': env_id,
                'serviceId': backend_id,
                'name': name,
                'value': value
            }
        })
        print(f"Set {name}")
    except Exception as e:
        print(f"Error setting {name}: {e}")

print("Environment variables set!")
