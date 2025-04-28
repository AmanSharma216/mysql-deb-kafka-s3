#!/bin/bash

namespace="mysql-deployment"

echo "Deleting all resources in namespace: $namespace..."
kubectl delete all --all -n "$namespace"

echo "Applying all YAML files in current directory to namespace: $namespace"
for file in *.yaml; do
    if [[ -f "$file" ]]; then
        echo "Applying $file"
        kubectl apply -n "$namespace" -f "$file"
    fi
done

echo "✅ All resources applied."