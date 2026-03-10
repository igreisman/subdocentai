"""Fix pam_112 entry in corpus: remove corrupt version and add clean one."""
import json

# Read all valid lines, strip empty/invalid ones, remove any pam_112 entries
lines_out = []
skipped = 0
with open('corpora/dieselsubs_faq_corpus.jsonl', 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
            if d.get('chunk_id') != 'pam_112':
                lines_out.append(line)
            else:
                print(f"Removing existing pam_112: {d['title'][:50]}")
        except Exception as e:
            skipped += 1
            print(f"Skipping invalid line: {e}")

print(f"Valid entries (without pam_112): {len(lines_out)}, skipped: {skipped}")

text = (
    "What was the longest any submarine stayed submerged?\n\n"
    "A WWII fleet submarine\u2019s submerged endurance was determined by battery capacity. "
    "Moving at 2 knots (barely creeping), the batteries on a Balao-class submarine could last roughly 48 hours. "
    "At higher speeds the batteries drained much faster \u2014 at maximum speed of about 8-9 knots submerged, "
    "batteries lasted only about an hour.\n\n"
    "In practice, submarines rarely stayed down for more than 24 hours. "
    "The battery had to be recharged by surfacing and running the diesels, which required access to air. "
    "Additionally, CO2 built up in the air after extended submersion, and oxygen was slowly depleted, "
    "making breathing increasingly difficult. "
    "Chemical canisters could absorb some CO2 and oxygen could be bled in from tanks, but these were limited. "
    "In extreme cases during depth charge attacks, crews endured 30+ hours submerged before surfacing was safe. "
    "The record during the war was reportedly over 40 hours submerged in an emergency situation."
)

entry = {
    "chunk_id": "pam_112",
    "doc_type": "dieselsubs_faq",
    "source": "dieselsubs_faq",
    "display_citation": "DieselSubs FAQ",
    "title": "What was the longest any submarine stayed submerged?",
    "text": text
}
lines_out.append(json.dumps(entry, ensure_ascii=False))

with open('corpora/dieselsubs_faq_corpus.jsonl', 'w') as f:
    for l in lines_out:
        f.write(l + '\n')

print(f"Written {len(lines_out)} entries total")
# Verify last entry
with open('corpora/dieselsubs_faq_corpus.jsonl', 'r') as f:
    last = None
    for line in f:
        if line.strip():
            last = line.strip()
d = json.loads(last)
print(f"Last entry: {d['chunk_id']} | {d['title']}")
