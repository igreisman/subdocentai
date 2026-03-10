"""Fix pam_119, pam_125, pam_128 titles and text opening lines."""
import json

FIXES = {
    "pam_119": {
        "new_title": "How did submarine crews handle a fire onboard?",
        "old_first_line": "How did submarine crews fight fires onboard?",
        "new_first_line": "How did submarine crews handle a fire onboard?",
    },
    "pam_125": {
        "new_title": "How did submarine crews get fresh water?",
        "old_first_line": "How did submarines get fresh water at sea?",
        "new_first_line": "How did submarine crews get fresh water?",
    },
    "pam_128": {
        "new_title": "How did the crew handle seasickness on a submarine?",
        "old_first_line": "Did submarine crews get seasick?",
        "new_first_line": "How did the crew handle seasickness on a submarine?",
    },
}

lines_out = []
fixes_applied = 0

with open("corpora/dieselsubs_faq_corpus.jsonl") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        cid = d.get("chunk_id", "")
        if cid in FIXES:
            fix = FIXES[cid]
            old_title = d["title"]
            d["title"] = fix["new_title"]
            d["text"] = d["text"].replace(fix["old_first_line"], fix["new_first_line"], 1)
            lines_out.append(json.dumps(d, ensure_ascii=False))
            fixes_applied += 1
            print(f"Fixed {cid}: '{old_title}' → '{d['title']}'")
        else:
            lines_out.append(json.dumps(json.loads(line), ensure_ascii=False))

with open("corpora/dieselsubs_faq_corpus.jsonl", "w") as f:
    for l in lines_out:
        f.write(l + "\n")

print(f"\nApplied {fixes_applied} fixes. Total lines: {len(lines_out)}")
