"""Opens the website in a real browser and clicks through it. Needs: pip install playwright && playwright install chromium
Usage: python tests/site_check.py [screenshot_dir]
The Anthropic API is mocked, so this never spends tokens.
"""
import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else None

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / "docs"))
handler.log_message = lambda *a, **k: None
server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
URL = f"http://127.0.0.1:{server.server_address[1]}/index.html"

calls = []


def mock_api(route):
    body = json.loads(route.request.post_data)
    calls.append({"headers": route.request.headers, "body": body})
    if "triage-ticket" in body["system"][:200]:
        text = json.dumps({"id": "T001", "category": "billing", "priority": "P1", "needs_human": False, "reason": "Charged twice."})
    else:
        text = json.dumps({"id": "T001", "language": "EN", "status": "waiting_for_approval",
                           "draft": "Hello, thank you for contacting us. We understand you were charged twice. A member of our team will review it and follow up. Kind regards, Customer Care Team"})
    route.fulfill(status=200, content_type="application/json", body=json.dumps({"content": [{"type": "text", "text": text}]}))


def check(label, condition):
    print(("PASS " if condition else "FAIL ") + label)
    if not condition:
        check.failed = True


check.failed = False

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.route("https://api.anthropic.com/**", mock_api)
    outside = []
    page.on("request", lambda r: outside.append(r.url) if not r.url.startswith("http://127.0.0.1") else None)

    page.goto(URL)
    page.wait_for_selector("#tickets button")
    check("30 tickets listed", page.locator("#tickets button").count() == 30)
    check("intake panel shows language", "Language EN" in page.inner_text("#panel"))
    if SHOTS: page.screenshot(path=str(SHOTS / "1_intake.png"))

    # Guided tour
    check("tour offers a start button", page.is_visible("#tourStart"))
    page.click("#tourStart")
    check("tour step 1 opens intake on T002", "step 1 of 8" in page.inner_text("#tourBody").lower() and "Language FR" in page.inner_text("#panel"))
    if SHOTS: page.screenshot(path=str(SHOTS / "0_tour.png"))
    for _ in range(3): page.click("#tourNext")
    check("tour step 4 shows the French draft", "Cordialement" in page.inner_text("#panel"))
    page.click("#tourNext")
    check("tour step 5 shows audit pass", "AUDIT PASS 20/20" in page.inner_text("#panel") and "AUDIT PASS 20/20" in page.inner_text("#batch"))
    page.click("#tourNext")
    check("tour step 6 shows audit fail naming 03_route", "AUDIT FAIL" in page.inner_text("#panel") and "03_route" in page.inner_text("#panel"))
    page.click("#tourNext")
    check("tour step 7 has the gate locked", page.is_disabled("#approve"))
    page.click("#tourNext")
    check("tour step 8 reopens the gate", page.is_enabled("#approve"))
    if SHOTS: page.screenshot(path=str(SHOTS / "0_tour_end.png"))
    page.click("#tourEnd")
    check("tour can be closed", not page.is_visible("#tour"))
    page.click("#reset")

    page.click("#tickets button[data-id='T002']")
    page.click("button[data-stage='01_intake']")
    check("French ticket detected as FR", "Language FR" in page.inner_text("#panel"))
    page.click("button[data-stage='02_classify']")
    check("classify shows recorded JSON", '"category": "delivery"' in page.inner_text("#panel"))
    page.click("button[data-stage='03_route']")
    check("route shows Delivery Support", "Delivery Support" in page.inner_text("#panel"))
    page.click("button[data-stage='04_reply']")
    check("reply is French", "Bonjour" in page.inner_text("#panel") and "Cordialement" in page.inner_text("#panel"))
    if SHOTS: page.screenshot(path=str(SHOTS / "2_reply.png"))
    page.click("button[data-stage='05_audit']")
    check("audit passes 20/20", "AUDIT PASS 20/20" in page.inner_text("#panel"))

    page.click("#runAll")
    check("batch audit passes", "AUDIT PASS 20/20" in page.inner_text("#batch"))
    check("batch intake 30 of 30", "Intake: 30 of 30 OK" in page.inner_text("#batch"))

    page.click("button[data-stage='gate']")
    check("approve enabled when audit passes", page.is_enabled("#approve"))
    page.click("#approve")
    check("approval shows outbox", "outbox.json" in page.inner_text("#panel").lower())
    if SHOTS: page.screenshot(path=str(SHOTS / "3_gate.png"))

    page.click("#tamper")
    check("tamper makes audit FAIL", "AUDIT FAIL" in page.inner_text("#batch") and "03_route" in page.inner_text("#batch"))
    page.click("button[data-stage='gate']")
    check("approve disabled after tamper", page.is_disabled("#approve"))
    if SHOTS: page.screenshot(path=str(SHOTS / "4_tamper.png"))
    page.click("#reset")
    page.click("#runAll")
    check("reset restores PASS", "AUDIT PASS 20/20" in page.inner_text("#batch"))

    check("no network call left the page before live mode", outside == [])
    check("live button off without a key", page.is_disabled("#runLive"))
    page.click("#live summary")
    page.fill("#apiKey", "sk-ant-test-key")
    page.click("#tickets button[data-id='T001']")
    page.click("#runLive")
    page.wait_for_selector("#liveOut .banner.warn")
    check("live mode made 2 calls", len(calls) == 2)
    check("live call sends the browser access header", calls and calls[0]["headers"].get("anthropic-dangerous-direct-browser-access") == "true")
    check("live call uses the key and model", calls and calls[0]["headers"].get("x-api-key") == "sk-ant-test-key" and calls[0]["body"]["model"] == "claude-haiku-5-5")
    check("live result is checked by scripts", "Draft passes every reply check" in page.inner_text("#liveOut"))
    if SHOTS: page.screenshot(path=str(SHOTS / "5_live.png"))

    page.set_viewport_size({"width": 390, "height": 800})
    page.reload(); page.wait_for_selector("#tickets button")
    check("mobile has no horizontal scroll", page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"))
    if SHOTS: page.screenshot(path=str(SHOTS / "6_mobile.png"))
    check("no console or page errors", errors == [])
    if errors: print(errors)
    browser.close()

server.shutdown()
sys.exit(1 if check.failed else 0)
