import json, urllib.request, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def ask_full(q):
    body = json.dumps({"question_text": q, "compartment_id": ""}).encode()
    req = urllib.request.Request("https://localhost:8443/ask", data=body,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
        return json.loads(r.read())

failing = [
    "What were the biggest dangers for submarine crews?",
    "How many American submarines were lost in WWII?",
    "Did submarines ever rescue people from the water?",
    "Did the Pampanito save POWs?",
    "How did you flush a toilet on a submarine?",
    "What is a conning tower?",
]

for q in failing:
    r = ask_full(q)
    got = r.get("faq_id") or (r.get("citations") or [{}])[0].get("chunk_id","??")
    ans = r.get("answer_short","")[:100]
    print(f"Q: {q}")
    print(f"   got={got}  ans={ans}")
    print()
