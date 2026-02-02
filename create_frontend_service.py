import json, urllib.request, sys

token = "rw_Fe26.2**69e77d4e9a7e4b79d98a8c31301d334cefe64f95964a6ec9737239ebb1e1a044*XPgjIlCZzrc2uR10MgFYxA*dDZLCv5aOfEOfgXboSaEhd2-eGgzWwph8ukcHO88sLrOTuGNNkszE0PqqMsGw5VyIGrXGkNKER9kn5WwwzMsqw*1772275391705*6d6cc6b10705ba4087e9bdf89985ca1d658b49c52e303bba28323d0518f1ece4*p5aioY74HdZ0_iVpwDEAp9LZnfz7a8AK39bSZ2deefQ"
project_id = "5fad707a-bcd2-4fb6-805f-282da19a459a"
env_id = "6a3e066a-0a24-49af-a509-737c33ee1c4b"
graphql = "https://backboard.railway.com/graphql/v2"

def graphql_req(query, variables):
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    body = {'query': query, 'variables': variables}
    req = urllib.request.Request(graphql, data=json.dumps(body).encode(), headers=headers, method='POST')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())

# Create new service
print("Creating new frontend service...")
q = 'mutation($input: ServiceCreateInput!) { serviceCreate(input: $input) { id name } }'
result = graphql_req(q, {
    'input': {
        'projectId': project_id,
        'name': 'frontend-v2'
    }
})
service_id = result['serviceCreate']['id']
print(f"Created service: {service_id}")

# Set root directory
print("Setting root directory...")
q = 'mutation($serviceId: String!, $environmentId: String!, $input: ServiceInstanceUpdateInput!) { serviceInstanceUpdate(serviceId: $serviceId, environmentId: $environmentId, input: $input) }'
graphql_req(q, {
    'serviceId': service_id,
    'environmentId': env_id,
    'input': {'rootDirectory': 'frontend'}
})
print("Root directory set")

# Set environment variable
print("Setting environment variables...")
q = 'mutation($input: VariableUpsertInput!) { variableUpsert(input: $input) }'
graphql_req(q, {
    'input': {
        'projectId': project_id,
        'environmentId': env_id,
        'serviceId': service_id,
        'name': 'NEXT_PUBLIC_API_URL',
        'value': 'https://backend-production-f8f2.up.railway.app'
    }
})
print("Environment variables set")

# Trigger deploy
print("Triggering deployment...")
q = 'mutation($serviceId: String!, $environmentId: String!) { serviceInstanceDeploy(serviceId: $serviceId, environmentId: $environmentId) }'
graphql_req(q, {
    'serviceId': service_id,
    'environmentId': env_id
})
print("Deployment triggered!")
print(f"Service ID: {service_id}")
