@echo off
REM echo Starting PostgreSQL container...

docker ps -a --format "{{.Names}}" | find "sql_container" >nul
if %errorlevel% equ 0 (
    echo Container sql_container already exists.
    echo Starting existing container...
    docker start sql_container
) else (
    echo Creating and starting new container...
    docker run --name sql_container ^
      -e POSTGRES_USER=denis ^
      -e POSTGRES_PASSWORD=denis ^
      -e POSTGRES_DB=test_sql ^
      -p 5433:5432 ^
      -d postgres:16
)

echo Waiting for PostgreSQL to start...
timeout /t 2

REM echo PostgreSQL is running!
REM echo To connect: docker exec -it sql_container psql -U denis-d test_sql