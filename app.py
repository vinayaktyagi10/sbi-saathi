"""Local web server for the Saathi demo — standard library only.

Run:  python app.py    then open  http://localhost:8000

No pip install, no API keys. One agent instance holds session state so the
'pause and re-confirm' flow works across requests.
"""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from saathi import MockBank, SaathiAgent, SessionContext

BANK = MockBank()
AGENT = SaathiAgent(BANK)
USER_ID = "U1001"
WEB_DIR = os.path.join(os.path.dirname(__file__), "web")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):  # quiet console
        pass

    def do_GET(self):
        path = "/index.html" if self.path in ("/", "") else self.path
        fp = os.path.join(WEB_DIR, path.lstrip("/"))
        if os.path.isfile(fp):
            ctype = "text/html" if fp.endswith(".html") else "text/plain"
            with open(fp, "rb") as f:
                return self._send(200, f.read(), ctype)
        self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/chat":
            return self._send(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length) or b"{}")

        ctx = SessionContext(
            remote_access_app_open=bool(payload.get("remote_access")),
            last_message=payload.get("scam_context", ""),
            recent_txn_count_5min=int(payload.get("recent_txn_count", 0)),
        )
        reply = AGENT.handle(USER_ID, payload.get("text", ""), ctx)
        self._send(200, {
            "text": reply.text,
            "blocked": reply.blocked,
            "awaiting_confirmation": reply.awaiting_confirmation,
            "risk_level": reply.risk.level.value if reply.risk else None,
            "balance": BANK.balance(USER_ID),
        })


if __name__ == "__main__":
    print("SBI Saathi running at http://localhost:8000  (Ctrl+C to stop)")
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
