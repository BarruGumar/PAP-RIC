# Audição do Piper tugão. Corre a partir da pasta do projeto.
# Cria voz-teste\ (fora do git), descarrega a voz e abre dois wav.

$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $raiz

if (-not (Test-Path (Join-Path $raiz "ric"))) {
    Write-Error "Não encontrei a pasta ric. Abre o terminal na pasta do projeto e volta a correr."
}

$destino = Join-Path $raiz "voz-teste"
New-Item -ItemType Directory -Force -Path $destino | Out-Null
Set-Location $destino

# "py -3.12" escreve no erro quando essa versão não existe. Com Stop, o script morria aí.
$oldNative = $null
if (Test-Path variable:PSNativeCommandUseErrorActionPreference) {
    $oldNative = $PSNativeCommandUseErrorActionPreference
    $PSNativeCommandUseErrorActionPreference = $false
}
$ErrorActionPreference = "Continue"

$pyCmd = $null
$tentativas = New-Object System.Collections.Generic.List[object]
foreach ($item in @(
    @("py", "-3"),
    @("py"),
    @("py", "-3.13"),
    @("py", "-3.12"),
    @("py", "-3.11"),
    @("py", "-3.10"),
    @("python"),
    @("python3")
)) {
    $tentativas.Add($item)
}
foreach ($dir in @(
    "$env:LOCALAPPDATA\Programs\Python",
    "$env:ProgramFiles\Python"
)) {
    if (-not (Test-Path $dir)) { continue }
    foreach ($sub in (Get-ChildItem $dir -Directory -ErrorAction SilentlyContinue)) {
        $exe = Join-Path $sub.FullName "python.exe"
        if (Test-Path $exe) { $tentativas.Add(@($exe)) }
    }
}

foreach ($t in $tentativas) {
    $exe = $t[0]
    $resto = @()
    if ($t.Count -gt 1) { $resto = $t[1..($t.Count - 1)] }
    & $exe @resto -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 1>$null 2>$null
    if ($LASTEXITCODE -eq 0) {
        $pyCmd = $t
        break
    }
}

$ErrorActionPreference = "Stop"
if ($null -ne $oldNative) { $PSNativeCommandUseErrorActionPreference = $oldNative }

if (-not $pyCmd) {
    Write-Error "Não encontrei Python 3.10 ou mais recente. Instala em https://www.python.org/downloads/ e marca Add python.exe to PATH. Depois corre outra vez."
}

$python = Join-Path $destino ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "A criar o ambiente em voz-teste..."
    $exe = $pyCmd[0]
    $resto = @()
    if ($pyCmd.Count -gt 1) { $resto = $pyCmd[1..($pyCmd.Count - 1)] }
    & $exe @resto -m venv (Join-Path $destino ".venv")
    if (-not (Test-Path $python)) {
        Write-Error "O ambiente voz-teste não foi criado."
    }
}

Write-Host "A instalar o Piper..."
& $python -m pip install -U pip piper-tts

$vozes = Join-Path $destino "vozes"
New-Item -ItemType Directory -Force -Path $vozes | Out-Null
$modelo = Join-Path $vozes "pt_PT-tugao-medium.onnx"
$ficha = "$modelo.json"
if (-not (Test-Path $modelo) -or -not (Test-Path $ficha)) {
    Write-Host "A descarregar a voz tugão..."
    curl.exe -L -o $modelo "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_PT/tug%C3%A3o/medium/pt_PT-tug%C3%A3o-medium.onnx"
    curl.exe -L -o $ficha "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_PT/tug%C3%A3o/medium/pt_PT-tug%C3%A3o-medium.onnx.json"
}

$aviso = Join-Path $destino "aviso-piper.wav"
$hora = Join-Path $destino "hora-piper.wav"
"são dezasseis horas, hora do comprimido" | & $python -m piper -m $modelo -f $aviso
"A consulta é às 16:54." | & $python -m piper -m $modelo -f $hora

Write-Host ""
Write-Host "WAV prontos em:"
Write-Host "  $aviso"
Write-Host "  $hora"
Start-Process $aviso
Start-Process $hora
Write-Host ""
Write-Host "Ouve os dois. O passo seguinte (Kokoro pt-PT e faster-whisper) está em docs\ROTEIRO-VOZ.md"
