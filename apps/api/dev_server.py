"""Kurulum gerektirmeyen geliştirme sunucusu (Termux için). Çalıştır: python dev_server.py"""
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from service import get_events, get_summary

class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/health":
            return self._send(200, {"ok": True})
        if path == "/events":
            return self._send(200, get_events())
        m = re.fullmatch(r"/areas/(\d+)/summary", path)
        if m:
            data = get_summary(int(m.group(1)))
            return self._send(200, data) if data else self._send(404, {"error": "Bölge bulunamadı"})
        self._send(404, {"error": "Bulunamadı"})

if __name__ == "__main__":
    print("Sunucu: http://localhost:8000  (durdurmak için Ctrl+C)")
    HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
