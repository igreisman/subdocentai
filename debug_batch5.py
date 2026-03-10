#!/usr/bin/env python3
"""Debug why pam_080 and other FAQs aren't winning"""
import sys
sys.path.insert(0, '.')
from api.main import tokenize, overlap_score, expand_query_tokens, STOPWORDS, QUERY_SYNONYMS, FAQ, TOUR, retrieve

def debug_query(q, target_id=None):
    raw_toks = tokenize(q)
    q_tokens = [t for t in raw_toks if t not in STOPWORDS]
    print(f"\n{'='*60}")
    print(f"Q: {q}")
    print(f"q_tokens: {q_tokens}")
    expanded = expand_query_tokens(q_tokens)
    print(f"expanded: {sorted(set(expanded))}")
    
    # Check target FAQ
    if target_id:
        for ch in FAQ:
            if ch.get('chunk_id') == target_id:
                text = ch.get('text','')
                s = overlap_score(q_tokens, text)
                text_toks = set(tokenize(text))
                matches = set(expanded) & text_toks
                lines = text.split('\n')
                title_line = lines[0] if lines else ''
                title_toks = set(tokenize(title_line))
                q_set = set(q_tokens)
                matched = len(set(expanded) & title_toks)
                coverage = matched / len(title_toks) if title_toks else 0
                all_q = all(
                    t in title_toks or any(syn in title_toks for syn in QUERY_SYNONYMS.get(t, []))
                    for t in q_set
                )
                ew = 1.2 * 4.0 * coverage if all_q else (1.2 * 2.0 * coverage if matched >= max(1, len(q_set)-1) else 1.2)
                print(f"\nTarget {target_id}:")
                print(f"  overlap={s}, matches={sorted(matches)}")
                print(f"  title_toks={sorted(title_toks)}")
                print(f"  coverage={coverage:.2f}, all_q_covered={all_q}")
                print(f"  effective_weight={ew:.2f}, SCORE={s*ew:.2f}")
                break
    
    # Show top 3 hits
    hits = retrieve(question_text=q, compartment_id='', playhead_time_ms=0, top_k=3)
    print(f"\nTop 3 hits:")
    for i, (score, ch, src) in enumerate(hits[:3]):
        cid = ch.get('chunk_id','?')
        title = ch.get('text','')[:60].replace('\n','\\n')
        print(f"  #{i+1} score={score:.2f} [{cid}] {title}")

debug_query("How far could a submarine travel on one fuel load", "pam_082")
debug_query("What was a Mark 14 torpedo", "pam_079")
debug_query("How did submarine crews track enemy ships", None)
debug_query("What was the battery room on a submarine", "pam_085")
debug_query("What happened to the crew after the war", "pam_080")
