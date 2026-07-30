# Engineering Career Path Database (by Branch)

Roles are grouped under the branch they are most relevant to, based on the highest `branch_relevance`
score in the source data. Branch codes: **BR001 = Computer Science / IT**, **BR002 = Electronics &
Communication**, **BR003 = Mechanical**, **BR004 = Civil**, **BR005 = Aerospace**. Each role entry
carries a structured block (for direct DB ingestion) followed by a career-path guide.

---

## BR001 — Computer Science & IT

### Software Engineer
```yaml
id: 1
family: Development
difficulty: Entry
skills: [Python, Java, Data Structures, Algorithms, SQL, Git]
```
Designs, builds, and maintains software applications using object-oriented principles.
- **Entry (0–2 yrs):** Junior/Associate Software Engineer — writing and testing modules, learning the codebase, contributing to bug fixes under review.
- **Mid (2–5 yrs):** Software Engineer II — owns features end-to-end, writes design docs, mentors interns.
- **Senior (5–8 yrs):** Senior Engineer — leads modules/services, drives code quality and architecture decisions.
- **Leadership (8+ yrs):** Staff Engineer / Engineering Manager — cross-team architecture or people management.
- **Guidance:** Strong DSA fundamentals and 2–3 solid GitHub projects matter more early on than framework breadth.

### Data Scientist
```yaml
id: 2
family: AI/ML
difficulty: Advanced
skills: [Python, SQL, Machine Learning, Statistics, Data Visualization, Deep Learning]
```
Builds predictive models, extracts insights from data, and deploys ML solutions.
- **Entry:** Data Analyst / Junior Data Scientist — cleaning data, building dashboards, basic regression/classification models.
- **Mid:** Data Scientist — owns a modeling pipeline end-to-end, A/B testing, feature engineering at scale.
- **Senior:** Senior/Lead Data Scientist — sets modeling strategy, reviews experiment design across teams.
- **Leadership:** Head of Data Science / ML Manager.
- **Guidance:** Statistics fundamentals (hypothesis testing, distributions) are tested more heavily than deep learning trivia at entry level.

### AI / Machine Learning Engineer
```yaml
id: 3
family: AI/ML
difficulty: Advanced
skills: [Python, Machine Learning, Deep Learning, TensorFlow, PyTorch, SQL]
```
Develops, trains, and deploys AI/ML models at production scale.
- **Entry:** ML Engineer I — implements and fine-tunes existing model architectures, builds training pipelines.
- **Mid:** ML Engineer — owns model deployment, monitoring, and retraining pipelines (MLOps).
- **Senior:** Senior ML Engineer — designs novel architectures, optimizes inference cost/latency.
- **Leadership:** Principal ML Engineer / ML Platform Lead.
- **Guidance:** Being able to take a model from notebook to a monitored production endpoint is the differentiator over pure research skill.

### Cybersecurity Analyst
```yaml
id: 4
family: Security
difficulty: Intermediate
skills: [Linux, Networking, Python, SIEM, Firewalls, Vulnerability Assessment]
```
Monitors, protects, and defends IT infrastructure against cyber threats.
- **Entry:** SOC Analyst (L1) — monitors alerts, triages incidents using SIEM tools.
- **Mid:** Security Analyst (L2/L3) — threat hunting, vulnerability assessments, incident response.
- **Senior:** Security Engineer / Lead — designs defenses, runs red-team/blue-team exercises.
- **Leadership:** Security Architect / CISO track.
- **Guidance:** A CompTIA Security+ or CEH-style certification plus a home-lab (Linux + firewall rules) is standard proof of practical skill.

### Cloud Engineer
```yaml
id: 5
family: Infrastructure
difficulty: Intermediate
skills: [AWS, Linux, Docker, Kubernetes, Terraform, Python]
```
Designs, implements, and manages scalable cloud infrastructure and deployment pipelines.
- **Entry:** Cloud/DevOps Engineer I — manages CI/CD pipelines, basic infra-as-code scripts.
- **Mid:** Cloud Engineer — owns multi-service deployments, container orchestration, cost optimization.
- **Senior:** Senior Cloud/Platform Engineer — designs multi-region architecture, reliability engineering (SRE).
- **Leadership:** Cloud Architect / Head of Platform.
- **Guidance:** One cloud certification (AWS/Azure Associate level) plus a documented personal deployment project is the usual entry bar.

