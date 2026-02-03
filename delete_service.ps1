$token = "rw_Fe26.2**69e77d4e9a7e4b79d98a8c31301d334cefe64f95964a6ec9737239ebb1e1a044*XPgjIlCZzrc2uR10MgFYxA*dDZLCv5aOfEOfgXboSaEhd2-eGgzWwph8ukcHO88sLrOTuGNNkszE0PqqMsGw5VyIGrXGkNKER9kn5WwwzMsqw*1772275391705*6d6cc6b10705ba4087e9bdf89985ca1d658b49c52e303bba28323d0518f1ece4*p5aioY74HdZ0_iVpwDEAp9LZnfz7a8AK39bSZ2deefQ"
$serviceId = "0897eded-6dc0-445d-996e-8e7e4779fe55"

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$body = @{
    query = "mutation(`$id: String!) { serviceDelete(id: `$id) }"
    variables = @{
        id = $serviceId
    }
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "https://backboard.railway.com/graphql/v2" -Method Post -Headers $headers -Body $body
    Write-Host "Service deleted successfully"
} catch {
    Write-Host "Error: $_"
}
