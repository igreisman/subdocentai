#!/usr/bin/env python3
"""Add pam_067-085 to dieselsubs_faq_corpus.jsonl"""
import json

CORPUS = "corpora/dieselsubs_faq_corpus.jsonl"

NEW_FAQS = [
    {
        "chunk_id": "pam_067",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How many torpedoes did a submarine carry?",
        "text": """How many torpedoes did a submarine carry?

A Balao-class fleet submarine like the Pampanito carried 24 torpedoes in a full load. The forward torpedo room had six torpedo tubes and space for ten reload torpedoes — a total of sixteen ready forward. The after torpedo room had four tubes and four reloads — eight aft. Together that was exactly 24.

Once all 24 were fired or the patrol was over, the submarine returned to base to reload. Reloading torpedoes at sea from a tender was possible but rare — it was a slow, difficult operation in open water. Most patrols ended when the torpedo supply ran out."""
    },
    {
        "chunk_id": "pam_068",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the temperature like inside a submarine?",
        "text": """What was the temperature like inside a submarine?

Heat was a constant problem, especially in the Pacific. The four diesel engines generated enormous heat, and the engine rooms could reach 120 degrees Fahrenheit or higher in tropical waters. Crewmen in the engine room wore as little as possible and dripped sweat constantly. The rest of the boat was hot too — there was no real air conditioning, just ventilation fans moving warm, humid air.

When submerged, the diesels stopped and the boat cooled slightly, but heat from battery charging, equipment, and 80 men's bodies still built up. By the end of a long dive, the air could be thick and uncomfortably warm. Cold-water patrols near Japan were a different story — crews sometimes bundled up. The tropics were the hardest."""
    },
    {
        "chunk_id": "pam_069",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How loud was it inside a submarine?",
        "text": """How loud was it inside a submarine?

On the surface with diesels running, a fleet submarine was extremely loud. The four engines each produced 1,600 horsepower and roared constantly. The engine rooms were close to 100 decibels — a level that causes hearing damage over time. Many World War II submariners suffered significant hearing loss by the end of the war.

When submerged on batteries, the main motors hummed quietly, and the overall noise level dropped dramatically. Submerged running was much more bearable. But during a depth charge attack, the noise was terrifying — explosions rattling the hull, lights flickering, equipment failing. The crew learned to stay silent during those moments so sonar could hear enemy propellers and the captain could plan the next move."""
    },
    {
        "chunk_id": "pam_070",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How long was a typical war patrol?",
        "text": """How long was a typical war patrol?

A typical war patrol for a fleet submarine like the Pampanito lasted between 45 and 75 days. The duration was limited by fuel, food, and torpedoes. When the torpedoes were gone or food ran critically low, the submarine headed back to base. Mechanical breakdowns could also cut a patrol short.

The Pampanito completed six war patrols between June 1944 and July 1945, ranging from about 40 to 75 days each. Between patrols, the crew had a rest period — usually three to six weeks — while the boat was refueled, provisioned, repaired, and loaded with fresh torpedoes. At the peak of the Pacific war, when bases moved closer to Japan, patrols became more efficient and more dangerous."""
    },
    {
        "chunk_id": "pam_071",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What did the crew do when they spotted an enemy ship?",
        "text": """What did the crew do when they spotted an enemy ship?

When a lookout or radar operator spotted an enemy vessel, the officer of the deck called "battle stations — torpedoes" over the intercom. Every man immediately went to his battle station. The captain went to the conning tower and took over at the periscope. The bridge watch dove below and the hatches were sealed.

The crew began a careful approach — tracking the target's speed, course, and distance. These measurements were fed into the torpedo data computer, which calculated the correct firing solution. The approach could take minutes or hours depending on daylight, sea conditions, and enemy escorts. When the solution was ready, the captain gave the order to fire, typically sending a spread of two to four torpedoes at the target."""
    },
    {
        "chunk_id": "pam_072",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Did submarines ever fight other submarines?",
        "text": """Did submarines ever fight other submarines?

It happened, but it was rare. US submarines did sink several Japanese submarines during World War II, mostly using torpedoes when the enemy submarine was spotted on the surface, or by depth charges when detected submerged. However, submerged submarine-vs-submarine combat was extremely difficult — both boats were maneuvering blind with only sonar to detect each other.

The primary mission of US fleet submarines was attacking enemy surface ships — freighters, tankers, warships, and troop transports. Submarine-vs-submarine engagements were an occasional bonus, not the main focus of patrols. The Japanese submarine force suffered heavily not from US submarines but from US destroyers and aircraft using depth charges and hedgehogs."""
    },
    {
        "chunk_id": "pam_073",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the largest submarine in WWII?",
        "text": """What was the largest submarine in WWII?

Japan built the largest submarines of World War II. The I-400 class — called "Sen Toku" submarines — were about 400 feet long and could carry three aircraft in a watertight hangar on deck. They were designed to launch planes to attack the Panama Canal or US cities but arrived too late to be used in those missions.

American fleet submarines like the Balao class, which includes the Pampanito, were about 312 feet long and 27 feet in diameter at the pressure hull — considered large, capable ocean-going warships. German Type VII U-boats, the most common submarine of the war, were much smaller at about 220 feet long. US fleet submarines were larger and had far greater range than their German counterparts."""
    },
    {
        "chunk_id": "pam_074",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Did submarines ever carry troops or special forces?",
        "text": """Did submarines ever carry troops or special forces?

Yes. US submarines performed a wide variety of special missions beyond standard war patrols. Submarines landed scouts, agents, and Filipino guerrilla fighters behind Japanese lines — sneaking them ashore in rubber boats at night. They also evacuated personnel from occupied islands and supported resistance fighters throughout the Philippines by delivering weapons, medicine, and supplies.

The Pampanito was dedicated to attack patrols as a fleet submarine, but many submarines in the Pacific fleet spent time on these special missions. Some submarines were specially configured to carry swimmer-delivery vehicles or teams of commandos. The submarine's ability to approach enemy coastlines undetected made it a natural choice for covert operations."""
    },
    {
        "chunk_id": "pam_075",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was a war patrol?",
        "text": """What was a war patrol?

A war patrol was an officially designated combat mission assigned to a submarine by fleet command. The Navy formally recognized patrols as "war patrols" when the submarine entered a combat zone and operated against the enemy. Completing a successful war patrol earned the crew a combat patrol pin — a prestigious decoration.

Each patrol was assigned a geographic area, called a patrol zone or patrol area, within which the submarine was authorized to attack enemy shipping. Fleet command tried to route multiple submarines through areas where Japanese convoys were expected. The patrol ended when torpedoes were expended, supplies ran low, the submarine was damaged, or the time limit was reached. The Pampanito completed six war patrols, earning battle stars for each one."""
    },
    {
        "chunk_id": "pam_076",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did the crew handle doing laundry?",
        "text": """How did the crew handle doing laundry?

Doing laundry on a submarine was nearly impossible. Fresh water was extremely precious — the boat's evaporators could produce only a limited amount, and it was reserved primarily for drinking and cooking. There was nothing to spare for washing clothes.

Most sailors wore the same clothes for days at a time. In the tropical Pacific, many men worked in shorts and little else to cope with the heat — which also reduced the laundry problem. Personal items might be rinsed in a bucket of water, but full laundry had to wait until the submarine returned to port. Once ashore, the crew could use proper Navy laundry facilities. Submariners joked that the best part of coming back from patrol was a hot shower, a real meal, and clean clothes."""
    },
    {
        "chunk_id": "pam_077",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Did the Pampanito crew get shore leave?",
        "text": """Did the Pampanito crew get shore leave?

Yes. Between each war patrol, the crew received rest and recuperation — called R&R. Submarine crews were considered elite and received some of the best leave facilities in the Navy. Pearl Harbor had rest camps with swimming pools, good food, and comfortable bunks. Australia — primarily Brisbane and Fremantle — was another popular rest destination for submarine crews early in the war.

A typical turnaround between patrols lasted three to six weeks. During that time, the crew got real food, clean beds, sports, movies, and time away from the boat. The Navy understood that the psychological and physical strain of submarine patrols was severe, and that well-rested crews would be more effective than exhausted ones. The short time ashore was eagerly anticipated after weeks at sea."""
    },
    {
        "chunk_id": "pam_078",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What ports did the Pampanito operate from?",
        "text": """What ports did the Pampanito operate from?

The Pampanito operated primarily from Pearl Harbor, Hawaii and advanced bases in the Central Pacific. As the war progressed and American forces moved closer to Japan, the Navy established forward submarine bases at Midway and later at Guam and other recaptured islands in the Marianas. Operating from Guam cut roughly 3,000 miles off the trip to Japanese waters and allowed longer time on patrol.

All six of the Pampanito's war patrols were in the Pacific — mostly in the waters of the South China Sea, the Luzon Strait, and the East China Sea. Japanese waters were heavily patrolled by enemy aircraft and warships, making every approach dangerous. The Pampanito returned to the United States in the summer of 1945 for an overhaul when the war ended before she could go out again."""
    },
    {
        "chunk_id": "pam_079",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the Mark 14 torpedo?",
        "text": """What was the Mark 14 torpedo?

The Mark 14 was the standard torpedo used by US fleet submarines during World War II. It was 21 inches in diameter and 21 feet long, with a 643-pound explosive warhead. The Mark 14 could travel at 31 knots for 4,500 yards, or at 46 knots for a shorter sprint of about 1,000 yards.

Unfortunately, the Mark 14 had serious problems early in the war. The depth-control mechanism made it run deeper than set, causing it to pass under targets. The exploder — both the magnetic and contact versions — often failed to detonate on impact. Submariners reported torpedo after torpedo hitting enemy ships and failing to explode. The Navy resisted fixing these problems for years, but by 1943 the depth problem and exploder failures were finally corrected. After that, the Mark 14 performed reliably and became a highly effective weapon."""
    },
    {
        "chunk_id": "pam_080",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What happened to the Pampanito crew after the war?",
        "text": """What happened to the Pampanito crew after the war?

When Japan surrendered in August 1945, the Navy began rapidly demobilizing. Most of the Pampanito's crew returned to civilian life. Many used the GI Bill to go to college, start businesses, or buy homes. They got married, started families, and worked to rebuild their lives after years of wartime service.

Some stayed in the Navy and had long careers, rising through the ranks. A few remained connected through the USS Pampanito Association, a veterans' group that kept former crewmembers in touch. Over the decades, veterans returned to visit the boat after she became a museum ship at Fisherman's Wharf in San Francisco. They brought their children and grandchildren, shared their stories, and helped preserve the history of what they had done. The last surviving Pampanito veterans passed away in their 90s and 100s in the early decades of the twenty-first century."""
    },
    {
        "chunk_id": "pam_081",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Were Pampanito crew members awarded medals?",
        "text": """Were Pampanito crew members awarded medals?

Yes. The Pampanito received the Navy Unit Commendation ribbon and earned battle stars for each of her six war patrols. Individual crew members earned a range of decorations including the Bronze Star, Silver Star, and Navy Cross for acts of valor in combat.

The most celebrated event was the rescue of Allied prisoners of war in September 1944. After sinking Japanese ships that turned out to be carrying British and Australian POWs, the Pampanito turned back to pull survivors from the water. The crew rescued 73 men — working in the dark, in enemy waters, under the constant threat of attack. The officers and men involved in the rescue were rightly honored. Their actions saved lives that would otherwise have been lost without any record of what had happened."""
    },
    {
        "chunk_id": "pam_082",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How much fuel did a submarine carry?",
        "text": """How much fuel did a submarine carry?

A Balao-class submarine like the Pampanito carried approximately 116,000 gallons of diesel fuel. This fuel was stored in tanks built into the outer hull, called fuel ballast tanks, which were flooded with seawater as fuel was consumed to maintain the submarine's balance and buoyancy.

With 116,000 gallons aboard, the Pampanito had a surface range of roughly 11,000 nautical miles at cruise speed — enough to travel from Hawaii almost to Japan and back. The Navy also positioned submarine tenders and forward bases closer to the combat zones to reduce the distance submarines had to travel, stretching that range further and allowing submarines to spend more time on patrol rather than in transit."""
    },
    {
        "chunk_id": "pam_083",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What happened if a submarine got stuck on the bottom?",
        "text": """What happened if a submarine got stuck on the bottom?

Submarines could end up on the bottom either by accident — running aground in shallow water — or intentionally during a depth charge attack, when a captain might order the boat to the bottom to reduce noise and wait out the hunt.

If the submarine bottomed intentionally during a hunt, the crew would shut down all non-essential systems and wait silently, sometimes for hours, while the batteries slowly discharged and the air quality declined. If the submarine was damaged and trapped, the crew could use emergency escape equipment — breathing devices called Davis Submerged Escape Apparatus, or later the Momsen Lung — to swim to the surface. If the submarine broached in shallow water, compressed air could blow the ballast tanks and the engines could back the boat free. Grounding in deep water was nearly always fatal."""
    },
    {
        "chunk_id": "pam_084",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the diving alarm sound?",
        "text": """What was the diving alarm sound?

The diving alarm was a Klaxon horn that made a distinctive AAOOGA sound — two blasts to signal a normal dive or three blasts for a crash dive emergency. The sound instantly sent every man on the boat scrambling to dive stations.

Lookouts on the bridge dove down the conning tower hatch in seconds. The officer of the deck was the last man below and dogged — sealed — the hatch behind him. Below, men opened flood valves to fill the ballast tanks with seawater, pulled in the radio antenna, shut vents, and angled the diving planes down. A well-trained crew could take a fleet submarine from cruising on the surface to fully submerged in 30 to 45 seconds. The AAOOGA sound of the Klaxon became one of the most iconic sounds of World War II and is still recognized worldwide as the sound of a diving submarine."""
    },
    {
        "chunk_id": "pam_085",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the battery compartment on a submarine?",
        "text": """What was the battery compartment on a submarine?

Fleet submarines like the Pampanito had two battery compartments — the forward battery and the after battery — located in the lower hull, directly beneath the berthing areas. Each compartment held 126 large lead-acid battery cells, for a total of 252 cells in the whole boat.

Each cell was enormous — about the size of a large trunk and weighing over 1,600 pounds. The full battery system weighed hundreds of tons and provided the electric power to run the main motors when the submarine was submerged. The batteries were recharged every time the submarine surfaced and ran the diesels. Battery capacity determined how long the submarine could stay submerged — typically 24 to 48 hours at slow speed before the batteries were exhausted and the boat had to surface to run the diesels and recharge."""
    },
]

# Read existing entries
with open(CORPUS, "r", encoding="utf-8") as f:
    lines = [l.strip() for l in f if l.strip()]

existing_ids = set()
for line in lines:
    try:
        obj = json.loads(line)
        if obj.get("chunk_id"):
            existing_ids.add(obj["chunk_id"])
    except Exception:
        pass

added = 0
with open(CORPUS, "a", encoding="utf-8") as f:
    for faq in NEW_FAQS:
        if faq["chunk_id"] in existing_ids:
            print(f"SKIP {faq['chunk_id']} (already exists)")
            continue
        f.write(json.dumps(faq, ensure_ascii=False) + "\n")
        print(f"ADD  {faq['chunk_id']}: {faq['title']}")
        added += 1

print(f"\nAdded {added} entries.")
