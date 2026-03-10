"""add_faqs9.py — Batch 11: pam_198–pam_210 (13 new FAQs)"""
import json, pathlib

CORPUS = pathlib.Path("corpora/dieselsubs_faq_corpus.jsonl")

NEW_FAQS = [
    {
        "chunk_id": "pam_198",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did a submarine conduct a periscope attack step by step?",
        "text": """How did a submarine conduct a periscope attack step by step?

A periscope attack was a carefully choreographed sequence that could unfold over hours or be compressed to minutes, depending on how quickly the target was closing.

Initial approach: The submarine detected the target — by sound, radar, or sighting — and maneuvered to an attack position. The ideal setup was to be ahead of the target's track, roughly 90 degrees off its bow, at a range of 1,500 to 3,500 yards when firing. The captain approached submerged, usually at around 3 knots to minimize noise and periscope wake.

Observation and solution-building: When close enough, the captain began "shooting" periscope bearings — raising the scope for a few seconds, marking the target's bearing, estimating range by stadimeter or by comparing the target's mast height to the scope's scale, then lowering immediately. The XO (or approach officer) fed each observation into the Torpedo Data Computer (TDC), which continuously updated the firing solution: target course, speed, range, angle on the bow.

Firing: When the TDC solution was "generated" — stable and reliable — the captain ordered "stand by." Torpedoes were fired at 6-second intervals to spread the spread across the target. The captain called "Fire!" (or "fire" was triggered automatically from the TDC). Four to six torpedoes per attack was typical.

Evasion: Immediately after firing, the captain went deep and changed course. "Rig for depth charge" — crew braced, secured machinery, prepared for counterattack. The crew listened for hits. A hit sounded like a metallic "clang" at depth. Multiple hits meant a sinking; silence meant a miss.""",
    },
    {
        "chunk_id": "pam_199",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the after engine room on a submarine?",
        "text": """What was the after engine room on a submarine?

Fleet submarines like the Pampanito had two engine rooms: the forward engine room and the after engine room, separated by the maneuvering room. Together the four Fairbanks-Morse diesel engines (two per room) gave the submarine its surface propulsion and battery-charging power.

The after engine room was located directly aft of the maneuvering room and housed two of the four Fairbanks-Morse Model 38D8-1/8 opposed-piston diesel engines. Each engine drove a generator rather than the propeller shafts directly. The generators fed power either to the main motors (for propulsion) or to the batteries (for recharging), and the maneuvering room controlled which configuration was in use at any given moment.

The after engine room was operated by machinist's mates (MM rating). Conditions were brutally hot — the engines radiated enormous heat, and in tropical patrol areas the temperature in the engine rooms could exceed 120°F. Noise was deafening; communication required shouting or hand signals. Despite this, machinists took great pride in their engines and kept meticulous logs of operating hours, temperatures, and fuel consumption.

In a submerged boat, both engine rooms were shut down. The engines were diesel and required air — running underwater was impossible. The after engine room went quiet and the crew worked in the dark heat, waiting for the next surface period when the engines could be restarted.""",
    },
    {
        "chunk_id": "pam_200",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What were the diving planes on a submarine and how did they work?",
        "text": """What were the diving planes on a submarine and how did they work?

Diving planes were the horizontal control surfaces — like horizontal rudders — that controlled a submarine's depth and pitch angle. Fleet submarines used two sets: the bow planes (forward) and the stern planes (aft, near the propellers).

Bow planes: Mounted on the forward part of the hull. When angled down, they pushed the bow downward, helping the boat dive. When angled up, they helped level off or climb. On fleet submarines the bow planes were retractable — they folded flat against the hull when surfaced so waves wouldn't damage them, and were rigged out before diving.

Stern planes: Located at the aft end of the boat near the screws. These were the primary depth-control surface and were used constantly while submerged to maintain ordered depth. The stern planesman sat in the control room next to the helmsman, watching the depth gauge and bubble (inclinometer) and working the planes continuously — it was essentially the same skill as flying an airplane.

The two planesmen worked together: bow planes controlled angle, stern planes controlled depth. On the attack team, the diving officer supervised both and was responsible for keeping the boat at periscope depth — shallow enough to use the scope, deep enough to avoid showing hull.

A full crash dive combined putting the bow planes on full dive, flooding the ballast tanks, and increasing speed. An experienced crew could take a surfaced submarine below periscope depth in under 60 seconds.""",
    },
    {
        "chunk_id": "pam_201",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did submarines use radar during World War II?",
        "text": """How did submarines use radar during World War II?

Radar transformed submarine warfare. US fleet submarines were equipped with two types: the SJ surface search radar and the SD air search radar.

SJ surface search radar: The most tactically important. It could detect a large surface ship at 10–12 miles and a small vessel at 4–6 miles, day or night, in rain or fog. The SJ gave precise bearing and range, which could be fed directly into the Torpedo Data Computer for a fire control solution. Night surface attacks using radar alone — without any periscope exposure — became standard practice by 1943–44 and were extremely effective against Japanese convoys. The radar operator became one of the most critical crew members.

SD air search radar: A simpler omnidirectional set that detected aircraft. It gave only range, not bearing, so it couldn't tell you which direction the plane was coming from — only how far away it was. When the SD showed a contact closing, the standing order was to dive immediately. The SD saved many submarines from air attack by giving a warning that visual lookouts might have missed.

Risk of radar: Transmitting radar pulses could be detected by enemy radar warning receivers beginning in 1944. Japanese aircraft were eventually equipped with radar detectors that could pick up SJ transmissions. This forced submariners to use radar intermittently rather than continuously, reducing the advantage. Nonetheless, radar remained one of the greatest tactical advantages US submarines had over Japanese naval and merchant forces.""",
    },
    {
        "chunk_id": "pam_202",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did submarine crews cope with the heat in the tropics?",
        "text": """How did submarine crews cope with the heat in the tropics?

The Pacific War was fought in some of the hottest waters on earth, and fleet submarines of the World War II era had no air conditioning — the crews simply endured.

In tropical patrol areas, below-decks temperatures routinely reached 95–110°F, and the engine rooms could exceed 120°F. The air was thick with diesel fumes and humidity. Men working the engine rooms sweated through their clothes within minutes. Condensation ran down the steel hull as warm air met cold seawater temperatures, making surfaces slippery and equipment rust-prone.

Water was rationed strictly. Fresh water was used for drinking, cooking, and battery maintenance. Showers were infrequent — a "Navy shower" meant a 30-second rinse. Men slept and worked in minimal clothing — shorts and T-shirts, or nothing at all in the worst compartments. Significant weight loss over a patrol (five to ten pounds) was common.

The ice cream machine was not a luxury but a morale necessity — cold food was one of the only reliefs from the heat. Submarine crews were known for receiving better rations than other Navy branches partly as compensation for the brutal conditions. The boats also carried more cold storage capacity than other ships of their size, refrigerating food and providing cold drinks that were small but real comforts in 100-degree heat.""",
    },
    {
        "chunk_id": "pam_203",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What qualities made a successful submarine commander?",
        "text": """What qualities made a successful submarine commander?

The submarine commanders who achieved the greatest success — the "aces" — shared a recognizable set of characteristics that went beyond technical skill.

Calculated aggression: The most successful captains were aggressive, pushing into close range and staying on the attack even when the tactical picture was uncertain. But they weren't reckless — they knew when to break off and when to accept risk. Dudley "Mush" Morton of USS Wahoo and Sam Dealey of USS Harder both exemplified this quality.

Decision speed: An attack unfolded in minutes. A captain who hesitated or second-guessed his TDC solution missed his shot. The ability to commit quickly, with incomplete information, was essential.

Crew confidence: In an enclosed steel tube with no escape, the crew had to trust their captain's judgment completely. A captain who inspired confidence — calm under depth charges, decisive at the scope, honest about dangers — could get more out of his crew than pure technical skill could explain.

Spatial reasoning: The mental geometry of an attack — visualizing a moving target, calculating intercept angles, estimating ranges — came more naturally to some officers than others. The best captains were almost running a parallel solution in their heads alongside the TDC.

Patience: Most of a patrol was boredom, watchful waiting. The captain set the tone. An impatient captain wasted torpedoes on poor setups; a patient one waited for the ideal firing position.

Well-known aces: Richard O'Kane (USS Tang), Dudley Morton (USS Wahoo), Samuel Dealey (USS Harder), Eugene Fluckey (USS Barb), Slade Cutter (USS Seahorse).""",
    },
    {
        "chunk_id": "pam_204",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was it like inside a submarine during a depth charge attack?",
        "text": """What was it like inside a submarine during a depth charge attack?

A depth charge attack was one of the most terrifying experiences a submarine crew could endure, and veterans who survived them rarely forgot the sound.

When the first depth charge exploded nearby, the shock came not as a distant rumble but as an instantaneous, skull-rattling CRACK — a physical concussion that shook the entire boat. Cork insulation flew off the interior walls. Light bulbs shattered. Gauges broke their mountings. Men were thrown against equipment. In a close pattern, the boat lurched sideways or pitched bow-down.

The boat went into "silent running": all non-essential equipment shut off, pumps and fans stopped, crew moved on sock feet and whispered. The temperature rose as ventilation stopped. CO₂ accumulated. Men sat motionless at their stations for hours, listening to the sonar operator track the destroyer's propeller sounds — "getting louder" meant another run; "fading" meant a miss.

The persistent dangers during a prolonged depth charge attack were flooding (from cracked seams, burst fittings, or failed gaskets), battery damage (seawater in the batteries generated chlorine gas, potentially fatal), and oxygen depletion from hours submerged without snorkeling. Submarines carried CO₂ absorbent and oxygen canisters for extended submergences.

Some boats absorbed 100 or more depth charges over a single engagement before escaping or being destroyed. The psychological toll on crews who survived repeated attacks was severe, and "depth charge nerves" was a recognized condition by the end of the war.""",
    },
    {
        "chunk_id": "pam_205",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did submarines evade destroyers and anti-submarine escorts?",
        "text": """How did submarines evade destroyers and anti-submarine escorts?

Surviving a destroyer counterattack required every tool available — mechanical, tactical, and in some cases luck.

Go deep and go slow: The first response to a depth charge attack was to dive below the estimated depth of the charges and slow to "creep speed" — as quiet as possible. At very slow speeds, the submarine's own propeller noise dropped dramatically, making it harder for the destroyer's sonar to track. Some captains stopped completely and let the boat drift, relying on neutral buoyancy.

Silent running: All non-essential machinery shut down. Pumps, fans, gyrocompasses — anything that made noise went off. Crew whispered. No one moved unnecessarily. A single dropped wrench could be heard by the enemy sonar.

Use the thermocline: Ocean temperatures drop with depth, and these temperature gradients — thermoclines — create acoustic barriers. A sonar ping from above the layer frequently bent or reflected rather than penetrating to the submarine hiding below. Experienced captains knew the water temperature profile and got below the thermocline when possible.

Maneuver unpredictably: Random course changes disrupted the destroyer's attack pattern, which required tracking the submarine's course ahead to place depth charges in the right spot.

Counter-attack: Some commanders fired a torpedo at an approaching destroyer both to defend themselves and to force the escort to evade, breaking up the attack run. This worked for a few extraordinary captains (Dealey sank five destroyers this way).

Time: Most attacks eventually ran out of depth charges or contact. Staying alive long enough for the enemy to give up was strategy in itself.""",
    },
    {
        "chunk_id": "pam_206",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Why were aircraft such a dangerous threat to submarines?",
        "text": """Why were aircraft such a dangerous threat to submarines?

Aircraft were uniquely dangerous to submarines because they could appear with almost no warning and attack before the submarine could dive to safety.

Speed of approach: A surfaced submarine had lookouts scanning the horizon, but an aircraft at high altitude could close from 10 miles to overhead in less than two minutes. The time from first sighting to crash dive completion was a race — a slow crash dive crew could easily be caught on the surface or at shallow depth where bombs and aircraft-delivered depth charges were most effective.

Depth of attack: Aircraft dropped shallower-set depth charges than surface ships, and they could also drop bombs. Shallow explosions were more effective against submarines caught at periscope depth or during the early phase of a dive than the deep patterns used by destroyers.

Coordination: Allied aircraft in the Atlantic learned to coordinate with surface ships, chasing submarines down while calling in surface escorts for the kill. Japan eventually developed similar coordinated ASW capability.

SD radar: The US developed the SD air search radar specifically to give submarine crews more warning time. When the SD scope showed a closing contact, standing orders were to dive immediately without visual confirmation. The SD saved many boats.

Aircraft losses: Aircraft were responsible for a significant portion of US submarine losses. Many boats vanished without survivors — believed sunk by air attack in shallow water where escape was impossible. The introduction of radar-equipped Japanese patrol aircraft in 1944–45 made the nighttime surface period — previously almost safe — significantly more dangerous.""",
    },
    {
        "chunk_id": "pam_207",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What were wolfpack tactics and how did the US Navy use them?",
        "text": """What were wolfpack tactics and how did the US Navy use them?

Wolfpack tactics were coordinated operations by multiple submarines against a single convoy or target area. While Germany's famous Rudeltaktik system used large packs tightly coordinated from shore, the US Navy developed a distinctly American version.

US wolfpacks were typically groups of two to four submarines placed under a task group commander — usually a senior officer embarked on one of the boats. The submarines were assigned overlapping patrol areas designed to catch a convoy no matter which route it took. When one submarine made contact, it tracked and reported while others moved into attack position.

US wolfpacks differed from German ones in key ways: they were coordinated more loosely, with individual captains retaining far more tactical independence; communication was minimal to reduce radio risk; and the primary goal was attacking the same convoy with multiple boats rather than massed night surface attacks.

Notable US wolfpacks included "Ben's Busters" (Cdr. Thomas Oakley, 1944), "Blair's Blasters" (Cdr. Leon Blair), and operations associated with the "Hit Parade" series. The South China Sea and Luzon Strait became primary wolfpack hunting grounds by 1944–45 as ULTRA intelligence identified convoy routes.

Results were mixed: some wolfpack operations sank many ships; others had poor coordination and individual boats got in each other's way. Most US skippers by 1944 were operating in the prime shipping lanes, and whether in a wolfpack or alone, were finding targets.""",
    },
    {
        "chunk_id": "pam_208",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Did US submarines ever sink enemy submarines?",
        "text": """Did US submarines ever sink enemy submarines?

Yes — US submarines did engage and sink enemy submarines, though this was never their primary mission. Fleet boats were tasked with attacking merchant shipping, fleet units, and troop transports; submarine-versus-submarine combat was relatively rare.

The most remarkable example was USS Batfish (SS-310), which sank three Japanese submarines in three consecutive nights in February 1945 in the Luzon Strait — an extraordinary feat that earned her a Presidential Unit Citation. All three kills were made on the surface by gunfire and torpedo.

Most US sub-vs-sub kills occurred when both submarines were surfaced and one sighted the other visually or by radar. Submerged torpedo attacks against submerged submarines were extremely difficult — the attacking boat had to fire on passive sonar contact without active pinging (which would reveal its own position), and a moving submerged target at periscope depth was a very small and elusive target.

Japanese submarines did sink several US submarines in return. I-176 sank USS Grunion, and other sinkings have been attributed to Japanese submarines though some remain uncertain. Neither side made sinking the other's submarines a high strategic priority — Japan because of the IJN's offensive doctrine, the US because of ULTRA intelligence showing that hitting Japanese logistics was far more valuable.

Overall, US submarines sank approximately 20–25 Japanese submarines during the war, a secondary but real contribution to the defeat of Japan's naval forces.""",
    },
    {
        "chunk_id": "pam_209",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the difference between a magnetic exploder and a contact exploder on a torpedo?",
        "text": """What was the difference between a magnetic exploder and a contact exploder on a torpedo?

The exploder was the detonating mechanism in the torpedo's warhead, and its reliability — or lack of it — was one of the greatest scandals of American submarine warfare.

Contact exploder (Mark 5): The older, simpler mechanism. When the torpedo struck the hull of a ship, a firing pin was driven forward by the impact, detonating the explosive charge. It worked exactly as advertised — when the pin functioned correctly. Early in the war, the contact exploder was discovered to have a critical flaw: the firing pin was too fragile to withstand a direct, 90-degree bow-on impact. It bent rather than firing, causing duds even on dead-center hits.

Magnetic exploder (Mark 6): A more sophisticated device designed to detect the change in the earth's magnetic field caused by a ship's steel hull passing overhead. Rather than requiring direct contact, the torpedo was supposed to pass under the keel and detonate from the magnetic influence. The explosion beneath the keel was theoretically more lethal — it could break a ship's back rather than just punch a hole in the side.

In practice, the Mark 6 was a disaster. It detonated prematurely (up to 300 yards short), ran erratically at the wrong depth to trigger, or failed to detonate at all. Commanders in the Pacific were convinced the exploders were defective by early 1942, but the Bureau of Ordnance insisted the weapons were reliable and blamed submarine commanders for firing errors.

It was not until mid-1943 that the Navy officially acknowledged the exploder failures and corrected them. The combination of a faulty magnetic mechanism AND a flawed contact backup meant that many perfectly aimed shots produced duds — a catastrophic loss of opportunity in the critical early years of the submarine campaign.""",
    },
    {
        "chunk_id": "pam_210",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How effective was Japanese anti-submarine warfare against US submarines?",
        "text": """How effective was Japanese anti-submarine warfare against US submarines?

Japanese anti-submarine warfare (ASW) was effective enough to destroy 52 US submarines — about 22% of all US submarines deployed in the war — making it one of the most lethal aspects of the Pacific campaign for submariners.

Japanese capabilities: The IJN equipped its destroyers and convoy escorts with hydrophones, sonar (Type 93 underwater sound equipment), and depth charges comparable in basic capability to Allied equipment. Japanese destroyer crews were skilled and aggressive — many individual attacks were devastatingly well-executed. Some of the most significant US submarine losses happened in the first two years of the war when Japanese ASW patrols were frequently encountered and US crews were still learning.

Japanese weaknesses: Japan was slow to organize a coherent convoy escort system — convoys ran without adequate destroyer protection until relatively late in the war. Japan also never fully coordinated aerial and surface ASW the way the Allies did in the Atlantic. Japanese aircraft rarely carried updated radar, limiting their effectiveness against nighttime surfaced submarines until 1944–45.

Improvement over time: As the war progressed, Japanese ASW improved. More escorts were assigned to precious oil tanker convoys. Aircraft equipped with radar appeared by 1944, making night surface operations more dangerous. Magnetic mines and new depth charge patterns caused increased US losses in 1944.

By war's end, the combination of improved Japanese ASW, minefields, and the sheer operational intensity of US submarine patrols had made the submarine service the highest casualty rate of any branch of the US armed forces in the Pacific.""",
    },
]

existing = set()
with CORPUS.open() as f:
    for line in f:
        d = json.loads(line)
        existing.add(d.get("chunk_id", ""))

added = 0
with CORPUS.open("a") as f:
    for faq in NEW_FAQS:
        if faq["chunk_id"] in existing:
            print(f"SKIP {faq['chunk_id']}: already exists")
            continue
        f.write(json.dumps(faq) + "\n")
        print(f"ADD  {faq['chunk_id']}: {faq['title']}")
        added += 1

total = sum(1 for _ in CORPUS.open())
print(f"\nAdded {added} FAQs. Total lines: {total}")
