"""SAM.gov opportunities collector. Requires SAM_API_KEY GitHub Actions secret.
Never fabricates leads; outputs empty list with explicit status if unavailable.
"""
import datetime as dt
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

OUT = Path(__file__).with_name('opportunities.json')
KEYWORDS = ['tree removal', 'tree trimming', 'tree cutting', 'stump grinding',
            'land clearing', 'site clearing', 'brush clearing', 'vegetation management',
            'right of way clearing', 'forestry', 'hazardous trees', 'grubbing',
            'utility line clearance', 'site preparation']
COUNTIES = {'Chemung', 'Steuben', 'Schuyler', 'Tioga', 'Tompkins', 'Broome',
            'Cortland', 'Seneca', 'Yates', 'Bradford', 'Susquehanna', 'Lycoming'}

def run():
    now = dt.datetime.now(dt.timezone.utc)
    result = {'updated': now.isoformat(), 'opportunities': [], 'source_status': {},
              'coverage_note': 'Federal opportunities only; 2-hour driving times not verified. Other sources not connected.'}
    key = os.environ.get('SAM_API_KEY', '').strip()
    if not key:
        result['source_status']['SAM.gov'] = 'Not connected — SAM_API_KEY secret missing'
        return result
    # SAM.gov public opportunities API uses a required API key and date window.
    params = {'limit': 100, 'offset': 0, 'postedFrom': (now-dt.timedelta(days=30)).strftime('%m/%d/%Y'),
              'postedTo': now.strftime('%m/%d/%Y'), 'api_key': key}
    url = 'https://api.sam.gov/opportunities/v2/opportunities?' + urllib.parse.urlencode(params)
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'JonsContractRadar/1.0'})
        with urllib.request.urlopen(req, timeout=45) as response:
            payload = json.load(response)
        records = payload.get('opportunitiesData', [])
        for item in records:
            title = str(item.get('title') or '')
            description = str(item.get('description') or '')
            if not any(k in (title+' '+description).lower() for k in KEYWORDS):
                continue
            loc = item.get('placeOfPerformance') or {}
            state = (loc.get('state') or {}).get('code', '') if isinstance(loc.get('state'), dict) else ''
            city = (loc.get('city') or {}).get('name', '') if isinstance(loc.get('city'), dict) else ''
            if state not in ('NY', 'PA'):
                continue
            # Conservative location screen: state only; clearly flag unverified distance.
            notice_id = item.get('noticeId')
            link = item.get('uiLink') or (f'https://sam.gov/opp/{notice_id}/view' if notice_id else '')
            if not link.startswith('https://'):
                continue
            result['opportunities'].append({
                'title': title, 'market': 'Government', 'stage': 'Live' if item.get('active') == 'Yes' else 'Unverified',
                'location': ', '.join(x for x in (city, state) if x), 'distance_status': 'Driving time unverified',
                'posted': item.get('postedDate'), 'deadline': item.get('responseDeadLine'),
                'url': link, 'source': 'SAM.gov'})
        result['source_status']['SAM.gov'] = f'Fetched {len(records)} notices; {len(result["opportunities"])} NY/PA keyword matches (not road-time verified)'
    except Exception as exc:
        result['source_status']['SAM.gov'] = 'Fetch failed: ' + type(exc).__name__ + ' — check API key, endpoint, or rate limits'
    return result

if __name__ == '__main__':
    OUT.write_text(json.dumps(run(), indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
