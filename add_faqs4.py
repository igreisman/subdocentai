#!/usr/bin/env python3
"""Add pam_088-104 to dieselsubs_faq_corpus.jsonl"""
import json

CORPUS = "corpora/dieselsubs_faq_corpus.jsonl"

NEW_FAQS = [
    {
        "chunk_id": "pam_088",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What kind of food did the crew eat on a submarine?",
        "text": """What kind of food did the crew eat on a submarine?

Submarine crews ate surprisingly well — better than almost anyone else in the Navy. Because the boats had no room to carry large quantities of food, they had to turn around after a limited number of days, and the Navy compensated with high-quality rations and a $1.25-per-day subsistence bonus called "submarine pay."

At the start of a patrol, fresh food was plentiful: steaks, eggs, fresh vegetables, ice cream, and bread baked aboard. Sailors on submarines often ate steak for breakfast. As the patrol stretched toward six or eight weeks, fresh food ran out and the menu shifted to canned goods, powdered eggs, and preserved meats — still decent by wartime standards. The cook was one of the most important men on the boat; good food was crucial for morale. In the tight, stressful world of a submarine, a good meal was one of the few pleasures available."""
    },
    {
        "chunk_id": "pam_089",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was a submarine tender?",
        "text": """What was a submarine tender?

A submarine tender was a large support ship designed to service and resupply a fleet of submarines. Tenders carried spare parts, torpedoes, food, fuel, repair equipment, and even recreational facilities. When submarines returned from patrol, they tied up alongside the tender rather than going all the way back to a shore base for routine maintenance.

The tender's crew included machinists, electricians, torpedo technicians, and medical personnel who could overhaul engines, repair hydraulics, reload torpedoes, and treat injured sailors. Living conditions on the tender were also much better than aboard a submarine — it was a welcome break. Key submarine tenders in the Pacific included USS Fulton, USS Holland, and USS Sperry. Tenders were vital to keeping submarines operational far from home ports, especially as bases moved forward toward Japan."""
    },
    {
        "chunk_id": "pam_090",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What does the SS in USS Pampanito SS-383 stand for?",
        "text": """What does the SS in USS Pampanito SS-383 stand for?

The designation "SS" stands for "Submarine, Submersible" — the official US Navy hull classification for a conventional, diesel-electric attack submarine. The number 383 is Pampanito's hull number, assigned in the order submarines were authorized by Congress. USS Pampanito (SS-383) was the 383rd submarine authorized for construction, though it was not the 383rd built.

USS stands for "United States Ship." The "Pampanito" name comes from a type of Pacific Ocean fish — the pompano. Most American fleet submarines of World War II were named after fish. The SS designation distinguished conventional submarines from other underwater vessels like SSK (hunter-killer submarines) and SSBN (ballistic missile submarines) that appeared later in naval history."""
    },
    {
        "chunk_id": "pam_091",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did the crew identify the survivors as Allied prisoners?",
        "text": """How did the crew identify the survivors as Allied prisoners?

When the Pampanito and other submarines in the wolf pack realized they had been shooting at Japanese ships carrying Allied prisoners of war, the situation was horrifying. The initial attack on September 12, 1944 sank the Rakuyo Maru and Kachidoki Maru — Japanese ships that, unknown to the Americans, were transporting hundreds of British and Australian POWs captured in Singapore.

The crew first noticed the survivors were white men — a shocking sight in Pacific waters. As they were pulled aboard, the POWs identified themselves in English. Many wore rags or nothing at all after days in the water under a tropical sun. They were desperately weak, covered in oil, and barely alive. The Pampanito rescued 73 men; together with the submarine USS Sealion, which also turned back, a total of 159 POWs were saved. The Rakuyo Maru alone had been carrying about 1,300 prisoners; most were lost."""
    },
    {
        "chunk_id": "pam_092",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Were there doctors on submarines?",
        "text": """Were there doctors on submarines?

No. Fleet submarines did not carry a medical doctor. Medical care was provided by a Pharmacist's Mate — an enlisted man trained as a Navy corpsman, equivalent to a medic or paramedic today. The Pharmacist's Mate had a medical kit and some training, but was not a physician.

The Pharmacist's Mate was responsible for treating injuries, infections, dental emergencies, appendicitis, and any other medical crises that arose at sea. One famous case became part of submarine lore: in 1942, Pharmacist's Mate Wheeler "Wahoo" Lipes performed an emergency appendectomy on a sailor aboard USS Seadragon using the ship's wardroom table, improvised instruments, and ether as anesthesia. The patient survived. Such episodes highlighted both the limitations of submarine medical care and the resourcefulness of the men who served."""
    },
    {
        "chunk_id": "pam_093",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was submarine school and where was it?",
        "text": """What was submarine school and where was it?

The Naval Submarine School was — and still is — located in Groton, Connecticut, at the Naval Submarine Base New London, which despite its name is actually in Groton across the Thames River from New London. It has been the primary training center for US Navy submariners since 1916.

During World War II, candidates first had to complete basic Navy training, then volunteer and pass psychological and physical screening for submarine duty. Submarine school lasted about 12 weeks and covered diving procedures, torpedo operations, damage control, and every system on the boat. Graduates were assigned to submarines as qualified candidates — but the real training continued on the boat itself, where a sailor had to demonstrate competency in every compartment to earn his Dolphins pin. The submarine Dolphins — a qualification badge — could take six months to a year to earn after reporting to a boat."""
    },
    {
        "chunk_id": "pam_094",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the SJ radar and how did radar work on a WWII submarine?",
        "text": """What was the SJ radar and how did radar work on a WWII submarine?

The SJ radar was a surface-search radar introduced on US fleet submarines in 1942 and was one of the most important technological advantages American submarines had in the Pacific. The SJ stood for the Submarine-model J radar set. It transmitted microwave pulses from a rotating antenna on the periscope shears and detected the reflected echoes from ships or coastlines.

The SJ radar was revolutionary because it allowed submarines to find and track targets on the surface at night or in poor visibility — ranges up to 15 miles for large ships. Before radar, submarines had to rely entirely on lookouts, making night attacks much more dangerous and difficult. The radar allowed the Pampanito and other fleet submarines to stalk convoys in complete darkness, approach to firing range, attack, and escape before the enemy could locate them. An improved SD radar was used for air search — detecting aircraft — to give the submarine time to dive before a plane could reach attack position."""
    },
    {
        "chunk_id": "pam_095",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did submarines help win the war?",
        "text": """How did submarines help win the war?

US submarines played a decisive role in winning the war in the Pacific. Although submarines made up less than 2% of US Navy personnel, they sank approximately 55% of all Japanese shipping destroyed during the war — including 214 warships and over 1,100 merchant vessels.

Japan was an island nation almost entirely dependent on imports of oil, food, steel, and raw materials. As US submarines systematically destroyed Japanese merchant shipping, the Japanese war machine slowly starved. By 1945 Japan's tanker fleet was almost wiped out, fuel was critically short, pilots couldn't be trained because there was no aviation gasoline, ships couldn't move, and factories couldn't produce weapons. The submarine campaign against Japanese shipping was arguably the single most decisive factor shortening the Pacific war. Some historians compare it to the German U-boat campaign against Britain — but unlike Germany, the United States succeeded."""
    },
    {
        "chunk_id": "pam_096",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did submarines receive their patrol assignments?",
        "text": """How did submarines receive their patrol assignments?

Patrol assignments came from Commander Submarine Force Pacific Fleet — called ComSubPac — located at Pearl Harbor. Intelligence from codebreakers (who had broken Japanese naval codes), aerial reconnaissance, and reports from other submarines all fed into a detailed picture of Japanese convoy routes and schedules.

ComSubPac assigned each submarine a geographic patrol zone — a specific area of ocean where Japanese shipping was expected. The boat's captain received sealed orders that were opened only after leaving port. Radio communication during the patrol was one-way where possible — submarines received messages but rarely transmitted, to avoid giving away their position. If a submarine found a convoy or important target outside its assigned zone, it could pursue and attack at the captain's discretion. After the patrol, the captain filed a detailed patrol report, which was used to evaluate performance and plan future assignments."""
    },
    {
        "chunk_id": "pam_097",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Was the Pampanito ever damaged in combat?",
        "text": """Was the Pampanito ever damaged in combat?

The Pampanito experienced several close calls but was never seriously damaged. Like all submarines operating in Japanese waters, she was subjected to depth-charge attacks by enemy destroyers and patrol craft. Depth charges exploding nearby could crack gauges, pop light bulbs, rupture pipes, and rattle the crew badly, but no direct structural damage to the Pampanito was recorded in her patrol reports.

The Pampanito did experience mine threats during operations in waters that Japan had heavily mined, and encountered enemy aircraft that required emergency dives. The crew also had to navigate through areas with strong currents, shallow water, and enemy-swept channels. That the Pampanito completed all six war patrols and returned safely every time was a reflection of skilled seamanship, good luck, and the professionalism of her crew. 52 American submarines were lost during the war — making every safe return significant."""
    },
    {
        "chunk_id": "pam_098",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the Pampanito doing at the end of the war?",
        "text": """What was the Pampanito doing at the end of the war?

When Japan surrendered in August 1945, the Pampanito was stateside undergoing a refit and overhaul at Mare Island Naval Shipyard in Vallejo, California, preparing for what would have been her seventh war patrol. The news of Japan's surrender reached the crew while the boat was still in the shipyard — they would not need to go back to the Pacific.

After the surrender, many submarines were sent to Japan to participate in the formal occupation. The Pampanito was instead decommissioned in 1946 and placed in reserve at Mare Island. She sat in the reserve fleet for years while the Navy decided what to do with its large surplus of WWII-era submarines. Eventually she was transferred to the city of San Francisco, where she opened as a museum ship at Pier 45, Fisherman's Wharf in 1982. She is one of only four surviving Balao-class submarines open to the public."""
    },
    {
        "chunk_id": "pam_099",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How did the Pampanito become a museum ship?",
        "text": """How did the Pampanito become a museum ship?

After decommissioning in 1946, the Pampanito sat in reserve at Mare Island for decades. In 1976 she was struck from the Naval Vessel Register, and in 1978 she was transferred to the National Maritime Museum Association (now the San Francisco Maritime National Historical Park) for preservation as a museum ship.

The Pampanito was towed to San Francisco and opened to the public on July 4, 1982, at Pier 45, Fisherman's Wharf. A nonprofit organization, the Maritime Park Association, manages the boat and funds her preservation. Restoring and maintaining a 75-year-old submarine is a constant challenge — the salt air, seawater, and age are always working against the volunteers and staff who keep her seaworthy. The Pampanito was designated a National Historic Landmark in 1986, recognizing her importance as a surviving example of WWII naval history."""
    },
    {
        "chunk_id": "pam_100",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the commissioning of a submarine?",
        "text": """What was the commissioning of a submarine?

Commissioning was the ceremony at which a Navy ship officially entered active service. The shipbuilder formally delivered the submarine to the Navy, a commanding officer took command, and the crew formally "manned the ship." The commissioning ceremony included the reading of orders, the playing of the national anthem, and often a speech by a senior officer.

From that moment, the ship became a US Navy vessel and the crew had official military status aboard her. The Pampanito was commissioned on November 6, 1943, at Portsmouth, New Hampshire, after being built at the Portsmouth Naval Shipyard. The commissioning was the end of the building process and the beginning of the boat's service life. Decommissioning — the opposite ceremony — takes the ship out of active service."""
    },
    {
        "chunk_id": "pam_101",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How long can a submarine stay submerged?",
        "text": """How long can a submarine stay submerged?

A WWII fleet submarine's submerged endurance was determined by battery capacity. Moving at 2 knots (barely creeping), the batteries on a Balao-class submarine could last roughly 48 hours. At higher speeds the batteries drained much faster — at maximum speed of about 8-9 knots submerged, batteries lasted only about an hour.

In practice, submarines rarely stayed down for more than 24 hours. The battery had to be recharged by surfacing and running the diesels, which required access to air. Additionally, CO2 built up in the air after extended submersion, and oxygen was slowly depleted, making breathing increasingly difficult. Chemical canisters could absorb some CO2 and oxygen could be bled in from tanks, but these were limited. In extreme cases during depth charge attacks, crews endured 30+ hours submerged before surfacing was safe. The record during the war was reportedly over 40 hours submerged in an emergency situation."""
    },
    {
        "chunk_id": "pam_102",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "Were there discipline problems on submarines?",
        "text": """Were there discipline problems on submarines?

Serious discipline problems were rare on submarines, partly because the selection process screened out men who showed behavioral issues, and partly because the close quarters meant that troublemakers made life miserable for everyone. There were no mutinies recorded on US WWII submarines.

Minor discipline issues — arguments, petty theft, insubordination — certainly happened. A captain on a submarine had nearly absolute authority at sea and could confine a man to the boat or restrict privileges. However, the culture on submarines was also more informal than on surface ships. Officers and men ate together, worked in close proximity, and depended on each other for survival. This mutual dependence usually created strong unit cohesion rather than resentment. When serious problems did arise, they were typically handled administratively when the boat returned to port."""
    },
    {
        "chunk_id": "pam_103",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "What was the Pacific Fleet submarine strategy in WWII?",
        "text": """What was the Pacific Fleet submarine strategy in WWII?

The core US submarine strategy in the Pacific was unrestricted submarine warfare — attacking all Japanese shipping without warning. This was in sharp contrast to prewar international law (which required warning before sinking merchant ships), but the Navy Department authorized unrestricted submarine warfare on December 8, 1941, the day after Pearl Harbor.

The strategic goal was to cut off Japan from the raw materials its economy required: oil from the Dutch East Indies, rubber from Malaya, steel from China, rice from Southeast Asia. Without these imports, Japan's military machine would grind to a halt. Submarine forces were organized into wolf packs that could coordinate attacks on convoys, and patrol zones were assigned based on Ultra intelligence — decoded Japanese naval communications — that told commanders exactly where convoys would be. The strategy worked: by 1944, Japanese oil imports were less than a third of pre-war levels, crippling their war effort."""
    },
    {
        "chunk_id": "pam_104",
        "doc_type": "dieselsubs_faq",
        "source": "dieselsubs_faq",
        "display_citation": "DieselSubs FAQ",
        "title": "How was the Pampanito resupplied during a patrol?",
        "text": """How was the Pampanito resupplied during a patrol?

During a war patrol, the Pampanito was on her own — there was no mid-patrol resupply. Everything the crew needed for 45-75 days had to be loaded before departure: food, torpedoes, fuel, spare parts, and medical supplies. The crew loaded as much as physically possible into every available space — under bunks, in passageways, in torpedo rooms, and in every storage locker.

Occasionally a submarine could transfer torpedoes from a submarine tender if one was operating nearby — but this was rare and difficult in open water. The primary means of between-patrol resupply was the return to a submarine base or tender, where the boat was completely restocked over two to three days. The Pampanito operated primarily from Pearl Harbor and later from Guam, where forward-positioned tenders provided fuel, food, torpedoes, and repair services between each of her six war patrols."""
    },
]

# Check for duplicates and append
with open(CORPUS, "r", encoding="utf-8") as f:
    existing_ids = {json.loads(l).get("chunk_id") for l in f if l.strip()}

added = 0
with open(CORPUS, "a", encoding="utf-8") as f:
    for faq in NEW_FAQS:
        if faq["chunk_id"] in existing_ids:
            print(f"SKIP {faq['chunk_id']} (already exists)")
            continue
        f.write(json.dumps(faq, ensure_ascii=False) + "\n")
        print(f"ADD  {faq['chunk_id']}: {faq['title']}")
        added += 1

print(f"\nAdded {added} entries. Total lines: ", end="")
import subprocess
result = subprocess.run(["wc", "-l", CORPUS], capture_output=True, text=True)
print(result.stdout.strip())
