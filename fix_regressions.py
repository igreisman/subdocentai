import json

lines = open('corpora/dieselsubs_faq_corpus.jsonl').readlines()
changes = {
    # pam_024: add WWII to dilute perfect single-token "pampanito" coverage
    'pam_024': 'What happened to the Pampanito after WWII ended?',
    # pam_031: use WWII instead of "World War II" so title_toks includes "wwii"
    'pam_031': 'Were women allowed to serve on submarines in WWII?',
}

out = []
changed = []
for l in lines:
    d = json.loads(l)
    cid = d.get('chunk_id')
    if cid in changes:
        old = d.get('title')
        d['title'] = changes[cid]
        # Also update first paragraph of text to match new title
        text = d['text']
        # Replace the old title in the first line of text
        first_newline = text.index('\n')
        old_first_line = text[:first_newline]
        if old_first_line.strip() == old:
            d['text'] = changes[cid] + text[first_newline:]
        changed.append(f'{cid}: {old!r} -> {changes[cid]!r}')
    out.append(json.dumps(d))

open('corpora/dieselsubs_faq_corpus.jsonl', 'w').write('\n'.join(out) + '\n')
for c in changed:
    print('Changed:', c)

# Also append new paraphrase aliases
NEW = [
    {
        "chunk_id": "pam_065",
        "doc_type": "dieselsubs_faq",
        "source": "pampanito_docent",
        "type": "faq",
        "title": "How did submarines run underwater without air for the engines?",
        "text": "How did submarines run underwater without air for the engines?\n\nWhen a submarine submerged, its diesel engines had to stop. Diesel engines need air to run \u2014 specifically, they need large quantities of fresh air to burn fuel. Underwater, there is no fresh air available, so the diesels were shut down as the boat went under.\n\nInstead, the submarine ran on electric motors powered by large banks of lead-acid batteries, just like a very large flashlight. The batteries had been charged while the boat was on the surface, with the diesels driving generators rather than the propellers. A fully charged battery bank could power the submarine at slow speed for 24 to 36 hours, or at higher speed for a much shorter time.\n\nWhen the batteries ran low, the submarine had to surface to run the diesels again, both to drive the boat and to recharge the batteries. This is why WWII submarines spent most of their time on the surface at night \u2014 they needed the surface time to recharge for the next day\u2019s submerged operations."
    },
    {
        "chunk_id": "pam_066",
        "doc_type": "dieselsubs_faq",
        "source": "pampanito_docent",
        "type": "faq",
        "title": "Why did submarines stay on the surface at night?",
        "text": "Why did submarines stay on the surface at night?\n\nWWII submarines spent the majority of their time on the surface, surfacing at dusk and diving again at dawn. This was driven by two practical necessities: battery charging and speed.\n\nSubmarines ran on batteries while submerged, and those batteries had to be recharged by diesel generators on the surface. A full day submerged at patrol speed would drain the batteries significantly. Night was the safest time to operate on the surface \u2014 aircraft, the most dangerous threat to a surfaced submarine, could not spot you as easily. So submarines surfaced at night to charge their batteries and traveled as far as possible toward their patrol area or toward their next target.\n\nSpeed was the other reason. A fleet submarine on the surface could make 17 to 20 knots. Submerged, it could only manage 8 to 9 knots for brief periods, or 2 to 3 knots for extended running. Covering hundreds of miles to reach a patrol area was only practical on the surface. Submarines were really surface ships that could dive for evasion and attack, not true underwater vessels."
    },
]

with open('corpora/dieselsubs_faq_corpus.jsonl', 'a') as f:
    for e in NEW:
        f.write(json.dumps(e) + '\n')

lines2 = open('corpora/dieselsubs_faq_corpus.jsonl').readlines()
print(f'Total: {len(lines2)} entries')
print('Last IDs:', [json.loads(l)['chunk_id'] for l in lines2[-3:]])
