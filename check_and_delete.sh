#!/bin/bash

# Check if 'backup-service' exists in the list of services
if kubectl get svc | grep -q 'backup-service'; then
    echo "'backup-service' found. Deleting the deployment..."
    kubectl delete -f /home/ubuntu/backup_deployment.yaml
else
    echo "'backup-service' not found. No action taken."
fi

