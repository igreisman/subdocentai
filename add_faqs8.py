"""Add batch 10 FAQs (pam_177-197) to the corpus."""
import json

NEW_FAQS = [

{
"chunk_id": "pam_177",
"title": "What was the officer of the deck responsible for on a submarine?",
"text": """What was the officer of the deck responsible for on a submarine?

The officer of the deck (OOD) was the captain's direct representative and the individual responsible for the safe navigation and operation of the submarine at any given moment. When the captain was off watch, the OOD had command authority over all routine decisions — course, speed, dive or surface timing in safe waters, and watch standing. He was the one person who could order the ship to take action without waiting for the captain, within standing orders.

On the surface, the OOD was posted on the bridge, scanning the horizon with binoculars, managing the watch, and making sure the boat was proceeding safely. When submerged in the patrol area, the OOD held the conn in the conning tower, monitoring the periscope watch cycle, tracking sonar contacts, and deciding when to report developments to the captain.

The OOD was always a qualified officer (ensign through lieutenant commander). Junior officers served as OODs first under supervision, then independently once they had demonstrated competence. The position was a training ground for future commanding officers — the skills of ship-handling, decision-making under pressure, and crew management that made a good OOD were exactly the skills that made a good submarine captain. Every submarine CO started as a junior OOD, learning the craft watch by watch."""
},

{
"chunk_id": "pam_178",
"title": "What was a conning tower on a submarine?",
"text": """What was a conning tower on a submarine?

The conning tower was a small, heavily reinforced compartment built into the top of the pressure hull, accessed by a vertical ladder from the control room below. On fleet submarines like Pampanito, it was roughly 8-9 feet in diameter, shaped like a cylinder, and designed to be the command center for torpedo attacks.

Key equipment in the conning tower included: the attack periscope (thin, low-signature, used for final attack observations), the search periscope (larger, used for long-range horizon scanning), the Torpedo Data Computer (TDC), the helm (wheel for steering), radar repeaters, and sound-powered phone connections to every compartment. During an attack, the captain would be at the periscope, the XO or approach officer at the TDC, a helmsman at the wheel, and additional personnel tracking the fire control solution.

The conning tower was structurally separate from the main hull — it had its own flood and vent valves, and in theory could be sealed independently. Above the conning tower was the bridge access trunk, a watertight hatch leading up through the fairwater (the streamlined "sail" structure) to the open bridge on top. The conning tower was accessible only through the control room below and the bridge above, making it a well-protected, central command space shielded from the worst of any depth charge attack."""
},

{
"chunk_id": "pam_179",
"title": "How were new submarine crew members trained?",
"text": """How were new submarine crew members trained?

New submarine sailors went through a structured pipeline before joining a fleet boat. First, enlisted men attended basic submarine school at New London, Connecticut (the "Submarine Capital" of the US Navy). The course covered basic submarine systems, emergency procedures, physics of pressure and buoyancy, torpedo handling, and the theory of submarine operations. Officers attended a separate officer basic course at the same facility.

After formal school, new crew members joined their assigned submarine as "non-quals" — men not yet certified. The qualification process aboard the boat was the real education: each man had to trace and demonstrate knowledge of every system, from the diesel engines to the trim pumps to the weapons systems. Senior hands guided the process, checking off each system after the trainee could describe its function and demonstrate its operation. The oral board — a formal examination by officers — was the final gate before awarding the submarine warfare insignia (dolphins).

Practical experience came fast in wartime. A new crew member who joined during refit between patrols might be on a combat patrol within a month of arriving on the boat. The compressed timeline of wartime training meant that some men qualified remarkably quickly, while others took longer. Throughout, the culture of the submarine service emphasized self-sufficiency: every man was expected to be able to fight the boat in any compartment if the regular operator was incapacitated."""
},

{
"chunk_id": "pam_180",
"title": "What was a sound-powered telephone on a submarine?",
"text": """What was a sound-powered telephone on a submarine?

A sound-powered telephone (SPT) was a communication device that required no electrical power supply to operate. The user's voice vibrated a diaphragm in the handset, which generated a small electrical current through electromagnetic induction. That current traveled through wires to the receiving handset, where it was converted back to sound — no battery, no amplifier, no external power source needed.

Sound-powered phones were essential on submarines because they functioned even when the main electrical systems were shut down, damaged by depth charges, or deliberately powered off for silent running. The system was reliable, simple, and nearly impossible to jam or intercept.

The submarine's sound-powered telephone network connected every key station: bridge to conning tower to control room to engine rooms to torpedo rooms to maneuvering room. Specific circuits (labeled by letter and color) served different functions — the JV circuit for the primary command circuit, JA for battle stations, 21MC for captain's orders, and so forth. During battle stations, every station manned its phones and reported readiness sequentially ("Forward torpedo room, manned and ready…") up the chain to the officer of the deck. This roll call confirmed the entire crew was at their posts before any attack began. The sound-powered phone system was one of the most critical pieces of non-combat equipment on the boat."""
},

{
"chunk_id": "pam_181",
"title": "How did submarines identify enemy ships at night?",
"text": """How did submarines identify enemy ships at night?

Identifying enemy ships at night — distinguishing the type, size, and value of a target — was one of the more challenging skills in submarine warfare, and it was critical because the target identification determined whether to attack and how many torpedoes to fire.

The primary tool was the SJ radar, which could detect surface targets at ranges of 8-10 miles and greater. The radar return gave the target's bearing, range, and a rough size indication — a large return meant a big ship, a smaller return meant a smaller vessel or an escort. By tracking the radar return over several minutes, the crew could determine the target's course and speed.

When close enough, the periscope was used even at night. The Fleet-era attack periscope incorporated a "night glass" capability — a wider-aperture lens that gathered more light, making it possible to distinguish ship silhouettes in starlight or moonlight. Experienced captains could identify ship types from their silhouettes. The ONI (Office of Naval Intelligence) published silhouette recognition books that submarine crews studied before patrol — being able to instantly recognize a Maru-class freighter from a destroyer escort from a tanker by profile was a trained skill.

Acoustic information from the sonar operator also helped — propeller count and rhythm gave a rough sense of the number and type of ships in a convoy before visual or radar contact was made."""
},

{
"chunk_id": "pam_182",
"title": "What was the after torpedo room used for on a submarine?",
"text": """What was the after torpedo room used for on a submarine?

The after torpedo room was at the stern of the submarine and mirrored the forward torpedo room in function — it was both a weapons space and a crew berthing compartment. Unlike the forward room's six tubes pointing forward, the after torpedo room had four torpedo tubes pointing aft, allowing the submarine to fire at targets while running away from them.

The four after tubes were a tactically important capability. If a target appeared astern of the submarine after a forward attack, or if the submarine needed to attack an escort that was pursuing it from behind, the after tubes provided an option. Some attack solutions were worked specifically for an "up the kilt" shot — firing aft torpedoes directly at a pursuing destroyer.

Like the forward room, spare torpedoes rested on skids in the after torpedo room, held in place by cradles and securing chains. A small crew of torpedomen bunked in the space on racks mounted above and between the weapons. The aftermost compartment of the submarine, it was also the farthest from the conn — communication was by sound-powered telephone, and torpedo room personnel had to be sharp at interpreting both routine commands and emergency instructions rapidly. The after torpedo room chief was responsible for tube readiness, torpedo maintenance, and the safety of the crew members who lived and worked in that compartment."""
},

{
"chunk_id": "pam_183",
"title": "How did the Navy select men for submarine duty?",
"text": """How did the Navy select men for submarine duty?

Submarine duty was voluntary in the US Navy — no one was assigned to submarines against their will. Men had to volunteer, and the Navy then screened volunteers through a selection process designed to identify those physically and psychologically suited for the unique demands of submarine service.

Physical requirements included: normal or corrected-to-normal vision (severe visual impairment disqualified), no chronic ear problems (pressure changes during diving were a concern), no significant heart or lung conditions, and an ability to pass a pressure test in the escape training tank at New London — where recruits proved they could equalize pressure in their ears and handle the physical sensations of increasing water pressure.

The psychological screening was less formalized but no less real. Instructors and evaluators watched for signs of claustrophobia, poor stress response, or extreme anxiety. Men who showed these traits during training exercised in the mock-up tanks or drills were quietly directed elsewhere.

Beyond formal screening, submarines sought intelligent, adaptable sailors who could learn complex systems rapidly. The qualification requirement — that every man learn every other man's job — meant that below-average learners struggled to earn their dolphins and sometimes transferred off the boat. The combination of volunteer selection, physical screening, and the rigorous qualification process produced submarine crews that were, on average, among the most capable and self-sufficient men in the Navy."""
},

{
"chunk_id": "pam_184",
"title": "What happened to the crew of a submarine that was sunk?",
"text": """What happened to the crew of a submarine that was sunk?

Of the 52 US submarines lost in World War II, virtually all were lost with all hands or with only rare survivors. The survival rate from sunken submarines was extremely low — the combination of depth, violent sinking, enemy action, and the Pacific Ocean made escape nearly impossible in most cases.

When a submarine was sunk in shallow water by depth charges, there was occasionally a slim possibility of using the escape apparatus — a rubber hooded suit (the Momsen lung or escape set) that allowed one or two men to breathe from a small air supply while ascending from a flooding compartment. The forward and after escape trunks were small flooding chambers that could cycle one man at a time to the surface. However, these devices worked only at relatively shallow depths (under about 100 feet) and required the submarine to be on the bottom intact with compartments still holding air.

In practice, most wartime submarine sinkings occurred under conditions where escape was impossible: at depth under sustained depth charge attack, through catastrophic flooding or explosion, or at depths far beyond where any escape device could function. Of the approximately 3,506 US submariners killed in WWII, the vast majority went down with their boats. The overall casualty rate for US submarine service was among the highest of any branch — roughly 22% of those who deployed on combat patrols were killed, the highest loss rate in the US Navy."""
},

{
"chunk_id": "pam_185",
"title": "How did submarines attack targets at night on the surface?",
"text": """How did submarines attack targets at night on the surface?

Night surface attacks became one of the most successful and distinctive tactical developments of US submarine warfare in the Pacific. Instead of submerging to use the periscope, a submarine would approach a target convoy on the surface at night, using the low silhouette of the hull to remain nearly invisible against the dark water while taking advantage of its higher surface speed.

Surface attacks used the SJ radar as the primary targeting tool. The radar could track targets precisely enough to develop a fire control solution — bearing, range, course, and speed — without any visual contact. The Torpedo Data Computer received this radar data to calculate gyro angles, and torpedoes were fired using a radar-derived solution, sometimes without the captain ever seeing the target visually.

The advantages were significant: the submarine was faster on the surface than submerged, allowing longer pursuit of a convoy; radar provided accurate ranges that periscope rangefinding could not match at night; and the submarine avoided the battery drain of sustained submerged approach. The risk was reciprocal — the submarine was on the surface, visible to radar-equipped escorts and potentially to visual lookouts. Night surface attacks required nerve, fast decision-making, and a captain willing to close to relatively short range before firing. Many of the most devastating US submarine attacks on Japanese convoys in 1944-45 were executed precisely this way."""
},

{
"chunk_id": "pam_186",
"title": "What did the lookouts on a submarine watch for?",
"text": """What did the lookouts on a submarine watch for?

Lookouts on the bridge of a surfaced submarine were among the most critical crew members at any given moment — their eyes were the first line of defense against the threats that could send the boat to the bottom. Typically three or four lookouts were posted on the bridge during surface running, each assigned a sector of the horizon to scan continuously. They were equipped with high-powered 7x50 binoculars, chosen for their light-gathering ability in darkness.

The primary threat lookouts watched for was aircraft — a single Japanese or Allied patrol plane could get within gun range before radar detected it, especially if the aircraft was flying low or the radar was temporarily off (to avoid detection). Lookouts shouted "Aircraft! [bearing]!" immediately upon sighting, giving the OOD the few seconds needed to initiate a crash dive. "Clear the bridge!" sent every man below in a controlled rush.

Lookouts also watched for ships — enemy surface vessels, other submarines (friendly and hostile), and surface debris. In enemy-controlled shipping lanes, a smudge on the horizon at dusk could be a smoke stack leading to a convoy. Lookouts were trained to distinguish silhouettes, estimate distances, and report bearing and elevation immediately without delay. An alert lookout who spotted a distant destroyer before it closed within gun range might save the boat; a distracted one who missed an approaching aircraft might doom it. Bridge watch duty was exhausting, cold, and wet — but profoundly consequential."""
},

{
"chunk_id": "pam_187",
"title": "How were submarines refueled in the Pacific?",
"text": """How were submarines refueled in the Pacific?

Fleet submarines in the Pacific were refueled primarily at fixed bases rather than at sea. The main base was Pearl Harbor, Hawaii, which served as the central hub for submarine operations throughout the war. Submarines returned to Pearl after each patrol to refuel, rearm, provision, and undergo maintenance and repair.

As the war progressed into 1944-45, the US established advance submarine bases closer to the patrol areas. Midway Atoll became an important forward base, as did Guam and other captured islands that were developed into submarine support facilities. Operating from Guam reduced the transit time to and from Japanese waters significantly, allowing longer time on patrol and shorter logistics tails.

Submarine tenders — large support ships like USS Proteus and USS Fulton — also provided fuel, torpedoes, provisions, and repair services. A tender anchored in a harbor or lagoon could support dozens of submarines simultaneously, giving each boat the equivalent of a small shipyard's worth of support. Tenders were particularly important at advance bases that hadn't yet developed full shore-based facilities.

At-sea replenishment of submarines from surface vessels (as was done for surface warships) was not a standard practice in WWII, primarily because the fuel transfer required both vessels to be relatively stationary and the process was difficult and dangerous. The standard model was: patrol for 60-75 days, return to base, refuel and refit, depart for the next patrol."""
},

{
"chunk_id": "pam_188",
"title": "What was a target's angle on the bow?",
"text": """What was a target's angle on the bow?

Angle on the bow (AOB) was one of the most critical measurements in setting up a torpedo attack. It was the angle between the target ship's heading (where the ship was pointed) and the direct line of sight from the submarine to the target — essentially, "how much of the target ship's course is angled toward you or away from you?"

An angle on the bow of zero degrees meant the target was headed directly toward the submarine (bow-on). An AOB of 90 degrees (starboard or port) meant the target was crossing at a perfect right angle. An AOB of 180 degrees meant the target was running directly away. The angle was measured from the target's bow — "port 45" meaning the target was heading 45 degrees to the left of the line of sight from the submarine.

AOB was estimated visually through the periscope by the captain, who compared the silhouette of the target ship to a standard recognition table — the more foreshortened the target appeared, the more bow-on or stern-on it was; the more the full profile was visible, the closer to 90 degrees crossing. Accurately estimating AOB was a trained skill that separated experienced submarine captains from novices. An error in AOB of just 10-15 degrees could mean the torpedo fired with a slightly wrong lead angle, causing a miss. The Torpedo Data Computer continuously used the AOB estimate as one of its key inputs to generate the final firing solution."""
},

{
"chunk_id": "pam_189",
"title": "How did submarines communicate with Pearl Harbor during a patrol?",
"text": """How did submarines communicate with Pearl Harbor during a patrol?

Radio communication between submarines on patrol and submarine headquarters at Pearl Harbor followed a carefully managed protocol designed to balance the need for information against the risk of radio direction finding (RDF) — the Japanese ability to detect and locate a transmitting submarine.

Submarines received traffic continuously. Pearl Harbor broadcast on a low-frequency schedule that submarines could receive while submerged or surfaced, using a trailing wire antenna. A submarine could stay current with headquarters orders, intelligence updates, and convoy position reports by simply copy the broadcast without ever transmitting — remaining completely silent and undetectable.

Transmitting from a submarine was avoided as much as possible. When a captain needed to send a contact report (reporting a sighting of enemy vessels), a sinking, or an emergency message, he would compose the shortest possible encoded transmission, surface briefly if necessary for better antenna height, transmit rapidly, and dive immediately. The message was encrypted using the Navy's communications codes, so the content was unreadable by the Japanese — but the transmission itself, even encoded, could be located by RDF at a range of hundreds of miles if Japanese shore stations triangulated simultaneously.

Ultra intelligence — decoded Japanese traffic — was sometimes used to vector submarines to specific convoy routes. These orders came via the broadcast, keeping the submarine entirely passive. The combination of one-way broadcast reception and rare, brief transmissions kept submarines as electronically invisible as possible."""
},

{
"chunk_id": "pam_190",
"title": "What was the forward engine room on a submarine?",
"text": """What was the forward engine room on a submarine?

Fleet submarines like Pampanito had two engine rooms — the forward engine room and the after engine room — each containing two large diesel engines for a total of four main engines. The forward engine room was located amidships, just aft of the crew's forward living spaces.

Each engine room contained two Fairbanks-Morse Model 38D-8⅛ opposed-piston diesels (on Pampanito's class). These engines drove electrical generators: on the surface, the generators powered the propulsion motors and charged the batteries simultaneously. The forward and after engine rooms were essentially identical in layout and function, giving the submarine redundancy — if any one engine or even a full engine room was disabled, the other could continue to provide power.

The engine rooms were among the noisiest and hottest spaces on the boat. Working in them while running at full speed was a physically demanding environment — the engines were enormous, the heat from four large diesel engines operating at high load was intense, and the noise level made normal communication impossible without shouted words directly into the ear. Engine room personnel wore ear protection.

The engines required constant maintenance: oil changes, fuel injection system service, cooling water monitoring, and mechanical adjustments. The machinist's mates and motor machinist's mates assigned to the engine rooms were among the most technically skilled enlisted men aboard, responsible for keeping the prime movers of the submarine running reliably on patrols that could last 60-75 days from any repair facility."""
},

{
"chunk_id": "pam_191",
"title": "How did submarines navigate to their patrol areas from Pearl Harbor?",
"text": """How did submarines navigate to their patrol areas from Pearl Harbor?

The transit from Pearl Harbor to a patrol area in the central or western Pacific was itself a significant navigation challenge — distances measured in thousands of miles, with no landmarks and no GPS. Submarines relied on a combination of celestial navigation and dead reckoning.

On the surface at night, the navigator used a sextant to shoot star sights (measuring the altitude of known stars above the horizon) and calculated the submarine's precise position from those astronomical observations using spherical trigonometry and pre-computed tables. A skilled navigator could fix the submarine's position to within a mile or two using star sights taken at morning and evening twilight. Sun lines were taken at noon for a noon latitude fix.

Submerged during the day (when in potentially hostile waters), the boat navigated by dead reckoning: tracking course, speed, and time from the last known position to estimate current position. The submarine's log (a device measuring speed through the water) and the gyrocompass provided the inputs. Dead reckoning accumulated error over time — currents, compass drift, and small speed errors all added up — which is why surface position fixes by celestial navigation were essential every night.

Approaching the patrol area, the captain used more frequent periscope observations to cross-check the navigator's estimate against recognizable landmasses, landmarks, or coastal soundings. The accuracy required to navigate safely through narrow straits or mine-suspected channels demanded meticulous navigation work throughout the entire transit."""
},

{
"chunk_id": "pam_192",
"title": "How did submarine captains decide when to surface?",
"text": """How did submarine captains decide when to surface?

The decision to surface was one of the most consequential a submarine captain made regularly — it was the moment of greatest vulnerability and also of operational necessity. Batteries needed recharging, fresh air was needed to ventilate the boat, and the higher surface speed allowed repositioning for the next day's patrol.

The standard pattern was to surface at or shortly after dark. The captain would order a thorough periscope sweep of the horizon and sky before surfacing — checking for ships, aircraft, and anything suspicious. Radar was used to check for contacts before the bridge watch was sent topside. Only when satisfied that the immediate area was clear would the captain order the ballast tanks blown and the crew to surface stations.

Factors influencing the timing included: remaining battery charge (how urgent was recharging?), the distance to potentially hostile shipping routes (closer = riskier to surface), moon phase (a full moon made the submarine visible; new moon favored surfacing), sea state (rough seas were both uncomfortable and reduced visibility for enemy lookouts and aircraft), and any specific tactical situation. In waters close to Japanese airfields or with known air patrols, surfacing in the early hours before dawn — when Japanese air patrols were least active — was sometimes preferred over surfacing at dusk when evening patrols were possible.

The captain never delegated the surfacing decision itself. However careful the preparation, surfacing in enemy waters was always a calculated risk."""
},

{
"chunk_id": "pam_193",
"title": "What was the escape trunk on a submarine?",
"text": """What was the escape trunk on a submarine?

The escape trunk (also called the escape hatch) was a small flooding chamber built into the pressure hull of a fleet submarine, designed to allow crew members to escape from a sunken submarine. Fleet submarines had two: one in the forward torpedo room and one in the after torpedo room — the same hatches that also served as access points for loading torpedoes.

The escape trunk worked as an airlock: the inner hatch was sealed, the chamber was flooded with water until the pressure equalized with the outside water pressure, then the outer hatch was opened and the crew member could swim to the surface. Each man wore a rebreather device (the Momsen lung) that recycled exhaled breath through a CO₂ absorbent canister, providing a small air supply for the ascent.

In practice, the escape trunk was of limited usefulness in actual wartime conditions. It required the submarine to be on the bottom in relatively shallow water (not more than 100-150 feet) with at least one compartment intact, pressure below crushing depth, and crew members who had trained on the device and could remain calm enough to use it while the boat was flooding. Most wartime submarine sinkings did not meet these conditions — they occurred at depth, through violent destruction, or in circumstances that left no time or structural integrity for escape. The escape trunk was a last-resort tool, and few men used it successfully during the war."""
},

{
"chunk_id": "pam_194",
"title": "How did sonar operators track enemy ships on a submarine?",
"text": """How did sonar operators track enemy ships on a submarine?

The sonar operator — typically a rated sonarman or an experienced petty officer trained in sound listening — worked at the sonar station in the forward torpedo room or control room, wearing headphones and listening to the ocean through the submarine's hydrophone arrays. His job was to detect, identify, classify, and track any acoustic contacts.

Passive listening was the primary technique. The operator would slowly rotate the sonar head through the water, listening for the distinctive sounds of propellers. Different ships made different sounds: a destroyer's high-speed turbines produced a high, whirring scrape; slow merchant diesels produced a lower, rhythmic thudding; propeller blade count and rpm gave a rough indication of ship type and speed. An experienced sonarman could estimate how many propellers a contact had and whether it was approaching or receding based on pitch change (the Doppler effect).

When tracking an attacking destroyer, the operator became as important as the captain. His reports — "contact bearing 020, getting closer," "contact drawing left, bearing now 010" — gave the captain the information needed to evade. When the sonarman reported "pinging" (active sonar transmissions from an enemy vessel), it meant they had been detected and the counter-attack was imminent. The interval between pings told the captain how far away the attacker was and whether its sonar was in contact with the submarine. Sonarmen who could maintain calm, continuous tracking data during a depth charge attack were invaluable."""
},

{
"chunk_id": "pam_195",
"title": "What was the role of the chief of the boat on a submarine?",
"text": """What was the role of the chief of the boat on a submarine?

The chief of the boat (COB) was the senior enlisted man aboard the submarine — typically a chief petty officer or master chief — and the most important non-commissioned position on the boat. He was the primary link between the enlisted crew and the officers, serving as both the crew's advocate and the enforcer of standards and discipline below the officer level.

The COB's responsibilities included: supervising the enlisted watch bill in coordination with the executive officer, maintaining crew discipline and morale, managing the boat's daily administrative routine for enlisted personnel, monitoring the physical condition of the submarine's systems with the department heads, and advising the captain directly on crew matters. The COB was expected to know every enlisted man — his performance, his personal situation, his strengths and problems — and to bring issues to the officers' attention before they became crises.

During depth charge attacks and battle stations, the COB typically took the diving station in the control room, managing the ballast and trim to execute the captain's maneuvers. He was responsible for the boat's trim — the fore-and-aft balance — more than any other individual on a routine basis. A good COB who ran a tight, professional boat and looked after his crew was one of the defining characteristics of a successful submarine. Captains who had excellent chiefs of the boat were fortunate; those with weak or ineffective COBs often struggled to maintain the standards that a combat-ready submarine required."""
},

{
"chunk_id": "pam_196",
"title": "How did torpedo spreads work on a submarine?",
"text": """How did torpedo spreads work on a submarine?

A torpedo spread (also called a fan shot) was the technique of firing multiple torpedoes at a single target, with each torpedo's gyro angle set slightly differently so the weapons fanned out to cover a range of potential target positions. Rather than firing one torpedo at a precise predicted position, a spread sent three or four torpedoes covering slightly different tracks — accounting for uncertainty in the target's exact course and speed.

The standard spread for a large merchant or tanker target was typically three to four torpedoes, with the angles spread several degrees apart. The first torpedo was aimed at the target's expected bow position, the last at its expected stern, and the middle torpedoes covered the area between. If the target had not changed course, at least one or two torpedoes should hit. If the speed estimate was slightly off and the target was farther ahead or behind the predicted position, the spread increased the probability that at least one weapon would still connect.

The decision to fire a spread was the captain's. Firing more torpedoes improved hit probability but consumed the boat's limited supply. With 24 torpedoes total, firing four-torpedo spreads at every target would leave a submarine with very few shots for subsequent opportunities. Captains had to balance aggressive engagement (increasing damage to the enemy) against conservation (maintaining weapons for the remainder of a 60-75 day patrol). On a successful patrol, a submarine might fire 15-20 torpedoes and return with the remainder."""
},

{
"chunk_id": "pam_197",
"title": "How did submarines work together to avoid colliding with each other?",
"text": """How did submarines work together to avoid colliding with each other?

Deconflicting submarines operating in the same area — avoiding blue-on-blue (friendly submarine vs. friendly submarine) incidents — was a serious, and sometimes fatal, problem during World War II. Several US submarines were fired upon or sunk by other US submarines in cases of mistaken identity.

The primary method of avoiding collision and fratricide was geographic separation. Submarine command at Pearl Harbor assigned each submarine a specific patrol zone, and submarines operating in adjacent zones were on strictly defined boundaries. A submarine was expected to remain in its assigned area; crossing into another submarine's zone without explicit permission and coordination was forbidden.

For submarines operating in coordinated wolf packs, deconfliction was managed by assigning specific attack sectors and timing windows — one submarine attacked from one bearing while another waited, preventing simultaneous convergence. Voice radio on short-range frequencies allowed brief coordination between pack members.

The challenge was that in the dark ocean, a surfaced submarine looking for convoy targets and a friendly submarine transiting the same area could converge rapidly. Emergency identification signals — light blinker codes, specific radar emissions, radio challenges — helped, but only if both parties were alert. Several losses were attributed to friendly fire: USS Dorado (SS-248) was likely sunk by a US aircraft, and USS Grunion's loss has been attributed to a possible own-torpedo circular run. These tragedies drove continuous improvement in identification protocols throughout the war."""
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
