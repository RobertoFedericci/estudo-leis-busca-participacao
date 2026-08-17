"""Cliente mínimo para a API interna do Google Trends (explore + multiline).

Não existe API oficial. Usamos os mesmos endpoints do site (widget token flow),
com cookie de sessão, backoff e cache em disco para não repetir chamadas.
"""

import json
import os
import random
import time

import requests

BASE = "https://trends.google.com/trends/api"
HL = "pt-BR"
TZ = 180  # minutos (UTC-3 -> Google usa offset invertido, 180 = America/Sao_Paulo)
GEO = "BR"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


class TrendsError(RuntimeError):
    pass


class TrendsClient:
    def __init__(self, cache_dir, min_interval=2.0, max_retries=6):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.min_interval = min_interval
        self.max_retries = max_retries
        self._last_call = 0.0
        self.s = requests.Session()
        self.s.headers.update(HEADERS)
        # cookie NID: obtido visitando a home de trends
        try:
            self.s.get("https://trends.google.com/trends/explore", timeout=20)
        except requests.RequestException:
            pass

    # ---------- infra ----------
    def _throttle(self):
        wait = self.min_interval - (time.time() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.time()

    def _get(self, url, params):
        for attempt in range(self.max_retries):
            self._throttle()
            try:
                r = self.s.get(url, params=params, timeout=40)
            except requests.RequestException as exc:
                last = f"conexão: {exc}"
            else:
                if r.status_code == 200:
                    # a API prefixa a resposta com )]}',\n
                    return json.loads(r.text[r.text.find("{"):])
                if r.status_code in (400, 404):
                    raise TrendsError(f"HTTP {r.status_code} (consulta sem dados?)")
                last = f"HTTP {r.status_code}"
            sleep = min(90, (2 ** attempt) * 4) + random.uniform(0, 3)
            print(f"    retry {attempt + 1}/{self.max_retries} ({last}) em {sleep:.0f}s")
            time.sleep(sleep)
            if attempt == 2:  # renova cookie no meio do caminho
                self.s.cookies.clear()
                try:
                    self.s.get("https://trends.google.com/trends/explore", timeout=20)
                except requests.RequestException:
                    pass
        raise TrendsError(f"falhou após {self.max_retries} tentativas ({last})")

    # ---------- API ----------
    def _explore(self, terms, timeframe, geo=GEO):
        req = {
            "comparisonItem": [
                {"keyword": t, "geo": geo, "time": timeframe} for t in terms
            ],
            "category": 0,
            "property": "",
        }
        data = self._get(
            f"{BASE}/explore",
            {"hl": HL, "tz": TZ, "req": json.dumps(req, ensure_ascii=False)},
        )
        for w in data["widgets"]:
            if w.get("id") == "TIMESERIES":
                return w
        raise TrendsError("widget TIMESERIES ausente")

    def interest_over_time(self, terms, timeframe="2016-01-01 2026-08-17", geo=GEO):
        """Retorna {termo: [(data_iso, valor), ...]}. Máx. 5 termos por chamada."""
        assert 1 <= len(terms) <= 5
        key = json.dumps([terms, timeframe, geo], ensure_ascii=False, sort_keys=True)
        cache_file = os.path.join(
            self.cache_dir, str(abs(hash(key)) % (10**16)) + ".json"
        )
        if os.path.exists(cache_file):
            with open(cache_file, encoding="utf-8") as fh:
                blob = json.load(fh)
            if blob.get("key") == key:
                return blob["data"]

        w = self._explore(terms, timeframe, geo)
        payload = dict(w["request"])
        payload["requestOptions"]["property"] = ""
        raw = self._get(
            f"{BASE}/widgetdata/multiline",
            {
                "hl": HL,
                "tz": TZ,
                "req": json.dumps(payload, ensure_ascii=False),
                "token": w["token"],
            },
        )
        out = {t: [] for t in terms}
        for point in raw["default"]["timelineData"]:
            date = point["formattedAxisTime"]
            ts = point.get("time")
            for i, t in enumerate(terms):
                out[t].append(
                    {
                        "ts": int(ts) if ts else None,
                        "label": date,
                        "value": point["value"][i],
                    }
                )
        with open(cache_file, "w", encoding="utf-8") as fh:
            json.dump({"key": key, "data": out}, fh, ensure_ascii=False)
        return out
