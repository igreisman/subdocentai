import json

NEW_ENTRIES = [

{"chunk_id": "pam_061", "doc_type": "dieselsubs_faq", "source": "pampanito_docent", "type": "faq",
 "title": "How many American submarines were lost in WWII?",
 "questions": ["How many US submarines were sunk in World War II?", "How many submarines did the US lose in the war?"],
 "text": "How many American submarines were lost in WWII?\n\nThe United States lost 52 submarines during World War II \u2014 roughly 18% of all US submarines that went on war patrol. Each submarine lost took its entire crew of 60 to 80 men with it. In total, approximately 3,505 American submariners died in the war, representing the highest per-capita casualty rate of any branch of the US armed forces.\n\nOf the 52 submarines lost, the majority were sunk by Japanese anti-submarine forces \u2014 destroyers, aircraft, and smaller patrol craft equipped with depth charges. A number were lost to mines, especially in the early war years when enemy minefields were poorly charted. For about eight submarines there is no confirmed cause: they simply went missing on patrol and were never heard from again.\n\nDespite these losses, the US submarine force inflicted devastating damage on Japan: sinking approximately 55% of all Japanese merchant tonnage and one-third of the Japanese Navy \u2014 with fewer than 2% of Navy personnel. The 52 boats and their crews are commemorated with the phrase still used in the submarine community: they are \u201con eternal patrol.\u201d"},

{"chunk_id": "pam_062", "doc_type": "dieselsubs_faq", "source": "pampanito_docent", "type": "faq",
 "title": "Did submarines ever rescue survivors from the water?",
 "questions": ["Did any submarines rescue people from the ocean?", "Could a submarine pick up survivors from a sinking ship?"],
 "text": "Did submarines ever rescue survivors from the water?\n\nYes, though it was rare and dangerous. A submarine on patrol was primarily a weapon of war, not a rescue vessel. Stopping on the surface to pull survivors from the water exposed the boat to air and surface attack. For most of the war, submarine captains could not risk their crew and boat on rescue operations, however grim that reality was.\n\nThe most famous exception in the Pacific was the rescue mission carried out by USS Pampanito (SS-383), USS Sealion II (SS-315), and several other submarines in September 1944. After attacking a Japanese convoy, the submarines surfaced and discovered hundreds of British and Australian prisoners of war in the water \u2014 men who had been aboard Japanese prison ships unknowingly caught in the attack. Pampanito rescued 73 survivors; Sealion II rescued 54. Other ships arriving later pulled more from the sea. Of the approximately 2,200 POWs who had been aboard the doomed ships, about 159 were rescued in total. The rest perished.\n\nThis remains one of the most dramatic rescue operations in the history of the submarine service, and it is central to the story the Pampanito tells today."},

{"chunk_id": "pam_063", "doc_type": "dieselsubs_faq", "source": "pampanito_docent", "type": "faq",
 "title": "Did the Pampanito save the POWs?",
 "questions": ["How many POWs did the Pampanito save?", "Did the Pampanito rescue British and Australian prisoners?"],
 "text": "Did the Pampanito save the POWs?\n\nOn its third war patrol in September 1944, the Pampanito took part in one of the most remarkable rescue operations in submarine history. After attacking Japanese convoy HI-72 in the South China Sea, Pampanito and the other submarines in its patrol group surfaced to find hundreds of men in the water \u2014 emaciated, oil-covered survivors who turned out to be British and Australian prisoners of war.\n\nThe convoy had been unknowingly transporting over 2,200 Allied POWs aboard Japanese prison ships, and the submarines had attacked without knowing this. When Commander Paul Summers realized what was happening, Pampanito diverted all efforts to rescue. In about nine hours, the boat pulled 73 survivors aboard \u2014 men in desperate condition after years of brutal captivity and days in the open ocean. Every available space on the submarine was used to care for the injured.\n\nUSS Sealion II (SS-315) rescued an additional 54. Other ships reached the area and saved more. Of the 2,200 POWs, approximately 159 survived. Commander Summers received the Navy Cross for this patrol. Today the rescue is the centerpiece of the Pampanito\u2019s story as a museum ship."},

{"chunk_id": "pam_064", "doc_type": "dieselsubs_faq", "source": "pampanito_docent", "type": "faq",
 "title": "How did you flush a toilet on a submarine?",
 "questions": ["How did you use the bathroom on a submarine?", "How did the head work on a submarine?"],
 "text": "How did you flush a toilet on a submarine?\n\nFlushing a toilet \u2014 called the \u201chead\u201d on any Navy vessel \u2014 on a submerged submarine required a careful procedure. You could not simply flush as you would on land, because the submarine was under pressure from the surrounding water. Waste had to be blown outboard against sea pressure using compressed air.\n\nThe procedure involved a specific sequence of valves and levers: close the hull valve, open the blow valve, use compressed air to force the contents into the sea, then reverse the sequence carefully. Signs were posted in each head explaining the steps. Getting any part of the procedure wrong \u2014 opening valves in the wrong order or at the wrong time \u2014 could result in the contents being blown back into the boat and covering the user. Veteran submariners have a word for this mishap, and it is not polite.\n\nAt deeper depths the procedure was more complicated because greater air pressure was needed to overcome the sea pressure outside. Some submarines had sanitary retention tanks that held waste until the boat surfaced, when it could be discharged normally. Either way, the heads were few in number (one for officers, one for crew, for 80 men), the procedure was fiddly, and long lines during busy periods were simply part of submarine life."},

]

corpus_path = "corpora/dieselsubs_faq_corpus.jsonl"
with open(corpus_path, "a") as f:
    for entry in NEW_ENTRIES:
        f.write(json.dumps(entry) + "\n")

print(f"Appended {len(NEW_ENTRIES)} entries (pam_061 through pam_064)")
# Verify
lines = open(corpus_path).readlines()
print(f"Total corpus entries: {len(lines)}")
