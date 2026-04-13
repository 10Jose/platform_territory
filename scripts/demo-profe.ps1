# Demostración HU-07: asume que ya corre `docker compose up --build` en la raíz del repo.
# Uso:  .\scripts\demo-profe.ps1
#      .\scripts\demo-profe.ps1 -BaseUrl "http://127.0.0.1:8002"

param(
    [string]$BaseUrl = "http://localhost:8002"
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== 1) GET /health (servicio vivo) ===" -ForegroundColor Cyan
$h = Invoke-RestMethod -Uri "$BaseUrl/health"
$h | ConvertTo-Json -Compress
if ($h.status -ne "ok") { throw "Health no devolvio status=ok" }

Write-Host ""
Write-Host "=== 2) POST /sync/zones (descarga CSV mock -> transforma -> guarda en BD) ===" -ForegroundColor Cyan
$r = Invoke-RestMethod -Method Post -Uri "$BaseUrl/sync/zones"
$r | ConvertTo-Json -Depth 6

Write-Host ""
Write-Host "=== Listo ===" -ForegroundColor Green
Write-Host "Pide a la docente que abra tambien: $BaseUrl/docs (Swagger UI)" -ForegroundColor Yellow
Write-Host "Datos clave: transformation_run_id=$($r.transformation_run_id) rows_read=$($r.rows_read) insertados=$($r.rows_inserted) actualizados=$($r.rows_updated)" -ForegroundColor Yellow

Write-Host ""
Write-Host "=== 3) (Opcional) Ver filas en Postgres ===" -ForegroundColor Cyan
Write-Host "Si tienes Docker, en otra terminal:" -ForegroundColor Gray
Write-Host '  docker compose exec db-transformation psql -U postgres -d db_transformation -c "SELECT zone_key, densidad_poblacional FROM transformed_zone_data;"' -ForegroundColor Gray
