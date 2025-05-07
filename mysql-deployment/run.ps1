$namespace = "mysql-deployment"

Write-Host "deleting all in  namespace..."
kubectl delete all --all -n mysql-deployment

Write-Host "Applying all YAML files in current directory to namespace: $namespace"

Get-ChildItem -Filter *.yaml | ForEach-Object {
    Write-Host "Applying $($_.Name)"
    kubectl apply -n $namespace -f $_.FullName
}

Write-Host "✅ All resources applied."
