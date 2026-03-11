"""add_faqs10.py — Batch 12: pam_211–pam_226 (16 new FAQs)"""
import json, pathlib

CORPUS = pathlib.Path("corpora/dieselsubs_faq_corpus.jsonl")

NEW_FAQS = [
    {
        "chunk_id": "pam_211",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was a submarine tender and what did it provide to submarines?",
        "text": """What was a submarine tender and what did it provide to submarines?

A submarine tender was a large support ship that served as a mobile base for a flotilla of submarines. Without tenders, the US submarine campaign in the Pacific would have been impossible — submarines needed constant resupply, repair, and crew rest that no shore base in the combat zone could provide.

What the tender provided: A tender carried everything a submarine needed: torpedoes, fuel, food, spare parts, fresh water, and technical specialists. The machine shops aboard a tender could perform almost any repair short of drydocking — overhauling engines, reconditioningtorpedoes, replacing electronics, patching hull damage. Tenders also had medical facilities, including surgeons, since submarines had only pharmacist's mates.

Crew rest: Between patrols, submarine crews lived aboard the tender in relative comfort while their boat was serviced. A proper bunk, hot meals in a real galley, and freedom from the cramped, smelly submarine interior made the tender a significant morale and readiness resource.

Key tenders in the Pacific: USS Fulton (AS-11), USS Sperry (AS-12), USS Euryale (AS-22), USS Holland (AS-3), and USS Proteus (AS-19) supported fleet operations at Pearl Harbor, Midway, Majuro, Guam, and later Subic Bay. The forward staging of tenders — moving them closer to the patrol areas as the war progressed — allowed longer operational time on station and shorter transit time from patrol area to refit.

Organizational hub: The tender was also the administrative home for the squadron. The squadron commander (ComSubRon or ComSubDiv) was usually embarked aboard the tender, where patrol reports were filed, orders were received, and awards were presented.""",
    },
    {
        "chunk_id": "pam_212",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Why did the Mark 14 torpedo run deeper than set and what was done about it?",
        "text": """Why did the Mark 14 torpedo run deeper than set and what was done about it?

The Mark 14 torpedo's depth-running failure was one of the most damaging and frustrating equipment failures of the entire war. Submarine commanders saw torpedo after torpedo pass harmlessly under their targets, and for over a year the Bureau of Ordnance refused to believe them.

The problem: The Mark 14 ran approximately 10 to 11 feet deeper than its depth setting. A torpedo set to run at 10 feet — aimed at piercing a destroyer's hull — actually ran at 20 to 21 feet, passing under the keel without making contact. Against shallow-draft vessels, this meant a clean miss every time, regardless of how perfectly the firing solution was calculated.

Why it wasn't caught: Pre-war testing used exercise heads (empty) rather than live warheads. The exercise heads were slightly lighter than war shots, causing the torpedo to run accordingly shallower during testing. The weight difference, and therefore the depth discrepancy, was never measured or reported. The torpedo entered service uncorrected.

Cover-up and resistance: The Bureau of Ordnance insisted the weapons were correct and blamed the submarine captains for poor technique. Reports of duds and missed shots were dismissed as operator error. It took nearly 18 months of combat failures before Admiral Lockwood in 1942 authorized his own tests at Fremantle — using nets strung in a harbor — to prove the depth was wrong.

Fix: Once the depth problem was confirmed in late 1942, the depth mechanisms were corrected. A separate problem — the firing pin in the contact exploder — took until September 1943 to fix. And the magnetic exploder's failures had already been known since early 1942. The complete set of fixes to the Mark 14 didn't come until mid-to-late 1943 — nearly two years into the war.""",
    },
    {
        "chunk_id": "pam_213",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did ULTRA codebreaking intelligence help US submarines find targets?",
        "text": """How did ULTRA codebreaking intelligence help US submarines find targets?

ULTRA was the Allied codebreaking program that broke the Japanese naval cipher system JN-25 and the Maru (merchant shipping) codes. It gave US submarine commanders intelligence of extraordinary value — advance knowledge of convoy routes, departure times, composition, and escort strength.

How it worked operationally: When codebreakers at Pearl Harbor, Brisbane, or FRUPAC (Fleet Radio Unit Pacific Fleet) decrypted a Japanese naval message indicating a convoy departure, that information was relayed to ComSubPac (Commander Submarines Pacific). Patrol orders were issued routing submarines into the convoy's path. To conceal the source, submarines were sometimes told they had received intelligence from "a reliable source" or from a fictional reconnaissance aircraft.

Impact: By 1943–44 ULTRA was enabling an average of 20–25% of all US submarine sinkings. Some analysts credit ULTRA with an even higher fraction of the decisive sinkings in 1944 when the oil convoy routes were targeted. The ability to intercept specific, high-value convoys — including tankers carrying oil from the Dutch East Indies — was directly enabled by ULTRA.

Secrecy: The intelligence was so sensitive that submarine captains were not formally told they were receiving ULTRA-sourced intelligence. Commander John P. Cromwell of USS Sculpin knew the full extent of ULTRA — and when Sculpin was sunk and the crew ordered to abandon ship, Cromwell chose to go down with the boat rather than risk capture and interrogation. He was awarded a posthumous Medal of Honor for this decision.

Long-term effect: Japan never suspected its codes were broken. The JN-25 cipher was periodically updated, but each new version was eventually broken. The most valuable decryption period was 1943–1945, when the submarine campaign was reaching its decisive phase.""",
    },
    {
        "chunk_id": "pam_214",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was a down-the-throat shot on a submarine?",
        "text": """What was a down-the-throat shot on a submarine?

A down-the-throat shot was a torpedo fired directly at an oncoming enemy warship — a destroyer or escort heading straight toward the submarine at high speed, usually during a depth charge attack.

The tactical situation: After a submarine attacked a convoy, the escort vessels counterattacked. A destroyer tracking the submarine would line up and charge directly at it. The submarine was in a desperate position — it could dive deeper, evade, and absorb depth charges, or in some cases choose to fight back. A down-the-throat shot gave the submarine a chance to stop the attack before it reached firing point.

Why it was difficult and desperate: The geometry was extremely challenging. The target's profile was almost nothing — a ship coming bow-on presents a tiny target cross-section, maybe 30 feet wide. The gyro angle was near zero (torpedoes fired straight ahead), so there was almost no room for error in timing. The range had to be correct. The submarine also had to be at periscope depth to fire — shallow enough to be vulnerable to ramming and gun fire, at exactly the moment the attacker was closest.

Why it worked sometimes: Despite the difficulty, some captains scored down-the-throat kills. Commander Samuel Dealey of USS Harder made a specialty of it — he sank five destroyers, many with close-range bow-or-stern shots that became legendary. The Japanese destroyer captains who pressed their attacks straight in, line-abreast, gave submarines this opportunity.

Risk and reward: A successful down-the-throat shot eliminated the attacking escort, freeing the submarine to continue with its patrol. Failure meant a close-aboard explosion, possible ramming, or an accurate depth charge pattern at close range. It was a last-resort tactic that required exceptional nerve.""",
    },
    {
        "chunk_id": "pam_215",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did mines threaten US submarines and how did crews cope?",
        "text": """How did mines threaten US submarines and how did crews cope?

Mines were a constant, silent threat to US submarines operating in Japanese-controlled waters. Unlike aircraft or destroyers, a mine gave no warning and no chance to evade — the first sign of a mine field was sometimes an explosion.

Japanese minefields: Japan heavily mined the shallow approaches to its home islands, harbor entrances, and key shipping straits. Minefields were placed in the waters around Japan proper, in the Tsushima/Korea Strait, around Okinawa, and in the East and South China Seas. These fields were known to exist but their exact boundaries were uncertain — charts were based on intelligence that was often incomplete.

How submarines avoided them: Submarine headquarters distributed mine-avoidance routing charts, and ULTRA intelligence sometimes revealed newly-laid fields from decrypted Japanese naval messages. Submarines were routed around known fields where possible. In shallow waters, a submarine could try to stay deep (below mine depth) or navigate narrow swept channels. Sound gear could sometimes detect anchored mine cables.

Notable losses: USS Grunion (SS-216) was lost in 1942, probably to a mine or a malfunctioning torpedo. USS Flier (SS-250) was sunk by a mine in the Balabac Strait in August 1944 — eight survivors managed to reach shore and were eventually rescued. USS Tullibee was lost to her own circular-running torpedo, illustrating how fine the line was between enemy weapons and friendly ones going wrong.

The final barrier: Operation Barney (June 1945) sent nine submarines through the heavily mined Sea of Japan as a coordinated penetration, using FM sonar to detect and navigate around mines. One submarine, USS Bonefish, was lost to a surface ASW attack inside the Sea of Japan. The operation proved submarines could operate inside a mined region — at significant risk.""",
    },
    {
        "chunk_id": "pam_216",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Were the sinking claims made by US submarines accurate?",
        "text": """Were the sinking claims made by US submarines accurate?

No — US submarine sinking claims during the war were significantly overstated, a finding that emerged after the war when postwar assessment teams compared American claims against captured Japanese records.

The Joint Army-Navy Assessment Committee (JANAC): After the war, JANAC reviewed every US submarine patrol report against Japanese shipping loss records. JANAC's final report (1947) credited US submarines with sinking approximately 1,314 merchant ships totaling 5.3 million tons, plus 201 warships. This was roughly one-third less than what submariners had claimed during wartime.

Why overclaiming happened: In the pressure of an attack, a submarine heard explosions after firing and noted the target had disappeared from the periscope field. These were interpreted as hits and sinkings. In reality, explosions could be depth charges, the target could have turned away or sped up, and a hit was not always a sink. Submarines rarely had the luxury of surfacing to confirm a sinking.

Was it dishonest? No. The claims were made in good faith in highly stressful conditions, with limited information and under immediate threat. Overclaiming was universal in all navies in all theaters — Japanese and German submarine claims were also substantially inflated.

Historical context: Even the JANAC figures represent a devastating strategic achievement. The 1,314 confirmed merchant sinkings destroyed Japan's ability to import the oil, ore, and food required to sustain its war economy and population. By 1945 Japan had essentially no functional merchant marine. US submarines, representing less than 2% of US Navy personnel, accounted for more than 55% of all Japanese shipping losses.""",
    },
    {
        "chunk_id": "pam_217",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the overall strategic impact of the US submarine campaign?",
        "text": """What was the overall strategic impact of the US submarine campaign?

The US submarine campaign against Japan was one of the most decisive strategic operations of World War II — arguably the single factor most responsible for Japan's economic and military collapse by 1945.

Shipping losses: US submarines sank approximately 1,314 merchant ships totaling over 5 million tons, plus about 200 warships. Japan's merchant fleet, which it needed to import oil, ore, food, and raw materials from its conquered territories, was reduced from approximately 6 million tons in 1941 to under 2 million tons by mid-1945.

Oil embargo effect: Japan's critical vulnerability was oil. Its entire military machine, from aircraft carriers to fighter planes, ran on oil imported from the Dutch East Indies. By 1944 US submarines were intercepting the tanker convoys on the routes from Southeast Asia to Japan with devastating effect. By late 1944 the Japanese Navy curtailed training flights because aviation fuel was unavailable. Capital ships that sortied to Leyte Gulf in October 1944 barely had enough fuel for a one-way trip.

Warship sinkings: Among the warships sunk by US submarines were the carriers Shinano (the world's largest carrier at the time, sunk by USS Archerfish four days after commissioning), Taiho, Unyo, Chuyo, Shokaku; the battleships Kongo and Musashi (partially); and scores of cruisers and destroyers.

Human cost: 52 US submarines were lost — about 22% of all submarines that made war patrols. Approximately 3,500 US submariners died, giving the submarine service the highest proportional casualty rate of any branch of the US armed forces in the Pacific. The motto "Run Silent, Run Deep" captures both the method and the sacrifice of these men.""",
    },
    {
        "chunk_id": "pam_218",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did a torpedo tube work to launch a torpedo?",
        "text": """How did a torpedo tube work to launch a torpedo?

Firing a torpedo from a submarine was a carefully engineered sequence, not simply pulling a trigger. Each step had to be correct — an error could sink the submarine.

Loading: The torpedo, weighing about 3,000 pounds and 20 feet long, was loaded into the tube breech-first by the torpedo room crew using a hand-cranked loading mechanism that slid it along a track from the stowage rack into the tube. The breech door (rear door) was then sealed and locked.

Pre-firing preparation: The tube was flooded with sea water to equalize pressure with the outside ocean, preventing the outer door from being blown off when it was opened. A hydraulic piston or compressed-air manifold was connected at the rear. The outer door on the hull exterior was then opened. The submarine at periscope depth meant water pressure outside was relatively low.

Firing: When the captain called "Fire!", the fire control panel electrically completed a circuit that opened the high-pressure air impulse valve at the back of the tube. The impulse charge — a pre-set volume of high-pressure air at about 200–400 psi — pushed the torpedo out of the tube in approximately one second. As the torpedo exited, its engine started (steam turbine for Mark 14, battery for Mark 18).

After firing: The impulse air ejected behind the torpedo vented through an inboard vent to prevent an air bubble from rising to the surface and revealing the firing position — called "clearing the air bubble." The outer door was then closed, the tube inboard-vented, drained, and reloaded. Reloading took about 15–20 minutes.

The submarine could fire multiple tubes in rapid succession — the Pampanito and other Balao-class boats had six forward and four aft tubes.""",
    },
    {
        "chunk_id": "pam_219",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the forward battery compartment and why did officers live there?",
        "text": """What was the forward battery compartment and why did officers live there?

The forward battery compartment served a dual purpose that was unique and somewhat uncomfortable: it was both the home of one of the two main battery banks and the officers' living area.

Beneath the deck: The forward battery contained 126 lead-acid battery cells housed below the wooden deck plating in a watertight compartment that extended the full length of the space. These cells — each weighing several hundred pounds — were the submarine's underwater power source. Battery maintenance required periodic ventilation and produced hydrogen gas, making open flame strictly prohibited throughout the compartment.

Above the deck — officers' country: On the main deck level sat the wardroom (officers' dining room and lounge), the commanding officer's private cabin, the executive officer's stateroom, and four or five additional officers' staterooms. By warship standards these were reasonably private quarters — each officer had a bunk, a small desk, and a curtain. The CO's cabin was the largest, roughly the size of a small closet.

The wardroom: Officers ate meals in the wardroom, which doubled as a meeting room, game room, and planning space. The captain held pre-attack briefings here. Meals were eaten in shifts, and the wardroom steward (often a Filipino mess attendant in pre-war Navy tradition) served the officers' meals.

Battery smell: Despite the wooden deck covering, a faint sulfurous odor was a constant feature of the forward battery compartment. If the battery was damaged — particularly by seawater contamination — it would produce toxic chlorine gas, one of the most feared emergency scenarios on a submarine. "Battery gas" drills were practiced regularly.""",
    },
    {
        "chunk_id": "pam_220",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Were any submarine crew members awarded the Medal of Honor in World War II?",
        "text": """Were any submarine crew members awarded the Medal of Honor in World War II?

Yes — five US submariners received the Medal of Honor during World War II, and all five stories reflect extraordinary acts of courage, often at the cost of their own lives.

Commander Howard W. Gilmore, USS Growler (posthumous): In February 1943, after ramming a Japanese ship during a night surface engagement, Gilmore was wounded on the bridge and unable to climb down to the hatch as enemy fire continued. Knowing he could not make it inside before the submarine was sunk, he ordered "Take her down" — commanding his crew to dive without him. He went down with the sea. His Medal of Honor was awarded posthumously.

Commander John P. Cromwell, USS Sculpin (posthumous): When USS Sculpin was heavily damaged and sinking in November 1943, Cromwell ordered the crew to abandon ship. He knew the full extent of ULTRA intelligence — convoy schedules, codes, future operations — and refused to be captured for fear of what the Japanese might extract. He went down with Sculpin. Posthumous Medal of Honor.

Commander Samuel D. Dealey, USS Harder (posthumous): Over multiple patrols, Dealey sank five destroyers in close-quarters attacks, including down-the-throat shots that destroyed escort vessels that would have defended valuable convoys. USS Harder was lost in August 1944. Posthumous Medal of Honor.

Commander Richard H. O'Kane, USS Tang: O'Kane pressed USS Tang into extraordinarily aggressive attacks until a circular-running torpedo from his own boat sank Tang in October 1944. O'Kane survived as a Japanese prisoner of war. Medal of Honor awarded on his return.

Commander Eugene B. Fluckey, USS Barb: Fluckey's extraordinary patrol record included operations in the Sea of Japan and a landing party mission to blow up a Japanese train. Medal of Honor awarded in 1945.""",
    },
    {
        "chunk_id": "pam_221",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did submarine crews send and receive mail during war patrols?",
        "text": """How did submarine crews send and receive mail during war patrols?

Mail was one of the most powerful morale factors for submarine crews, and the Navy went to significant effort to route it through the forward areas — but the logistics of delivering mail to a submarine on a secret patrol were inherently awkward.

Receiving mail: A submarine's home base fleet post office (FPO) at Pearl Harbor, Brisbane, Fremantle, or later Guam held accumulated mail for the crew while the boat was on patrol. When the submarine returned to base and tied up to the tender, mail was one of the first things delivered. After a 50–60 day patrol, a crewman might receive a stack of dozens of letters in a single delivery. Any mail that had arrived after the submarine departed was held for the next return.

V-mail: Later in the war the Navy used V-mail (Victory mail) — a system in which letters were microfilmed, shipped on microfilm rolls rather than as bulky paper packages, and printed at the receiving end. This allowed vast quantities of correspondence to be moved with minimal cargo weight and volume.

Outgoing mail: Letters written aboard a submarine were held until the boat reached port. Outgoing mail was censored — a censor (usually a junior officer) read all letters and blacked out any information about location, convoy sightings, patrol areas, or recent actions. Sailors quickly learned what could and could not be written. Some developed private codes with their families to convey a general sense of location; if discovered, such codes were forbidden.

Holiday packages: Families mailed cookies, candy, and small gifts. During long patrols approaching the holidays, mail was especially important — and its absence especially hard. A lost boat meant a stack of undeliverable mail accumulating on a tender, which was how families sometimes first suspected something had gone wrong.""",
    },
    {
        "chunk_id": "pam_222",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "When did submarines use their deck guns instead of torpedoes?",
        "text": """When did submarines use their deck guns instead of torpedoes?

Deck guns — primarily the 4-inch/50 caliber and later the 5-inch/25 caliber guns mounted on the submarines' weather decks — were not just defensive weapons. In the right circumstances, submarines used them aggressively for surface attacks, conserving torpedoes for higher-priority targets.

Against small and shallow-draft targets: Torpedoes were expensive (roughly equivalent to a small house in wartime cost) and carried in limited quantities — 24 aboard a Balao-class submarine. Small Japanese vessels — coastal freighters, sampans, barges, fishing boats, harbor tenders — were simply too small and shallow-draft for torpedoes to work reliably. Gun action was faster, cheaper, and more certain against these targets. Submarines sank hundreds of small vessels by gunfire.

When torpedoes were already expended: Late in a patrol, after firing most torpedoes, a submarine might still have deck gun rounds available and a tempting target. Rather than return with ammunition unused, captains would attack by gun.

Finishing off damaged ships: If a torpedo had damaged but not sunk a ship, a surfaced gun action could finish the job, saving precious torpedoes. This was particularly useful against tankers, which were hard to sink with a single torpedo.

Conditions for deck gun action: A deck gun attack required calm sea conditions (the deck was only feet above the waterline), absence of aircraft, and minimal escort threat. At night, a radar-equipped surfaced submarine had a significant advantage over an unescorted freighter with no fire control equipment. In these conditions, gun attacks were safer than they might appear.

Late-war evolution: By 1944–45 torpedo reliability had improved and targets were more heavily escorted. Pure gun actions became less common, though the guns remained in use.""",
    },
    {
        "chunk_id": "pam_223",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the difference between the conning tower and the control room?",
        "text": """What was the difference between the conning tower and the control room?

The conning tower and the control room were adjacent but distinct spaces with different functions, located one above the other via a hatch and ladder. Visitors often confuse them because both played vital roles in operating and fighting the submarine.

The conning tower: The conning tower was the small cylindrical compartment above the pressure hull, inside the fairwater (the vertical structure also often called the "sail" or "tower"). It contained the primary attack equipment: the two periscopes, the torpedo data computer (TDC), the helm (steering wheel), the sonar operator's position, and the attack periscope's optics. During a submerged torpedo attack, the commanding officer, TDC operator, and helmsman all worked in the conning tower. It was cramped — roughly 8 feet in diameter and maybe 7 feet tall.

The control room: Directly below the conning tower, accessed through a hatch in the conning tower deck, was the larger control room. This was the depth and diving management center. It contained the ballast and trim control manifolds, the diving planes controls (operated by the two planesmen), the depth gauges, and the Christmas tree (the ballast tank indicator panel). The diving officer supervised the control room during dives; the chief of the watch managed the diving panel. The navigation plot table was also in the control room.

Division of command: During an attack, the captain in the conning tower handled the tactical picture — he was looking through the periscope, reading bearings, calling the solution. The diving officer in the control room kept the boat at periscope depth — a few feet too shallow or too deep would take the scope out of the water or submerge the hull too much. The two spaces had to work in constant coordination through the open hatch between them.""",
    },
    {
        "chunk_id": "pam_224",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was a Presidential Unit Citation and how did the Pampanito earn one?",
        "text": """What was a Presidential Unit Citation and how did the Pampanito earn one?

A Presidential Unit Citation (PUC) was the highest collective military honor the President of the United States could award to a military unit. For a ship or submarine crew, receiving the PUC was the unit equivalent of an individual receiving the Navy Cross — second only to the Medal of Honor in the hierarchy of valor awards.

What it recognized: The PUC was awarded for extraordinary heroism in action against an armed enemy, performed with distinction that set the unit apart from others facing similar challenges. It required combat action, not merely meritorious service.

USS Pampanito's citation: The Pampanito earned her Presidential Unit Citation for her third and fourth war patrols — conducted in 1944 under Commander Paul E. Summers. These patrols included the September 12, 1944 engagement in the South China Sea in which Pampanito, operating with USS Sealion II and USS Growler, attacked Convoy HI-72 and sank multiple vessels. After the attack, Pampanito and Sealion discovered that the convoy's freighters had been carrying British and Australian prisoners of war from Singapore. Pampanito rescued 73 POWs from the water — the most rescued by any US submarine from a single action — and Sealion rescued additional survivors.

The combination of aggressive convoy attack and the extraordinary humanitarian rescue operation, in enemy waters, under threat of counterattack, was the basis for the citation. The crew also received individual combat awards across these patrols.

What it means for visitors: The Pampanito was not just a museum piece — she is a decorated combat vessel with a documented record of valor and one of the most remarkable rescue operations of the submarine war.""",
    },
    {
        "chunk_id": "pam_225",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Why did submarines have two periscopes and what was each one for?",
        "text": """Why did submarines have two periscopes and what was each one for?

Fleet submarines like the Pampanito carried two periscopes, and each served a different tactical purpose. Having two periscopes allowed the captain to choose the right tool for the situation rather than compromise between opposing requirements.

The attack periscope (No. 1 scope): The attack periscope was designed to be as small and hard to detect as possible. It was very thin — approximately 1.4 inches in diameter at the upper end — with minimal top optics to reduce the visual disturbance ("feather") at the surface. The trade-off was smaller lenses and lower light-gathering capability. The attack scope was used during the actual firing phase, raised only momentarily for last-second observations. Being thinner, it was less likely to be spotted by a sharp-eyed lookout on the target ship.

The search periscope (No. 2 scope): The search periscope was significantly larger in diameter — approximately 5 inches — with superior optics, higher magnification, and better light gathering for use in limited visibility or dusk/dawn conditions. It also carried a radar antenna and could be equipped with bearing-and-elevation scales for firing control. The search scope was used for the approach phase, when the submarine was still distant from the target and needed maximum observation capability. Because it was larger, it produced a more visible feather at the surface and was retired once the attack run began.

Redundancy: Having two periscopes also provided redundancy. If the attack scope was damaged — not uncommon in rough seas or close action — the search scope could take over. During the entire attack sequence, from initial detection through firing, a submarine captain might alternate between scopes depending on what information he needed at that moment.""",
    },
    {
        "chunk_id": "pam_226",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How many ships did the USS Pampanito sink and what was her war record?",
        "text": """How many ships did the USS Pampanito sink and what was her war record?

USS Pampanito (SS-383) was commissioned on November 6, 1943, at Portsmouth Naval Shipyard. She conducted six war patrols before the end of World War II, earning a combat record that earned her a Presidential Unit Citation and four battle stars.

Confirmed sinkings: JANAC (Joint Army-Navy Assessment Committee) credited USS Pampanito with sinking five Japanese vessels, including merchant ships and a transport, totaling approximately 27,000 tons of shipping. She also damaged several additional ships.

Key patrols: Pampanito's third and fourth war patrols (1944, under Commander Paul E. Summers) were her most distinguished. She operated as part of a coordinated attack group with USS Sealion II and USS Growler in the South China Sea. On September 12, 1944, the group attacked Convoy HI-72 — a heavily loaded Japanese convoy. Pampanito and her partners sank multiple ships.

The POW rescue: The convoy's cargo ships turned out to be carrying British and Australian prisoners of war taken from Singapore. Many were on deck when the ships were attacked. After the convoy fight, Pampanito surfaced the following morning and found men in the water. She rescued 73 POWs, then sent messages bringing USS Sealion II back to rescue additional survivors. This was one of the most poignant episodes of the entire submarine war — rescuing men whose captors she had just sunk.

Post-war: Pampanito was decommissioned in 1946. After years in the reserve fleet, she was donated to the National Maritime Museum Association and opened as a memorial submarine and museum ship at Fisherman's Wharf, San Francisco, in 1982, where she remains today.""",
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
