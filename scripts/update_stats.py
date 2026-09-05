#!/usr/bin/env python3
"""Build small, GitHub-hosted profile cards from public GitHub data. No dependencies."""
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
import os
import re
import urllib.request
import urllib.parse

USER = 'Prakhyat-Srivastava'
ROOT = Path(__file__).resolve().parents[1]
BG, INK, MUTED, ACCENT, BORDER = '#0B1727', '#EAF2FF', '#AFC6D9', '#57D9EF', '#294556'


def fetch(url):
    headers = {'User-Agent': f'{USER}-profile', 'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GH_TOKEN')
    # Tokens only go to GitHub's API, never the public calendar endpoint.
    if token and url.startswith('https://api.github.com/'):
        headers['Authorization'] = f'Bearer {token}'
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return response.read().decode('utf-8')


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.labels = {}, {}
        self.target, self.buffer = None, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ('td', 'rect') and attrs.get('data-date'):
            self.cells[attrs['id']] = {'date': attrs['data-date'], 'level': int(attrs['data-level'])}
        if tag == 'tool-tip':
            self.target, self.buffer = attrs.get('for'), []

    def handle_data(self, data):
        if self.target:
            self.buffer.append(data)

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.target:
            self.labels[self.target] = ''.join(self.buffer).strip()
            self.target = None

    def days(self, today):
        start = today - timedelta(days=364)
        result = []
        for key, cell in self.cells.items():
            day = date.fromisoformat(cell['date'])
            if not start <= day <= today:
                continue
            label = self.labels.get(key, '')
            match = re.match(r'(No|[\d,]+) contributions? on ', label)
            if not match:
                raise ValueError(f'Missing or changed contribution label for {day}; retaining previous assets')
            count = 0 if match[1] == 'No' else int(match[1].replace(',', ''))
            if not 0 <= cell['level'] <= 4 or (count == 0) != (cell['level'] == 0):
                raise ValueError('Invalid contribution intensity')
            result.append({**cell, 'count': count})
        result.sort(key=lambda d: d['date'])
        expected = [(start + timedelta(days=i)).isoformat() for i in range(365)]
        if [d['date'] for d in result] != expected:
            raise ValueError('Incomplete contribution calendar; retaining previous assets')
        return result


def txt(x, y, value, size=14, fill=INK, weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}">{escape(str(value))}</text>'


def svg(width, height, title, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title">'
            f'<title id="title">{escape(title)}</title><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="12" fill="{BG}" stroke="{BORDER}"/>'
            f'<g font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">{body}</g></svg>\n')


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d['count'] else 0
        longest = max(longest, run)
    tail = days if days[-1]['count'] else days[:-1]
    current = 0
    for d in reversed(tail):
        if not d['count']:
            break
        current += 1
    return current, longest


def build(repos, days, today):
    # Keep the generated profile itself and forked projects out of project metrics.
    projects = [r for r in repos if not r['fork'] and not r['private'] and r['name'].lower() != USER.lower()]
    languages = Counter(r['language'] for r in projects if r['language'])
    total, active = sum(d['count'] for d in days), sum(d['count'] > 0 for d in days)
    stars = sum(r['stargazers_count'] for r in projects)
    current, longest = streaks(days)
    stamp = today.isoformat()
    body = txt(24, 34, 'PUBLIC GITHUB SNAPSHOT', 14, ACCENT, 600)
    metrics = [(len(projects), 'Project repositories'), (stars, 'Stars received'), (total, 'Contributions · 365 days'), (active, 'Active days · 365 days')]
    for (value, label), (x, y) in zip(metrics, [(24,94),(236,94),(24,181),(236,181)]):
        body += txt(x,y,value,38,INK,650) + txt(x,y+25,label,13,MUTED)
    body += txt(24,245,f'Updated {stamp} UTC · Public data only',12,MUTED)
    cards = {'assets/stats.svg': svg(440,270,'Public GitHub snapshot. '+', '.join(f'{v} {l}' for v,l in metrics)+f'. Updated {stamp}.',body)}
    body = txt(24,34,'REPOSITORY LANGUAGES',14,ACCENT,600)
    body += txt(24,58,'Primary language · original public projects',12,MUTED)
    ordered = sorted(languages.items(),key=lambda v:(-v[1],v[0]))
    if len(ordered)>6:
        ordered = ordered[:5] + [('Other',sum(v for _,v in ordered[5:]))]
    for i,(lang,count) in enumerate(ordered):
        y=87+i*28
        body += txt(24,y,lang,13) + f'<rect x="168" y="{y-10}" width="{count/max(languages.values())*210:.2f}" height="8" rx="2" fill="{ACCENT}"/>' + txt(395,y,count,13)
    body += txt(24,245,'Repository counts, not a measure of proficiency.',12,MUTED)
    cards['assets/languages.svg'] = svg(440,270,'Repository primary languages: '+', '.join(f'{k}: {v}' for k,v in ordered),body)
    body = txt(25,32,'PUBLIC CONTRIBUTION CALENDAR',15,ACCENT,600)
    body += txt(25,55,f"{days[0]['date']} to {days[-1]['date']} · {total} contributions · {active} active days",13,MUTED)
    colors=['#142D3D','#1D5870','#287F99','#38ACC5','#57D9EF']
    first=date.fromisoformat(days[0]['date'])
    start=first-timedelta(days=(first.weekday()+1)%7)
    months=set()
    for d in days:
        dt=date.fromisoformat(d['date']); col=(dt-start).days//7; row=(dt.weekday()+1)%7
        x,y=51+col*15,87+row*15
        if dt.day<=7 and dt.month not in months:
            months.add(dt.month);body += txt(x,78,dt.strftime('%b'),10,MUTED)
        body += f'<rect x="{x}" y="{y}" width="11" height="11" rx="2" fill="{colors[d["level"]]}"><title>{d["date"]}: {d["count"]} contributions</title></rect>'
    for label,row in [('Mon',1),('Wed',3),('Fri',5)]:body+=txt(16,96+row*15,label,9,MUTED)
    body += txt(25,220,f'Current streak: {current} days  /  Longest in this window: {longest} days',12,MUTED)
    body += txt(669,220,'Less',11,MUTED)
    for i,c in enumerate(colors):body+=f'<rect x="{700+i*15}" y="210" width="11" height="11" rx="2" fill="{c}"/>'
    body += txt(785,220,'More',11,MUTED)
    cards['assets/contributions.svg']=svg(860,243,f'Public contribution calendar from {days[0]["date"]} to {stamp}: {total} contributions.',body)
    source = {'updated_utc':stamp,'sources':[f'https://api.github.com/users/{USER}/repos?per_page=100',f'https://github.com/users/{USER}/contributions'], 'scope':'Original public repositories excluding profile repository; public calendar for trailing 365 days', 'repository_count':len(projects),'stars':stars,'languages_by_primary_repository_count':dict(languages),'unclassified_repositories':sum(not r['language'] for r in projects),'contributions':total,'active_days':active,'current_streak':current,'longest_streak_in_window':longest,'days':days}
    cards['assets/stats-data.json']=json.dumps(source,indent=2)+'\n'
    rows='\n'.join(f'| {escape(k)} | {v} |' for k,v in ordered)
    cards['docs/activity.md'] = f'''# Public GitHub activity

Updated **{stamp} UTC** from [GitHub public repositories](https://github.com/{USER}?tab=repositories) and the [public contribution calendar](https://github.com/users/{USER}/contributions).

- Original public project repositories: **{len(projects)}** (excludes forks and this profile repository).
- Stars received across those repositories: **{stars}**.
- Contributions: **{total}** from **{days[0]['date']}** through **{stamp}**.
- Active days: **{active}** (at least one contribution).
- Current streak: **{current} days**; longest within this 365-day window: **{longest} days**.

Current streak includes today when active, otherwise runs backward from yesterday to allow today to complete. Dates follow GitHub's public calendar; refresh dates use UTC. Calendar contributions follow GitHub's attribution rules and can include anonymized private counts only if the owner already makes those counts publicly visible. No private repositories or private activity details are queried.

## Primary repository language

| GitHub classification | Repositories |
| --- | ---: |
{rows}

**{sum(not r['language'] for r in projects)} repositories** have no primary language classification and are omitted from the language chart. These counts describe repository contents, not skill levels or time spent coding. Notebooks are retained as GitHub classifies them.

[Machine-readable snapshot](../assets/stats-data.json) · [Generator](../scripts/update_stats.py)
'''
    return cards


