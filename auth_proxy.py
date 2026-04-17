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

HERMES_HOME = "/root/.hermes"
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
<title>Hermes Agent</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0a0f14;
    --surface: #111920;
    --border: rgba(255,255,255,0.06);
    --border-focus: rgba(45,212,191,0.4);
    --text: #e0f0f0;
    --text-muted: #7899aa;
    --accent: #2dd4bf;
    --accent-dim: rgba(45,212,191,0.1);
    --error-bg: rgba(180,60,60,0.1);
    --error-border: rgba(180,60,60,0.25);
    --error-text: #d4908a;
  }
  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
  }
  body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
      radial-gradient(ellipse 80% 60% at 50% 0%, rgba(45,212,191,0.04) 0%, transparent 60%),
      radial-gradient(ellipse 60% 80% at 80% 100%, rgba(255,255,255,0.02) 0%, transparent 50%);
    pointer-events: none;
  }
  body::after {
    content: '';
    position: fixed;
    inset: 0;
    background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    opacity: 0.5;
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
  }
  @keyframes lineGrow {
    from { transform: scaleX(0); }
    to { transform: scaleX(1); }
  }
  .login-wrapper {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 400px;
    padding: 0 1.5rem;
    animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) both;
  }
  .brand {
    text-align: center;
    margin-bottom: 3rem;
  }
  .brand-icon {
    width: 36px;
    height: 36px;
    margin: 0 auto 1.2rem;
    border: 1.5px solid var(--accent);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--accent);
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    font-weight: 600;
    opacity: 0;
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
  }
  .brand h1 {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 400;
    font-size: 1.6rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text);
    opacity: 0;
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both;
  }
  .brand p {
    font-size: 0.78rem;
    color: var(--text-muted);
    margin-top: 0.5rem;
    letter-spacing: 0.04em;
    opacity: 0;
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.3s both;
  }
  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border-focus), transparent);
    margin-bottom: 2.5rem;
    transform-origin: center;
    animation: lineGrow 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.4s both;
  }
  .card {
    opacity: 0;
    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.45s both;
  }
  .field {
    margin-bottom: 1.25rem;
  }
  label {
    display: block;
    font-size: 0.7rem;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
  }
  input {
    width: 100%;
    padding: 0.75rem 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    outline: none;
    transition: border-color 0.3s, box-shadow 0.3s;
  }
  input::placeholder { color: var(--text-muted); opacity: 0.5; }
  input:focus {
    border-color: var(--border-focus);
    box-shadow: 0 0 0 3px var(--accent-dim);
  }
  button {
    width: 100%;
    padding: 0.8rem;
    margin-top: 0.5rem;
    background: var(--accent);
    color: var(--bg);
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    cursor: pointer;
    transition: transform 0.2s, opacity 0.2s;
  }
  button:hover { opacity: 0.88; transform: translateY(-1px); }
  button:active { transform: translateY(0); }
  .error {
    background: var(--error-bg);
    border: 1px solid var(--error-border);
    color: var(--error-text);
    padding: 0.6rem 0.9rem;
    border-radius: 8px;
    font-size: 0.8rem;
    margin-bottom: 1.25rem;
    text-align: center;
  }
</style>
</head>
<body>
<div class="login-wrapper">
  <div class="brand">
    <div class="brand-icon">H</div>
    <h1>Hermes</h1>
    <p>Agent Console</p>
  </div>
  <div class="divider"></div>
  <div class="card">
    $error
    <form method="POST" action="/login">
      <div class="field">
        <label for="username">Username</label>
        <input id="username" name="username" type="text" autocomplete="username" required>
      </div>
      <div class="field">
        <label for="password">Password</label>
        <input id="password" name="password" type="password" autocomplete="current-password" required>
      </div>
      <button type="submit">Continue</button>
    </form>
  </div>
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


RESTART_PATHS = {
    ("PUT", "/api/config"),
    ("PUT", "/api/env"),
    ("DELETE", "/api/env"),
}


def volume_attached():
    return os.path.ismount(HERMES_HOME)


async def restart_gateway(request):
    start_gateway()
    return web.json_response({"status": "gateway restarted"})


async def gateway_status(request):
    running = gateway_process is not None and gateway_process.poll() is None
    return web.json_response({
        "running": running,
        "volume": volume_attached(),
    })


GATEWAY_WIDGET = """
<div id="gw-widget" style="position:fixed;bottom:20px;right:20px;z-index:99999;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:13px;">
  <div style="background:#111920;border:1px solid rgba(45,212,191,0.2);border-radius:10px;
    padding:12px 16px;display:flex;flex-direction:column;gap:8px;
    box-shadow:0 4px 20px rgba(0,0,0,0.4);min-width:180px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <span id="gw-dot" style="width:8px;height:8px;border-radius:50%;background:#888;flex-shrink:0;"></span>
      <span id="gw-label" style="color:#7899aa;flex:1;">Gateway</span>
      <button id="gw-btn" onclick="gwRestart()" style="background:#2dd4bf;color:#0a0f14;border:none;
        border-radius:5px;padding:4px 12px;font-size:12px;font-weight:600;cursor:pointer;">Restart</button>
    </div>
    <div id="gw-vol" style="display:none;font-size:11px;padding-top:4px;border-top:1px solid rgba(45,212,191,0.1);"></div>
  </div>
</div>
<script>
function gwStatus(){
  fetch('/api/gateway/status').then(r=>r.json()).then(d=>{
    document.getElementById('gw-dot').style.background=d.running?'#4ade80':'#ef4444';
    document.getElementById('gw-label').textContent=d.running?'Gateway running':'Gateway stopped';
    var vol=document.getElementById('gw-vol');
    vol.style.display='block';
    if(d.volume){
      vol.innerHTML='<span style="color:#4ade80;">&#x2713;</span> <span style="color:#7899aa;">Volume attached</span>';
    }else{
      vol.innerHTML='<span style="color:#fbbf24;">&#x26A0;</span> <span style="color:#fbbf24;">No volume \u2014 data will not persist</span>';
    }
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
            if (request.method, request.path) in RESTART_PATHS and resp.status < 400:
                start_gateway()

            content_type = resp.headers.get("content-type", "")
            if "text/html" in content_type:
                html_headers = {k: v for k, v in proxy_headers.items() if k.lower() != "content-type"}
                html = content.decode("utf-8", errors="replace")
                html = html.replace("</body>", GATEWAY_WIDGET + "</body>")
                return web.Response(status=resp.status, headers=html_headers, text=html, content_type="text/html")
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
