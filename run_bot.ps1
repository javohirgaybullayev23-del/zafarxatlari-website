$ErrorActionPreference = 'Stop'
if (-not (Test-Path '.venv\Scripts\python.exe')) { py -m venv .venv }
& .venv\Scripts\python.exe -m pip install -r requirements.txt
if (Test-Path '.env') {
	Get-Content '.env' | ForEach-Object {
		$line = $_.Trim()
		if ($line -and -not $line.StartsWith('#') -and $line.Contains('=')) {
			$parts = $line.Split('=', 2)
			$value = $parts[1].Trim()
			$value = $value.Trim("'")
			$value = $value.Trim('"')
			[Environment]::SetEnvironmentVariable($parts[0].Trim(), $value, 'Process')
		}
	}
}
if (-not $env:BOT_TOKEN) { throw 'BOT_TOKEN environment variable sozlanmagan.' }
& .venv\Scripts\python.exe bot.py