### Full Stack Developer
```yaml
id: 6
family: Development
difficulty: Intermediate
skills: [JavaScript, React.js, Node.js, SQL, MongoDB, Git, REST APIs]
```
Builds end-to-end web applications across frontend and backend.
- **Entry:** Junior Full Stack Developer — builds UI components and simple API endpoints.
- **Mid:** Full Stack Developer — owns a feature vertically (DB schema → API → UI).
- **Senior:** Senior Full Stack / Tech Lead — makes stack-wide architecture calls, performance tuning.
- **Leadership:** Engineering Lead / Product Engineering Manager.
- **Guidance:** A deployed (not just local) full-stack project with auth and a real database is the strongest entry-level signal.

---

## BR002 — Electronics & Communication

### VLSI / Semiconductor Engineer
```yaml
id: 7
family: Hardware
difficulty: Advanced
skills: [Verilog, VHDL, FPGA, ASIC Design, Python, Electronics]
```
Designs and verifies integrated circuits, chips, and semiconductor components.
- **Entry:** Design/Verification Engineer I — writes RTL for sub-modules, basic testbenches.
- **Mid:** VLSI Engineer — owns a full block's design and verification sign-off.
- **Senior:** Senior VLSI Engineer — chip-level integration, timing closure, DFT strategy.
- **Leadership:** Principal Design Engineer / Silicon Architect.
- **Guidance:** Depth in one flow (either front-end RTL/verification or back-end physical design) beats shallow exposure to both.

### Embedded Systems Engineer
```yaml
id: 8
family: Hardware
difficulty: Intermediate
skills: [C, Embedded C, Microcontrollers, RTOS, Python, Electronics]
```
Develops firmware and software for microcontrollers and embedded devices.
- **Entry:** Firmware Engineer I — writes drivers for peripherals, basic RTOS tasks.
- **Mid:** Embedded Engineer — owns a subsystem's firmware, power/timing optimization.
- **Senior:** Senior Embedded Engineer — architects firmware across product lines, bring-up of new hardware.
- **Leadership:** Embedded Systems Architect / Hardware-Software Lead.
- **Guidance:** A personal project on a real microcontroller (Arduino/STM32) with a working RTOS task scheduler is a strong entry portfolio piece.

### Telecommunications Engineer
```yaml
id: 10
family: Networking
difficulty: Intermediate
skills: [Networking, Signal Processing, Wireless, Python, MATLAB, RF]
```
Designs and manages communication networks, wireless systems, and signal transmission.
- **Entry:** Network/RF Engineer I — site surveys, basic link-budget calculations, network configuration.
- **Mid:** Telecom Engineer — designs wireless coverage plans, optimizes network performance.
- **Senior:** Senior RF/Network Engineer — leads network rollout strategy, spectrum planning.
- **Leadership:** Network Architect / Telecom Systems Lead.
- **Guidance:** Familiarity with one simulation tool (MATLAB or a network simulator) plus core signal-processing math is what's usually tested.

---

## BR003 — Mechanical

### Robotics Engineer
```yaml
id: 9
family: Robotics
difficulty: Advanced
skills: [Python, C++, ROS, Control Systems, Electronics, Mechanics]
```
Designs, builds, and programs robotic systems for automation and industrial applications.
- **Entry:** Robotics Engineer I — writes ROS nodes, basic sensor integration.
- **Mid:** Robotics Engineer — owns a subsystem (perception, navigation, or manipulation).
- **Senior:** Senior Robotics Engineer — full-stack robot architecture, controls tuning.
- **Leadership:** Robotics Lead / Autonomy Architect.
- **Guidance:** A working ROS-based project (even simulated in Gazebo) is close to mandatory for interviews at this level.

