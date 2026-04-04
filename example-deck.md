# The Sense Lab, Inc.

## The emotional safety layer for embodied AI.

**Confidential Pre-Seed Pitch | $1.8M Raise**

> *[SLIDE FORMAT: 16:9. Clean white background. All illustrations rendered in navy blue ink, hand-drawn style with fine linework — architectural sketch aesthetic. No photography. No gradients. No color other than navy ink on white.]*

---

## Title Slide

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title at top: "The Sense Lab, Inc." Subtitle: "The emotional safety layer for embodied AI." Center: a humanoid robot in a minimalist kitchen facing a seated man at a counter. Between them, trajectory lines and coordinate annotations — "x: 14.5, y: 22.1," "THREAT VECTOR: 0.98." The robot is detailed; the man is sketched loosely. Bottom center box: "Confidential Pre-Seed Pitch."]*

---

## Slide 1 — The Problem

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title at top: "SOLVED. / UNSOLVED." Two panels divided by a vertical line. LEFT: robot placing a dish in a cabinet, kinematic vectors along each joint, annotation: "Perfect motion planning." RIGHT: robot extending a plate toward a seated woman whose shoulders are raised and body angled away, dashed stress waves from her torso, annotation: "Smiling but uncomfortable." Bottom banner: "Every robot OEM will hit this wall. The question is whether they have the software to see it coming."]*

**SPEAKING NOTES:** Boston Dynamics, Tesla, and Figure AI have solved how robots move. No sensor in any robot can see what that movement does to the human.

---

## Slide 2 — The Return Problem

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "The Robot That Makes You Flinch Gets Returned." Subtitle italic: "Consumer adoption is a comfort problem, not a hardware problem." Three panels. PANEL 1 "WEEK 1": man grinning at new robot, "$15,000" speech bubble. Below: "Novelty." PANEL 2 "WEEK 3": same man tense, arms crossed, robot passing behind. Below: "Tolerance." PANEL 3 "MONTH 2": robot alone on a closet shelf with return label. Below: "Return." Bottom banner: "Robots need a comfort function to be commercially viable."]*

**SPEAKING NOTES:** No OEM can absorb a 30-40% return rate on a $15,000 product. The mechanical performance is irrelevant if the human stops coexisting with it.

---

## Slide 3 — Why It Doesn't Go Away

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "But humans will get used to it?" Two columns divided by vertical line. LEFT "IF BEHAVIORAL": robot and human icons relaxed, clock with curved arrow. "Exposure solves it. Familiarity breeds comfort." RIGHT "IF BIOLOGICAL": robot with sonar waves, human bracing, clock with X. "Nothing solves it. The ANS computes threat regardless of exposure." Below both: horse sketch in profile — ears pinned, weight back, head raised. Bold italic: "Horses have lived alongside humans for 6,000 years. They still spook." Bottom banner: "The answer determines the size of the market."]*

**SPEAKING NOTES:** If discomfort is behavioral, it fades with exposure and this is a small, temporary market. If it's biological — an autonomic response — middleware is essential and the market is permanent.

---

## Slide 4 — The Product

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "The Empathy Engine." Subtitle italic: "A hardware-agnostic emotional safety layer that runs on the edge." Two circular loop diagrams. LEFT LOOP "THE FAST LOOP: PREDICTION": Robot Trajectory → Kinematic Model → P(discomfort | t+2s) → Select safest path. Center: "Prevents." Below: "Input: trajectory + human position. Output: predicted comfort 2s ahead." RIGHT LOOP "THE SLOW LOOP: REWARD": Robot Action → Comfort Scorer → Reward Signal → Update behavioral policy. Center: "Learns." Below: "Input: facial AUs, body pose, rPPG. Output: comfort score for RL training."]*

**SPEAKING NOTES:** Two loops. The fast loop is a physics problem — predicting comfort from trajectory, closing speed, and approach angle. Tractable. The slow loop reads arousal from camera — harder, but it operates as a reward signal for RL, not a safety system. Needs to be directionally correct, not clinically precise. OEMs need both. We provide both.

---

## Slide 5 — The Core Insight

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "The Signal Is Already Visible. The Labels Are Not." Two panels. LEFT "WHAT THEY TRAIN ON": man's face with exaggerated shock expression, large X over it. "Actors. Trained on performance." RIGHT "WHAT WE TRAIN ON": woman's face near-neutral — slight brow tension, gaze averted. Next to her, small biosensor traces: EDA spike, HRV compression. "Visible cues calibrated against biological ground truth." Below both: "They label performances. We label biology."]*

