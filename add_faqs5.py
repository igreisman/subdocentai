"""Add batch 7 FAQs (pam_113-pam_132) to the corpus."""
import json

NEW_FAQS = [

{
"chunk_id": "pam_113",
"title": "What was the lifeguard mission in WWII?",
"text": """What was the lifeguard mission in WWII?

The "lifeguard" mission was a special assignment where US submarines were stationed near Japanese-held islands or along the flight paths of bombing raids to rescue downed Allied airmen. Beginning seriously in 1944, as American air operations over Japan intensified, submarines were assigned to wait on the surface or nearby while B-29s and carrier aircraft flew their missions overhead.

When an aircrew ditched or bailed out, they radioed their position and a waiting submarine moved to retrieve them. Submarines rescued hundreds of airmen this way. Famous lifeguard rescues include USS Tang (SS-306), which rescued 22 aviators in one day, and USS Finback (SS-230), which famously rescued a young Navy pilot named George H.W. Bush in September 1944 after his aircraft was shot down over Chichi Jima.

The Pampanito was not specifically assigned a lifeguard role — she was primarily a combatant submarine on attack patrols. But the lifeguard mission shows the range of tasks US submarines performed beyond simply sinking ships."""
},

{
"chunk_id": "pam_114",
"title": "Did submarines lay mines in WWII?",
"text": """Did submarines lay mines in WWII?

Yes. US submarines played an important role in minelaying operations during World War II. Submarines could secretly plant mines in Japanese harbors, shallow coastal waters, and shipping lanes that surface ships could never safely reach. The mines were carried in the torpedo tubes and fired (or dropped) like torpedoes, sinking to the bottom or floating at set depths.

Several Gato and Balao-class fleet submarines were modified for minelaying missions, carrying a combination of mines and torpedoes. Notable minelaying operations included laying mines in the approaches to Japanese home ports, which sank or damaged ships that would have been impossible to reach by direct attack. Submarine-laid mines were credited with sinking dozens of Japanese ships.

The USS Pampanito (SS-383) was not specifically used for minelaying — she was deployed as a front-line attack submarine and completed six war patrols focused on torpedo attacks against merchant and naval targets. Minelaying was a specialized assignment given to specific submarines on specific patrols."""
},

{
"chunk_id": "pam_115",
"title": "How did a depth charge attack feel inside a submarine?",
"text": """How did a depth charge attack feel inside a submarine?

A depth charge attack was one of the most frightening experiences a submarine crew could endure. When a depth charge exploded nearby, the shock wave struck the hull like a massive hammer blow — loud crashing, jolting the entire boat violently, knock men off their feet and sending loose gear flying. Light bulbs shattered, cork insulation showered down from the overhead, gauges cracked, and pipes could spring leaks.

The sounds were terrifying: a sharp CLICK as the charge detonated, followed instantly by an enormous BANG, then a deep rumbling. When charges were very close, the lights went out momentarily. Men who had been through attacks described the experience as sitting inside a steel drum being struck by a sledgehammer — over and over, sometimes for hours. The psychological toll was immense: not knowing how close the next one would be, whether the hull would hold, or whether the next one would be the last.

Submariners developed intense silent discipline during attacks — no unnecessary movement, no talking, only essential whispers. Every man knew that the slightest noise could travel through the water and help the enemy re-acquire the submarine. After surviving an attack, crews reported the silence afterwards as almost dreamlike."""
},

{
"chunk_id": "pam_116",
"title": "What was hot bunking on a submarine?",
"text": """What was hot bunking on a submarine?

Hot bunking (also called hot racking) was the practice of two or more sailors sharing a single bunk on alternating watch schedules. Because a WWII fleet submarine had more crew members than available bunks — especially for enlisted men — bunks had to be shared. While one watch section was on duty, another was sleeping in their bunks, and when duty rotated, the off-going watch took over the "warm" (hot) bunks just vacated.

On Balao-class submarines like the Pampanito, the torpedo rooms served double duty: the long flat skids that held reload torpedoes also served as bunks for the torpedo gang. When the spare torpedoes were fired or used, proper bunk frames could be installed. Some enlisted men had no assigned bunk at all during the first part of a patrol and slept wherever space was available.

Hot bunking was accepted as normal submarine life. Sailors didn't think much of it — they were so tired after watch that sleeping in a warm bunk didn't bother them. The practice required that men keep their personal gear in small individual lockers, bringing only what was needed for immediate use."""
},

{
"chunk_id": "pam_117",
"title": "How did the deck gun work on a submarine?",
"text": """How did the deck gun work on a submarine?

The deck gun on USS Pampanito was a 4-inch/50-caliber naval gun mounted on the forward deck, with a smaller 40mm anti-aircraft gun added later in the war. To use it, the submarine first surfaced. The gun crew — typically six to eight men — rushed up from below through the hatches, took their stations, and began firing within seconds. Speed was critical because a surfaced submarine was vulnerable.

Shells were stored in a below-deck ready locker near the gun. A trained crew could fire ten or more rounds per minute. The gun was used primarily against small merchant vessels, patrol boats, and larger targets when torpedoes were unavailable or would be wasted. Gun attacks were riskier than torpedo attacks because the submarine was exposed on the surface within visual range of the target.

As air patrols increased later in the war, deck gun attacks became more dangerous — an aircraft could appear before the crew could dive. By 1944-45, submarines relied more heavily on torpedoes and used the deck gun less. The gun required regular maintenance because of constant exposure to saltwater spray, which caused rapid corrosion."""
},

{
"chunk_id": "pam_118",
"title": "How did the Pampanito get its name?",
"text": """How did the Pampanito get its name?

USS Pampanito (SS-383) was named after the pampanito, a species of fish found in Pacific ocean waters — a small, silvery member of the pompano family. The United States Navy had a long tradition of naming submarines after fish and sea creatures, a practice that began with the earliest American submarines and was formalized for the fleet submarine program of World War II.

When a new submarine was ordered from the shipyard, the Bureau of Ships assigned a name from an approved list of fish names. The names were typically chosen to be distinctive (easy to distinguish by radio), not too similar to other ships already in service, and reasonably short. The assignment of "Pampanito" to SS-383 was essentially administrative — the name was available and appropriate. There was no particular connection between the pampanito fish and the submarine's mission or crew.

This naming tradition continues today — US Navy submarines are still named after underwater creatures, geographic features, or American cities and states, depending on the submarine's class."""
},

{
"chunk_id": "pam_119",
"title": "How did submarine crews fight fires onboard?",
"text": """How did submarine crews fight fires onboard?

Fire was one of the most feared emergencies on a submarine. In a sealed steel hull with limited oxygen and no easy escape route, a fire could quickly become catastrophic. Submarine crews trained extensively for fire emergencies, drilling until the response was automatic.

The primary fire-fighting tools were CO2 extinguishers and foam applicators positioned throughout the boat. When a fire broke out, crew members donned Emergency Breathing Devices (EAB) — rubber masks that provided clean air from a central manifold system — so they could work in smoke without being incapacitated. Watertight doors between compartments were shut to prevent smoke and fire from spreading. The affected compartment was isolated, and the fire was attacked from inside while fresh air supply was cut.

Battery fires were particularly dangerous because the lead-acid batteries could produce hydrogen gas, which is explosive. Electrical fires in the engine room or battery compartment required immediate isolation of circuits. If a fire broke out while the submarine was on the surface, the fastest solution was sometimes to dive — seawater flooding over the hull could extinguish topside fires, and submerging reduced airflow to the fire. After any fire, the crew had to assess damage before the boat could safely continue its mission."""
},

{
"chunk_id": "pam_120",
"title": "Did American WWII submarines have a snorkel?",
"text": """Did American WWII submarines have a snorkel?

No. American fleet submarines in World War II did not use snorkels. The snorkel was a Dutch invention that the Germans adopted for their U-boats starting in 1944. It was a retractable mast that allowed a submarine to run its diesel engines while remaining just below the surface, sucking in air and exhausting fumes through the mast rather than having to fully surface.

American submarines worked differently — they surfaced at night to run their diesel engines, recharge batteries, and ventilate the boat. This required coming fully to the surface, making them detectable by radar and lookouts. The strategy relied on operating in areas where enemy surface patrols were manageable, and on careful watch-keeping to spot threats before they became dangerous.

The US Navy did adopt snorkels after World War II once the technology's value became clear. The post-war GUPPY (Greater Underwater Propulsion Power) conversion program modified many fleet submarines, including adding snorkel capability. The USS Pampanito, however, was preserved without these modifications, so she appears today essentially as she was during her active wartime service in 1944-1945."""
},

{
"chunk_id": "pam_121",
"title": "What was the role of submarines in the Battle of Midway?",
"text": """What was the role of submarines in the Battle of Midway?

At the Battle of Midway in June 1942, US submarines played a supporting but largely unsuccessful role. Twelve submarines were deployed in a defensive screen around Midway Atoll and along anticipated Japanese approach routes. The plan was for the submarines to intercept Japanese ships, but the fast-moving carrier air battle unfolded differently than expected.

USS Nautilus (SS-168) fired torpedoes at the already-damaged Japanese carrier Kaga, but the torpedoes failed to explode — a common problem with defective Mark 14 torpedoes early in the war. USS Grouper (SS-214) fired at the battleship Mikuma but also failed to score hits. Despite positioning some 12 submarines across the expected approach routes, the Japanese fleet's track and the rapid air battle left the submarines unable to effectively engage.

The submarines at Midway were largely bypassed by the engagement but did force Japanese ships to conduct evasive maneuvers that consumed time and fuel. After the battle, the decisive result came from the dive bombers that sank four Japanese carriers — not the submarines. However, the lessons of coordination between submarines and surface/air forces were absorbed and improved upon throughout the rest of the war."""
},

{
"chunk_id": "pam_122",
"title": "What was radio direction finding and how did it threaten submarines?",
"text": """What was radio direction finding and how did it threaten submarines?

Radio direction finding (RDF), also known as HF/DF or "Huff-Duff" (High Frequency Direction Finding), was technology that could locate a radio transmitter by triangulating the direction of its signal from multiple receiver stations. If a submarine broadcast a radio message, shore stations or ships with RDF equipment could detect the signal, measure its bearing from two or more positions, and plot the intersection to find the submarine's location — sometimes within miles or even less.

This technology posed a serious threat to submarines because Japanese shore stations and some warships were equipped with RDF. A submarine that transmitted a long message could be located quickly enough for aircraft or destroyers to be dispatched to attack it. American submariners learned to keep radio transmissions brief — compressed coded messages sent in seconds rather than minutes — to minimize the risk.

Ironically, the United States also used RDF against Japan with great success. The code-breaking operation at Station HYPO in Pearl Harbor combined decrypted Japanese signals (Ultra intelligence) with RDF bearings to track the movements of the Japanese fleet. This intelligence was critical to the American victory at Midway and many other operations throughout the Pacific War."""
},

{
"chunk_id": "pam_123",
"title": "How did the crew deal with claustrophobia on a submarine?",
"text": """How did the crew deal with claustrophobia on a submarine?

The submarine service screened carefully for men who could handle confined spaces. During the selection process, volunteers underwent psychological evaluation and observed responses to simulate enclosed environments. Men who showed signs of claustrophobia or extreme anxiety were disqualified. Even so, some sailors didn't fully discover their own reaction to confinement until they were underway.

On patrol, the best cure for claustrophobia was keeping busy. The watch schedule — four hours on, eight hours off — kept men occupied with their duties for much of the day. Off-watch time was filled with maintenance, training, card games, reading, movies (when a projector was available), and sleep. Veterans noted that the interior of a fleet submarine was larger than popular imagination suggests: men could stand upright in most compartments, and the forward and after torpedo rooms had relatively open spaces.

Experienced submariners generally became habituated to the environment after the first patrol. The sense of purpose — being part of an elite force doing important work — helped counteract psychological stress. Men who genuinely couldn't adapt were transferred off submarines without stigma; the Navy preferred motivated and capable volunteers to unwilling men in potentially dangerous situations."""
},

{
"chunk_id": "pam_124",
"title": "What was the galley like on a submarine?",
"text": """What was the galley like on a submarine?

The galley on USS Pampanito was a compact but well-equipped kitchen located just off the crew's mess. Despite the limited space, it was stocked to feed 70-80 men three hot meals a day, plus "mid-rats" (midnight rations) for the mid-watch section coming off duty at midnight.

Fleet submarines were famous throughout the Navy for having the best food. This was partly a deliberate morale policy: the Navy believed that good food made up for the hardships of submarine duty. Fresh meat, vegetables, and fruit were loaded at the start of each patrol and consumed first, before the boat shifted to canned and dehydrated food. The cook made ice cream when milk was available, baked fresh bread and pies, and generally went to great lengths to vary the menu.

The ship's cook was the most important morale figure after the captain and executive officer. A good cook was valued above almost anyone else on the crew. Cooking in a small galley while the boat pitched and rolled on the surface — and without being able to open a window — required skill, creativity, and physical toughness. The galley was also the social heart of the boat, where off-watch crew gathered, got coffee, and talked."""
},

{
"chunk_id": "pam_125",
"title": "How did submarines get fresh water at sea?",
"text": """How did submarines get fresh water at sea?

Fresh water on fleet submarines like Pampanito came primarily from a distillation plant (evaporator) that used engine heat to boil seawater and condense the steam into drinkable fresh water. The evaporator ran continuously when the engines were operating, producing several hundred gallons per day, but this had to serve all the boat's needs — drinking, cooking, and minimal washing.

Water was strictly rationed. Drinking and cooking water was always available, but bathing was another matter. Fresh water showers were rare luxuries — most crew members bathed infrequently, using small amounts of fresh water or bucket baths with salt water and special salt-water soap that would lather without fresh water. Laundry was done in salt water. By the end of a long patrol, the entire crew smelled strongly of sweat, diesel fuel, and machinery oil — this was accepted as normal.

When submarines visited a tender or returned to port, the first priority for many men was a long hot fresh water shower. Fresh water tanks could also be topped off from a submarine tender at sea, though this required rendezvousing with a surface ship, which was unusual on a standard war patrol."""
},

{
"chunk_id": "pam_126",
"title": "Was the Pampanito ever close to being sunk?",
"text": """Was the Pampanito ever close to being sunk?

Yes, on multiple occasions. During Pampanito's third war patrol in September 1944, she participated in a wolf pack attack on a Japanese convoy in the South China Sea. After the attack, Japanese escorts pursued the attacking submarines with depth charges. Pampanito went deep and ran silent for hours while depth charges exploded around her. Some charges were close enough to damage cork insulation and rattle the crew severely.

Even more dangerous was the surface time immediately following the attack, when Pampanito and USS Sealion (SS-315) stopped to rescue British and Australian POWs from the water. For nearly two hours, Pampanito sat fully surfaced in daylight in enemy-controlled waters while survivors — many barely alive — were pulled aboard by hand. A submarine stopped on the surface was completely vulnerable to aircraft or ship attack. The crew worked frantically knowing they were exposed. Fortunately, no Japanese forces appeared during the rescue.

Throughout her six war patrols, Pampanito survived multiple depth charge attacks without sustaining serious damage to her pressure hull, a testament to solid construction, the skill of her crews, and a measure of luck that every submarine depended on."""
},

{
"chunk_id": "pam_127",
"title": "How did submarines attack a convoy?",
"text": """How did submarines attack a convoy?

Attacking a Japanese convoy required patience, tracking skill, and precise timing. The submarine first detected the convoy — typically by radar at night or by periscope during the day — and began tracking its course and speed. The captain's goal was to get ahead of the convoy and position the submarine for the best firing angle, ideally from the side (a beam shot) or slightly ahead.

While tracking, the crew set battle stations. In the conning tower, the approach officer and tracking party fed bearings, ranges, and target speeds into the Torpedo Data Computer (TDC), which continuously calculated a firing solution. When the geometry was right, the captain ordered a spread of torpedoes — typically three to six — fired in sequence against individual ships in the convoy.

After firing, the submarine immediately dove deep or changed course to evade. The convoy's escort ships (destroyers and frigates) would charge toward the torpedo wakes and begin dropping depth charges while the attacked ships scattered. The submarine dodged, went silent, and waited — sometimes for hours — before cautiously returning to periscope depth to assess damage. A successful convoy attack might sink one to three ships; attacking a well-escorted convoy was one of the most dangerous operations a submarine undertook."""
},

{
"chunk_id": "pam_128",
"title": "Did submarine crews get seasick?",
"text": """Did submarine crews get seasick?

Yes, seasickness was a real problem on fleet submarines — particularly early in a patrol and for men new to submarine duty. On the surface in rough Pacific seas, a submarine rolls and pitches quite noticeably. The hull is round-bottomed with relatively limited width, making it susceptible to rolling motion. Some men were quite uncomfortable in rough weather.

The best cure for surface seasickness was simply to dive: once submerged, submarines are isolated from wave action and become extremely stable. Even in a severe storm, the crew submerged below the wave layer experienced none of the motion. Veterans said that many sailors who became seasick on surface ships found submarine duty easier because so much time was spent submerged.

Most sailors got their "sea legs" quickly — the regular motion of operating on the surface became normal within a few days, and the body adapted. Ginger tablets and other remedies were available in the pharmacist's locker. Men who were chronically prone to severe seasickness were generally not suited for submarine duty and were screened out during training or after their first patrol, as a seasick crew member at battle stations was a danger to the boat."""
},

{
"chunk_id": "pam_129",
"title": "Did the Pampanito sink Japanese warships?",
"text": """Did the Pampanito sink Japanese warships?

Pampanito's confirmed sinkings were primarily Japanese transport and merchant vessels — not warships. Her most famous victims were the transport RAKUYO MARU and the transport KACHIDOKI MARU, both sunk during her third war patrol in September 1944. These ships were tragically carrying British and Australian prisoners of war, which led to Pampanito's famous rescue mission. She also sank several freighters and tankers in other patrols.

This pattern was typical for US submarines. The primary strategic objective of the Pacific submarine campaign was to strangle Japan's economy and war effort by sinking merchant ships, tankers, and supply vessels — cutting the flow of oil, food, and raw materials to the Japanese home islands. Attacking warships was a secondary priority and was usually much more dangerous, as warships were faster, better armed, and accompanied by anti-submarine escorts.

Pampanito did participate in attacks on Japanese naval vessels. During one patrol, she fired at what was believed to be a light cruiser, without confirmed results. Warship sinkings by submarines did occur throughout the war — USS Darter (SS-227) and USS Dace (SS-247) sank Japanese cruisers at the Battle of Leyte Gulf — but the real measure of submarine success was tonnage of merchant shipping sunk."""
},

{
"chunk_id": "pam_130",
"title": "How did submarines handle the threat of aircraft?",
"text": """How did submarines handle the threat of aircraft?

Aircraft were among the most dangerous threats to surfaced submarines. A patrol plane or carrier aircraft could spot a submarine from altitude and attack before the crew had time to react. The primary defense was simple: stay submerged during daylight in enemy-controlled waters whenever possible, and surface only at night. The general rule was: if in doubt, dive.

When a submarine was caught on the surface by aircraft, the crash dive was the only reliable defense. The bridge watch immediately sounded the diving alarm (AOO-GAH), and every man on the bridge dropped through the hatch as fast as possible — sometimes literally falling down the ladder — while the officer of the deck pulled the hatch shut behind him. From alarm to periscope depth could be accomplished in 30-40 seconds on a well-trained crew.

For aircraft that attacked before a dive was complete, fleet submarines carried anti-aircraft guns — a 40mm Bofors and 20mm cannon guns — mounted on the bridge fairwater. These were used to fight off low-flying aircraft during the few seconds of exposure. Late in the war, as American and Allied air superiority over the Pacific grew, the threat to US submarines from aircraft diminished. Japanese submarines, by contrast, faced constant attack from US aircraft and lost many boats to air attack."""
},

{
"chunk_id": "pam_131",
"title": "What were wolfpack tactics in WWII submarines?",
"text": """What were wolfpack tactics in WWII submarines?

Wolfpack tactics were coordinated attacks by multiple submarines against a single convoy or task group. The concept was pioneered by Germany's U-boat service under Admiral Dönitz, where groups of 10-20 U-boats would converge on an Atlantic convoy and attack simultaneously from multiple angles, overwhelming the escorts.

American submarines used a more limited version of wolf packs — typically groups of two to four submarines operating in the same patrol area and coordinating attacks via radio. These US wolf packs were called "coordinated attack groups." One famous example is the wolf pack that included USS Pampanito, USS Sealion, and USS Barb during the September 1944 patrol in the South China Sea, which sank the Japanese convoy carrying POWs.

American wolfpack tactics differed from German practice in several ways: US packs were smaller, had better radar and communications equipment, operated in waters where the Japanese anti-submarine effort was less intense than the Allied escort forces in the Atlantic, and benefited from Ultra intelligence about convoy routes. The coordinated approach allowed submarines to attack from several angles at once, forcing escorts to split their response and making it harder to prosecute all the submarines simultaneously."""
},

{
"chunk_id": "pam_132",
"title": "Were submarines used to land spies or special forces?",
"text": """Were submarines used to land spies or special forces?

Yes. US submarines frequently carried out special missions to land agents, OSS personnel (Office of Strategic Services, the WWII predecessor to the CIA), Filipino guerrillas, and other intelligence operatives on enemy-held shores throughout the Pacific. Navy submarine special missions also included resupplying guerrilla forces, evacuating important personnel, and delivering critical supplies to isolated outposts.

Submarines were the ideal vehicle for these "cloak and dagger" operations: they could approach enemy coastlines silently at night, surface briefly to offload or recover personnel via rubber boats, and disappear before daylight. Several submarines became specialists in these missions. USS Narwhal (SS-167) and USS Nautilus (SS-168), converted from minelayers, were the most extensively used special mission submarines, making dozens of trips to the Philippines.

The USS Pampanito served as a standard attack submarine and did not participate in documented special forces missions — her six war patrols were focused on attacking Japanese shipping. However, several fleet submarines were temporarily diverted from combat patrols to support special operations when required, reflecting the versatility that made submarines uniquely valuable throughout the Pacific campaign."""
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
