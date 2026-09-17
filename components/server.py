# 延續這個庫的方式進行續寫，嚴禁任何的變更與刪除
# 下方註解表示功能需求，嚴禁刪除
# 不能使用任何 javascript 語言且需要使用 python 庫
# 需具備 TLS 握手協議(HTTPS)，未來可直接替換成真實 DNS 網域的憑證
import http.server, ssl, os, sys
from urllib.parse import parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from login import verify_login
from register import register_user, init_db

HOST = "0.0.0.0"
PORT = 4433

# 本機自簽憑證，之後部署到真實 DNS 網域時，
# 只要把這兩個路徑換成 Let's Encrypt / 憑證商核發的 fullchain.pem、privkey.pem 即可
CERT_FILE = os.path.normpath("cert.pem")
KEY_FILE = os.path.normpath("key.pem")

LOGIN_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>登入</title></head>
<body>
<h1>登入</h1>
{message}
<form method="POST" action="/login">
  帳戶：<input type="text" name="account"><br>
  密碼：<input type="password" name="password"><br>
  <button type="submit">登入</button>
</form>
<p><a href="/register">還沒有帳號？前往註冊</a></p>
</body></html>"""

REGISTER_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>註冊</title></head>
<body>
<h1>註冊帳號</h1>
{message}
<form method="POST" action="/register">
  帳戶：<input type="text" name="account"><br>
  密碼：<input type="password" name="password"><br>
  <button type="submit">註冊</button>
</form>
<p><a href="/login">已經有帳號？前往登入</a></p>
</body></html>"""


class AuthHandler(http.server.BaseHTTPRequestHandler):
    def _send_html(self, body, status=200):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _read_form(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        fields = parse_qs(body)
        return fields.get("account", [""])[0], fields.get("password", [""])[0]

    def do_GET(self):
        if self.path in ("/", "/login"):
            self._send_html(LOGIN_PAGE.format(message=""))
        elif self.path == "/register":
            self._send_html(REGISTER_PAGE.format(message=""))
        else:
            self._send_html("<h1>404 Not Found</h1>", status=404)

    def do_POST(self):
        if self.path == "/login":
            acc, pwd = self._read_form()
            if verify_login(acc, pwd):
                message = "<p>登入成功，請輸入TOTP驗證碼或使用指紋識別</p>"
            else:
                message = "<p>帳戶或密碼有誤!請重新輸入</p>"
            self._send_html(LOGIN_PAGE.format(message=message))
        elif self.path == "/register":
            acc, pwd = self._read_form()
            if register_user(acc, pwd):
                message = "<p>註冊成功！請前往登入</p>"
            else:
                message = "<p>帳戶已存在，請重新輸入</p>"
            self._send_html(REGISTER_PAGE.format(message=message))
        else:
            self._send_html("<h1>404 Not Found</h1>", status=404)


def main():
    init_db()

    if not (os.path.exists(CERT_FILE) and os.path.exists(KEY_FILE)):
        print(f"找不到憑證檔案，請先產生 {CERT_FILE} / {KEY_FILE}（本機測試可用自簽憑證）")
        return

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    httpd = http.server.HTTPServer((HOST, PORT), AuthHandler)
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

    print(f"HTTPS 伺服器啟動：https://localhost:{PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    main()
