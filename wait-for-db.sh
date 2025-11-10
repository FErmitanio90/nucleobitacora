#!/bin/sh
set -e

# Opción 1:
# Si DATABASE_URL contiene "@db:", asumimos que estamos dentro de Docker.
# Si no, usamos localhost.
if echo "$DATABASE_URL" | grep -q "@db:"; then
  host="db"
else
  host="localhost"
fi

port="5432"

echo "Esperando a que PostgreSQL ($host:$port) esté disponible..."
until nc -z "$host" "$port"; do
  sleep 1
done

echo "Base de datos disponible, iniciando Flask..."
exec "$@"


