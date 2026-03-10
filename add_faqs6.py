"""Add batch 8 FAQs (pam_133-155) to the corpus."""
import json

NEW_FAQS = [

{
"chunk_id": "pam_133",
"title": "What did the captain do during a depth charge attack?",
"text": """What did the captain do during a depth charge attack?

During a depth charge attack, the captain's primary job was to keep the submarine alive while maintaining crew discipline and calm. He would typically be in or near the conning tower, receiving reports from sonar on the position of the attacking ships and directing the helmsman and diving officer on course, speed, and depth changes to evade the next pattern of charges.

The captain had to read the enemy's attack pattern — decide when to change depth, when to slow down to reduce noise, and when to sprint away at high speed to open the distance. Some captains ordered the boat deep, below the set depth of the charges. Others made radical course changes to get out from under the attacking escort. The captain had to make rapid decisions with incomplete information, often in total darkness with men bracing against the hull for the next explosion.

Veteran submarine captains like Ben Oakley, who commanded Pampanito's third war patrol, were known for their steady, controlled demeanor during attacks. The crew took its cue from the captain — if he appeared calm and decisive, the men maintained their discipline. Panic or poor judgment in those moments could cost everyone's life."""
},

{
"chunk_id": "pam_134",
"title": "How did the crew communicate with each other inside the submarine?",
"text": """How did the crew communicate with each other inside the submarine?

Fleet submarines had a shipboard intercom system called the "JV" or "JC" system — a network of sound-powered telephones that ran between all compartments and key stations. These phones required no electrical power source: the voice vibrated a diaphragm that generated a small current, which drove the earpiece in the listener's phone. Sound-powered phones worked even if the main electrical systems were damaged or shut down.

Specific phone circuits connected key stations: the bridge to the conning tower, the engine rooms to the maneuvering room, the torpedo rooms to the conn, and the control room to all compartments. When battle stations were called, each station manned its phones and reported readiness up the chain to the officer of the deck.

For voice communication between adjacent compartments, crew members simply passed through the watertight doorways or shouted through them when open. A loudspeaker 1MC public address system allowed general announcements throughout the boat. During quiet running under depth charge attack, however, all voice communication was kept to whispers, and finger taps on pipes or hand signals replaced verbal orders to minimize any sound that might travel through the water to the enemy's sonar."""
},

{
"chunk_id": "pam_135",
"title": "What did crew members wear on a submarine?",
"text": """What did crew members wear on a submarine?

Clothing aboard WWII submarines was notably informal compared to the rest of the Navy. Because submarines operated in tropical Pacific waters, the interior was warm, and formal uniform regulations were relaxed. Crew members typically wore dungarees (denim work trousers and shirts) while on duty inside the boat. Many sailors wore t-shirts or went shirtless in the hottest spaces like the engine rooms.

There was little room to carry or stow large amounts of clothing. Each man had a small personal locker for his gear. Dress uniforms were brought on patrol to wear in port, but on patrol, utility clothing was the norm. Shoes were sometimes forgone inside the submarine — many men wore sandals or went barefoot, especially in sleeping areas.

In cold weather or on the bridge at night, heavy foul-weather gear and watch coats were worn, as bridge watches in the open air were cold and wet with spray. Officers wore the same informal clothing as enlisted men inside the boat — one of the leveling aspects of submarine culture was that rank formalities were reduced in tight quarters. When submarines returned to port, dress uniforms were donned for official ceremonies or liberty ashore."""
},

{
"chunk_id": "pam_136",
"title": "What did it mean to be qualified in submarines?",
"text": """What did it mean to be qualified in submarines?

"Qualified in submarines" was the Navy's formal certification that a sailor had demonstrated the knowledge and ability to operate every critical system on the boat — not just his own specialty, but every other man's job as well. Qualification was not automatic: arriving on a submarine did not make you "qualified." It was earned.

A new crew member received a qualification card that listed every system, piece of equipment, and emergency procedure on the submarine. He was required to trace every pipe, cable, valve, and piece of machinery; demonstrate to senior petty officers that he understood what each system did and how to operate it; and pass an oral board (examination) conducted by officers.

The process typically took six months to a year. Until qualified, a sailor was informally known as a "non-qual" (or sometimes a "nub") — not yet a full-fledged submariner. Once finished, he was awarded the coveted Submarine Warfare Insignia — the gold (officers) or silver (enlisted) dolphins pin. Earning your dolphins was one of the proudest moments in a submariner's career. The tradition continues today: every sailor, regardless of rate or rank, must qualify on submarines before being considered a full member of the crew."""
},

{
"chunk_id": "pam_137",
"title": "What was the submarine combat patrol insignia?",
"text": """What was the submarine combat patrol insignia?

The Submarine Combat Patrol Insignia (also called the "patrol pin" or "combat pin") was a special award given to submariners who completed at least one officially designated "successful" combat war patrol. A successful patrol was one where the submarine either sank or damaged enemy vessels, or completed a special mission determined to be of equivalent importance.

The pin was a small gold (for officers) or silver (for enlisted men) badge bearing a submarine design with a star and dolphins (or a similar combat symbol, depending on the year issued). Each additional successful patrol earned an additional small gold star to be affixed to the ribbon or medal.

This was separate from the Submarine Warfare Insignia (the dolphins pin earned upon becoming qualified). The combat patrol pin was specifically for wartime action. It was a mark of distinction — a submariner who wore many stars on his combat pin had been through a great deal of danger. The Pampanito completed six war patrols, all of them officially designated as successful, so her crew members were eligible for up to six stars on their combat patrol pins."""
},

{
"chunk_id": "pam_138",
"title": "How did the Pampanito crew rescue the POWs from the water?",
"text": """How did the Pampanito crew rescue the POWs from the water?

On the night of September 15, 1944, USS Pampanito received a radio message from USS Sealion reporting survivors in the water at the site where the two submarines had torpedoed a Japanese convoy two days earlier. Pampanito reversed course and raced to the scene. What the crew found was horrifying: hundreds of emaciated British and Australian prisoners of war were floating in the South China Sea, clinging to wreckage after two days in shark-infested water.

The rescue was physically demanding and emotionally overwhelming. Crew members hung over the side, reaching into the water to grab men too weak to climb up themselves. Lines were thrown and men were hauled aboard. Many survivors were so weakened by years of captivity, starvation, tropical disease, and days in the ocean that they could barely hold on. Some died even as they were being pulled from the water.

Pampanito rescued 73 men. The submarine was so crowded that the crew gave up their bunks and personal space, feeding and caring for the survivors using the last of the fresh food supplies. The medical implications were severe — many survivors had serious wounds, infections, and malnutrition. USS Sealion rescued an additional 54. Together, 127 Allied POWs were brought to safety, in what became the largest rescue of Allied prisoners by a US submarine in the entire Pacific War."""
},

{
"chunk_id": "pam_139",
"title": "What was the role of the executive officer on a submarine?",
"text": """What was the role of the executive officer on a submarine?

The executive officer (XO), also called the "exec," was the second-in-command of the submarine and the captain's right hand. While the captain set strategic direction and made key tactical decisions, the XO managed the day-to-day operation of the boat and functioned as the ship's administrator.

The XO was responsible for: maintaining the watch bill (the schedule of all watches and duty assignments), coordinating training and qualification of new crew members, enforcing discipline, overseeing the department heads (engineering, navigation, weapons, supply), and managing the boat's administrative paperwork including the patrol report. When general quarters (battle stations) was called, the XO typically took charge of the approach party and fire control in the conning tower while the captain conned the boat.

The XO was also the enforcer of procedure — when the captain was resting, the XO ran the boat. A good exec who could anticipate the captain's intentions and keep the crew sharp and disciplined was essential to a successful submarine. Many famous WWII submarine commanders served as exec before getting their own command. The relationship between captain and exec was crucial: a submarine with a good command team, working in sync, performed far better than one with friction between them."""
},

{
"chunk_id": "pam_140",
"title": "What were battle stations on a submarine?",
"text": """What were battle stations on a submarine?

"Battle stations" (or "general quarters") was the highest state of combat readiness on a submarine. When the captain ordered battle stations, a klaxon alarm sounded and every man on the crew immediately reported to his designated battle station — a specific position on the boat assigned to him for conducting combat operations.

Key battle stations included: the captain at the periscope in the conning tower, the approach officer and fire controlman at the Torpedo Data Computer (TDC), the helmsman and diving officer in the control room, sonar operators at their equipment, a battle stations watch in the torpedo rooms ready to reload tubes, maneuvering room operators at the engine and motor controls, and lookouts and officers on the bridge (if on the surface). All watertight doors were checked closed. Reports came in by sound-powered telephone: "Forward room manned and ready," "After room manned and ready," and so forth, until the officer of the deck acknowledged all stations ready.

The difference between a successful attack and a missed opportunity — or between escaping a depth charge attack and being sunk — often came down to how fast and how smoothly the crew transitioned to battle stations. Submarines drilled this evolution constantly, and a well-trained crew could go from off-watch sleep to fully manned battle stations in under two minutes."""
},

{
"chunk_id": "pam_141",
"title": "What was the role of the pharmacists mate on a submarine?",
"text": """What was the role of the pharmacists mate on a submarine?

Fleet submarines in World War II did not carry a ship's doctor. Instead, they relied on a hospital corpsman (pharmacist's mate, or PhM) who was responsible for all medical care aboard the boat. This individual had received intensive medical training — far beyond the basics — specifically to handle the wide range of emergencies that could occur on a 70-day patrol far from any medical facility.

The pharmacist's mate performed routine sick call (treating injuries, infections, dental emergencies, and illness), managed the medical supplies and the pharmacist's locker, and in serious emergencies performed procedures including emergency appendectomies, wound treatment, and amputations when necessary. The most famous example was Pharmacist's Mate 1st Class Wheeler Lipes, who performed an emergency appendectomy on USS Seadragon (SS-194) in 1942 using improvised instruments and spinal anesthesia — with the patient surviving.

When Pampanito rescued the British and Australian POWs in September 1944, the pharmacist's mate was overwhelmed with casualties. The survivors presented with malnutrition, infected wounds, tropical diseases, and shock. The medical challenge of caring for 73 severely ill men in the limited space of a submarine was enormous. Pharmacist's mates on submarines routinely demonstrated a level of medical skill and resourcefulness that far exceeded their official training."""
},

{
"chunk_id": "pam_142",
"title": "Did any American submarines get captured by the enemy?",
"text": """Did any American submarines get captured by the enemy?

No. Not a single US submarine was captured by Japanese forces during World War II. Every submarine that was lost in the Pacific was destroyed — sunk by depth charges, mines, aerial bombs, or other causes — with no known case of a surviving submarine being boarded and taken as a prize by the enemy.

This was partly by design. Standing orders for submarine commanders were that the boat must be scuttled (intentionally sunk by the crew) before allowing it to fall into enemy hands. The cryptographic equipment on board — code machines, code books, and intelligence materials — was to be destroyed or jettisoned at sea before any surrender. In practice, the situations that sent submarines to the bottom were almost always violent and rapid, leaving no opportunity for the Japanese to capture a boat intact.

One incident came close: USS Tullibee (SS-284) was accidentally sunk by her own torpedo in 1944, leaving one survivor who was captured by the Japanese. But the submarine itself was gone. In the Atlantic, the Germans actually captured a British submarine (HMS Seal) intact, and the Allies famously captured the German U-505 by boarding in 1944 — but nothing comparable happened to US submarines in the Pacific."""
},

{
"chunk_id": "pam_143",
"title": "What was a ballast tank on a submarine?",
"text": """What was a ballast tank on a submarine?

A ballast tank was a large tank built into the outer hull of the submarine, used to make the boat dive beneath the surface or surface again. In simple terms: fill the ballast tanks with seawater and the submarine sinks; blow the seawater out with compressed air and the submarine floats back up.

Fleet submarines like Pampanito had main ballast tanks located along the sides of the hull, between the outer pressure hull and the streamlined outer casing. These tanks had flood valves on the bottom and vent valves on the top. To dive, the vent valves were opened, letting the tanks flood with seawater while air escaped from the top. The submarine's overall density increased until it was heavier than water, and the boat descended. To surface, high-pressure air was blown into the tanks, forcing the water back out through the bottom flood valves. The submarine became lighter than water and rose.

There were also trim tanks and variable ballast tanks used for fine-tuning the submarine's fore-and-aft balance (trim) while submerged. Managing trim was a constant task for the diving officer — fuel was consumed, water was used, and torpedoes were fired, all changing the boat's balance. The diving officer and chief of the watch had to constantly adjust water between tanks to keep the submarine level and at the correct depth."""
},

{
"chunk_id": "pam_144",
"title": "What was a war patrol report?",
"text": """What was a war patrol report?

A war patrol report (officially the "Patrol Report" or "War Patrol Report") was a detailed official document prepared by the commanding officer after each war patrol, describing everything that happened during the mission. These reports became critical intelligence documents and historical records.

A typical patrol report included: the date and location of the patrol area, all contacts with enemy vessels (including date, time, position, course, speed, and identification), all torpedo attacks (number of torpedoes fired, estimated hits, observed results, and damage assessment), any surface engagements using the deck gun, enemy anti-submarine attacks received (depth charges, aircraft, escort attacks), observations of enemy shipping patterns and routes, weather conditions, and administrative matters such as crew performance and mechanical issues. The captain also included his own tactical assessments and recommendations for future patrols.

These reports were closely analyzed by submarine command at Pearl Harbor and the Naval War College. Commanders who consistently reported aggressive tactics and accurate results were promoted; those with poor performance — too cautious, too many misses — were relieved of command. The patrol reports were also cross-referenced with Japanese records after the war as part of the Joint Army-Navy Assessment Committee (JANAC) review that officially credited ship sinkings."""
},

{
"chunk_id": "pam_145",
"title": "How did submarines avoid enemy minefields?",
"text": """How did submarines avoid enemy minefields?

Avoiding minefields was one of the most nerve-wracking navigation challenges for WWII submarine commanders. Mines could not be detected by sonar — they appeared as passive, silent threats. The primary defense was intelligence: US submarines received detailed mine charts from submarine command at Pearl Harbor showing known or suspected enemy minefields, and commanders were expected to navigate around them.

Navigating through mine-infested waters required precise position-keeping. Submarines transited at very slow speed, often at periscope depth or fully surfaced at night, with the captain personally supervising the approach. In narrow straits like the Lombok Strait, Luzon Strait, or the approaches to Japanese ports, submarines carefully followed swept channels or chose deep-water routes where mines were less likely to be anchored successfully.

Despite precautions, several US submarines were lost to mines during the war, including USS Grunion (SS-216), which may have been sunk by her own circular-running torpedo or a mine. Submarines often had no warning: if a submarine hit a mine, it was almost always fatal with complete loss of crew. The uncertainty of not knowing whether a charted route was still clear was a constant background anxiety during any patrol in restricted, mine-threatened waters."""
},

{
"chunk_id": "pam_146",
"title": "What was a fleet boat?",
"text": """What was a fleet boat?

"Fleet boat" was the informal nickname for the Gato, Balao, and Tench class fleet submarines that formed the backbone of US submarine operations in World War II — the same general type as USS Pampanito. The term distinguished these large, ocean-going submarines from smaller coastal or minelaying submarines and from experimental or specialized types.

Fleet boats were designed to operate with the fleet — meaning they had the speed (nominally 20+ knots on the surface), range (11,000+ nautical miles), and endurance (75 days) to operate across the entire Pacific Ocean alongside surface task forces. In practice, they were used independently on long-range war patrols, but the "fleet" designation reflects the original requirement that they be able to keep up with fast-moving surface forces.

They were the largest and most capable conventional submarines the United States had ever built, and they proved devastatingly effective against Japanese shipping. Fleet boats like Pampanito were approximately 311-312 feet long, displaced about 1,500 tons surfaced, carried 24 torpedoes, and had a crew of around 70-80 men. By contrast, earlier submarines like the S-class boats were much smaller, slower, and shorter-ranged — not suited for the vast distances of Pacific warfare."""
},

{
"chunk_id": "pam_147",
"title": "How did submarines recharge their batteries?",
"text": """How did submarines recharge their batteries?

Fleet submarines like Pampanito used a diesel-electric propulsion system. When on the surface, the diesel engines drove generators that both propelled the submarine and charged the large banks of storage batteries located below the crew quarters. When submerged, the diesels couldn't run — they require air — so the submarine ran on battery power alone.

Recharging the batteries required coming to the surface and running the diesel engines. A full charge took several hours. Submarines typically surfaced after dark to recharge, since daylight on the surface in enemy waters was dangerous. The crew followed a routine: diesel engines started, generators clutched in, battery charging began, while simultaneously the boat was ventilated with fresh air and any routine maintenance was done topside. A watch was kept on the bridge with radar scanning for surface or air threats.

The batteries had a limited capacity: at slow submerged speed (2-3 knots), they lasted roughly 24-48 hours. At higher submerged speed, they drained in hours. The balance between conserving battery power while submerged and finding safe opportunities to surface and recharge was one of the fundamental strategic constraints of submarine warfare in the diesel-electric era. This is why the snorkel (absent on US WWII submarines) was such an important development — it allowed recharging while remaining nearly submerged."""
},

{
"chunk_id": "pam_148",
"title": "What was the difference between a Gato and a Balao class submarine?",
"text": """What was the difference between a Gato and a Balao class submarine?

The Gato and Balao class submarines were nearly identical externally and very similar in most respects — the Balao was essentially an improved version of the Gato, incorporating lessons learned early in the war. The most important difference was hull strength and diving depth.

The Gato class (built 1941-43) had a test depth of 300 feet and could go somewhat deeper in emergencies. The Balao class (built 1942-45) used stronger, higher-yield steel in the pressure hull, giving it a test depth of 400 feet. This extra 100 feet of depth was significant — it allowed Balao-class submarines to dive below the set depth of many Japanese depth charges, which were often set to explode at shallower depths. USS Pampanito is a Balao-class submarine (look for the SS-383 hull number range: Gatos were roughly SS-212 to SS-284, Balao class SS-285 to SS-416).

The Tench class, which followed, was a further improvement with more internal space and better equipment. All three classes were visually similar to the untrained eye, and the crews operated them in essentially the same way. The deeper diving capability of the Balao gave her crews slightly better odds of surviving depth charge attacks in the later years of the Pacific war when Japanese anti-submarine techniques were improving."""
},

{
"chunk_id": "pam_149",
"title": "What were the daily duties of the captain of a submarine?",
"text": """What were the daily duties of the captain of a submarine?

On a WWII fleet submarine, the captain's daily routine revolved around keeping the boat combat-ready, maintaining the crew's morale and discipline, and pursuing the mission. A typical patrol day included reviewing the night's radio traffic from submarine command, studying charts and intelligence on enemy shipping in the patrol area, conducting or attending training drills, reviewing the engineering plant status with the chief engineer, and conducting periscope watches in the patrol area.

The captain did not stand a regular watch — he was always "on call" and expected to be at the conn whenever a contact was made, whenever conditions were dangerous (restricted waters, poor visibility, aggressive enemy activity), or when any decision of consequence had to be made. In practice, experienced captains slept in brief intervals near their battle station, ready to be awakened instantly.

The captain also managed the human side of the boat. He knew every man by name and maintained personal contact with the crew, which was easier on a submarine than on any larger warship. He dealt with crew concerns, discipline issues, and morale — the latter being crucial on a 70-day patrol. The evening meal was sometimes a briefing time when the captain told the crew where they were and what was happening. A commanding officer who kept his crew informed and treated them with respect earned extraordinary loyalty from men willing to follow him into mortal danger."""
},

{
"chunk_id": "pam_150",
"title": "How did submarines handle the threat of enemy destroyers?",
"text": """How did submarines handle the threat of enemy destroyers?

Destroyers were the primary anti-submarine threat to US submarines in the Pacific. They were fast, maneuverable, and equipped with sonar and depth charge throwers. When a submarine was detected, a destroyer could run down on it at 30+ knots and deliver a pattern of depth charges with deadly precision.

The submarine's primary defense was to dive deep, change course frequently, and reduce speed to minimize noise. By going deep (the Balao class could reach 400 feet or beyond in emergencies), submarines could get below the depth setting of many Japanese depth charges, which were often preset before the attack and couldn't be changed mid-drop. Radical course changes made the submarine's position harder to predict. Slowing to 1-2 knots minimized propeller noise, making it harder for enemy sonar to track the boat.

Experienced commanders also used the ocean's thermal layers — changes in water temperature at different depths that bend or scatter sonar waves — to hide from active sonar pings. Going deep and creeping under a thermocline layer could make a submarine effectively invisible to sonar above the layer. The cat-and-mouse battle between a submarine and a destroyer hunting it was a battle of nerve, technique, and endurance. Some attacks lasted many hours; a few went on for more than a day before the destroyer withdrew or ran out of depth charges."""
},

{
"chunk_id": "pam_151",
"title": "What was the sound of a torpedo being fired?",
"text": """What was the sound of a torpedo being fired?

Firing a torpedo from a submarine was a distinctive sensory experience. The crew in the torpedo room heard and felt a sharp, compressed-air WHUMP — a quick shudder as high-pressure air (or water-ram, depending on the firing system) ejected the torpedo from the tube. Immediately after, the outer door of the tube thudded shut. In most cases, the submarine barely moved from the force, but in shallow water or when multiple torpedoes were fired in quick succession, a slight shudder ran through the hull.

The conning tower crew listened for the "fish running hot, straight, and normal" confirmation from the torpedo room: the torpedo's own turbine engine starting up and running correctly. If the torpedo ran erratically or circled back (occasionally happened with defective torpedoes), the submarine had to take emergency evasive action.

After the torpedo left the tube and crossed the distance to the target — typically 1 to 3 minutes at 46 knots — the crew listened for the explosion. A hit produced a deep, rolling BOOM heard clearly through the hull, sometimes followed by secondary explosions as the target's boilers or ammunition detonated. A miss produced no sound. The tension of those silent minutes between firing and impact (or non-impact) was one of the defining emotional experiences of submarine warfare."""
},

# Aliases for better matching
{
"chunk_id": "pam_152",
"title": "What was commissioning day like for a new submarine?",
"text": """What was commissioning day like for a new submarine?

What was the commissioning of a submarine?

Commissioning was the ceremony that officially brought a new warship into the United States Navy. For a submarine, commissioning day was a milestone in the boat's history: the first time the crew formally took possession of the vessel, raised the national ensign, and placed the ship "in commission" as an active unit of the US Navy.

The ceremony typically took place at the shipyard where the submarine was built. The crew was assembled on deck or on the pier in dress uniform. A Navy official read the commissioning orders, the commanding officer officially accepted the ship, and the first watch was set — symbolically beginning the submarine's naval service. The Commissioning Pennant was broken at the masthead and the ensign raised for the first time. Family members and shipyard workers were often present.

After commissioning, the submarine underwent sea trials and shakedown exercises to correct any deficiencies found during testing, before proceeding to a fleet command for combat assignment. USS Pampanito was commissioned on November 6, 1943, at the Portsmouth Naval Shipyard in Kittery, Maine, and she completed her shakedown before heading to the Pacific to begin combat operations."""
},

{
"chunk_id": "pam_153",
"title": "What happened to Japanese submarines at the end of WWII?",
"text": """What happened to Japanese submarines at the end of WWII?

What happened to the Japanese submarine force in WWII?

Japan entered the war with roughly 60 front-line submarines and built many more during the conflict, eventually deploying over 170 submarines. By the end of the war in August 1945, Japan's submarine force had been devastated. The Japanese lost approximately 130 submarines during the war — more than 75% of their wartime submarine strength — to US destroyers, destroyer escorts, aircraft, mines, and accidents.

Japan's submarine force had been misused strategically: instead of deploying them primarily against Allied merchant shipping (as the US used its submarines against Japan), the Imperial Japanese Navy assigned submarines to resupply isolated island garrisons, carry supplies to besiege outposts, and conduct fleet support roles rather than commerce raiding. This reflected a fundamental difference in doctrine. The few Japanese submarines that did conduct attacks on merchant shipping had some successes, but the potential for a Pacific "unrestricted submarine warfare" campaign against Allied supply lines was largely squandered.

At the war's end, surviving Japanese submarines were surrendered to American and Allied forces. Most were eventually scuttled at sea by the US Navy in 1946 as part of "Operation Road's End," since no Allied nation wanted to keep them and the cost of returning them to Japan was not justified."""
},

{
"chunk_id": "pam_154",
"title": "What happened if a crew member died while on patrol?",
"text": """What happened if a crew member died while on patrol?

What happened to men who were killed on a submarine patrol?

If a sailor died on a WWII submarine patrol — from illness, accident, or combat — the body could not be preserved or brought back to port. After any appropriate ceremony the captain deemed possible under the circumstances, burial at sea was the only option. The body was committed to the ocean. A full burial at sea with all honors was conducted if conditions permitted; in the middle of a combat patrol in enemy waters, a simpler and quicker ceremony was necessary.

The captain was required to document the death fully in the ship's log, recording the name, rate, circumstances of death, date, location, and any witnesses. Official notification was eventually sent to the Navy Department, which notified the sailor's family. Because a submarine's mission and location were classified, families often received only a minimal official notification that their loved one had died at sea.

The submarine's crew dealt with loss in the same stoic way they handled all hardships. On a small boat where every man knew every other, the death of a shipmate was deeply personal. Morale had to be maintained, and the mission continued. Veterans of WWII submarine service rarely spoke in detail about losing shipmates — it was one of the experiences that remained too difficult to discuss long after the war ended."""
},

{
"chunk_id": "pam_155",
"title": "How did submarines get their orders for each war patrol?",
"text": """How did submarines get their orders for each war patrol?

How did submarines receive their patrol assignments?

Patrol assignments came from Submarine Command Pacific (ComSubPac), headquartered at Pearl Harbor under Admirals Withers, Lockwood, and their staff. When a submarine returned from a patrol and the crew had rested, the captain and executive officer met with the submarine command staff. They reviewed the previous patrol, received intelligence briefs on Japanese shipping traffic and known escort strengths in various areas, and then received their next patrol order.

The patrol order was a written document specifying the submarine's patrol area (designated by a grid zone in the Pacific), any special missions or restrictions, radio frequencies and schedules, liaison with other submarines or wolf packs in the area, and the expected duration of the patrol. The specific targets — what to attack — were left entirely to the captain's judgment once in the assigned area. Commanders had broad discretion on how aggressively to pursue contacts, when to attack, and when to evade.

Ultra intelligence (decoded Japanese radio transmissions from the code-breaking program at Pearl Harbor) was sometimes incorporated directly into patrol orders: a submarine might be directed to a specific location and time where a Japanese convoy was expected based on decoded traffic. This intelligence was among the most closely guarded secrets of the Pacific War."""
},

]

BASE = {
    "doc_type": "dieselsubs_faq",
    "source": "dieselsubs_faq",
    "display_citation": "DieselSubs FAQ",
}

lines = []
with open("corpora/dieselsubs_faq_corpus.jsonl") as f:
    for line in f:
        if line.strip():
            lines.append(line.strip())

existing_ids = {json.loads(l)["chunk_id"] for l in lines}

added = 0
for faq in NEW_FAQS:
    if faq["chunk_id"] in existing_ids:
        print(f"SKIP {faq['chunk_id']} (already exists)")
        continue
    entry = {**BASE, "chunk_id": faq["chunk_id"], "title": faq["title"], "text": faq["text"].strip()}
    lines.append(json.dumps(entry, ensure_ascii=False))
    added += 1
    print(f"ADD  {faq['chunk_id']}: {faq['title']}")

with open("corpora/dieselsubs_faq_corpus.jsonl", "w") as f:
    for l in lines:
        f.write(l + "\n")

print(f"\nAdded {added} FAQs. Total lines: {len(lines)}")
