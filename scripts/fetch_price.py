"""장 마감 후 삼성전자(005930) 종가를 가져와 price.json에 기록한다."""
import datetime as dt
import json
import sys
import urllib.request

CODE = "005930"
UA = {"User-Agent": "Mozilla/5.0 (samsung-pbr price bot)"}
KST = dt.timezone(dt.timedelta(hours=9))


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def num(v):
    return int(str(v).replace(",", "").strip())


def from_basic():
    d = get(f"https://m.stock.naver.com/api/stock/{CODE}/basic")
    day = (d.get("localTradedAt") or "")[:10]
    return num(d["closePrice"]), day, d.get("marketStatus", "")


def from_polling():
    d = get(f"https://polling.finance.naver.com/api/realtime/domestic/stock/{CODE}")
    x = d["datas"][0]
    day = (x.get("localTradedAt") or "")[:10]
    return num(x["closePrice"]), day, x.get("marketStatus", "")


def main():
    err = []
    for fn in (from_basic, from_polling):
        try:
            close, day, status = fn()
            break
        except Exception as e:  # noqa: BLE001
            err.append(f"{fn.__name__}: {e}")
    else:
        sys.exit("종가를 가져오지 못했습니다: " + " | ".join(err))
    if not day:
        day = dt.datetime.now(KST).date().isoformat()
    out = {
        "code": CODE,
        "date": day,
        "close": close,
        "marketStatus": status,
        "fetchedAt": dt.datetime.now(KST).isoformat(timespec="seconds"),
        "source": "네이버 증권",
    }
    with open("price.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(out)


if __name__ == "__main__":
    main()
