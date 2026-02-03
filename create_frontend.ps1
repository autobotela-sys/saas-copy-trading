$token = "rw_Fe26.2**69e77d4e9a7e4b79d98a8c31301d334cefe64f95964a6ec9737239ebb1e1a044*XPgjIlCZzrc2uR10MgFYxA*dDZLCv5aOfEOfgXboSaEhd2-eGgzWwph8ukcHO88sLrOTuGNNkszE0PqqMsGw5VyIGrXGkNKER9kn5WwwzMsqw*1772275391705*6d6cc6b10705ba4087e9bdf89985ca1d658b49c52e303bba28323d0518f1ece4*p5aioY74HdZ0_iVpwDEAp9LZnfz7a8AK39bSZ2deefQ"
$projectId = "5fad707a-bcd2-4fb6-805f-282da19a459a"
$envId = "6a3e066a-0a24-49af-a509-737c33ee1c4b"
$repo = "autobotela-sys/saas-copy-trading"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Create service
Write-Host "Creating frontend service..."
$body = @{
    query = "mutation(`$input: ServiceCreateInput!) { serviceCreate(input: `$input) { id name } }"
    variables = @{
        input = @{
            projectId = $projectId
            name = "frontend"
            source = @{
                repo = $repo
                branch = "master"
            }
        }
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "https://backboard.railway.com/graphql/v2" -Method Post -Headers $headers -Body $body
$serviceId = $response.data.serviceCreate.id
Write-Host "Created service: $serviceId"

# Set root directory
Write-Host "Setting root directory to 'frontend'..."
$body = @{
    query = "mutation(`$serviceId: String!, `$environmentId: String!, `$input: ServiceInstanceUpdateInput!) { serviceInstanceUpdate(serviceId: `$serviceId, environmentId: `$environmentId, input: `$input) }"
    variables = @{
        serviceId = $serviceId
        environmentId = $envId
        input = @{
            rootDirectory = "frontend"
        }
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "https://backboard.railway.com/graphql/v2" -Method Post -Headers $headers -Body $body
Write-Host "Root directory set"

# Set environment variable
Write-Host "Setting environment variables..."
$body = @{
    query = "mutation(`$input: VariableUpsertInput!) { variableUpsert(input: `$input) }"
    variables = @{
        input = @{
            projectId = $projectId
            environmentId = $envId
            serviceId = $serviceId
            name = "NEXT_PUBLIC_API_URL"
            value = "https://backend-production-f8f2.up.railway.app"
        }
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "https://backboard.railway.com/graphql/v2" -Method Post -Headers $headers -Body $body
Write-Host "Environment variables set"

# Trigger deployment
Write-Host "Triggering deployment..."
$body = @{
    query = "mutation(`$serviceId: String!, `$environmentId: String!) { serviceInstanceDeploy(serviceId: `$serviceId, environmentId: `$environmentId) }"
    variables = @{
        serviceId = $serviceId
        environmentId = $envId
    }
} | ConvertTo-Json -Depth 10

$response = Invoke-RestMethod -Uri "https://backboard.railway.com/graphql/v2" -Method Post -Headers $headers -Body $body
Write-Host "Deployment triggered!"

Write-Host ""
Write-Host "=========================================="
Write-Host "Frontend service created and deploying!"
Write-Host "Service ID: $serviceId"
Write-Host "Monitor at: https://railway.com/project/$projectId"
Write-Host "=========================================="