### Design Engineer (Mechanical)
```yaml
id: 17
family: Core Engineering
difficulty: Entry
skills: [CAD, SolidWorks, Finite Element Analysis, Materials Science, Mechanics]
```
Creates mechanical components, assemblies, and product designs using engineering software.
- **Entry:** Design Engineer I — 2D/3D CAD modeling, drafting under supervision.
- **Mid:** Design Engineer — owns assembly design, runs FEA validation.
- **Senior:** Senior Design Engineer — design-for-manufacture decisions, tolerance stack-ups.
- **Leadership:** Design Lead / Product Engineering Manager.
- **Guidance:** Proficiency in one CAD suite (SolidWorks or equivalent) demonstrated through a complete assembly project is the standard bar.

### Manufacturing Engineer
```yaml
id: 18
family: Core Engineering
difficulty: Entry
skills: [CAD, CNC, Lean Manufacturing, Six Sigma, Materials Science, Python]
```
Optimizes production processes, improves efficiency, and manages manufacturing operations.
- **Entry:** Process/Manufacturing Engineer I — shop-floor support, documentation, small process tweaks.
- **Mid:** Manufacturing Engineer — owns a production line's efficiency and quality metrics.
- **Senior:** Senior Manufacturing Engineer — leads Lean/Six Sigma projects across lines.
- **Leadership:** Plant/Operations Manager.
- **Guidance:** A basic Six Sigma (Yellow/Green Belt) credential is a common, low-cost differentiator.

### Automotive Engineer
```yaml
id: 19
family: Core Engineering
difficulty: Intermediate
skills: [CAD, Thermodynamics, Fluid Mechanics, Control Systems, Python]
```
Designs and develops vehicle components, powertrains, and automotive systems.
- **Entry:** Automotive Design/Test Engineer I — component-level CAD and test support.
- **Mid:** Automotive Engineer — owns a subsystem (powertrain, chassis, or controls).
- **Senior:** Senior Automotive Engineer — vehicle-level integration and validation sign-off.
- **Leadership:** Vehicle Program Lead.
- **Guidance:** Exposure to one simulation domain (thermal, CFD, or controls) in a college project is a strong talking point.

### HVAC Engineer
```yaml
id: 20
family: Core Engineering
difficulty: Entry
skills: [Thermodynamics, Fluid Mechanics, AutoCAD, Revit, Building Systems]
```
Designs heating, ventilation, and air conditioning systems for buildings and infrastructure.
- **Entry:** HVAC Design Engineer I — load calculations, duct/pipe layout drafting.
- **Mid:** HVAC Engineer — owns full building system design and equipment selection.
- **Senior:** Senior HVAC Engineer — energy-efficiency optimization, code compliance sign-off.
- **Leadership:** MEP Engineering Lead.
- **Guidance:** Comfort with AutoCAD/Revit and basic thermodynamics load calculations covers most entry-level screening.

### Maintenance Engineer
```yaml
id: 21
family: Core Engineering
difficulty: Entry
skills: [Mechanics, Troubleshooting, Planned Maintenance, Safety, Documentation]
```
Ensures reliability and uptime of industrial machinery and plant equipment.
- **Entry:** Maintenance Engineer I — executes planned maintenance schedules, logs faults.
- **Mid:** Maintenance Engineer — root-cause analysis, downtime reduction initiatives.
- **Senior:** Senior/Reliability Engineer — predictive maintenance strategy, spare-parts planning.
- **Leadership:** Maintenance/Reliability Manager.
- **Guidance:** Practical troubleshooting experience (even from an internship or workshop) outweighs theoretical knowledge here.

---

## BR004 — Civil

