# Literature Review: Virtual Reality + Artificial Intelligence for Disaster Management & First-Responder Training

**Date:** 2 March 2026  
**Scope:** VR (and XR where relevant) combined with AI for disaster preparedness, response, recovery, and first-responder training (firefighters, EMS/EMT, SAR, civil defense, incident commanders).

---

## 1. Search Strategy

### Databases Searched
- **PubMed / PMC** (288 results screened from broad query)
- **Semantic Scholar** (20+ targeted queries)
- **Frontiers** (16,682 results screened, top hits reviewed)
- **ScienceDirect / Elsevier**
- **IEEE Xplore** (via Semantic Scholar cross-refs)
- **ACM Digital Library** (via Semantic Scholar cross-refs)
- **Springer Link**

### Keyword Combinations Used
1. `("virtual reality" OR VR) AND ("intelligent tutoring" OR "AI tutor" OR "virtual instructor" OR coaching) AND (emergency OR disaster OR firefighting OR first responder)`
2. `VR AND (protocol training OR guideline compliance OR SOP) AND (EMT OR firefighting OR incident command)`
3. `VR AND (reinforcement learning OR procedural content generation OR adaptive scenario) AND (evacuation OR disaster training)`
4. `VR AND (automated assessment OR performance analytics OR debriefing) AND emergency training`
5. `"virtual reality" AND ("BDI agent" OR "multi-agent") AND emergency training`
6. `"virtual reality" AND ("eye tracking" OR biosensor) AND ("first responder" OR firefighter) AND assessment`
7. `"digital twin" AND VR AND disaster emergency training AI`
8. `VR AND "crowd simulation" AND "agent behavior" AND emergency evacuation training`
9. `AUGGMED OR XVR OR ADMS AND VR AND emergency training`

### Inclusion Criteria
- VR/XR system with at least one AI component (tutoring, evaluation, scenario generation, or agent intelligence)
- Domain: disaster management, emergency response, first-responder training
- Preference for implemented prototypes/pilots; conceptual papers clearly labeled
- English-language, 2006–2026

---

## 2. Master Table of Included Systems

