Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Synchronous Counter Design Assistant - Launching Application" -ForegroundColor Cyan
Write-Host "  Course: EC2201 Unit III - Synchronous Sequential Circuits" -ForegroundColor Yellow
Write-Host "  Student: Sabariayyan P (Section B)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

try {
    $pyVersion = python --version
    Write-Host "Detected: $pyVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

Write-Host "Starting Web Server on http://127.0.0.1:5000 ..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:5000"
python app.py
