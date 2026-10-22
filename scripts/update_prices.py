# Reads tgju's public price feed and writes prices.json for the calculator's bubble tab.
# Usage: python3 update_prices.py <tgju ajax.json> <prices.json>
# prices.json is only rewritten when a price changed, so unchanged runs make no commit.
import json, sys, datetime

KEYS = ['ons', 'silver', 'price_dollar_rl', 'sekee', 'sekeb', 'nim', 'rob', 'gerami', 'geram18', 'geram24', 'silver_999']

def number(s):
    return float(str(s).replace(',', '').strip())

def main(src, dst):
    cur = json.load(open(src, encoding='utf-8'))['current']
    items = {}
    for k in KEYS:
        v = cur.get(k)
        if not v: continue
        try: p = number(v['p'])
        except (KeyError, ValueError): continue
        if p > 0: items[k] = {'p': p, 't': v.get('ts', '')}
    if len(items) < len(KEYS) - 2:
        sys.exit(f'too few prices found ({len(items)}), keeping the old file')
    try: old = json.load(open(dst, encoding='utf-8'))
    except (OSError, ValueError): old = {}
    if old.get('items') == items:
        print('no change'); return
    out = {'updated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'source': 'tgju.org', 'unit': 'rial', 'items': items}
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('updated', len(items), 'prices')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
