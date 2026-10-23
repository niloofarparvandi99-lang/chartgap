# Builds history.json for the bubble chart: one point per day with each item's closing price and bubble.
# Usage: python3 update_history.py <dir with tgju summary-table-data/<key>.json files> <history.json> [days]
# Same weights and formula as Engine.Bubble in the page; ounce, silver and dollar carry over days they did not trade.
import json, sys, datetime

OZ = 31.1034768
ITEMS = {'sekee': (8.133, 0.9, 'ons'), 'sekeb': (8.133, 0.9, 'ons'), 'nim': (4.0665, 0.9, 'ons'), 'rob': (2.03325, 0.9, 'ons'),
         'gerami': (1.011, 0.9, 'ons'), 'geram18': (1, 0.75, 'ons'), 'silver_999': (1, 0.999, 'silver')}
BASE = ['ons', 'silver', 'price_dollar_rl']

def closes(path):
    # rows: open, low, high, close, change, change %, gregorian date, jalali date (newest first)
    rows = json.load(open(path, encoding='utf-8'))['data']
    out = {}
    for r in rows:
        try: out[r[6]] = (float(str(r[3]).replace(',', '')), r[7])
        except (IndexError, ValueError): pass
    return out

def main(src, dst, days=365):
    series = {k: closes(f'{src}/{k}.json') for k in BASE + list(ITEMS)}
    dates = sorted({d for k in ITEMS for d in series[k]})[-days:]
    jdates, last, out = [], {}, {k: [] for k in ITEMS}
    # seed carried values from the days just before the window
    for k in BASE:
        before = [d for d in series[k] if d < dates[0]]
        if before: last[k] = series[k][max(before)][0]
    keep = []
    for d in dates:
        for k in BASE:
            if d in series[k]: last[k] = series[k][d][0]
        if any(k not in last for k in BASE): continue
        keep.append(d); jdates.append(next(series[k][d][1] for k in ITEMS if d in series[k]))
        for k, (w, f, metal) in ITEMS.items():
            p = series[k].get(d)
            if not p: out[k].append(None); continue
            iv = last[metal] * last['price_dollar_rl'] / OZ * w * f
            out[k].append([round(p[0] / 10), round((p[0] - iv) / iv * 100, 2)])
    res = {'updated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'source': 'tgju.org', 'unit': 'toman',
           'note': 'items[key][i] = [closing price in toman, bubble %] for dates[i]; null = no trade that day',
           'dates': keep, 'jdates': jdates, 'items': out}
    if len(keep) < 30: sys.exit(f'only {len(keep)} days, keeping the old file')
    json.dump(res, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('history:', len(keep), 'days', keep[0], '..', keep[-1])

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 365)
