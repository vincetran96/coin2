#! /usr/bin/env bash
set -eo pipefail

# Create exchange schemas in schema registry
SCHEMA_REGISTRY="http://localhost:58081"
SCHEMAS_DIR="${1:-./assets/kafka/schemas}"

echo "Registering schemas from: $SCHEMAS_DIR"

# Loop through all schema files
for schema_file in "$SCHEMAS_DIR"/*.json; do
    [ -e "$schema_file" ] || continue
    
    exchange=$(basename "$schema_file" .json)
    subject="${exchange}-value"  # Standard naming usually: {topic}-value
    
    echo "Registering schema: $subject"
    
    payload=$(jq -R -s '{schema: .}' < "$schema_file")

    tmp=$(mktemp)
    http_code=$(curl -s -o "$tmp" -w "%{http_code}" -X POST "$SCHEMA_REGISTRY/subjects/$subject/versions" \
        -H "Content-Type: application/vnd.schemaregistry.v1+json" \
        -d "$payload" || true)
    body=$(cat "$tmp"); rm -f "$tmp"

    if [ "$http_code" -eq 200 ] || [ "$http_code" -eq 201 ]; then
        schema_id=$(echo "$body" | jq -r '.id // empty')
        if [ -n "$schema_id" ]; then
            echo "   Registered with ID: $schema_id"
        else
            echo "   Unexpected response (no id): $body"
            exit 1
        fi
    else
        echo "   Schema registration failed: HTTP $http_code — $body"
        exit 1
    fi
done

echo "All schemas registered!"


# Deploy Iceberg JSON config for each exchange
KAFKA_CONNECT_ENDPOINT="http://localhost:58083"
CONFIGS_DIR="${2:-./assets/kafka/kafka_connect/iceberg}"

echo "Deploying Iceberg connectors from: $CONFIGS_DIR"

for config_file in "$CONFIGS_DIR"/*.json; do
    [ -e "$config_file" ] || continue

    connector_name=$(jq -r '.name' "$config_file")
    echo "Deploying: $connector_name"

    tmp=$(mktemp)
    http_code=$(curl -s -o "$tmp" -w "%{http_code}" -X POST "$KAFKA_CONNECT_ENDPOINT/connectors" \
        -H "Content-Type: application/json" \
        -d @"$config_file")

    body=$(cat "$tmp"); rm -f "$tmp"

    if [ "$http_code" -eq 201 ]; then
        echo "   Created: $(echo "$body" | jq -r '.name' 2>/dev/null || echo "$connector_name")"
    elif [ "$http_code" -eq 409 ]; then
        echo "  i Connector exists, updating config for $connector_name"
        cfg=$(jq -c '.config' "$config_file")
        tmp2=$(mktemp)
        http_code2=$(curl -s -o "$tmp2" -w "%{http_code}" -X PUT "$KAFKA_CONNECT_ENDPOINT/connectors/$connector_name/config" \
            -H "Content-Type: application/json" \
            -d "$cfg")
        body2=$(cat "$tmp2"); rm -f "$tmp2"
        if [ "$http_code2" -eq 200 ]; then
            echo "   Updated"
        else
            echo "   Update failed: HTTP $http_code2 — $body2"
            exit 1
        fi
    else
        echo "   Deploy failed: HTTP $http_code — $body"
        exit 1
    fi
done

echo ""
echo "Checking connector status:"
curl -s "$KAFKA_CONNECT_ENDPOINT/connectors" | jq -r '.[]'
