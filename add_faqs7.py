"""Add batch 9 FAQs (pam_156-176) to the corpus."""
import json

NEW_FAQS = [

{
"chunk_id": "pam_156",
"title": "What was the control room used for on a submarine?",
"text": """What was the control room used for on a submarine?

The control room was the nerve center of the submarine — the space from which the boat was dived, surfaced, and steered. It was located amidships, directly below the conning tower. While the conning tower handled periscope observations and fire control during attacks, the control room handled the mechanical business of controlling the submarine's depth, trim, and position.

Key equipment in the control room included: the helm (steering wheel) for controlling the submarine's course, the bow plane and stern plane controls for adjusting depth, the ballast tank controls (flood and blow valves), the diving officer's station, and the Christmas Tree — a panel of red and green indicator lights showing whether every hull opening (hatches, torpedo tube outer doors, ventilation valves) was open (red) or shut (green). Before diving, the diving officer needed all green lights — "green board" meant safe to submerge.

The diving officer supervised the control room team, constantly adjusting trim by transferring water between tanks to keep the submarine level at the ordered depth. It was demanding, precise work: a poorly trimmed submarine in a combat situation could cost seconds that meant the difference between escaping and being sunk. The executive officer (XO) often stationed himself in the control room during battle stations while the captain used the periscope in the conning tower above."""
},

{
"chunk_id": "pam_157",
"title": "What did the forward torpedo room look like?",
"text": """What did the forward torpedo room look like?

The forward torpedo room was in the bow of the submarine, and it was both a weapons magazine and a crew berthing space. Six torpedo tubes were built into the forward bulkhead, each 21 inches in diameter and about 25 feet long. The tubes pointed forward and could be aimed only by steering the entire submarine toward the target.

Spare torpedoes — typically six to eight reloads — rested on heavy steel skids on the deck and in overhead racks. Each torpedo weighed over 3,000 pounds and was nearly 21 feet long. Handling these weapons in the confined space required a specialized team, and torpedo reloads at sea were slow, dangerous work done by men using chain hoists, rollers, and muscle power.

A small number of the crew (typically 8-10 men) bunked in the forward torpedo room. Their racks were mounted between and above the torpedo skids. This meant enlisted torpedomen slept inches from live warheads. When torpedoes were loaded or fired, the men working in the room had to navigate around each other in a space with almost no free floor area. Despite the cramped conditions, the torpedo room crew took great pride in their weapons and their ability to load and fire rapidly under pressure."""
},

{
"chunk_id": "pam_158",
"title": "How did the crew dispose of garbage on a submarine?",
"text": """How did the crew dispose of garbage on a submarine?

Garbage disposal on a WWII submarine was a serious operational concern — not just a matter of cleanliness, but of tactical security. Any garbage or oil floating on the surface could reveal a submarine's position to enemy aircraft or ships.

Fleet submarines used a "garbage disposal unit" (GDU), also called the "Hanson" launcher — a dedicated tube that allowed garbage sealed inside weighted metal cans to be ejected from the submarine while submerged or on the surface. The can sank, taking the garbage to the bottom. This was the standard procedure while in enemy waters: all garbage was carefully collected, packed into the cans with sufficient weight to sink, and ejected through the GDU.

The crew also had strict policies against throwing any loose material over the side in enemy waters — no coffee grounds, food scraps, or waste paper. Even small amounts of floating debris could become a trail leading enemy forces to the boat or revealing that a submarine had recently been in the area. Oil leaks were another concern; a sheen of diesel fuel on the surface was a telltale sign that a submarine had been forced deep, and crews worked hard to fix any external leaks quickly."""
},

{
"chunk_id": "pam_159",
"title": "What happened to enemy survivors after a submarine attack?",
"text": """What happened to enemy survivors after a submarine attack?

The policy for US submarines regarding enemy survivors was difficult and evolved during the war. The official position was generally that submarines should not stop to rescue enemy sailors from sinking ships — the danger of remaining on the surface near a burning or sinking vessel, with the risk of anti-submarine aircraft or escorts arriving, was too great. Submarines were the most irreplaceable and strategically valuable assets in the Pacific Fleet; losing one to rescue enemy survivors was considered unacceptable.

In practice, some submarine commanders did have their boats approach survivors briefly to ask about the nature of their cargo, the names of their vessels, or to take a prisoner for intelligence purposes. Others fired warning shots to alert survivors to lifeboats. But picking up large numbers of enemy survivors was not generally done.

This was in sharp contrast to Pampanito's famous rescue of Allied POWs in September 1944. When the Pampanito and Sealion sank the Japanese convoy carrying British and Australian prisoners, US submarine command authorized the submarines to break from mission and rescue all survivors they could find — precisely because these were Allied servicemen, not enemies. The rescue of 127 POWs was an extraordinary act in a war when combat necessity normally prevented any rescue operations."""
},

{
"chunk_id": "pam_160",
"title": "How did submarines handle fires or flooding emergencies?",
"text": """How did submarines handle fires or flooding emergencies?

Fire and flooding were among the most feared emergencies on a submarine. In a sealed pressure hull with no escape routes while submerged, either could be fatal within minutes. Submarine crews drilled emergency procedures constantly.

For flooding, the first response was to isolate the affected compartment by closing the watertight doors — heavy steel hatches that could be dogged shut to contain flooding to one section of the boat. Pumps were activated to dewater the compartment if possible. If flooding was severe, the captain had to decide whether to surface immediately (dangerous in enemy waters) or attempt to control the flooding while submerged. Emergency surfacing was always possible by blowing all ballast tanks, but this exposed the submarine on the surface.

Fire on a submerged submarine was equally dangerous because burning consumes oxygen and generates toxic gases in an enclosed space. CO2 fire extinguishers were the primary tool, backed by Aquafoam for electrical fires. Crew members wore EABs (Emergency Air Breathers) — small chemical oxygen sets that provided a few minutes of clean air. The electrical and fuel systems presented the greatest fire risks. Several US submarines were lost or nearly lost to battery explosions and fires caused by seawater flooding into battery compartments and generating hydrogen gas or chlorine gas — one of the most dangerous scenarios the crew could face."""
},

{
"chunk_id": "pam_161",
"title": "What was a periscope feather?",
"text": """What was a periscope feather?

A periscope feather was the small white wake — a V-shaped bow wave — created on the surface of the ocean when a submarine's periscope was raised while the boat was moving at periscope depth. The periscope head, typically only 1.5 to 2 inches in diameter, would push against the water as the submarine moved forward, creating a small spray or ripple on the surface.

The feather was a serious tactical concern. A trained lookout on an enemy ship or an aircraft crew scanning the ocean could spot a periscope feather at considerable distance, especially in calm seas. Once spotted, the feather immediately revealed the submarine's position, course, and approximate speed.

Experienced submarine captains minimized feather exposure by: limiting periscope observation to brief "looks" — raising the scope for only a few seconds at a time; slowing the submarine to the minimum steerage speed (typically 3-4 knots) before raising the scope, which reduced the feather size; avoiding periscope observations in calm, flat seas when the feather was most visible; and keeping the periscope as low as possible, with only the very tip above the surface. The standard operating technique was called "a quick sweep" — up for a few seconds, a rapid 360-degree scan, then back down. A captain who kept his scope up too long in enemy waters was making himself easy to find."""
},

{
"chunk_id": "pam_162",
"title": "How did the crew deal with boredom on a long patrol?",
"text": """How did the crew deal with boredom on a long patrol?

A 60-75 day war patrol involved long stretches of routine — transiting to the patrol area, hours of waiting for contacts, and repeated watch cycles. Boredom and monotony were real challenges for crew morale, and submarine commanders took them seriously.

The crew's mess was the social center of the submarine. Card games (cribbage, pinochle, acey-deucy) ran almost continuously. Many boats had a small library of paperback books that circulated through the crew. Some submarines carried board games, and a few men played chess. Movies were shown on some boats using a small 16mm projector — a reel might be watched dozens of times over a patrol.

Food was a major morale booster. Submarine crews ate better than any other branch of the Navy: fresh food was loaded for the first two weeks, supplemented by an extraordinary range of canned goods, frozen meats, and freshly-baked bread. The cook was one of the most important men aboard for morale purposes.

Practical jokes were common — submarine culture was intensely informal compared to surface ships, and hazing/humor kept men loose. Some men spent free hours writing letters (to be mailed when they returned to port), reading, sleeping, or maintaining their equipment beyond what was required. The constant underlying tension of operating in enemy waters, paradoxically, made the quiet moments more valuable rather than less."""
},

{
"chunk_id": "pam_163",
"title": "What was the role of the TDC operator on a submarine?",
"text": """What was the role of the TDC operator on a submarine?

The TDC (Torpedo Data Computer) operator, typically a senior torpedoman or fire control officer, was one of the most critical positions during a torpedo attack. The TDC was an electromechanical analog computer that continuously calculated the firing solution — the gyro angle setting to be transmitted to each torpedo so it would arrive at the target's predicted position.

The TDC operator maintained the attack solution by constantly entering updated data from the captain's periscope observations: target bearing, estimated target angle on the bow (the angle between the target's course and the line of sight to the sub), estimated range, and estimated target speed. The TDC automatically solved the geometry of the intercept problem and set the torpedo gyro angles.

The operator had to track multiple inputs simultaneously: updating bearing from the captain's calls ("mark" each time the periscope was on target), reading the target's course from the bearing rate, and confirming that the firing solution made sense. If the TDC's solution diverged from what the captain was seeing, the operator had to quickly diagnose the discrepancy and correct it — often while the attack was already underway. A bad TDC solution meant torpedoes that missed. The Torpedo Data Computer and its skilled operator were what separated a successful attack from a waste of expensive weapons and a potentially fatal exposure of the submarine's position."""
},

{
"chunk_id": "pam_164",
"title": "What happened if a submarine ran aground?",
"text": """What happened if a submarine ran aground?

Running aground was a nightmare scenario for any submarine commander — it immobilized the boat, made it vulnerable to enemy attack, and was often the precursor to the loss of the vessel. Groundings were most likely in restricted, poorly-charted waters such as harbor approaches, shallow coastal areas, or island passages where navigation was difficult and bottom depth could change rapidly.

When a submarine ran aground, the first priority was to free it. The captain would order emergency ballast blowing, all engines to full power in reverse, and crew members shifting aft to change the trim. If the boat had gone hard aground, pumping out all ballast and variable tanks to reduce weight was tried. In some cases, a submarine could back itself off a grounding with engine power alone; in others, it remained fast.

The situation became desperate quickly. A stationary submarine visible from the surface or detectable as an anomaly on sonar was highly vulnerable to air and surface attack. If enemy forces arrived before the sub could free itself, the captain faced the impossible choice of surrendering the boat (against all orders and tradition) or scuttling. Several submarines were lost in circumstances involving groundings. USS Grunion (SS-216) disappeared in 1942 in shallow Alaskan waters under circumstances that may have involved a grounding or a circular-running torpedo. Navigation in restricted waters was taken extremely seriously, and captains were generally cautious about transiting poorly-charted areas."""
},

{
"chunk_id": "pam_165",
"title": "What did a Japanese convoy look like?",
"text": """What did a Japanese convoy look like?

A Japanese convoy typically consisted of merchant ships — freighters, tankers, and troop transports — traveling in formation, escorted by naval vessels tasked with anti-submarine defense. The size varied enormously: small coastal convoys might have 3-5 ships with 1-2 escorts, while major strategic convoys could have 10-20 or more merchant vessels with multiple destroyer escorts, submarine chasers, and occasionally air cover.

The convoy formation was usually several columns of merchant ships, with escort vessels positioned ahead, on the flanks, and astern. The escorts would zigzag and conduct active sonar searches while the merchants maintained a fairly steady course. Japan's convoy system was poorly organized early in the war — ships often sailed independently, without escort, making them easy prey. As the war progressed and losses mounted, Japan improved its escort doctrine and convoy organization, which made US submarine attacks more dangerous and complicated.

From a submarine commander's perspective, attacking a convoy required threading between or around the escorts to get a shooting position on the high-value targets (large tankers and troop transports were the priority). After firing torpedoes, the submarine had to evade the inevitable counter-attack by the surviving escorts, who would immediately attack the submarine's last known position with depth charges. The Pampanito attacked convoys on her third, fourth, and fifth war patrols, contributing to the destruction that steadily throttled Japan's ability to supply its far-flung empire."""
},

{
"chunk_id": "pam_166",
"title": "How did the Pampanito earn her battle stars?",
"text": """How did the Pampanito earn her battle stars?

USS Pampanito (SS-383) earned six battle stars during World War II — one for each of her six official war patrols, all six of which were designated as "successful" combat patrols.

Her most significant achievements came on the third and fifth patrols. On the third patrol (August–September 1944), Pampanito was part of a coordinated attack group with USS Sealion and USS Growler that attacked a major Japanese convoy carrying Allied POWs. The group sank multiple ships including the passenger-cargo vessel Rakuyo Maru and the tanker Zuiho Maru. After the attack, Pampanito returned to rescue 73 British and Australian prisoners of war — the largest number of POWs rescued by a US submarine in the Pacific War.

Over her six patrols, Pampanito was officially credited with sinking five Japanese ships and damaging others, contributing to the systematic destruction of Japanese merchant shipping that strangled Japan's ability to supply its empire. She operated in some of the most dangerous waters in the Pacific, including the South China Sea and the waters around Japan itself. The six battle stars reflect not just confirmed sinkings, but the full scope of her combat operations — torpedo attacks, convoy interdiction, and the extraordinary mercy mission that followed her most dangerous patrol."""
},

{
"chunk_id": "pam_167",
"title": "What was the flying bridge on a submarine?",
"text": """What was the flying bridge on a submarine?

The "flying bridge" on a fleet submarine referred to the open platform at the very top of the conning tower fairwater (the streamlined structure built around the periscope shears), above the main bridge level. In some usages, "bridge" referred to the entire open top of the conning tower fairwater; the "flying bridge" was the highest platform, giving the officers and lookouts the maximum height above the water for better visibility.

On the main bridge, the officer of the deck (OOD) conn'd the submarine on the surface — giving orders for course, speed, and diving. Lookouts were stationed in the periscope shears or on the bridge wings, scanning the horizon with binoculars in all directions. On Pampanito and similar Balao-class submarines, the bridge was equipped with a compass repeater, engine order telegraphs, and communication to the conning tower below via voice tube or sound-powered telephone.

Bridge watches on the surface were wet, cold, and uncomfortable in rough weather — the bridge was open to the sea, and spray regularly soaked the watch standers. Rain, wind, and darkness made four-hour watches exhausting. When a dive was ordered, the bridge watch was the last to leave — the OOD was required to visually confirm all lookouts were below before dropping down the hatch himself, pulling it shut behind him as the boat went under."""
},

{
"chunk_id": "pam_168",
"title": "How deep could the Pampanito dive?",
"text": """How deep could the Pampanito dive?

USS Pampanito is a Balao-class submarine. The Balao class had an official test depth of 400 feet — the depth to which the submarine was certified safe by the Navy. In practice, Balao-class submarines could (and sometimes did) go significantly deeper than 400 feet in emergencies, though the risk of hull failure increased with every foot below test depth.

The improvement over the earlier Gato class (test depth 300 feet) was achieved by using higher-yield steel (HY-42 steel) in the pressure hull construction. This extra hundred feet of diving depth was operationally important: it allowed Balao-class submarines to dive below the set depth of many Japanese depth charges, which were often preset by the attacking destroyer crew before the run and couldn't be changed mid-attack.

The "crush depth" — the depth at which the hull would actually implode — was estimated at roughly twice the test depth, meaning around 800 feet, though this was never tested deliberately. In reality, any submarine diving well past its test depth was gambling with the lives of its crew. The depth gauge, the groaning of the hull under compression, and the sound of leaking fittings were constant reminders during deep dives of exactly how thin the steel walls were between the crew and instant death at the bottom of the Pacific."""
},

{
"chunk_id": "pam_169",
"title": "What was the magnetic exploder problem with US torpedoes?",
"text": """What was the magnetic exploder problem with US torpedoes?

The magnetic exploder (called the Mark 6 exploder) was one of the worst weapons failures in US naval history, and it cost the lives of many American submariners who attacked ships and got no results in the first two years of the war.

The concept was clever: instead of requiring a direct contact hit, the torpedo's magnetic influence exploder would detect the magnetic signature of an enemy ship's hull and detonate beneath it, breaking the keel with a massive water hammer effect — far more destructive than a simple hull puncture. The weapon was so secret it was not adequately tested before the war.

In actual combat, the Mark 6 failed in multiple ways. The exploder was set too sensitively and detonated prematurely (before reaching the target), or failed to detonate at all due to manufacturing tolerances, magnetic anomalies in tropical waters, or simple design flaws. Submarine commanders reported torpedo after torpedo running hot, straight and normal — striking an enemy ship and failing to explode. These were called "duds." The Bureau of Ordnance initially blamed the submarine commanders for poor targeting, an infuriating accusation that delayed fixing the problem. Admiral Lockwood, Commander Submarines Pacific, eventually ran direct tests in Hawaii and confirmed the defects. The magnetic exploder was officially deactivated in 1943, and the simpler contact exploder replaced it — but not before the confidence, morale, and tactical results of the entire submarine force had suffered for nearly two years."""
},

{
"chunk_id": "pam_170",
"title": "Who was the most successful US submarine commander of WWII?",
"text": """Who was the most successful US submarine commander of WWII?

By official postwar damage assessments (JANAC — Joint Army-Navy Assessment Committee), Commander Dudley W. "Mush" Morton in USS Wahoo (SS-238) is often cited as one of the most aggressive and legendary submarine commanders of the war, though the records for confirmed tonnage sunk are held by others.

By total tonnage officially credited, Commander Richard H. O'Kane in USS Tang (SS-306) is generally considered the top US submarine ace of WWII, credited with sinking 24 ships totaling approximately 93,824 tons. O'Kane had previously served as Morton's executive officer aboard Wahoo, and brought that aggressive style to his own command. He was captured after USS Tang was sunk by one of her own circular-running torpedoes in 1944, survived a Japanese prison camp, and received the Medal of Honor.

Other top-credit commanders included Eugene Fluckey (USS Barb), Samuel Dealey (USS Harder — known as "The Destroyer Killer"), and Slade Cutter (USS Seahorse). These men shared a common characteristic: extreme aggressiveness in pressing attacks at close range, tenacity in following convoys despite counterattacks, and a willingness to accept risk that less decorated commanders avoided. The submarine force as a whole, however — not individual commanders — is credited with sinking over 55% of all Japanese shipping lost during the war."""
},

{
"chunk_id": "pam_171",
"title": "How did the crew celebrate after a successful attack?",
"text": """How did the crew celebrate after a successful attack?

After a successful torpedo attack and the subsequent evasion of the inevitable depth charge response, submarine crews celebrated in ways appropriate to their confined circumstances. The first celebration was often simply survival — enduring a depth charge attack and emerging undamaged was itself worthy of relief bordering on elation.

When the danger had passed and the boat was clear, the cook would be called upon to prepare a special meal — something more elaborate than the routine fare. Ships that had sunk multiple vessels in a single patrol sometimes had a modest "victory dinner." The captain might pass the word through the boat with a brief announcement of the results, and the crew's mess would buzz with men comparing notes on what they'd heard — the explosion sounds, the secondary detonations, the sounds of a ship breaking up on the sonar.

Officers sometimes kept a running tally of ships sunk — some boats displayed pennants or flags on their periscope shears representing confirmed kills when they entered port. In port, the real celebration began: liberty in Pearl Harbor (or later Guam, Midway, or other advance bases), food, alcohol, and rest. Submarine sailors in port were known for their enthusiasm — they had money accumulated over a patrol (submarine duty pay was a premium), they were alive when many of their comrades had not come back, and they had roughly two weeks before the next patrol began."""
},

{
"chunk_id": "pam_172",
"title": "What did submariners do when they returned to port after a patrol?",
"text": """What did submariners do when they returned to port after a patrol?

Returning to port after a 60-75 day war patrol was one of the most anticipated moments in a submariner's life. The first order of business after tying up at the submarine base was a medical inspection and rest. The crew was typically sent to a rest facility — in Pearl Harbor, this was the Royal Hawaiian Hotel, which the Navy had leased for submarine rest and recreation. The "Pink Palace" on Waikiki Beach became legendary among submariners: two weeks of the finest available food, beachside rest, swimming, and whatever recreation the men chose.

During the rest period, the submarine itself was turned over entirely to the relief crew — a permanent yard crew that handled repairs, maintenance, torpedo reload, provisioning, and any upgrades ordered by submarine command. The regular crew did essentially nothing related to their submarine during this period, by design.

The captain and XO were busy during the rest period: writing and submitting the patrol report, meeting with submarine command staff for debrief, receiving intelligence for the next patrol, and processing promotions, decorations, and disciplinary matters from the patrol. When the rest period ended, returning crew members were expected to be ready — physically recovered, mentally reset, and prepared for another two months in enemy waters. The knowledge that each patrol might be the last provided an intensity to the liberty period that peacetime shore leave never matched."""
},

{
"chunk_id": "pam_173",
"title": "Why were submarines called the Silent Service?",
"text": """Why were submarines called the Silent Service?

"The Silent Service" was the popular nickname for the US submarine force in World War II, and it reflected two distinct characteristics of submarine operations.

The first was tactical: submarines operated by stealth and silence. They hunted while running as quietly as possible, avoided detection by minimizing machinery noise, and executed their attacks without warning. The silence of a submarine's approach — a vessel that could kill from an invisible position — was one of its defining tactical qualities.

The second meaning was institutional: during the war, the submarine service deliberately suppressed information about its operations. Unlike the surface Navy or the Army Air Forces, which publicized their battles and celebrated their victories with press coverage and public fanfare, submarine operations were kept secret. The locations of patrols, the names of ships sunk, even the names of submarine commanders were kept out of the newspapers. The reasons were operational security — telling the enemy which shipping routes were being interdicted would allow them to divert convoys — and also to protect code-breaking intelligence. If Japan knew that certain convoys were being targeted based on decoded radio traffic, it would suspect its codes were broken.

As a result, submariners returned from patrols that had devastated Japanese shipping and received almost no public recognition. The men who served in the Silent Service did so knowing that their extraordinary courage and sacrifice would go largely unacknowledged until long after the war ended."""
},

{
"chunk_id": "pam_174",
"title": "How did submarine construction change during the war?",
"text": """How did submarine construction change during the war?

The US submarine construction program underwent a massive acceleration during World War II. Before the war, submarines were built in small numbers at a measured pace — a single fleet submarine took 18-24 months or more from keel-laying to commissioning. After Pearl Harbor, the Navy and shipyards restructured everything to build faster.

Construction time dropped dramatically: by mid-war, some fleet submarines were being commissioned in as little as 12-15 months. Shipyards like Portsmouth Naval Shipyard, Electric Boat in Groton, Manitowoc Shipbuilding in Wisconsin (which built submarines inland and floated them down the Mississippi River), and Mare Island Naval Shipyard all expanded capacity and adopted modern production techniques including prefabricated hull sections.

The designs themselves evolved. The Gato class (1941-43) gave way to the improved Balao class (1942-45) with deeper diving capability, and then the Tench class (1944-46) with more internal volume and improved equipment. Each class incorporated lessons from combat experience — crew habitability improvements, better radar, improved fire control, reduced construction time. By 1945, the US had placed over 200 fleet submarines in service, transforming the small pre-war force into the strategic weapon that sank over 5 million tons of Japanese shipping and contributed decisively to Japan's defeat."""
},

{
"chunk_id": "pam_175",
"title": "What was a snorkel on a submarine?",
"text": """What was a snorkel on a submarine?

A snorkel (or snort) was a retractable breathing tube that allowed a diesel-electric submarine to run its diesel engines while submerged just below the surface. It consisted of an air intake mast and an exhaust mast that extended above the waterline just enough to draw in air and expel exhaust gases, while the main hull of the submarine remained underwater.

The snorkel was a German invention, developed by the Dutch Navy in the 1930s and adopted and perfected by the German U-boat arm in 1943-44 as Allied anti-submarine warfare became increasingly effective. By snorkeling, a submarine could recharge its batteries and run on diesel power without having to surface entirely — massively reducing its radar and visual signature. A snorkeling submarine could be detected only by radar (the small mast was difficult to pick up), by its exhaust signature, or visually, making it far harder to find than a fully surfaced boat.

American WWII fleet submarines including Pampanito were not equipped with snorkels during the war — the US Navy chose not to adopt the technology during the Pacific conflict, in part because US submarines still found adequate opportunities to surface safely at night for battery charging. The snorkel became standard on post-war submarines, and its adoption (along with faster battery technology) was a key step in the evolution toward the nuclear submarines that made the entire surface/submerge cycle unnecessary."""
},

{
"chunk_id": "pam_176",
"title": "What was periscope depth on a submarine?",
"text": """What was periscope depth on a submarine?

Periscope depth was the shallow depth at which a submarine could raise its periscope above the surface of the water to observe the surrounding area without fully surfacing. For fleet submarines like Pampanito, periscope depth was typically around 55-62 feet — deep enough that the submarine was completely below the surface (safe from ramming and surface waves), but shallow enough that the periscope head could be extended upward through the water.

Operating at periscope depth was a delicate balancing act for the diving officer. At that depth, ocean swells affected the submarine noticeably, and maintaining a steady depth required constant adjustment of the planes and ballast. If the boat was too shallow, the periscope might be swamped by waves or the periscope shears might briefly break the surface, creating a visible wake. If too deep, the periscope would be underwater and blind.

The periscope head itself was typically about 1.5-2 inches in diameter — just a thin tube above the surface — making it difficult to spot visually at distance, especially in choppy seas. The submarine's attack periscope was thin and low; the larger search periscope was used for longer-range observation. A submarine at periscope depth was in a position of controlled risk: able to see and potentially attack, but also potentially visible to enemy lookouts or radar, and much less protected than at deep running depth."""
},

]

BASE = {
    "doc_type": "dieselsubs_faq",
    "source": "dieselsubs_faq",
    "display_citation": "DieselSubs FAQ",
}

with open("corpora/dieselsubs_faq_corpus.jsonl") as f:
    lines = [l.strip() for l in f if l.strip()]

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
