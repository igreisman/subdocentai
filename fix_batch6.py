#!/usr/bin/env python3
"""Fix title coverage and add aliases for batch 6 FAQ entries."""
import json

CORPUS = "corpora/dieselsubs_faq_corpus.jsonl"

with open(CORPUS, "r", encoding="utf-8") as f:
    entries = [json.loads(l) for l in f if l.strip()]

changed = 0
for e in entries:
    cid = e.get("chunk_id")

    # Fix pam_104: add "sea" to title for "resupplied at sea" queries
    if cid == "pam_104":
        old = e["title"]
        e["title"] = "How was the Pampanito resupplied at sea?"
        e["text"] = e["text"].replace(
            "How was the Pampanito resupplied during a patrol?",
            "How was the Pampanito resupplied at sea?"
        )
        print(f"UPDATED {cid}: '{old}' → '{e['title']}'")
        changed += 1

    # Fix pam_093: add Groton to title so "What was Groton Connecticut?" routes here
    if cid == "pam_093":
        old = e["title"]
        e["title"] = "What was submarine school and where is it in Groton?"
        e["text"] = e["text"].replace(
            "What was submarine school and where was it?",
            "What was submarine school and where is it in Groton?"
        )
        print(f"UPDATED {cid}: '{old}' → '{e['title']}'")
        changed += 1

with open(CORPUS, "w", encoding="utf-8") as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"\nModified {changed} existing entries.")

# Add final aliases
ALIASES = [
    {
        "chunk_id": "pam_105",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the hull number of the Pampanito?",
        "text": """What was the hull number of the Pampanito?

The Pampanito's hull number is SS-383. "SS" is the Navy hull classification for a conventional (diesel-electric) submarine, and 383 was the sequential number assigned when the boat was authorized by Congress. The full official designation is USS Pampanito (SS-383).

The name "Pampanito" comes from a Pacific Ocean fish, the pompano. American fleet submarines of World War II were traditionally named after fish. Her keel was laid on March 15, 1943, she was launched on July 12, 1943, and commissioned into US Navy service on November 6, 1943, all at the Portsmouth Naval Shipyard in Kittery, Maine."""
    },
    {
        "chunk_id": "pam_106",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Were there doctors or medical care on submarines?",
        "text": """Were there doctors or medical care on submarines?

Fleet submarines did not carry a doctor. The medical officer was a Pharmacist's Mate — an enlisted Navy corpsman (medic). On the Pampanito, the Pharmacist's Mate had a small medical kit and first-aid training, but was not a physician.

For minor injuries, infections, and illnesses this was workable. For serious emergencies, the limitations could be life-threatening. The boat had no operating room, no X-ray equipment, and no means to get a sick man to a hospital in less than days or weeks. The Navy recognized this and gave Pharmacist's Mates extra training in emergency procedures. The most famous example of submarine medical improvisation was in 1942, when a Navy corpsman performed an emergency appendectomy on a sailor aboard USS Seadragon using a mess table, improvised instruments, and ether as anesthesia — and the patient survived."""
    },
]

with open(CORPUS, "r", encoding="utf-8") as f:
    existing_ids = {json.loads(l).get("chunk_id") for l in f if l.strip()}

added = 0
with open(CORPUS, "a", encoding="utf-8") as f:
    for faq in ALIASES:
        if faq["chunk_id"] in existing_ids:
            print(f"SKIP {faq['chunk_id']}")
            continue
        f.write(json.dumps(faq, ensure_ascii=False) + "\n")
        print(f"ADD  {faq['chunk_id']}: {faq['title']}")
        added += 1

print(f"\nAdded {added} aliases.")
import subprocess
r = subprocess.run(["wc", "-l", CORPUS], capture_output=True, text=True)
print("Total lines:", r.stdout.strip())
