# Reads tgju's public price feed and writes prices.json for the calculator's bubble tab.
# Usage: python3 update_prices.py <tgju ajax.json> <prices.json>
# prices.json is only rewritten when a price changed, so unchanged runs make no commit.
import json, sys, datetime

KEYS = ['ons', 'silver', 'price_dollar_rl', 'sekee', 'sekeb', 'nim', 'rob', 'gerami', 'geram18', 'geram24', 'silver_999']
# currency tab: rial prices (price_jpy is per 100 yen); crypto-bitcoin/ethereum are in dollars
FX = ['price_eur', 'price_gbp', 'price_aed', 'price_try', 'price_cny', 'price_cad', 'price_aud', 'price_chf', 'price_sar', 'price_kwd',
      'price_qar', 'price_omr', 'price_afn', 'price_rub', 'price_inr', 'price_azn', 'price_amd', 'price_jpy',
      'crypto-tether-irr', 'crypto-bitcoin', 'crypto-ethereum']

def number(s):
    return float(str(s).replace(',', '').strip())

def read(cur, keys):
    out = {}
    for k in keys:
        v = cur.get(k)
        if not v: continue
        try: p = number(v['p'])
        except (KeyError, ValueError): continue
        if p <= 0: continue
        out[k] = {'p': p, 't': v.get('ts', '')}
        # today's change in percent, signed
        try: out[k]['c'] = round(float(v.get('dp') or 0) * (-1 if v.get('dt') == 'low' else 1), 2)
        except (TypeError, ValueError): pass
    return out

def main(src, dst):
    cur = json.load(open(src, encoding='utf-8'))['current']
    items = read(cur, KEYS)
    fx = read(cur, FX)
    if len(items) < len(KEYS) - 2:
        sys.exit(f'too few prices found ({len(items)}), keeping the old file')
    try: old = json.load(open(dst, encoding='utf-8'))
    except (OSError, ValueError): old = {}
    if old.get('items') == items and old.get('fx') == fx:
        print('no change'); return
    out = {'updated': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'source': 'tgju.org', 'unit': 'rial', 'items': items, 'fx': fx}
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('updated', len(items), 'prices,', len(fx), 'currencies')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
