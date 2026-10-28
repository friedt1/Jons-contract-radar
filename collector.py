import os,json,re,datetime,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).parent
KEYWORDS=['tree removal','tree trimming','tree cutting','stump grinding','land clearing','site clearing','brush clearing','vegetation management','right of way clearing','forestry','hazardous trees','logging','grubbing','utility line clearance','site preparation']
# Approximate geographic screening; exact 120-minute road routing needs routing provider.
NEAR={'NY':{'Chemung','Steuben','Schuyler','Tioga','Tompkins','Broome','Cortland','Seneca','Yates','Ontario','Cayuga'},'PA':{'Bradford','Tioga','Susquehanna','Lycoming','Sullivan','Wyoming'}}
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'ContractRadar/1.0 (business lead research)'})
 with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)
def score(title,description):
 s=(title+' '+description).lower()
 return min(100,35+sum(12 for k in KEYWORDS if k in s)+ (15 if 'tree' in title.lower() or 'clearing' in title.lower() else 0))
def sam():
 key=os.getenv('SAM_API_KEY')
 if not key:return [],'SAM_API_KEY not configured'
 now=datetime.date.today(); start=now-datetime.timedelta(days=30)
 out=[];errors=[]
 for state in ('NY','PA'):
  params={'api_key':key,'postedFrom':start.strftime('%m/%d/%Y'),'postedTo':now.strftime('%m/%d/%Y'),'state':state,'limit':100,'offset':0}
  try:
   result=fetch('https://api.sam.gov/opportunities/v2/search?'+urllib.parse.urlencode(params))
   for item in result.get('opportunitiesData',[]):
    title=item.get('title') or '';desc=item.get('description') or ''
    if not any(k in (title+' '+desc).lower() for k in KEYWORDS):continue
    place=item.get('placeOfPerformance') or {}; st=(place.get('state') or {}).get('code') or state
    county=(place.get('county') or {}).get('name') or ''
    if county and county.title() not in NEAR.get(st,set()):continue
    out.append({'id':item.get('noticeId'),'title':title,'market':'Government','stage':'Live / verify deadline','location':(place.get('city') or {}).get('name','')+', '+st,'county':county,'posted':item.get('postedDate'),'deadline':item.get('responseDeadLine'),'source':'SAM.gov','url':item.get('uiLink') or 'https://sam.gov/opportunities','score':score(title,desc),'distance_status':'Regional candidate — drive time unverified'})
  except Exception as e:errors.append(state+': '+str(e))
 return out,'; '.join(errors)
def main():
 jobs,error=sam();dedup={j['id'] or j['title']:j for j in jobs}
 payload={'updated':datetime.datetime.now(datetime.timezone.utc).isoformat(),'opportunities':sorted(dedup.values(),key=lambda j:-j['score']),'source_status':{'SAM.gov':error or 'Fetched successfully'},'coverage_note':'Federal feed only; county/city/private/development feeds not connected. Travel times not verified. Missing deadline is not an active bid confirmation.'}
 (ROOT/'data'/'opportunities.json').write_text(json.dumps(payload,indent=2))
 print('Saved',len(dedup),'opportunities; status:',error)
if __name__=='__main__':main()