### Structural Engineer
```yaml
id: 22
family: Core Engineering
difficulty: Intermediate
skills: [AutoCAD, STAAD Pro, RCC Design, Steel Design, Structural Analysis]
```
Designs buildings, bridges, and infrastructure using concrete, steel, and composite materials.
- **Entry:** Structural Design Engineer I — runs analysis models under a senior engineer's checks.
- **Mid:** Structural Engineer — owns design of a building/bridge component, prepares drawings for approval.
- **Senior:** Senior Structural Engineer — signs off on structural safety, leads complex designs.
- **Leadership:** Chief Structural Engineer / Principal.
- **Guidance:** Hands-on STAAD Pro/ETABS project work is checked more than theory recall in interviews.

### Construction Project Engineer
```yaml
id: 23
family: Core Engineering
difficulty: Entry
skills: [Project Management, AutoCAD, Cost Estimation, Scheduling, Safety]
```
Manages construction projects, budgets, timelines, and on-site coordination.
- **Entry:** Site/Project Engineer I — daily site coordination, progress tracking.
- **Mid:** Project Engineer — owns a project phase's budget and schedule.
- **Senior:** Senior Project Engineer / Project Manager — full project P&L and stakeholder management.
- **Leadership:** Construction Manager / Program Director.
- **Guidance:** Basic exposure to MS Project or Primavera scheduling tools is commonly expected even at entry level.

### Transportation Engineer
```yaml
id: 24
family: Core Engineering
difficulty: Intermediate
skills: [AutoCAD, Civil 3D, Traffic Analysis, Urban Planning, Surveying]
```
Plans and designs transportation systems, highways, and traffic management.
- **Entry:** Transportation Engineer I — traffic data collection, basic Civil 3D drafting.
- **Mid:** Transportation Engineer — owns roadway/intersection design proposals.
- **Senior:** Senior Transportation Engineer — leads corridor/network-level planning.
- **Leadership:** Transportation Planning Lead.
- **Guidance:** Familiarity with Civil 3D and basic traffic-flow analysis is the usual technical screen.

### Geotechnical Engineer
```yaml
id: 25
family: Core Engineering
difficulty: Intermediate
skills: [Soil Mechanics, Foundation Engineering, Geological Mapping, AutoCAD, Rock Mechanics]
```
Analyzes soil and rock properties to design foundations, tunnels, and earth structures.
- **Entry:** Geotechnical Engineer I — site investigation support, lab soil testing.
- **Mid:** Geotechnical Engineer — owns foundation design recommendations for a project.
- **Senior:** Senior Geotechnical Engineer — leads investigation strategy for large/complex sites.
- **Leadership:** Chief Geotechnical Engineer.
- **Guidance:** Practical soil-testing lab experience is a strong, often-overlooked entry-level credential.

### Environmental Engineer
```yaml
id: 26
family: Core Engineering
difficulty: Entry
skills: [AutoCAD, Fluid Mechanics, Environmental Regulations, Waste Management, GIS]
```
Designs systems to manage pollution, waste, and environmental impact.
- **Entry:** Environmental Engineer I — compliance data collection, permit documentation.
- **Mid:** Environmental Engineer — owns a treatment/waste-management system design.
- **Senior:** Senior Environmental Engineer — leads environmental impact assessments.
- **Leadership:** Environmental Compliance Manager.
- **Guidance:** Basic GIS familiarity plus knowledge of local environmental regulation is frequently tested.

### Urban Planner
```yaml
id: 27
family: Core Engineering
difficulty: Entry
skills: [GIS, AutoCAD, Urban Design, Policy, Surveying]
```
Develops land use plans and urban development strategies for sustainable growth.
- **Entry:** Junior Planner — data collection, zoning research, basic GIS mapping.
- **Mid:** Urban Planner — owns a neighborhood/land-use plan draft.
- **Senior:** Senior Planner — leads master-planning projects, stakeholder consultations.
- **Leadership:** City/Regional Planning Director.
- **Guidance:** A GIS-based mapping project is the most common entry-level portfolio piece.

---

## BR005 — Aerospace

