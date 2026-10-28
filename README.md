# Jon's Tree Service Contract Radar

Public dashboard: https://friedt1.github.io/Jons-contract-radar/

## Setup

1. Upload `index.html`, `opportunities.json`, `collector.py`, and `.github/workflows/daily-collector.yml` into the repository with the same relative paths.
2. Keep GitHub Pages deployed from `main` / `(root)`.
3. Get a SAM.gov API key from the official SAM.gov service and add it under repository Settings > Secrets and variables > Actions > New repository secret named `SAM_API_KEY`. Never paste API keys into the public repository or chat.
4. In Actions, run `Daily contract collector` manually once. Confirm it updates `opportunities.json` and review the run logs. Then scheduled daily runs should occur (GitHub schedule timing is approximate).
5. Check Settings > Actions > General > Workflow permissions if push fails; enable Read and write permissions, if allowed.

## Limitations

Only SAM.gov is implemented as an API integration, and it is not connected until a key is provided and a successful run is verified. The collector screens by NY/PA state and keyword, not actual 2-hour road travel time. No 64-source coverage, SMS, or verified leads are claimed. GitHub Pages is public: do not put private notes, phone numbers, or credentials in JSON.
