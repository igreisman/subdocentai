import json
lines = open('corpora/dieselsubs_faq_corpus.jsonl').readlines()
targets = {'pam_007', 'pam_008', 'pam_022', 'pam_024', 'pam_026', 'pam_031'}
for l in lines:
    d = json.loads(l)
    if d.get('chunk_id') in targets:
        print(d['chunk_id'], ':', repr(d.get('title', '')))
