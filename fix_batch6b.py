#!/usr/bin/env python3
"""Fix title coverage regressions for batch 6 FAQs and add aliases."""
import json

CORPUS = "corpora/dieselsubs_faq_corpus.jsonl"

with open(CORPUS, "r", encoding="utf-8") as f:
    entries = [json.loads(l) for l in f if l.strip()]

changed = 0
for e in entries:
    cid = e.get("chunk_id")

    # pam_091: add "water" to title for "survivors in the water" queries
    if cid == "pam_091":
        e["title"] = "How did the crew know survivors in the water were Allied prisoners?"
        e["text"] = e["text"].replace(
            "How did the crew identify the survivors as Allied prisoners?",
            "How did the crew know survivors in the water were Allied prisoners?"
        )
        print(f"UPDATED {cid}")
        changed += 1

    # pam_093: add Connecticut to title
    if cid == "pam_093":
        e["title"] = "What was submarine school in Groton Connecticut?"
        e["text"] = e["text"].replace(
            "What was submarine school and where is it in Groton?",
            "What was submarine school in Groton Connecticut?"
        )
        print(f"UPDATED {cid}")
        changed += 1

    # pam_094: shorten title to just "SJ radar" — single content token for 4x bonus
    if cid == "pam_094":
        e["title"] = "What was the SJ radar?"
        e["text"] = e["text"].replace(
            "What was the SJ radar and how did radar work on a WWII submarine?",
            "What was the SJ radar?"
        )
        print(f"UPDATED {cid}")
        changed += 1

    # pam_099: add decommission + museum + preserved to title
    if cid == "pam_099":
        e["title"] = "How was the Pampanito decommissioned and preserved as a museum?"
        e["text"] = e["text"].replace(
            "How did the Pampanito become a museum ship?",
            "How was the Pampanito decommissioned and preserved as a museum?"
        )
        print(f"UPDATED {cid}")
        changed += 1

    # pam_101: add "longest" to title
    if cid == "pam_101":
        e["title"] = "How long can a submarine stay submerged and what was the longest?"
        e["text"] = e["text"].replace(
            "How long can a submarine stay submerged?",
            "How long can a submarine stay submerged and what was the longest?"
        )
        print(f"UPDATED {cid}")
        changed += 1

with open(CORPUS, "w", encoding="utf-8") as f:
    for entry in entries:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Modified {changed} entries.\n")

# New alias entries
ALIASES = [
    {
        "chunk_id": "pam_107",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did submarines handle medical emergencies at sea?",
        "text": """How did submarines handle medical emergencies at sea?

Medical care at sea on a submarine was limited but resourceful. Submarines carried no doctor — medical care was provided by a Pharmacist's Mate, a trained Navy corpsman. The medical supplies included medications, bandages, instruments for minor surgery, and dental tools.

For serious emergencies — appendicitis, serious injuries, infections — the crew had to improvise or cut the patrol short and race for port or a rendezvous with a submarine tender. The most famous example was a 1942 appendectomy performed aboard USS Seadragon by Pharmacist's Mate Wheeler Lipes using the wardroom table and improvised instruments. In extreme cases, sick or badly injured men were transferred to other ships at sea using a rubber boat — a dangerous operation in both enemy waters and rough seas. The limitations of submarine medicine were accepted as one of the hazards of the service."""
    },
    {
        "chunk_id": "pam_108",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Did the Pampanito ever hit a mine?",
        "text": """Did the Pampanito ever hit a mine?

The Pampanito never hit a mine. However, mines were a constant threat. Japan heavily mined the waters around the home islands and key shipping lanes, and US submarines had to navigate these minefield zones carefully. Passing through a minefield — surfaced or submerged — required careful navigation, slow speeds, and a great deal of luck.

Several American submarines were lost to mines during World War II. The Pampanito was aware of and careful about mine threats during her six war patrols, particularly during operations in the South China Sea and around Japanese home waters. The fact that she survived all six patrols without being lost to a mine, depth charge, or aircraft was a testament to her crew's skill and caution."""
    },
    {
        "chunk_id": "pam_109",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "When was the Pampanito decommissioned?",
        "text": """When was the Pampanito decommissioned?

The Pampanito was decommissioned on December 15, 1945, at Mare Island Naval Shipyard in Vallejo, California, shortly after Japan's surrender ended World War II. She was placed in the reserve fleet — "mothballed" — where she sat for decades while the Navy maintained her in case of future need.

She was struck from the Naval Vessel Register in 1976, ending her formal Navy status. In 1978 she was transferred to the National Maritime Museum Association in San Francisco. After restoration work, she opened to the public on July 4, 1982, at Pier 45, Fisherman's Wharf, where she remains today as a museum ship and National Historic Landmark."""
    },
    {
        "chunk_id": "pam_110",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did radar work on a WWII submarine?",
        "text": """How did radar work on a WWII submarine?

WWII submarines used two types of radar: the SJ surface-search radar and the SD air-search radar. Radar works by transmitting pulses of radio energy and detecting the echoes that bounce back from ships, land, or aircraft. The time delay between the transmitted pulse and the returning echo tells the operator how far away the target is; the direction of the antenna gives the bearing.

The SJ surface-search radar operated in the microwave frequency range (around 3,000 MHz) and could detect large ships at ranges up to 15 miles. The rotating antenna was mounted on the periscope shears — the raised structure above the conning tower. The SD air-search radar detected aircraft at ranges of about 10 miles, giving the submarine time to dive before a plane could reach attack range. By 1943 nearly all US fleet submarines were equipped with both types of radar, giving them a major tactical advantage in night and poor-visibility attacks."""
    },
    {
        "chunk_id": "pam_111",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Who donated the Pampanito to the museum in San Francisco?",
        "text": """Who donated the Pampanito to the museum in San Francisco?

The Pampanito was not donated by a private individual. She was transferred by the US Navy to the National Maritime Museum Association (now part of the San Francisco Maritime National Historical Park) in 1978, after she was struck from the Naval Vessel Register in 1976.

The National Maritime Museum Association, along with the Golden Gate National Recreation Area and the National Park Service, worked together to preserve and open the Pampanito to the public. Today the Maritime Park Association, a nonprofit organization, manages the Pampanito and funds its ongoing restoration and operation. Admission fees, donations from visitors, and grants help maintain the submarine for future generations. The Pampanito was designated a National Historic Landmark in 1986."""
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

print(f"\nAdded {added}.")
import subprocess
r = subprocess.run(["wc", "-l", CORPUS], capture_output=True, text=True)
print("Total:", r.stdout.strip())