**SPEAKING NOTES:** Any human in the room can tell when someone is uncomfortable. The signal is already visible. The problem is labeling — existing emotion AI trains on performances, not on moments of genuine autonomic activation. We use biosensors to label when the biology fires, then train a model to recognize which visible cues predicted it.

---

## Slide 6 — The Scientific Approach

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Humans Already Read This Signal. We Calibrate It." TOP HALF: a woman at a kitchen table, someone approaching from her left. Annotation lines to visible cues: "Shoulder elevation." "Micro-lean away." "Jaw tension." "Gaze aversion." "Grip tightening." Label: "The signal is already visible." BOTTOM HALF: two-layer diagram. TOP LAYER (dashed border) "THE TEACHER": same woman wearing biosensors, four waveforms converging to "GROUND TRUTH." BOTTOM LAYER (solid border) "THE STUDENT": robot camera view of same woman without sensors, visible features feeding into "Predicted Comfort Score." Arrow between layers: "Knowledge distillation."]*

**SPEAKING NOTES:** The teacher stack exists solely to provide calibration — it tells us when discomfort is real versus performed. The student learns which visible cues reliably predict the biological moment. The raise builds the teacher. The product ships the student.

---

## Slide 7 — The Data Pipeline

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Three Stages. One Dataset No One Else Can Build." Three columns left to right with arrows between. COLUMN 1: university icon. "STAGE 1: CONTROLLED VALIDATION. Months 4-7." Small room diagram: two figures, sensor rig, "STOP" bubble. COLUMN 2: handshake/shield icon. "STAGE 2: HIGH-AROUSAL CAPTURE. Months 8-14." Person with sensor rig, biometric waveforms flowing into funnel. COLUMN 3: robot icon. "STAGE 3: DEPLOYMENT TELEMETRY. Continuous." Fleet of robots with upward data arrows. Bottom arrow: "Increasing arousal → Increasing ecological validity → Increasing scale."]*

**SPEAKING NOTES:** Stage 1 at Stanford: expectation-violation studies with biosensors + RGB. Stage 2 with consent-expert communities: genuine high-arousal boundary negotiation. IRB-equivalent consent, anonymized data, expert collaborators. Stage 3: every deployed robot returns data. The model improves with every unit shipped.

---

## Slide 8 — Why This Data Matters

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Acting vs. Biology." Two panels with "≠" between. LEFT "ACTOR PERFORMING FEAR": exaggerated face. Below: flat EDA trace, flat EEG. "The camera sees drama. The biology shows nothing." RIGHT "GENUINE BOUNDARY VIOLATION": near-neutral face with subtle shoulder rise, jaw tension. Below: EDA spike, EEG potential. "The camera sees subtle cues. The biosensors confirm they're real."]*

**SPEAKING NOTES:** The dataset gap isn't about invisible signals. It's about knowing which visible cues correspond to genuine autonomic events versus social performance. Without biosensor ground truth during real arousal, you can't tell the difference.

---

## Slide 9 — The Team

> *[VISUAL — 16:9, white background. Title: "The Team to Execute." Two columns. LEFT: Amelie's headshot (circular crop), name and title. Below, five small navy ink vignettes connected by downward arrows: (1) bed + heart waveform "Heart rate from a shared bed." (2) car seat + cardiac trace "Heart rate from a moving car." (3) shoe + waveform "Heart rate from a shoe." (4) barn floor + pig "Pig health from floor vibrations." (5, larger) RGB camera + arousal waveform "Autonomic state from a camera. This study." RIGHT: Justin's headshot (circular crop), name and title. Below, exploded-view diagram of sensor components converging into single synchronized data stream.]*

**Amelie Bonde, CEO** — PhD CMU. Post-Doc Stanford, Structures as Sensors Lab. 20+ papers, 400+ citations. Extracted heart rate from floor vibrations, car seats, and shoes. Built PigNet/PigSense for livestock monitoring. Career pattern: biological signal extraction from dismissed channels.

**Justin Lange, CPO** — Technical founder, former CTO LynQ Technologies (Techstars). 10+ utility patents. Shipped manufactured sensing hardware through FCC certification. Builds the synchronized multi-sensor capture pipeline.

---

## Slide 10 — Competitive Landscape

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Why Not Them." Three columns with dividers. LEFT "PHYSICAL SAFETY": shield icon. "3Laws Robotics. Collision avoidance. THE LIMIT: No model of comfort." CENTER "EMOTION AI": theatrical mask icon. "Hume / Affectiva. Expression classification. THE LIMIT: Trained on fake data. No spatial context." RIGHT "SENSE LAB": brain+camera icon. "Comfort prediction. Trained on biology. Ships on a camera." Bottom banner: "3Laws stops the hit. Emotion AI detects the upset. Sense Lab prevents the moment."]*

