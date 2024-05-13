docker pull postgres:alpine
docker run --name my-postgres-container -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