### Aerospace Design Engineer
```yaml
id: 11
family: Core Engineering
difficulty: Advanced
skills: [Aerodynamics, CAD, Finite Element Analysis, MATLAB, Mechanics]
```
Designs aircraft, spacecraft, and aerodynamic structures.
- **Entry:** Design Engineer I — CAD modeling of components under senior review.
- **Mid:** Aerospace Design Engineer — owns sub-assembly design and FEA validation.
- **Senior:** Senior Design Engineer — full airframe/structure design sign-off.
- **Leadership:** Chief Design Engineer.
- **Guidance:** A CAD + basic aerodynamics simulation project (even a simple wing analysis) is the standard entry portfolio piece.

### Aircraft Maintenance Engineer
```yaml
id: 12
family: Core Engineering
difficulty: Entry
skills: [Mechanics, Aircraft Systems, Troubleshooting, Safety Compliance, Documentation]
```
Inspects, repairs, and maintains aircraft to ensure airworthiness and safety.
- **Entry:** Junior AME (licensed trainee) — line maintenance under supervision.
- **Mid:** Licensed AME — signs off routine maintenance independently.
- **Senior:** Senior AME — heavy maintenance checks, fault diagnosis leadership.
- **Leadership:** Maintenance Manager / Quality Manager.
- **Guidance:** This role requires a DGCA (or equivalent regulator) license — plan certification timelines early, alongside academics.

### Propulsion Engineer
```yaml
id: 13
family: Core Engineering
difficulty: Advanced
skills: [Thermodynamics, Fluid Mechanics, Combustion, MATLAB, CAD]
```
Develops engines and propulsion systems for aircraft, rockets, and spacecraft.
- **Entry:** Propulsion Engineer I — component-level thermal/fluid analysis.
- **Mid:** Propulsion Engineer — owns a subsystem's performance modeling.
- **Senior:** Senior Propulsion Engineer — engine-level integration and test sign-off.
- **Leadership:** Propulsion Systems Lead.
- **Guidance:** Strong thermodynamics + a MATLAB-based combustion/cycle-analysis project is the usual technical bar.

### Avionics Engineer
```yaml
id: 14
family: Core Engineering
difficulty: Intermediate
skills: [Electronics, Control Systems, Communication, MATLAB, C, Signal Processing]
```
Designs electronic systems for aviation, including navigation, communication, and flight controls.
- **Entry:** Avionics Engineer I — tests and integrates existing avionics modules.
- **Mid:** Avionics Engineer — owns a navigation/communication subsystem design.
- **Senior:** Senior Avionics Engineer — flight-control system integration and certification support.
- **Leadership:** Avionics Systems Lead.
- **Guidance:** Control-systems coursework plus a signal-processing project (even simulated) is what's usually checked first.

### Flight Test Engineer
```yaml
id: 15
family: Core Engineering
difficulty: Intermediate
skills: [Aerodynamics, Data Analysis, Instrumentation, MATLAB, Python]
```
Plans and executes flight tests, collecting and analyzing data to validate aircraft performance.
- **Entry:** Flight Test Engineer I — instrumentation setup, data logging support.
- **Mid:** Flight Test Engineer — designs test plans, analyzes flight data.
- **Senior:** Senior Flight Test Engineer — leads certification test campaigns.
- **Leadership:** Flight Test Program Manager.
- **Guidance:** Data-analysis skill (Python/MATLAB on real or simulated flight data) matters as much as aerodynamics theory.

### Space Systems Engineer
```yaml
id: 16
family: Core Engineering
difficulty: Advanced
skills: [Satellite Systems, Aerodynamics, MATLAB, CAD, Orbital Mechanics]
```
Designs and integrates spacecraft, satellites, and space mission systems.
- **Entry:** Systems Engineer I — subsystem-level requirements and testing support.
- **Mid:** Space Systems Engineer — owns a satellite subsystem's design and integration.
- **Senior:** Senior Systems Engineer — mission-level architecture and verification.
- **Leadership:** Mission/Program Systems Lead.
- **Guidance:** Orbital-mechanics fundamentals plus any CubeSat/satellite-club project experience stand out strongly at entry level.

---

*Guidance notes above describe typical industry patterns and are not a guarantee of placement, timeline, or compensation.*
