docker run --name week5-postgres ^
  -e POSTGRES_USER=denis ^
  -e POSTGRES_PASSWORD=denis ^
  -e POSTGRES_DB=analytics ^
  -p 5432:5432 ^
  -d postgres:16
