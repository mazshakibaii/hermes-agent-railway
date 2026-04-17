#!/usr/bin/env python3
"""Cookie-based auth proxy for Hermes dashboard on Railway."""

import hashlib
import hmac
import os
import secrets
import string
import subprocess
import sys
import time

from aiohttp import web, ClientSession, WSMsgType

UPSTREAM = "http://127.0.0.1:9119"
USERNAME = os.environ.get("DASHBOARD_USER", "admin")
PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "")
SECRET = secrets.token_bytes(32)
COOKIE = "hermes_auth"
MAX_AGE = 7 * 86400

if not PASSWORD:
    print("ERROR: DASHBOARD_PASSWORD must be set.", file=sys.stderr)
    sys.exit(1)


def make_token():
    expires = str(int(time.time()) + MAX_AGE)
    sig = hmac.new(SECRET, expires.encode(), hashlib.sha256).hexdigest()
    return f"{expires}.{sig}"


def check_token(token):
    try:
        expires, sig = token.rsplit(".", 1)
        if int(expires) < time.time():
            return False
        expected = hmac.new(SECRET, expires.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False


LOGIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Hermes Agent — Login</title>
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0a0f14;
    color: #e0f0f0;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
  }
  .card {
    background: #111920;
    border: 1px solid rgba(45, 212, 191, 0.15);
    border-radius: 12px;
    padding: 2.5rem;
    width: 100%;
    max-width: 380px;
    box-shadow: 0 0 40px rgba(45, 212, 191, 0.05);
  }
  h1 {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    text-align: center;
    color: #2dd4bf;
  }
  label {
    display: block;
    font-size: 0.8rem;
    color: #7899aa;
    margin-bottom: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  input {
    width: 100%;
    padding: 0.6rem 0.8rem;
    margin-bottom: 1rem;
    background: #0a0f14;
    border: 1px solid rgba(45, 212, 191, 0.2);
    border-radius: 6px;
    color: #e0f0f0;
    font-size: 0.95rem;
    outline: none;
    transition: border-color 0.2s;
  }
  input:focus { border-color: #2dd4bf; }
  button {
    width: 100%;
    padding: 0.7rem;
    background: #2dd4bf;
    color: #0a0f14;
    border: none;
    border-radius: 6px;
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    transition: opacity 0.2s;
  }
  button:hover { opacity: 0.85; }
  .error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fca5a5;
    padding: 0.5rem 0.8rem;
    border-radius: 6px;
    font-size: 0.85rem;
    margin-bottom: 1rem;
    text-align: center;
  }
</style>
</head>
<body>
<div class="card">
  <h1>Hermes Agent</h1>
  $error
  <form method="POST" action="/login">
    <label for="username">Username</label>
    <input id="username" name="username" type="text" autocomplete="username" required>
    <label for="password">Password</label>
    <input id="password" name="password" type="password" autocomplete="current-password" required>
    <button type="submit">Sign in</button>
  </form>
</div>
</body>
</html>"""


async def login_page(request):
    error = ""
    if request.query.get("error"):
        error = '<div class="error">Invalid username or password</div>'
    return web.Response(
        text=string.Template(LOGIN_HTML).safe_substitute(error=error),
        content_type="text/html",
    )


async def login_post(request):
    data = await request.post()
    username = data.get("username", "")
    password = data.get("password", "")

    if hmac.compare_digest(username, USERNAME) and hmac.compare_digest(password, PASSWORD):
        resp = web.HTTPFound("/")
        resp.set_cookie(COOKIE, make_token(), max_age=MAX_AGE, httponly=True, samesite="Lax")
        return resp

    raise web.HTTPFound("/login?error=1")


async def logout(request):
    resp = web.HTTPFound("/login")
    resp.del_cookie(COOKIE)
    return resp


@web.middleware
async def auth_middleware(request, handler):
    if request.path in ("/login", "/logout", "/api/health"):
        return await handler(request)

    token = request.cookies.get(COOKIE)
    if not token or not check_token(token):
        if request.path.startswith("/api/"):
            raise web.HTTPUnauthorized()
        raise web.HTTPFound("/login")

    return await handler(request)


gateway_process = None


def start_gateway():
    global gateway_process
    if gateway_process and gateway_process.poll() is None:
        gateway_process.terminate()
        try:
            gateway_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            gateway_process.kill()
    gateway_process = subprocess.Popen(["hermes", "gateway", "run"])


async def restart_gateway(request):
    start_gateway()
    return web.json_response({"status": "gateway restarted"})


async def gateway_status(request):
    running = gateway_process is not None and gateway_process.poll() is None
    return web.json_response({"running": running})


GATEWAY_WIDGET = """
<div id="gw-widget" style="position:fixed;bottom:20px;right:20px;z-index:99999;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;">
  <div style="background:#111920;border:1px solid rgba(45,212,191,0.2);border-radius:10px;
    padding:12px 16px;display:flex;align-items:center;gap:10px;
    box-shadow:0 4px 20px rgba(0,0,0,0.4);">
    <span id="gw-dot" style="width:8px;height:8px;border-radius:50%;background:#888;flex-shrink:0;"></span>
    <span id="gw-label" style="color:#7899aa;">Gateway</span>
    <button id="gw-btn" onclick="gwRestart()" style="background:#2dd4bf;color:#0a0f14;border:none;
      border-radius:5px;padding:4px 12px;font-size:12px;font-weight:600;cursor:pointer;">Restart</button>
  </div>
</div>
<script>
function gwStatus(){
  fetch('/api/gateway/status').then(r=>r.json()).then(d=>{
    document.getElementById('gw-dot').style.background=d.running?'#4ade80':'#ef4444';
    document.getElementById('gw-label').textContent=d.running?'Gateway running':'Gateway stopped';
  }).catch(()=>{});
}
function gwRestart(){
  var b=document.getElementById('gw-btn');b.textContent='Restarting...';b.disabled=true;
  fetch('/api/gateway/restart',{method:'POST'}).then(()=>{
    setTimeout(()=>{b.textContent='Restart';b.disabled=false;gwStatus();},3000);
  }).catch(()=>{b.textContent='Restart';b.disabled=false;});
}
gwStatus();setInterval(gwStatus,10000);
</script>
"""


async def health(request):
    return web.json_response({"status": "ok"})


async def proxy_ws(request):
    ws_client = web.WebSocketResponse()
    await ws_client.prepare(request)

    async with ClientSession() as session:
        url = f"ws://127.0.0.1:9119{request.path_qs}"
        async with session.ws_connect(url) as ws_upstream:

            async def forward(src, dst):
                async for msg in src:
                    if msg.type == WSMsgType.TEXT:
                        await dst.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await dst.send_bytes(msg.data)
                    elif msg.type in (WSMsgType.CLOSE, WSMsgType.ERROR):
                        break

            import asyncio
            await asyncio.gather(
                forward(ws_client, ws_upstream),
                forward(ws_upstream, ws_client),
            )

    return ws_client


async def proxy(request):
    if request.headers.get("Upgrade", "").lower() == "websocket":
        return await proxy_ws(request)

    async with ClientSession() as session:
        url = f"{UPSTREAM}{request.path_qs}"
        headers = {k: v for k, v in request.headers.items() if k.lower() not in ("host", "transfer-encoding")}

        body = await request.read()
        async with session.request(
            request.method,
            url,
            headers=headers,
            data=body,
            allow_redirects=False,
        ) as resp:
            excluded = {"transfer-encoding", "content-encoding", "content-length"}
            proxy_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded}
            content = await resp.read()
            content_type = resp.headers.get("content-type", "")
            if "text/html" in content_type:
                html = content.decode("utf-8", errors="replace")
                html = html.replace("</body>", GATEWAY_WIDGET + "</body>")
                return web.Response(status=resp.status, headers=proxy_headers, text=html, content_type="text/html")
            return web.Response(status=resp.status, headers=proxy_headers, body=content)


async def on_startup(app):
    start_gateway()


def create_app():
    app = web.Application(middlewares=[auth_middleware])
    app.on_startup.append(on_startup)
    app.router.add_get("/login", login_page)
    app.router.add_post("/login", login_post)
    app.router.add_get("/logout", logout)
    app.router.add_get("/api/health", health)
    app.router.add_post("/api/gateway/restart", restart_gateway)
    app.router.add_get("/api/gateway/status", gateway_status)
    app.router.add_route("*", "/{path_info:.*}", proxy)
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web.run_app(create_app(), host="0.0.0.0", port=port)
