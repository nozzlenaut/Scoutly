[CmdletBinding()]
param(
    [switch]$Commit,
    [switch]$Push
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".git")) {
    throw "Run this script from the root of your Scoutly repository (the folder containing .git)."
}

if ($Push -and -not $Commit) {
    throw "Use -Commit together with -Push."
}

$readme = @'
# PriceSift

**Find the best price for what you already want.**

PriceSift is an exact-item price finder for used and secondhand products. Instead of making shoppers dig through broad marketplace searches, it resolves the item they mean, removes obvious mismatches and risky listings, and surfaces a small set of useful current prices.

`Scoutly` remains the internal repository and infrastructure name.

## What PriceSift does

- Resolves searches to an exact catalog product, specification, or ISBN.
- Searches current marketplace inventory from eBay and supported specialty retailers.
- Filters parts-only, broken, incomplete, accessory-only, wrong-model, and misleading variation listings when detectable.
- Separates fixed-price results from optional ending-soon auctions.
- Ranks a small set of useful listings instead of returning a wall of marketplace noise.
- Tracks price snapshots and provides typical-price context after enough inventory history is available.
- Supports an optional **US listings only** filter for eBay results.
- Collects lightweight product-usage analytics without storing accounts, cookies, IP addresses, or personal identifiers.

## Search styles

PriceSift uses different search flows depending on how a product is identified:

1. **Direct exact-item search** — cameras, GPUs, consoles, and LEGO sets.
2. **Specification builders** — RAM and desktop CPUs.
3. **Identifier search** — Books by ISBN-10 or ISBN-13.

This keeps each category focused on the details that actually define the product instead of forcing every category into the same generic form.

## Marketplace coverage

- **eBay** — used Buy It Now listings and optional ending-soon auctions.
- **KEH** — selected camera inventory through the current public pilot, with additional lens tooling kept private for testing.

Outbound merchant links may be affiliate links. This does not change the displayed price or ranking rules.

## Project structure

```text
backend/   FastAPI API, marketplace providers, filtering, ranking, analytics, and tests
frontend/  Next.js web application and admin tools
docs/      Architecture notes, status, roadmap, API notes, and changelog
```

## Run locally

### Backend

```bash
cd backend
py -3.12 -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS or Linux
source .venv/bin/activate
```

Install dependencies and start the API:

```bash
pip install -r requirements.txt
PYTHONPATH=. pytest -q
python -m uvicorn app.main:app --reload --port 8000
```

On Windows PowerShell, use `$env:PYTHONPATH="."` before running tests when needed.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000` and the backend at `http://localhost:8000` by default.

## Environment setup

Copy the included examples before adding local credentials:

```text
backend/.env.example
frontend/.env.example
```

The backend supports eBay credentials, optional affiliate tracking, PostgreSQL, admin authentication, and marketplace-notification configuration. Never commit real secrets.

## Deployment

The current production setup uses:

- **Vercel** for the Next.js frontend.
- **Railway** for the FastAPI backend and scheduled jobs.
- **PostgreSQL** for persistent analytics, reports, QA evaluations, and price history.

## Documentation

- [Changelog](docs/CHANGELOG.md)
- [Current status](docs/STATUS.md)
- [Roadmap](docs/ROADMAP.md)
- [Product catalog notes](docs/PRODUCT_CATALOG.md)
- [API notes](docs/API.md)
- [Database notes](docs/DATABASE.md)

## License

Licensed under the [MIT License](LICENSE).
'@

$releaseEntry = @'
## v0.6.27

- Corrects light-analytics click attribution.
- Counts a click toward search analytics only when it can be linked to a matching public search that occurred before the click.
- Excludes older affiliate click history from search-to-click rates, category click totals, and provider click totals.
- Shows older or unlinked clicks separately so historical records remain visible without distorting current usage.
- Keeps the existing privacy model: no IP addresses, cookies, accounts, or personal identifiers.
- Requires no new environment variables or database changes.
- Brings the backend suite to 216 passing tests; the production Next.js build passes.
'@

$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$readmePath = Join-Path $PWD "README.md"
[System.IO.File]::WriteAllText($readmePath, $readme + "`n", $utf8NoBom)

$changelogPath = Join-Path $PWD "docs\CHANGELOG.md"
if (-not (Test-Path $changelogPath)) {
    throw "Could not find docs\CHANGELOG.md."
}

$changelog = Get-Content $changelogPath -Raw
if ($changelog -notmatch '(?m)^## v0\.6\.27\s*$') {
    $withoutHeading = $changelog -replace '^\uFEFF?# Changelog\s*', ''
    $updatedChangelog = "# Changelog`r`n`r`n$releaseEntry`r`n`r`n" + $withoutHeading.TrimStart()
    [System.IO.File]::WriteAllText($changelogPath, $updatedChangelog.TrimEnd() + "`n", $utf8NoBom)
}

$oldReadmes = @(Get-ChildItem -Path $PWD -Filter "README-v*.md" -File)
foreach ($file in $oldReadmes) {
    Remove-Item $file.FullName -Force
}

Write-Host ""
Write-Host "README cleanup complete." -ForegroundColor Green
Write-Host "Replaced README.md with a permanent project overview."
Write-Host "Added v0.6.27 to docs/CHANGELOG.md when missing."
Write-Host "Removed $($oldReadmes.Count) versioned README files."
Write-Host ""

git status --short

if ($Commit) {
    git add -A
    git commit -m "Clean up README files"
    if ($LASTEXITCODE -ne 0) {
        throw "Git commit failed. Review the output above."
    }

    if ($Push) {
        git push
        if ($LASTEXITCODE -ne 0) {
            throw "Git push failed. Review the output above."
        }
    }
}