**SPEAKING NOTES:** Adjacent work, different problem. 3Laws prevents contact but has no model of whether the human is comfortable. Emotion AI reads emotion after it happens — no spatial model, no trajectory input, trained on performed expressions. We predict comfort from approach dynamics, trained on genuine autonomic response.

---

## Slide 11 — Scientific Foundation

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Is the Signal Real?" LEFT: four rows of before/after pairs — foot→ID waveform, car seat→cardiac trace, shoe→heart waveform, pig→health readout — each labeled with Bonde citation. Divider, then fifth row larger: RGB camera→arousal waveform "This study." RIGHT: three paper rectangles. "SympCam 2024: face video → EDA, r = 0.77." "CDGKD 2025: EEG teacher → visual student." "Makantasis 2021: LUPI, no accuracy drop without sensors."]*

**SPEAKING NOTES:** We don't claim this is easy. We claim it's tractable for this team. SympCam achieved 0.77 correlation predicting arousal from face video. The distillation paradigm works. Amelie's career is a series of "impossible" signal extractions that she published. If the Stanford study produces r > 0.5, we've validated the thesis. Specific, falsifiable, 18-month hypothesis.

---

## Slide 12 — Defensibility

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "The Moat Is the Dataset." Three geological strata in cross-section. BOTTOM (heaviest line): "THE PAIRED DATASET" — synchronized waveforms + face mesh on same timeline. MIDDLE: "THE MODEL" — neural network diagram, inputs (AUs, pose, rPPG) → comfort score. TOP (dotted): "DEPLOYMENT TELEMETRY" — robot icons with upward data arrows. Right edge: "TIME →" arrow.]*

**SPEAKING NOTES:** Moat 1: paired biosensor + RGB data during genuine arousal. 18+ months to replicate. Moat 2: the distilled model encodes biology that can't be recovered from weights alone. Moat 3: every shipped robot returns data. Core architecture is proprietary with provisional patent protection. Stanford validation licensed exclusively back through OTL.

---

## Slide 13 — The Market

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "The Market for Human-Safe Robotics." Two columns. LEFT "THE BEACHHEAD 2026-2028": clipboard with risk gauge in red zone. List of 6 company names (Agility, Apptronik, 1X, Unitree, Fourier, Sanctuary) bracketed "Resource-constrained." Separate bracket (Figure, Tesla, BD) "Later." RIGHT "THE PLATFORM MARKET 2030+": three industry estimate bars. Large hand-drawn "$3-5B." Bottom banner: "The return rate on a $15,000 home robot determines whether this market exists. We determine the return rate."]*

**SPEAKING NOTES:** 15-30 OEMs deploying human-proximate robots. Entry point: pre-launch risk assessment — we quantify which movements drive returns before units ship. $50-200K per engagement. Primary targets are resource-constrained companies who can't build this internally. The Stanford paper is the sales tool. Near-term opportunity: $1-3M.

---

## Slide 14 — Revenue Model

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "How We Make Money." Three horizontal bars stacked, each wider than the one above. Bar 1: "PRE-LAUNCH RISK ASSESSMENT — $50K-$200K per engagement." Bar 2: "EMBEDDED SDK — $30-$100 per robot." Bar 3: "CONNECTED PLATFORM — $10-$30 per robot/month." Right edge: simple vertical arrow.]*

**SPEAKING NOTES:** Phase 1 is project-based risk assessment — no integration required. Phase 2 is per-unit SDK licensing, Mobileye model. Phase 3 is SaaS with comfort analytics and model updates.

---

## Slide 15 — Use of Funds

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Use of Funds." LEFT: table with five rows, each with small icon. Sensor stack $150K. Stanford studies $350K. Community capture $200K. Model development $300K. Founder runway $475K. Reserve $325K. RIGHT: vertical timeline with five milestone nodes from Month 3 to Month 18. TOP RIGHT: bordered box "$1.8M / $15M Cap. SAFE. 20% Discount."]*

**SPEAKING NOTES:** Milestones: Month 3-4 sensor pipeline operational. Month 5-7 Stanford study complete, paper drafted. Month 7-8 paper submitted, OEM outreach begins. Month 8-12 community deployment. Month 12-15 student model v1. Month 15-18 first OEM engagement, seed raise begins. We are raising to build the dataset and the model.

---

## Slide 16 — The Close

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title large bold: "Make robots feel safe to be around." Center: robot sitting at kitchen table across from elderly woman, extending a cup of tea. Both at ease — woman reaching for cup, relaxed posture, faint smile. Kitchen sketched minimally. Below illustration italic: "So the consumer market for autonomous robots can finally become real."]*

