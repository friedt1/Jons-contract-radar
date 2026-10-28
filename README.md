# Jon's Tree Service Contract Radar

A working deployable first-stage website and scheduled federal contract collector. No invented leads.

## Launch
1. Create a GitHub repository and upload all files, including `.github/workflows/radar.yml`.
2. In GitHub Settings > Pages, set source to GitHub Actions.
3. Create a personal SAM.gov API key (https://open.gsa.gov/api/get-opportunities-public-api/).
4. In repository Settings > Secrets and variables > Actions, add `SAM_API_KEY` (do not put the key in source files).
5. In Actions, run `Refresh contract radar` manually once. GitHub Pages URL appears in deployment details.
6. Workflow runs daily at 12:15 UTC; schedules may be delayed.

## Limitations
- Collector currently fetches only federal SAM.gov postings, not local municipalities, private leads, permits or commercial jobs. Those require separate source connectors.
- Keyword search is not exhaustive; SAM.gov API quotas and limits apply.
- Regional screening is only approximate. A routing API is required to enforce 120-minute drive time.
- A listing may have closed since collection; verify the deadline and source.
- No SMS configured.

## 64-source expansion registry
source_registry.csv contains 64 distinct targets across six markets. These are research targets, NOT 64 live integrations. Unverified portals use search links rather than invented official bid URLs. Actual automation must add and test each connector, deduplicate results, verify dates, and calculate drive times.
