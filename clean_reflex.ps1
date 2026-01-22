# Script para limpar cache e forçar reconstrução do Reflex
# Execute isso no terminal quando tiver erros de "No module update" ou UI travada.

Write-Host "🛑 Parando processos do python..."
taskkill /F /IM python.exe /T 2>$null

Write-Host "🧹 Limpando pasta .web (cache do frontend)..."
if (Test-Path ".web") {
    Remove-Item -Recurse -Force ".web"
}

Write-Host "🧹 Limpando __pycache__..."
Get-ChildItem -Path "." -Filter "__pycache__" -Recurse | Remove-Item -Recurse -Force

Write-Host "✅ Limpeza concluída!"
Write-Host "🚀 Agora execute: reflex run"