def markdown_text(value):
    # Remote repository descriptions are data, never raw Markdown/HTML.
    value = ' '.join(str(value or '').split())
    value = escape(value)
    return re.sub(r'([\\`*_{}\[\]()#+.!|>~-])', r'\\\1', value)


def update_readme(repos):
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    projects = [r for r in repos if not r['fork'] and not r['private'] and r['name'].lower() != USER.lower()]
    by_name = {r['name']: r for r in projects}
    def replace(start, end, content):
        nonlocal readme
        if readme.count(start) != 1 or readme.count(end) != 1:
            raise ValueError('Missing or duplicate dynamic README markers')
        before, rest = readme.split(start, 1)
        _, after = rest.split(end, 1)
        readme = before + start + '\n' + content + '\n' + end + after
    recent = sorted(projects, key=lambda r: r['pushed_at'], reverse=True)[:3]
    content = '**Recently updated repositories**\n\n'
    for r in recent:
        description = markdown_text(r.get('description') or 'Explore the repository and its latest changes.')
        url = f'https://github.com/{USER}/' + urllib.parse.quote(r['name'], safe='')
        content += f"- **[{markdown_text(r['name'])}]({url})** · pushed {r['pushed_at'][:10]}\n  {description}\n"
    replace('<!-- RECENT-PROJECTS:START -->', '<!-- RECENT-PROJECTS:END -->', content.rstrip())
    for name in ('analytics-platform-admin-dashboard-powerbi','Amazon_Product_Sentiment_Analysis','movie-rating-prediction','HeartDisease-Analysis'):
        r = by_name.get(name)
        if r:
            content = f"<sub>Latest repository push: {r['pushed_at'][:10]} · {r['stargazers_count']} stars · {r['forks_count']} forks</sub>" + '\n\n' + markdown_text(r.get('description') or 'Explore this repository for its current project documentation.')
        else:
            content = '<sub>This repository is no longer publicly listed. See the recent-project list for current work.</sub>'
        replace(f'<!-- REPO-{name}:START -->', f'<!-- REPO-{name}:END -->', content)
    return readme


def main():
    today=datetime.now(timezone.utc).date()
    repos=[]
    for page in range(1,101):
        batch=json.loads(fetch(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}'))
        if not isinstance(batch,list):raise ValueError('Invalid repositories response')
        repos.extend(batch)
        if len(batch)<100:break
    if not repos:raise ValueError('Empty repository response')
    parser=Calendar();parser.feed(fetch(f'https://github.com/users/{USER}/contributions'))
    days=parser.days(today)
    outputs=build(repos,days,today)
    outputs['README.md']=update_readme(repos)
    # Validate all data before replacing any last-known-good assets.
    for filename,content in outputs.items():
        path=ROOT/filename;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(content,encoding='utf-8')
    print(f'Refreshed {len(outputs)} files for {today}.')


if __name__=='__main__':main()