**SPEAKING NOTES:** The next trillion-dollar hardware platform needs a psychology layer. We are building the science to train it and the model to ship it.

---

## Appendix

*The following slides are available for deep-dive discussions and due diligence.*

---

## Appendix A — The Teacher-Student Architecture

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "How Distillation Works." TOP "TRAINING": human wearing sensors. Four teacher streams (eye tracking, EDA, EEG, ECG) converge to "TEACHER MODEL → Ground Truth: 0.73." Separately, RGB camera feeds three student channels (rPPG, Facial AUs, Body Pose) into "STUDENT MODEL → Predicted: ?" Loss arrow: "L = |teacher - student|²." BOTTOM "DEPLOYMENT": robot with single camera. Student model standalone → "Predicted: 0.71" → motion planner. Teacher streams crossed out "Not needed."]*

**SPEAKING NOTES:** Training: both models observe the same person simultaneously. Teacher provides ground truth. Student learns to predict it from camera alone. Deployment: only the student ships. Replicating the model requires replicating the dataset.

---

## Appendix B — The Experimental Protocol

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Hacking the Autonomic Nervous System." Four top-down room diagrams in 2x2 grid. (1) "BROKEN CONTRACT": two figures, "STOP" bubble, researcher continues past, burst symbol. (2) "TAU ACCELERATION": approaching figure, speed arrows increasing at 6ft mark. (3) "PERIPHERAL APPROACH": subject at counter, researcher from 135°, startle waveform. (4) "MULTI-AGENT": 8-10 figures with crossing trajectory lines.]*

**SPEAKING NOTES:** Experiment 1: subject says stop, researcher ignores it. ANS fires in 1.5 seconds. Experiment 2: approach speed increases imperceptibly by 15% at 6 feet. Experiment 3: approach from blind spot during distraction task. Experiment 4: multi-person spatial negotiation. All capture paired biosensor + RGB.

---

## Appendix C — Research Foundations

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Seven Traditions. One Missing System." Seven horizontal timeline tracks left to right, decade markers 1950s-2020s. Track 1 "PROXEMICS": Hall 1966, Burgoon 1988, Sorokowska 2017. Gap: "defined the zones — never measured the alarm." Track 2 "PERIPERSONAL SPACE": Rizzolatti 1981, Graziano 1994, Kennedy 2009. Gap: "found the alarm neurons — never built a detector." Track 3 "TAU / LOOMING": Schiff 1962, Lee 1976, Sun & Frost 1998. Gap: "proved threat from closing speed — never left the highway." Track 4 "NONVERBAL COMMUNICATION": Birdwhistell 1952, Ekman 1978, Barrett 2019. Gap: "catalogued visible signals — never checked the wiring underneath." Track 5 "AFFECTIVE COMPUTING": Picard 1995, Affectiva 2009, Hume 2021. Gap: "trained on actors — never on genuine arousal during approach." Track 6 "KNOWLEDGE DISTILLATION": Vapnik 2009, Hinton 2015, MT-PKDOT 2024. Gap: "proved the method — never applied to comfort." Track 7 "HRI COMFORT": Kulić 2007, Takayama 2009, AFFECT-HRI 2024. Gap: "collected ground truth — never distilled into a deployable sensor." All converge to "SENSE LAB 2026."]*

**SPEAKING NOTES:** Each field asked its own question for decades. They are all the same question: what does the body's alarm look like from the outside, and can a camera learn to read it?

---

## Appendix D — Why Not Build In-House

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Why OEMs Won't Build This Themselves." Three sections with icons. (1) Mismatched puzzle pieces: "THE EXPERTISE GAP." (2) Robot with data arrow ✓, human with missing arrow ?: "THE DATA PROBLEM." (3) Car with sensor box and lock-in arrow: "THE MOBILEYE PRECEDENT."]*

**SPEAKING NOTES:** Different discipline. No OEM has the paired dataset. Switching cost exceeds renewal cost once the SDK is embedded.

---

## Appendix E — Why Not Off-the-Shelf Emotion AI

> *[VISUAL — 16:9, white background, navy blue ink hand drawing: Title: "Why Hume and Affectiva Can't Pivot Here." Two paths. LEFT "THEIR DATA": actor face → model → "emotion label." X through output. RIGHT "OUR DATA": near-neutral face + ECG + EDA + EEG → teacher → student (rPPG + AUs + pose) → "comfort score + 2s prediction." Checkmark.]*

**SPEAKING NOTES:** Their training data is wrong — performances, not biology. Their architecture is wrong — categorical labels, not continuous comfort. Their domain is wrong — faces on screens, not bodies in rooms with approaching machines. Rebuilding their pipeline puts them where we are today.