| # | Citation (APA) | Year | Domain | AI Role | Protocol Training? | VR Stack | Metrics | Link/DOI |
|---|---|---|---|---|---|---|---|---|
| 1 | Lourdeaux, D., Afoutni, Z., Ferrer, M.-H., Sabouret, N., et al. VICTEAMS: A virtual environment to train medical team leaders. *IVA '19*, ACM. | 2019 | Military/disaster medical team leadership | **Trainer + Agents**: BDI-based subordinates + ITS pedagogical director adapting difficulty | Y — Non-technical leadership skills, triage prioritization | Custom VR environment | Learner profile, communication quality, leadership NTS | [10.1145/3308532.3329418](https://doi.org/10.1145/3308532.3329418) |
| 2 | Nguyen, V. T., Jung, K., & Dang, T. VRescuer: A VR application for disaster response training. *IEEE AIVR 2019*. | 2019 | Disaster response / urban SAR | **Agents + Scenario**: AI ambulance agent with autonomous path planning; real-time re-routing | Y — Disaster response protocols | Unity3D, Oculus Rift | Usability (n=20), path optimality, interference handling | [10.1109/AIVR46125.2019.00042](https://doi.org/10.1109/AIVR46125.2019.00042) |
| 3 | Kman, N. E., Price, A., Berezina-Blackburn, V., et al. First Responder VR Simulator (FRVRS). *J Am Coll Emerg Physicians Open*, 4(1), e12903. | 2023 | MCI triage (EMS/prehospital) | **Scenario + Evaluator**: Programmable patient acuity/count, automated triage tracking | **Y — SALT Triage** | Wireless VR HMD, desktop-linked | Triage accuracy, treatment correctness, navigation, automated AAR | [10.1002/emp2.12903](https://doi.org/10.1002/emp2.12903) |
| 4 | Way, D. P., Panchal, A. R., Price, A., et al. Learner evaluation of an immersive VR MCI simulator for triage training. *BMC Digital Health*, 2(1), 56. | 2024 | MCI triage (EMS) | **Evaluator**: Automated assessment + post-encounter debriefing (FRVRS system) | **Y — SALT Triage** | Same FRVRS (wireless HMD) | Satisfaction (95%), realism (95%), recommendation rate (95%), n=375 | [10.1186/s44247-024-00117-5](https://doi.org/10.1186/s44247-024-00117-5) |
| 5 | Baetzner, A. S., Hill, Y., Roszipal, B., et al. MCI training in immersive VR: Multimethod performance indicators. *J Med Internet Res*, 27, e63241. | 2025 | MCI triage (paramedics, EM physicians) | **Evaluator**: Eye-tracking analytics for automated multi-method performance assessment | Y — MCI triage categories | Immersive VR + integrated eye tracking | Triage accuracy (d=0.48), speed (d=0.42), info transmission (d=1.13), gaze patterns, n=76 | [10.2196/63241](https://doi.org/10.2196/63241) |
| 6 | Agarwal, J. & Shridevi, S. Procedural content generation using RL for disaster evacuation training in a virtual 3D environment. *IEEE Access*. | 2023 | Disaster evacuation (civilian) | **Scenario engine**: RL-based PCG dynamically generates evacuation scenarios | N | Virtual 3D environment | Evacuation task performance, disaster preparedness | [10.1109/ACCESS.2023.3314120](https://doi.org/10.1109/ACCESS.2023.3314120) |
| 7 | Doroudian, S. & Dorodchi, M. Optimizing rescue mission strategies: Integrating human intuition with AI efficiency in VR using RL. *IEEE AIIoT 2025*. | 2025 | Search & rescue | **Scenario + Agents**: RL optimizes rescue strategy, resource management, mission planning | Not explicit | VR simulation | Rescue speed, survivors saved, resource management, mission success | IEEE AIIoT 2025 |
| 8 | Liaw, S. Y., Tan, J. Z., Lim, S., et al. AI in VR simulation for interprofessional communication training. *Nurse Educ Today*, 122, 105718. | 2023 | Emergency nursing / interprofessional communication | **Agent + Coach**: AI doctor avatar (NLP/dialogue) for nurse-physician communication | Y — SBAR-like communication frameworks | VR simulation platform | Communication knowledge, self-efficacy, usability, human-likeness, 157 cit. | [10.1016/j.nedt.2023.105718](https://doi.org/10.1016/j.nedt.2023.105718) |
| 9 | Gutiérrez Maquilón, R., Uhl, J., Schrom-Feiertag, H., & Tscheligi, M. GPT-based AI virtual patients for MFR communication training. *JMIR Form Res*. | 2024 | EMS / prehospital MFR (traffic accident) | **Agent**: LLM (GPT-4) virtual patient for verbal assessment; TTS integration | Y — MFR patient assessment verbal protocols | MR simulation, ChatGPT API | Usability (MOS-X, SASSI), n=24 MFRs | [10.2196/58623](https://doi.org/10.2196/58623) |
| 10 | Dib, N., Alattas, N., et al. EMT VR — A gamified emergency response training system using VR and AI. *IEEE SWC 2023*. | 2023 | EMS / EMT | **Scenario + Evaluator**: AI-assisted scenario generation + AI certification exam | **Y — UAE national EMT protocols** | Immersive VR HMD, 3D ER simulation | Certification exam scores, training scenario completion | [10.1109/SWC57546.2023.10449292](https://doi.org/10.1109/SWC57546.2023.10449292) |
| 11 | Sirandass, H., Jaiswal, C., & Sukumar, M. Q-VMedSim: A training platform for emergency response through VR and AI. *IEEE AIIoT 2025*. | 2025 | Emergency medical procedures | **Trainer**: AI virtual medical assistant guides procedure training | Y — Emergency medical procedures | Unity + C#, VR-based | Procedure completion, training effectiveness | IEEE AIIoT 2025 |
| 12 | Dini, A., Schneeberger, M., Pszeida, M., Heiler, L., & Paletta, L. Immersive skill training for first responders with biosensor-based SA assessment. *AHFE 2023*. | 2023 | Firefighting (squad leader) | **Agents + Evaluator**: AI-driven team member movement; ML-based biosensor analytics (eye-tracking, HR, EDA, temp) | Y — Situation reporting | VR HMD + eye-tracking, Cyberith Virtualizer, wearable biosensors | SART, PVT, determination test, SA biomarkers, cognitive flexibility | [10.54941/ahfe1003979](https://doi.org/10.54941/ahfe1003979) |
| 13 | Paletta, L., Schneeberger, M., et al. Digital human factors measurements in first responder VR-based skill training. *iLRN 2022*, IEEE. | 2022 | First responder (situation reporting) | **Evaluator**: Computational psychophysiological assessment of cognitive-emotional stress | Y — Situation reporting protocols | Flexible VR training environment + biosensors | Cognitive-emotional stress, situation report quality | IEEE iLRN 2022, doi:10.1109/... |
| 14 | Reim, L., Kallus, K. W., et al. VR-based first responder training under physiological and cognitive-emotional strain. *AHFE 2022*. | 2022 | First responder (firefighting) | **Evaluator**: Biosensor-based strain assessment | Y — Decision-making under stress | Immersive VR + biosensor integration | Physiological strain, decision quality under stress | [10.54941/ahfe1001840](https://doi.org/10.54941/ahfe1001840) |
| 15 | Mehta, R. K., Kang, J., Shi, Y., & Du, J. Effectiveness of training under stress in immersive VR: Firefighter gaze entropy and pupillometry. *Front. Virtual Reality*. | 2025 | Firefighting | **Evaluator**: Eye-tracking gaze entropy + pupillometry for cognitive state analysis | Not explicit (visuospatial emergency tasks) | Immersive VR + eye-tracking HMD | Task performance, gaze entropy, pupil dilation, workload, anxiety, n=40 firefighters | [10.3389/frvir.2025.1542507](https://doi.org/10.3389/frvir.2025.1542507) |
| 16 | Spain, R. D., Saville, J. D., et al. VR-based emergency response scenario and intelligent UI for first responders. *HFES Annual Meeting*. | 2020 | Firefighting (structural fire) | **Trainer**: Intelligent user interface providing real-time SA cues on firefighter HUD | Y — Firefighter operational tasks | Desktop VR, prototype intelligent UI | Usability with active firefighters | [10.1177/1071181320641513](https://doi.org/10.1177/1071181320641513) |
| 17 | Saville, J. D., Spain, R. D., et al. Evaluating usability of a next-gen HUD for firefighters in VR. *HFES Annual Meeting*. | 2022 | Firefighting | **Trainer**: Context-aware AR HUD with real-time task info/alerts | Implicit (structural firefighting tasks) | Desktop VR + AR HUD prototype | Usability study | [10.1177/1071181322661199](https://doi.org/10.1177/1071181322661199) |
| 18 | Saunders, J., Gibson, H., Leitão, R., & Akhgar, B. AUGGMED: Multiplayer serious games for first responder training. *EU H2020*. | 2017 | Counter-terrorism, multi-agency response | **Scenario + Agents**: AI-driven civilian/threat NPCs, adaptive multiplayer scenarios | Y — Multi-agency interoperability protocols | Unity-based serious game, multiplayer VR | Multi-agency coordination, scenario adaptability | EU H2020 AUGGMED |
| 19 | Sharma, S., Devreaux, P., et al. AI agents for crowd simulation in immersive environment for emergency response. *IS&T ERVR 2019*. | 2019 | Disaster evacuation (bomb attack) | **Agents**: AI-controlled crowd agents interacting with user-controlled agents in CVE | Implicit (disaster response decision-making) | CAVE-like immersive CVE | Agent behavior fidelity, evacuation decision quality | [10.2352/issn.2470-1173.2019.2.ervr-176](https://doi.org/10.2352/issn.2470-1173.2019.2.ervr-176) |
| 20 | Shendarkar, A., Vasudevan, K., Lee, S., & Son, Y. Crowd simulation for emergency response using BDI agents based on VR. *Winter Simulation Conf.* | 2006 | Evacuation / counter-terrorism | **Agents**: BDI agents for realistic crowd evacuation behavior | N — Focuses on crowd modeling | VR environment (simulation-based) | Route behavior, 138 citations (seminal BDI+VR crowd work) | ACM DL 1218216 |
| 21 | Danial, S. N., Smith, J. A., Khan, F., & Veitch, B. Human-like sequential learning of escape routes for VR agents. *Fire Technology*, 55, 1057–1083. | 2019 | Fire evacuation / emergency egress | **Agents**: Sequential learning algorithm for human-like NPC escape behavior | N | VR environment | Route optimality, human-likeness of paths | [10.1007/s10694-019-00819-7](https://doi.org/10.1007/s10694-019-00819-7) |
| 22 | Liu, Y. Closed-loop neuro-adaptive counter-terrorism training model for VR-based BCI simulation. *ICMNWC 2025*, IEEE. | 2025 | Counter-terrorism | **Scenario engine**: EEG-BCI closed-loop adaptive scenario (threat density, difficulty, cues adapt to neural state) | Implicit (mission progression) | VR + EEG BCI headset | Precision 0.89, recall 0.79, F1 0.82 | IEEE ICMNWC 2025 |
| 23 | Truong, H., Qi, D., et al. VR AI-enhanced simulation training for OR fire response. *Surg. Endoscopy*. | 2021 | OR fire emergency (hospital) | **Evaluator**: AI-enhanced pass/fail assessment for fire response protocol | **Y — RACE protocol, fire extinguisher use** | VR HMD simulation | Multi-attempt tracking, pass/fail, team response | [10.1007/s00464-021-08602-y](https://doi.org/10.1007/s00464-021-08602-y) |
| 24 | Chan, M. M. K., Cheung, D. S. K., et al. AI-powered VR simulation for clinical handover training. *Nurse Educator*. | 2025 | Emergency clinical handover | **Trainer + Agent**: ChatGPT-driven adaptive ISBAR avatar for handover practice + gamification | **Y — ISBAR protocol** | Immersive VR, 3-layer architecture, real-person avatar | Handover accuracy, communication quality | [10.1097/NNE.0000000000002018](https://doi.org/10.1097/NNE.0000000000002018) |
| 25 | Xiong, K., Li, J., et al. AI-VR escape room for disaster nursing education. *Nurse Educ Practice*, 88, 104529. | 2025 | Disaster emergency nursing | **Scenario engine**: ChatGPT generates escape room narrative/puzzles | N | Insta360 X3, Blender, 360° web (not HMD) | Acceptance (n=247), SUS usability, qualitative | [10.1016/j.nepr.2025.104529](https://doi.org/10.1016/j.nepr.2025.104529) |
| 26 | Huang, C., Zhang, J., & Song, W. LLM and VR empowering building fire safety training. *Fire Safety Journal*, Jan 2026. | 2026 | Building fire safety | **Scenario + Trainer**: LLM combined with VR for fire safety instruction | Likely (fire safety procedures) | VR (specifics behind paywall) | Performance comparison: VR vs. video-based | *Fire Safety J.* Jan 2026 |
| 27 | Fan, P. M., Zhuang, Y., et al. GenAI for automated assessment and feedback in VR procedural training. *IEEE TALE 2024*. | 2024 | Surgical/procedural (transferable pattern) | **Evaluator**: LLM automated performance scoring + formative feedback | Y — Surgical procedure steps | VR procedural simulation | Automated scores, feedback quality | IEEE TALE 2024 |
| 28 | Koutitas, G., Smith, S., & Lawrence, G. Performance evaluation of AR/VR training for EMS first responders. *Virtual Reality* (Springer). | 2020 | EMS first responder | **Evaluator**: Performance analytics framework | Y — EMS protocols | AR and VR platforms | Accuracy +46%, speed +29% | [10.1007/s10055-020-00436-8](https://doi.org/10.1007/s10055-020-00436-8) |
| 29 | Vassell, M., Apperson, O., Calyam, P., et al. Intelligent dashboard for AR-based incident command coordination. *IEEE CCNC 2016*. | 2016 | Incident command | **Decision support**: Intelligent AR dashboard with IoT sensor integration for ICS | **Y — ICS (Incident Command System)** | AR: heads-up displays, virtual beacons, QR cards, mesh network | Communication efficiency, SA, 30 cit. | IEEE CCNC 2016 |
| 30 | Sermet, Y. & Demir, I. GeospatialVR: Immersive decision support system for disaster response. *ACM VRST 2020*. | 2020 | Disaster response / flood management | **Scenario engine**: Data-driven 3D environment from geospatial data (GIS-driven) | N | Open-source; desktop, mobile, VR & AR HMD compatible | Decision-making quality, environmental accuracy | ACM VRST 2020 |
| 31 | Amokrane, K. & Lourdeaux, D. HERA: VR contribution to training and risk prevention. *ICAI 2009*. | 2009 | Industrial risk / safety | **Trainer (ITS)**: HERA system — learner tracking, error detection, causal risk model | Y — Procedural error-risk causality | VET/L virtual environment | Error detection, risk causality | ICAI 2009 |
| 32 | Kwakye, K., Mwakalonge, J., et al. SMART VR: Scalable VR framework with AI-driven hazard simulation and physiological monitoring. *AHFE 2025*. | 2025 | Vehicle safety / emergency driving | **Scenario + Evaluator**: AI-driven dynamic hazard injection; physiological monitoring (gaze, HRV, EDA) | Not directly (driver safety protocols) | CARLA + Unreal Engine + VR HMD + wearable biosensors | Hazard response, physiological measures | [10.54941/ahfe1006905](https://doi.org/10.54941/ahfe1006905) |
| 33 | Shafian, S. A., Xu, H., Khalid, A., & Hu, D. 3D Gaussian splatting for interactive VR disaster training. *IEEE Intl Conf Industrial Revolution 2025*. | 2025 | Disaster response (general damage) | **Scenario engine**: CV-based (3D Gaussian splatting) photorealistic disaster scene reconstruction | N | Game engine VR + HMD | Scene fidelity, interaction quality | IEEE 2025 |
| 34 | Szczepaniak, D., Harvey, M., & Deligianni, F. Real-time cognitive training adaptation via eye-tracking + ML in VR. *arXiv 2512.17882*. | 2025 | Cognitive training (generalizable) | **Scenario engine**: BiLSTM + self-attention for real-time difficulty adaptation based on cognitive load | N | VR HMD + eye-tracking + PPG + GSR | Cognitive load prediction, n=74 training / n=54 deploy | [arXiv:2512.17882](https://arxiv.org/abs/2512.17882) |
| 35 | Moinnereau, M. A., Tiwari, A., et al. Subjective/objective assessment of stress and cybersickness in VR training. *AHFE 2025*. | 2025 | First responder (driving sim) | **Evaluator**: EEG/EOG/PPG/ECG real-time cognitive state extraction | N | Instrumented Meta Quest 3 (16 EEG + EOG sensors) + wearables | Cognitive workload, cybersickness, stress, n=12 (target 60) | [10.54941/ahfe1006348](https://doi.org/10.54941/ahfe1006348) |
| 36 | Rai, R. K., Kumar, D., et al. VR's potential in CBRN training: AI, HCI, and psychology. *Springer LNCS (AVR Conf)*. | 2025 | CBRN response | **Review**: AI for scenario adaptation, behavioral modeling | Y — CBRN response protocols | (Review covers multiple) | (Review metrics) | [10.1007/978-3-031-97778-7_33](https://doi.org/10.1007/978-3-031-97778-7_33) |
| 37 | Kwok, B. W., Lee, J. S., et al. VR for HAZMAT decontamination facility training. *CHI EA 2025*, ACM. | 2025 | HAZMAT mass decontamination | Structured procedural VR (limited AI) | Y — Decontamination workflow protocols | VR HMD, modular design | Mixed-methods: VR vs. conventional | [10.1145/3706599.3720024](https://doi.org/10.1145/3706599.3720024) |
| 38 | Kang, J., Chen, Z., & Kang, W. VR + AI in intelligent combat training simulation. *IEEE PEEEC 2024*. | 2024 | Military combat (transferable) | **Scenario + Agents**: ML-adaptive difficulty, AI enemy agents adjusting tactics, data mining for personalization | Implicit (military tactical procedures) | VR HMD, "God of War" system | Tactical performance, adaptiveness | IEEE PEEEC 2024 |

### Commercial Systems

| System | Developer | Year | Domain | AI Role | SOPs | Stack |
|---|---|---|---|---|---|---|
| **ADMS** (Advanced Disaster Management Simulator) | ETC Simulation | ~2008+ | Incident command, fire, hazmat, multi-agency | Rule-based scenario engine, fire/smoke spread models, AAR analytics | **Y — ICS, NIMS** | Desktop 3D, multi-screen, custom engine |
| **XVR Simulation** | XVR Simulation BV (NL) | ~2005+ | Multi-domain: fire, EMS, police, IC | Rule-based/scripted, instructor-controlled dynamic events | **Y — ICS, paramedicine** | Desktop 3D, newer VR HMD support |

### Key Review Papers

| Citation | Year | Scope | Key Findings |
|---|---|---|---|
| Khanal, S., et al. VR and AR in disaster management technology: A literature review. *Front. Virtual Reality*, 3, 843195. | 2022 | 84 papers on XR + disaster management (2011–2022) | 5 major application categories, 19 sub-categories; identifies intelligent interaction and adaptive difficulty as emerging themes |
| Khorram-Manesh, A., et al. Technology's contribution to SA and disaster mindset. *OJPHI/JMIR*, 17, e75404. | 2025 | 49 studies on technology for disaster preparedness (2005–2025) | 86% address SA, only 2% target "disaster mindset"; calls for AI-integrated adaptive training |
| Hancko, D., et al. VR/AR/MR/XR and simulation-based systems for fire and rescue service training. *Fire* (MDPI). | 2025 | Review of XR in fire & rescue | Identifies AI-enhanced scenario generation, biometric feedback, cloud collaboration as future directions |
| Dasa, D., Board, M., & Tang, W. AI-driven characters in XR healthcare simulations: Systematic review. *Artif Intell Med*. | 2025 | AI-driven virtual characters across XR healthcare sims | Categorizes AI character types, evaluation methods, effectiveness measures |
| Laine, J., et al. Systematic review of ITS for hard skills training in VR environments. *IJTES*. | 2022 | ITS architectures for VR hard skills training | Reviews rule-based, Bayesian, agent-based ITS approaches; identifies gaps in emergency domain |
| Engelbrecht, H., Lindeman, R., & Hoermann, S. A SWOT analysis of VR for firefighter training. *Front. Robotics AI*. | 2019 | VR firefighter training landscape | Identifies strengths (safety, repeatability), weaknesses (fidelity gaps), opportunities (AI integration), threats (cost, acceptance) |
| Wheeler, S., Engelbrecht, H., & Hoermann, S. Human factors in immersive VR firefighter training: Systematic review. *Front. Virtual Reality*. | 2021 | Human factors in VR firefighter training | Reviews presence, workload, SA measurement approaches |

---

## 3. Thematic Synthesis

### 3.1 AI as Trainer / Coach / Intelligent Tutoring System (ITS)

This theme covers systems where AI provides real-time guidance, coaching, or adaptive instruction during or around VR training sessions.

**Key systems:**

- **VICTEAMS** (Lourdeaux et al., 2019) is the most complete ITS implementation in this domain. Its "pedagogical director" dynamically adjusts scenario difficulty based on an evolving learner profile, while BDI-driven virtual subordinates exhibit realistic erroneous behaviors that the trainee must detect and correct. This represents the gold standard for AI-as-trainer in VR emergency training.

- **HERA** (Amokrane & Lourdeaux, 2009) is an earlier ITS from the same research group, providing learner tracking, error detection, and a causal risk model linking procedural errors to safety outcomes. While focused on industrial safety rather than emergency response, its architecture (learner model → error detection → causal reasoning → intervention) is directly transferable.

- **Q-VMedSim** (Sirandass et al., 2025) integrates an AI virtual medical assistant into a Unity-based VR environment to guide emergency procedure training — representing the newer LLM-powered coaching paradigm.

- **Spain et al. (2020)** developed an intelligent user interface for firefighters in VR that provides real-time situational awareness cues on a heads-up display — an AI coach that augments rather than replaces instructor guidance.

- **Chan et al. (2025)** use ChatGPT to drive an adaptive ISBAR-protocol avatar that provides real-time handover practice with gamification — a 3-layer architecture (system/interaction/presentation) that could serve as a design pattern for LLM-driven VR coaching.

**Gaps:** Very few systems provide *closed-loop* adaptive tutoring where trainee performance is continuously assessed and instruction is modified in real time. VICTEAMS achieves this with rule/BDI models; no emergency training system yet uses RL or LLM-driven continuous adaptation for real-time coaching.

### 3.2 AI for Automated Assessment & Debriefing

This theme covers systems where AI automates performance scoring, protocol compliance checking, or after-action review generation.

**Key systems:**

- **FRVRS** (Kman et al., 2023; Way et al., 2024) provides automated triage performance tracking against the **SALT Triage** protocol. The system records every triage decision, treatment action, and navigation path, then generates automated after-action feedback. Validated with n=375 learners at 95% satisfaction.

- **Baetzner et al. (2025)** integrate eye-tracking into VR MCI training to compute objective performance indicators: triage accuracy (d=0.48), triage speed (d=0.42), and information transmission efficiency (d=1.13). Eye-tracking gaze patterns correlate with expertise level.

- **Dini et al. (2023) / Paletta et al. (2022) / Reim et al. (2022)** form a coherent research program (JKU/Paletta group) using **biosensor-driven ML analytics** — eye-tracking, cardiovascular, electrodermal, and temperature data — to assess situation awareness, cognitive-emotional stress, and fatigue during VR first responder training. This represents the most advanced physiological assessment pipeline in the field.

- **Mehta et al. (2025)** contribute gaze entropy and pupillometry as automated cognitive state indicators for firefighter VR training (n=40 real firefighters), finding that training under stress conditions alters eye behavior predictably.

- **Fan et al. (2024)** demonstrate **LLM-based automated scoring** of VR procedural training — a paradigm that could be directly applied to emergency procedure compliance checking.

- **Truong et al. (2021)** use AI-enhanced assessment for OR fire response training, evaluating RACE protocol compliance with automated pass/fail scoring.

- **Moinnereau et al. (2025)** have instrumented a **Meta Quest 3** with 16 EEG + EOG sensors for continuous neurophysiological assessment during VR first responder training — potentially the most advanced wearable sensing setup reported.

**Gaps:** Automated debriefing generation (natural language summaries of performance) is essentially absent. All current systems produce dashboards or scores but not narrative feedback. LLM integration for generating personalized debrief reports is an open opportunity.

### 3.3 AI for Scenario Generation / Adaptation (PCG / RL)

This theme covers systems where AI generates, modifies, or dynamically adapts training scenarios.

**Key systems:**

- **Agarwal & Shridevi (2023)** present the most explicit VR + RL-PCG system: reinforcement learning generates disaster evacuation scenarios with dynamic difficulty and layout adaptation. Published in IEEE Access, this is the closest existing system to a "VR + RL scenario engine" for disaster training.

- **Doroudian & Dorodchi (2025)** use RL to optimize rescue mission strategies in VR, blending human intuition with AI efficiency — the AI learns optimal resource allocation and mission planning across trials.

- **Liu (2025)** implements a **closed-loop neuro-adaptive** training model where scenario difficulty (threat density, environmental cues) adapts in real-time based on EEG-derived neural state (precision 0.89, F1 0.82). While focused on counter-terrorism, the architecture is directly applicable to first responder training.

- **Szczepaniak et al. (2025)** demonstrate real-time cognitive load prediction (BiLSTM + self-attention on eye-tracking + PPG + GSR) driving VR difficulty adaptation — the first reported system achieving real-time closed-loop cognitive load control in VR.

- **Sermet & Demir (2020)** take a data-driven approach using **geospatial data (GIS) to dynamically generate 3D disaster environments** in VR — an open-source pipeline for creating training scenarios from real-world terrain and hazard data.

- **Shafian et al. (2025)** use **3D Gaussian splatting** (computer vision) to reconstruct photorealistic disaster scenes from imagery for interactive VR training — a novel reconstruction-to-VR pipeline.

- **Xiong et al. (2025)** and **Huang et al. (2026)** use **LLMs (ChatGPT)** for scenario narrative generation — a rapidly emerging approach that could complement procedural generation.

**Gaps:** No system yet combines RL-based scenario adaptation with geospatial data-driven environments in a single pipeline. Digital twin integration (real building/infrastructure → VR training scenario) with AI-driven dynamic event injection is the logical next step but not yet demonstrated for emergency training.

### 3.4 AI for Agent Behaviors (Crowds / Hazards / Teammates)

This theme covers systems where AI controls non-player characters (crowd evacuees, casualties, teammates, adversarial agents) or physical hazard models.

**Key systems:**

- **VICTEAMS** (Lourdeaux et al., 2019) remains the state of the art for intelligent teammate agents: BDI subordinates with autonomous behavior that reproduces followership attitudes, stress responses, and errors.

- **Shendarkar et al. (2006)** is the seminal work on BDI agents for VR crowd evacuation (138 citations), establishing the paradigm of combining BDI belief-desire-intention architectures with VR environments.

- **Sharma et al. (2019)** advance this to hybrid human-AI agent crowds in immersive collaborative virtual environments (bomb attack scenario), with AI agents interacting alongside user-controlled agents.

- **Danial et al. (2019)** contribute sequential learning algorithms that teach VR agents human-like escape routes in fire scenarios — ensuring NPC evacuees behave realistically for immersive training.

- **AUGGMED** (Saunders et al., 2017) is an EU H2020 project that implements AI-driven civilian and threat NPCs in multiplayer serious games for counter-terrorism first responder training with multi-agency interoperability.

- **Kang et al. (2024)** demonstrate AI enemy agents that adjust tactics based on trainee behavior — ML-driven adversarial adaptation — in a military VR combat system ("God of War").

- **Dini et al. (2023)** implement AI-controlled movement of 5 virtual first responder team members in firefighter training scenarios.

**Gaps:** No system integrates LLM-driven conversational agents with BDI behavioral agents in a unified VR training environment. Agents that can both *speak* and *behave* intelligently in the same scenario (e.g., a virtual casualty that verbally reports symptoms while exhibiting stress behaviors) is an unsolved integration challenge.

---

## 4. Implementation Blueprint

### 4.1 What to Build First (Phased Approach)

**Phase 1 — Minimum Viable Training System (3–4 months)**
- Single-scenario VR training environment (e.g., building fire + casualties)
- Rule-based scenario scripting (branching events, timer-triggered hazard escalation)
- Automated protocol compliance tracking (checklist-based: SALT triage or firefighter SOPs)
- Post-session summary dashboard (scores, timeline, errors)

**Phase 2 — AI Agents & Assessment (2–3 months)**
- LLM-powered virtual casualty/patient (GPT-4 + TTS for verbal patient interaction)
- BDI-based NPC teammates/civilians (decision trees or behavior trees for crowd movement)
- Eye-tracking-based situation awareness assessment
- Automated debrief generation (LLM summarizes session performance into narrative report)

**Phase 3 — Adaptive Scenario Engine (3–4 months)**
- RL-based difficulty adaptation (PPO/DQN agent observes trainee performance, adjusts hazard intensity/patient acuity/timeline compression)
- Procedural content generation for scenario variation (fire origin location, number of casualties, building layout randomization)
- GIS/digital twin integration for geographically-realistic training environments

**Phase 4 — Full ITS Integration (2–3 months)**
- Learner model tracking performance across sessions
- Adaptive coaching (real-time hints via AI instructor voice or HUD overlay)
- Multi-user collaborative training with intelligent role assignment
- Physiological monitoring integration (HRV, EDA via wearable) for stress-aware adaptation

### 4.2 Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VR Training Platform                      │
├──────────────┬──────────────┬──────────────┬────────────────┤
│  VR Runtime  │  AI Services │  Assessment  │   Data Layer   │
│  (Unity XR)  │  (Python)    │  Engine      │   (Database)   │
│              │              │              │                │
│ • XR Interac-│ • LLM Agent  │ • Protocol   │ • Session logs │
│   tion Toolkit│   (GPT-4/   │   compliance │ • Learner      │
│ • Scene Mgmt │   local LLM) │   checker    │   profiles     │
│ • Physics/   │ • RL Scenario│ • Eye-track  │ • Scenario     │
│   Fire sim   │   Adapter    │   SA scoring │   templates    │
│ • Multiplayer│ • BDI Agent  │ • Physiology │ • Performance  │
│   (Netcode/  │   Controller │   analytics  │   history      │
│   Photon)    │ • NLP/TTS/STT│ • LLM Debrief│ • GIS/BIM data │
│              │              │   Generator  │                │
└──────┬───────┴──────┬───────┴──────┬───────┴────────┬───────┘
       │              │              │                │
       ▼              ▼              ▼                ▼
  ┌─────────┐  ┌───────────┐  ┌──────────┐   ┌──────────────┐
  │ VR HMD  │  │  Compute  │  │ Wearable │   │  Instructor  │
  │ (Quest 3│  │  Server   │  │ Sensors  │   │  Dashboard   │
  │ /Pro)   │  │ (GPU for  │  │ (HR/EDA/ │   │  (Web UI)    │
  │ +Eye    │  │  RL + LLM)│  │  EEG opt)│   │              │
  │  Track  │  │           │  │          │   │              │
  └─────────┘  └───────────┘  └──────────┘   └──────────────┘
```

### 4.3 Minimum Viable Hardware/Software Stack

| Component | Recommendation | Rationale |
|---|---|---|
| **VR HMD** | **Meta Quest 3** (standalone) or **Quest Pro** (eye-tracking) | Best cost/capability ratio; standalone + PCVR modes; integrated eye-tracking on Pro; huge install base |
| **Game Engine** | **Unity 2022 LTS + XR Interaction Toolkit + OpenXR** | Most VR training prototypes use Unity; largest ecosystem; XR Toolkit standardizes input |
| **AI Runtime** | **Python (FastAPI)** microservice on GPU server | Keeps AI logic decoupled from Unity; supports PyTorch RL, LangChain/LLM orchestration, scikit-learn |
| **LLM** | **GPT-4o API** (prototyping) → **local Llama 3 70B** (deployment) | GPT-4o for rapid iteration; local LLM for latency, cost, and data sovereignty in production |
| **RL Framework** | **Stable-Baselines3** (PPO) + **Unity ML-Agents** | ML-Agents bridges Unity ↔ Python; SB3 provides production-grade RL implementations |
| **TTS/STT** | **Azure Speech Services** or **Whisper + Bark/XTTS** | Real-time voice for virtual patients/coach; Whisper for trainee speech recognition |
| **Eye Tracking** | Quest Pro built-in or **Tobii integration** (Varjo XR-4) | Quest Pro is affordable; Varjo if research-grade foveated data needed |
| **Physiology** | **Empatica E4** (wrist: HR, EDA, temp) or **Polar H10** (chest HR) | Research-validated; BLE streaming; unobtrusive during VR use |
| **Fire/Smoke Sim** | **Unity VFX Graph + custom solver** or **FluXY** (open-source) | Real-time GPU-based fire/smoke; sufficient for training realism |
| **Networking** | **Unity Netcode for GameObjects** or **Photon Fusion** | Multi-user collaborative training; Photon for robust production use |
| **Database** | **PostgreSQL + InfluxDB** (time-series) | Structured session data + high-frequency sensor streams |
| **Instructor Dashboard** | **React + D3.js** (web app) | Real-time visualization of trainee performance; accessible from any device |

### 4.4 Recommended Build Order

1. **Unity VR scene** — single disaster scenario (burning building, 3–5 virtual patients, smoke/fire FX)
2. **Protocol checklist engine** — rule-based; checks trainee actions against SOP decision tree (e.g., SALT: walk → wave → assess → tag)
3. **LLM virtual patient** — GPT-4o via API, prompted with patient profile; STT for trainee speech → LLM → TTS response
4. **Performance logger** — timestamp every action, decision, gaze fixation to database
5. **Post-session debrief** — LLM generates narrative summary from session log
6. **RL scenario adapter** — PPO agent observes aggregate trainee metrics, adjusts next-session parameters
7. **Eye-tracking SA scoring** — correlate gaze patterns with known SA indicators
8. **Multi-user mode** — add Netcode/Photon for collaborative team training
9. **Instructor dashboard** — web UI showing real-time trainee status and historical analytics
10. **GIS integration** — load real building/terrain data to generate location-specific scenarios

---

## 5. Key Findings & Research Gaps

### What Exists
- **Protocol-grounded VR training with automated scoring** is well-established for MCI/SALT triage (FRVRS) and ICS (ADMS/XVR).
- **Biosensor-based cognitive state assessment** during VR training is an active research front (Paletta group, Mehta, Baetzner, Moinnereau).
- **BDI and multi-agent crowd simulation** in VR has a solid theoretical and implementation base (Shendarkar 2006 → Sharma 2019 → VICTEAMS 2019).
- **LLM integration** with VR is rapidly emerging (2024–2026) for both scenario generation and virtual patient interaction.

### What's Missing
1. **End-to-end adaptive ITS for emergency VR training** — No system combines real-time performance assessment → adaptive coaching → scenario modification → automated debriefing in a single loop. VICTEAMS comes closest but lacks RL-driven adaptation.
2. **LLM + BDI agent integration** — Conversational AI and behavioral AI remain separate; no system has agents that can both talk naturally and act autonomously.
3. **Digital twin → VR training pipeline** — Despite digital twin hype, no published emergency training system loads a real building's BIM/GIS data into VR and runs AI-adapted disaster scenarios on it.
4. **Longitudinal retention studies** — Almost all evaluations are single-session; long-term skill retention and transfer to real emergencies are unmeasured.
5. **Multi-agency collaborative AI training** — While AUGGMED and ADMS address multi-agency response, AI-driven coordination challenges (communication failures, resource conflicts) between heterogeneous responder teams are not modeled.
6. **Standardized benchmarks** — No shared scenario repository, performance metrics standard, or open-source reference implementation exists for VR + AI emergency training.

---

## References

1. Agarwal, J. & Shridevi, S. (2023). Procedural content generation using reinforcement learning for disaster evacuation training in a virtual 3D environment. *IEEE Access*. https://doi.org/10.1109/ACCESS.2023.3314120
2. Amokrane, K. & Lourdeaux, D. (2009). Virtual reality contribution to training and risk prevention. *International Conference on Artificial Intelligence (ICAI)*.
3. Baetzner, A. S., Hill, Y., Roszipal, B., et al. (2025). Mass casualty incident training in immersive virtual reality: Quasi-experimental evaluation of multimethod performance indicators. *Journal of Medical Internet Research*, 27, e63241. https://doi.org/10.2196/63241
4. Chan, M. M. K., Cheung, D. S. K., et al. (2025). AI-powered virtual reality simulation for clinical handover training: A development framework. *Nurse Educator*. https://doi.org/10.1097/NNE.0000000000002018
5. Danial, S. N., Smith, J. A., Khan, F., & Veitch, B. (2019). Human-like sequential learning of escape routes for virtual reality agents. *Fire Technology*, 55, 1057–1083. https://doi.org/10.1007/s10694-019-00819-7
6. Dasa, D., Board, M., & Tang, W. (2025). Evaluating AI-driven characters in extended reality (XR) healthcare simulations: A systematic review. *Artificial Intelligence in Medicine*.
7. Dib, N., Alattas, N., et al. (2023). EMT VR – A gamified emergency response training system using virtual reality and artificial intelligence. *IEEE Smart World Congress*. https://doi.org/10.1109/SWC57546.2023.10449292
8. Dini, A., Schneeberger, M., Pszeida, M., Heiler, L., & Paletta, L. (2023). Towards immersive skill training for first responders with biosensor-based assessment of situation awareness. *AHFE 2023*. https://doi.org/10.54941/ahfe1003979
9. Doroudian, S. & Dorodchi, M. (2025). Optimizing rescue mission strategies: Integrating human intuition with AI efficiency in VR simulations using reinforcement learning. *IEEE World AI IoT Congress*.
10. Engelbrecht, H., Lindeman, R., & Hoermann, S. (2019). A SWOT analysis of the field of virtual reality for firefighter training. *Frontiers in Robotics and AI*. https://doi.org/10.3389/frobt.2019.00101
11. Fan, P. M., Zhuang, Y., et al. (2024). GenAI for automated assessment and feedback in VR procedural training. *IEEE TALE 2024*.
12. Gutiérrez Maquilón, R., Uhl, J., Schrom-Feiertag, H., & Tscheligi, M. (2024). Integrating GPT-based AI into virtual patients to facilitate communication training among medical first responders. *JMIR Formative Research*. https://doi.org/10.2196/58623
13. Hancko, D., Majlingová, A., & Kačíková, D. (2025). Integrating VR, AR, MR, XR, and simulation-based systems into fire and rescue service training: Current practices and future directions. *Fire* (MDPI). https://doi.org/10.3390/fire8060228
14. Huang, C., Zhang, J., & Song, W. (2026). LLM and VR empowering the building fire safety training. *Fire Safety Journal*.
15. Kang, J., Chen, Z., & Kang, W. (2024). Virtual reality technology and algorithm application in intelligent combat training simulation system. *IEEE PEEEC 2024*. https://doi.org/10.1109/PEEEC63877.2024.00147
16. Khanal, S., Medasetti, U. S., Mashal, M., Savage, B., & Khadka, R. (2022). Virtual and augmented reality in the disaster management technology: A literature review of the past 11 years. *Frontiers in Virtual Reality*, 3, 843195. https://doi.org/10.3389/frvir.2022.843195
17. Khorram-Manesh, A., Johannessen, M. R., et al. (2025). Cultivating disaster preparedness: Scoping review of technology's contribution to situational awareness and disaster mindset. *Online Journal of Public Health Informatics*, 17, e75404. https://doi.org/10.2196/75404
18. Kman, N. E., Price, A., Berezina-Blackburn, V., et al. (2023). First Responder Virtual Reality Simulator to train and assess emergency personnel for mass casualty response. *Journal of the American College of Emergency Physicians Open*, 4(1), e12903. https://doi.org/10.1002/emp2.12903
19. Koutitas, G., Smith, S., & Lawrence, G. (2020). Performance evaluation of AR/VR training technologies for EMS first responders. *Virtual Reality* (Springer). https://doi.org/10.1007/s10055-020-00436-8
20. Kwakye, K., Mwakalonge, J., et al. (2025). SMART VR for commercial motor vehicles safety: A scalable virtual reality framework with AI-driven hazard simulation and physiological monitoring. *AHFE International*. https://doi.org/10.54941/ahfe1006905
21. Kwok, B. W., Lee, J. S., et al. (2025). Virtual reality for HAZMAT decontamination facility training: An initial case study. *CHI Extended Abstracts*, ACM. https://doi.org/10.1145/3706599.3720024
22. Laine, J., Lindqvist, T., Korhonen, T., & Hakkarainen, K. (2022). Systematic review of intelligent tutoring systems for hard skills training in virtual reality environments. *International Journal of Technology in Education and Science*.
23. Liaw, S. Y., Tan, J. Z., Lim, S., et al. (2023). Artificial intelligence in virtual reality simulation for interprofessional communication training: Mixed method study. *Nurse Education Today*, 122, 105718. https://doi.org/10.1016/j.nedt.2023.105718
24. Liu, Y. (2025). Closed-loop neuro-adaptive counter-terrorism training model for virtual reality based brain computer interface simulation. *IEEE ICMNWC 2025*.
25. Lourdeaux, D., Afoutni, Z., Ferrer, M.-H., et al. (2019). VICTEAMS: A virtual environment to train medical team leaders to interact with virtual subordinates. *Proceedings of the 19th ACM International Conference on Intelligent Virtual Agents*, 241–243. https://doi.org/10.1145/3308532.3329418
26. Mehta, R. K., Kang, J., Shi, Y., & Du, J. (2025). Effectiveness of training under stress in immersive VR: An investigation of firefighter performance, gaze entropy, and pupillometry. *Frontiers in Virtual Reality*. https://doi.org/10.3389/frvir.2025.1542507
27. Moinnereau, M. A., Tiwari, A., et al. (2025). Subjective and objective assessment of the impact of stress and mental workload on cybersickness during virtual reality training. *AHFE International*. https://doi.org/10.54941/ahfe1006348
28. Nguyen, V. T., Jung, K., & Dang, T. (2019). VRescuer: A virtual reality application for disaster response training. *IEEE International Conference on Artificial Intelligence and Virtual Reality*. https://doi.org/10.1109/AIVR46125.2019.00042
29. Paletta, L., Schneeberger, M., et al. (2022). Digital human factors measurements in first responder virtual reality-based skill training. *iLRN 2022*, IEEE.
30. Rai, R. K., Kumar, D., et al. (2025). Reviewing virtual reality's potential in CBRN training: Synergizing AI, HCI, and psychology for immersive preparedness. *Springer LNCS*. https://doi.org/10.1007/978-3-031-97778-7_33
31. Reim, L., Kallus, K. W., et al. (2022). Evaluation of virtual reality-based first responder training under physiological and cognitive-emotional strain. *AHFE 2022*. https://doi.org/10.54941/ahfe1001840
32. Saunders, J., Gibson, H., Leitão, R., & Akhgar, B. (2017). AUGGMED: Developing multiplayer serious games technology to enhance first responder training. *EU H2020 Project*.
33. Saville, J. D., Spain, R. D., et al. (2022). Evaluating the usability of a next-generation heads-up display for firefighters in a virtual environment. *Proceedings of the HFES Annual Meeting*. https://doi.org/10.1177/1071181322661199
34. Sermet, Y. & Demir, I. (2020). An immersive decision support system for disaster response. *ACM VRST 2020*.
35. Shafian, S. A., Xu, H., Khalid, A., & Hu, D. (2025). Simulating real-world damage environments for interactive virtual reality training via 3D Gaussian splatting. *IEEE International Conference Industrial Revolution*.
36. Sharma, S., Devreaux, P., et al. (2019). Artificial intelligence agents for crowd simulation in an immersive environment for emergency response. *IS&T ERVR*. https://doi.org/10.2352/issn.2470-1173.2019.2.ervr-176
37. Shendarkar, A., Vasudevan, K., Lee, S., & Son, Y. (2006). Crowd simulation for emergency response using BDI agent based on virtual reality. *Winter Simulation Conference*.
38. Sirandass, H., Jaiswal, C., & Sukumar, M. (2025). Q-VMedSim: A training platform for emergency response procedures through virtual reality and AI assistance. *IEEE World AI IoT Congress*.
39. Spain, R. D., Saville, J. D., et al. (2020). Investigating a virtual reality-based emergency response scenario and intelligent user interface for first responders. *Proceedings of the HFES Annual Meeting*. https://doi.org/10.1177/1071181320641513
40. Szczepaniak, D., Harvey, M., & Deligianni, F. (2025). Your eyes controlled the game: Real-time cognitive training adaptation based on eye-tracking and physiological data in virtual reality. *arXiv:2512.17882*. https://doi.org/10.48550/arXiv.2512.17882
41. Truong, H., Qi, D., et al. (2021). Does your team know how to respond safely to an operating room fire? Outcomes of a virtual reality, AI-enhanced simulation training. *Surgical Endoscopy*. https://doi.org/10.1007/s00464-021-08602-y
42. Vassell, M., Apperson, O., Calyam, P., et al. (2016). Intelligent dashboard for augmented reality based incident command response co-ordination. *IEEE CCNC 2016*.
43. Way, D. P., Panchal, A. R., et al. (2024). Learner evaluation of an immersive virtual reality mass casualty incident simulator for triage training. *BMC Digital Health*, 2(1), 56. https://doi.org/10.1186/s44247-024-00117-5
44. Wheeler, S., Engelbrecht, H., & Hoermann, S. (2021). Human factors research in immersive virtual reality firefighter training: A systematic review. *Frontiers in Virtual Reality*. https://doi.org/10.3389/frvir.2021.671664
45. Xiong, K., Li, J., et al. (2025). Evaluating an AI-VR escape room for disaster nursing education: A quasi-experimental study. *Nurse Education in Practice*, 88, 104529. https://doi.org/10.1016/j.nepr.2025.104529
