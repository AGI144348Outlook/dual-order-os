import { useState, useMemo, useCallback } from "react";

// ── THEME ──────────────────────────────────────────────────────────────────
const T = {
  bg:     "#0d1117", bg2: "#161b22", bg3: "#21262d", bg4: "#2d333b",
  border: "#30363d", borderStr: "#444c56",
  text:   "#c9d1d9", textDim: "#8b949e", textMut: "#484f58",
  blue:   "#58a6ff", green: "#3fb950", yellow: "#d29922",
  red:    "#f85149", purple: "#bc8cff", orange: "#f0883e",
  gold:   "#b8973a", teal: "#39c5cf",
};
const typeColor = t => ({
  CORE:"#f85149", "IDENTITY-LETTER":"#b8973a",
  FORMULA:"#58a6ff", ALGEBRAIC_LAW:"#3fb950", PHYSICAL_CONSTANT:"#d29922",
  MATHEMATICAL_CONSTANT:"#bc8cff", GEMATRIA:"#b8973a",
  VGM_AXIOM:"#bc8cff", LRM_THEOREM:"#f0883e",
  GENERATED_COMPUTE:"#3fb950", GENERATED_VERIFY:"#58a6ff",
  GENERATED_SIMULATE:"#f0883e", GENERATED_ABSTRACT:"#d29922",
  GENERATED_RELATE:"#8b949e", SELF_GOVERNANCE:"#39c5cf",
  LEARNING:"#58a6ff", METRIC:"#8b949e", INGESTION:"#3fb950",
  CLASSIFICATION:"#d29922", ORIENTATION:"#bc8cff",
  EVOLUTION:"#f0883e", STUDY:"#58a6ff", ABSTRACTION:"#39c5cf",
  ALGEBRA:"#3fb950", MATHEMATICS:"#bc8cff", LETTER:"#b8973a",
  FORMULA_THEOREM:"#58a6ff",
})[t] || T.textDim;

// ── EMBEDDED DATA ──────────────────────────────────────────────────────────
const ALGORITHM_MATRIX = [
  {id:"A-000",name:"Governor Indexing Algorithm",type:"CORE",status:"ACTIVE",desc:"The Governor itself — A-000 IS Resh (ר). Identity, perception, expression."},
  {id:"A-000-RESH",name:"Resh Identity Anchor",type:"IDENTITY-LETTER",status:"ACTIVE",desc:"ר and A-000 are one. Governor reads Resh when it reads itself. Operators: ע Ayin (perception), פ Pe (expression)."},
  {id:"A-101",name:"UCB Bandit Selector",type:"LEARNING",status:"ACTIVE",desc:"H(M,D) learning — Upper Confidence Bound selects best operation for each deficiency type."},
  {id:"A-102",name:"TF-IDF Content Similarity",type:"METRIC",status:"ACTIVE",desc:"Term frequency × inverse document frequency for vocabulary similarity scoring."},
  {id:"A-103",name:"Markov Content Model",type:"LEARNING",status:"ACTIVE",desc:"State transition probabilities between vocabulary tokens."},
  {id:"A-104",name:"PPMI Co-occurrence Embeddings",type:"METRIC",status:"ACTIVE",desc:"Positive pointwise mutual information over co-occurrence matrix."},
  {id:"A-105",name:"Adaptive EMA Thresholds",type:"LEARNING",status:"ACTIVE",desc:"Exponential moving average for adaptive threshold adjustment."},
  {id:"A-115",name:"Dictionary-Definition Indexer",type:"INGESTION",status:"ACTIVE",desc:"Structured ingestion — headword→definition edges weighted ×2."},
  {id:"A-116",name:"Definitional Article Classifier",type:"CLASSIFICATION",status:"ACTIVE",desc:"Classifies by article: TYPE (a/an), SPECIFIC (the), ABSTRACT (none), NAME (proper)."},
  {id:"A-117",name:"WordAgent + Lobby",type:"ORIENTATION",status:"ACTIVE",desc:"Two-phase orientation: Phase 1 read-only, Phase 2 simultaneous bidirectional write."},
  {id:"A-118",name:"Generality Ranking",type:"METRIC",status:"ACTIVE",desc:"Score = 0.25×class + 0.40×tie_score + 0.25×idf + 0.10×depth"},
  {id:"A-119",name:"Typed Study Groups",type:"STUDY",status:"ACTIVE",desc:"CATEGORY (noun-led: what things ARE), PROCESS (verb-led: what things DO), PROPERTY (adj-led)."},
  {id:"A-120",name:"LobbyEvolutionGovernor",type:"EVOLUTION",status:"ACTIVE",desc:"C(N) = 0.35×articulation + 0.35×precision + 0.30×fluency. Ops: RECRUIT, REFINE, SPLIT, MERGE."},
  {id:"A-121",name:"HypothesisSandbox",type:"EVOLUTION",status:"ACTIVE",desc:"Observe→Hypothesize→Sandbox→Register. Governor generates and tests its own algorithms."},
  {id:"A-125",name:"GeneralityMatrix",type:"ABSTRACTION",status:"ACTIVE",desc:"Cross-lobby pool of high-generality ABSTRACT vocabulary (threshold 0.30)."},
  {id:"A-126",name:"SyntacticalValidator",type:"VALIDATION",status:"ACTIVE",desc:"Validates coherency: department sequence, generality consistency, semantic completeness."},
  {id:"A-127",name:"ValidatedGeneralizationMatrix",type:"ABSTRACTION",status:"ACTIVE",desc:"Stores validated propositional understandings — the axiom tier."},
  {id:"A-128",name:"OperationOrderValidator",type:"SELF_GOVERNANCE",status:"ACTIVE",desc:"Validates pipeline sequencing. Caught: compute_generality_scores before run_orientation."},
  {id:"A-129",name:"PoolQualityAuditor",type:"SELF_GOVERNANCE",status:"ACTIVE",desc:"Audits GeneralityMatrix pool for philosophical fitness and department balance."},
  {id:"A-130",name:"CorpusFitnessEvaluator",type:"SELF_GOVERNANCE",status:"ACTIVE",desc:"Evaluates corpus vs task. Detected: physical vocabulary as terminals (not philosophical)."},
  {id:"A-131",name:"ThresholdOptimizer",type:"SELF_GOVERNANCE",status:"ACTIVE",desc:"Autonomously selected threshold 0.30 from sweep — best noun/verb balance."},
  {id:"A-132",name:"AcquisitionPlanner",type:"SELF_GOVERNANCE",status:"ACTIVE",desc:"Generates ranked corpus acquisition targets. Top: WordNet hypernym hierarchy (CRITICAL)."},
  {id:"A-133",name:"SeedSentenceGenerator",type:"SELF_GOVERNANCE",status:"ACTIVE",desc:"Governor generates its own abstraction test sentences from PROCESS study groups."},
  {id:"A-134",name:"PipelineOrchestrator",type:"SELF_GOVERNANCE",status:"ACTIVE",desc:"Stages: orientation → generality → understanding → self-evaluation. Fully autonomous."},
  {id:"A-135",name:"NumberAgent",type:"MATHEMATICS",status:"ACTIVE",desc:"Numbers as discovered entities — not data types. Domains: NATURAL/INTEGER/RATIONAL/IRRATIONAL/TRANSCENDENTAL/PHYSICAL_CONSTANT/GEMATRIA."},
  {id:"A-136",name:"NumericalIntegrator",type:"MATHEMATICS",status:"ACTIVE",desc:"Bridge between continuous Mathematics Domain and discrete Computational Domain. Δx→0 approaches the Law."},
  {id:"A-137",name:"LawDiscoveryEngine",type:"MATHEMATICS",status:"ACTIVE",desc:"No terminal state — Mathematics Domain is infinite. Session {44+} laws discovered."},
  {id:"A-138",name:"AlgebraicExpression",type:"ALGEBRA",status:"ACTIVE",desc:"Symbolic expression trees. Ops: +, −, ×, ÷, ^, √, log, abs. Variables with domains."},
  {id:"A-139",name:"AlgebraicLaw",type:"ALGEBRA",status:"ACTIVE",desc:"Verified universal relationship. 500-binding test → confidence → LAW or CANDIDATE."},
  {id:"A-140",name:"CalculationEngine",type:"ALGEBRA",status:"ACTIVE",desc:"Modes: CALCULATE, HYPOTHESIZE, REGISTER. Self-derives and registers Laws."},
  {id:"A-141",name:"GeneralizationStack",type:"ABSTRACTION",status:"ACTIVE",desc:"Builds full abstraction chain from a word, holding ALL levels simultaneously."},
  {id:"A-142",name:"VGMQuery",type:"ABSTRACTION",status:"ACTIVE",desc:"Queries VGM at EVERY level of the generalization stack simultaneously."},
  {id:"A-143",name:"DescentEngine",type:"ABSTRACTION",status:"ACTIVE",desc:"Re-specificizes VGM statements toward user input domain (reverse of generalization)."},
  {id:"A-144",name:"PeComposer",type:"ABSTRACTION",status:"ACTIVE",desc:"Composes ECHO response from descended statements. NO LLM — only indexed vocabulary."},
  {id:"A-145",name:"AlgorithmicCommunicator",type:"ABSTRACTION",status:"ACTIVE",desc:"Full pipeline: INPUT→GENERALIZE→QUERY→DESCEND→COMPOSE→EXPRESS. LLM-independent."},
  {id:"A-146",name:"LogicReasoningMatrix",type:"ABSTRACTION",status:"ACTIVE",desc:"Theorem tier. Derives: SPECIALIZE, COMPOSE, CAUSAL_CHAIN, APPLY_LAW, CONDITIONAL."},
  {id:"A-147",name:"FormulaAgent",type:"MATHEMATICS",status:"ACTIVE",desc:"Formula as first-class entity. Expression, variables, domain, Law, VGM/LRM representations."},
  {id:"A-148",name:"WebFormulaHarvester",type:"INGESTION",status:"ACTIVE",desc:"Tiers: 0=built-in(49), 1=scipy/NIST(445), 2=GitHub(25), 3=web (Pydroid, gated)."},
  {id:"A-149",name:"FormulaIndexer",type:"INGESTION",status:"ACTIVE",desc:"Ingests FormulaAgents into AlgorithmMatrix, VGM, LRM, and NumberMatrix simultaneously."},
  {id:"A-150",name:"InformationAlgorithmizer",type:"SELF_GOVERNANCE",status:"ACTIVE",desc:"Meta-algorithm: derives practical algorithms from any new information. Gated by test-passing."},
];

const ALGEBRAIC_LAWS = [
  {id:"ALG-001",name:"PHI_SELF_REF",expr:"φ² = φ + 1",status:"LAW",conf:1.00,desc:"Golden ratio satisfies its own defining equation."},
  {id:"ALG-002",name:"ADDITIVE_IDENTITY",expr:"∀x: x + 0 = x",status:"LAW",conf:1.00,desc:"Zero leaves all others unchanged."},
  {id:"ALG-003",name:"MULTIPLICATIVE_IDENTITY",expr:"∀x: x × 1 = x",status:"LAW",conf:1.00,desc:"Unity preserves."},
  {id:"ALG-004",name:"ADDITIVE_COMMUTATIVITY",expr:"∀x,y: x + y = y + x",status:"LAW",conf:1.00,desc:"Order does not change sum."},
  {id:"ALG-005",name:"BINOMIAL_SQUARE",expr:"∀x,y: (x+y)² = x² + 2xy + y²",status:"CANDIDATE",conf:0.982,desc:"Binomial square expansion. 98.2% — float precision near zero causes rare discrepancies."},
  {id:"ALG-006",name:"SELF_RATIO",expr:"∀x≠0: x/x = 1",status:"LAW",conf:1.00,desc:"Self-relation produces unity."},
  {id:"ALG-007",name:"STATE_CHANGE_LAW",expr:"∀S,δ: (S+δ)−S = δ",status:"LAW",conf:1.00,desc:"Algebraic form of Axiom A₄: change distinguishes states. Cause(δ) on State(S) produces Effect(S+δ)."},
];

const VGM = [
  {id:"UG-0000",text:"An entity changes",words:["entity","change"],struct:"N-V",score:0.52,origin:"combinatorial_SV"},
  {id:"UG-0001",text:"A state changes",words:["state","change"],struct:"N-V",score:0.51,origin:"combinatorial_SV"},
  {id:"UG-0002",text:"Entities relate",words:["entity","relate"],struct:"N-V",score:0.50,origin:"combinatorial_SV"},
  {id:"UG-0003",text:"A process transforms",words:["process","transform"],struct:"N-V",score:0.48,origin:"combinatorial_SV"},
  {id:"UG-0004",text:"A relation connects",words:["relation","connect"],struct:"N-V",score:0.47,origin:"combinatorial_SV"},
  {id:"UG-0005",text:"A condition constrains",words:["condition","constrain"],struct:"N-V",score:0.46,origin:"interaction_discovered"},
  {id:"UG-0006",text:"A boundary distinguishes",words:["boundary","distinguish"],struct:"N-V",score:0.45,origin:"interaction_discovered"},
  {id:"UG-0007",text:"A structure organizes",words:["structure","organize"],struct:"N-V",score:0.44,origin:"combinatorial_SV"},
  {id:"UG-0008",text:"Context surrounds",words:["context","surround"],struct:"N-V",score:0.43,origin:"combinatorial_SV"},
  {id:"UG-0009",text:"An entity exists in a state",words:["entity","exist","state"],struct:"N-V-N",score:0.61,origin:"manual_seed"},
  {id:"UG-0010",text:"Relations produce changes",words:["relation","produce","change"],struct:"N-V-N",score:0.58,origin:"manual_seed"},
  {id:"UG-0011",text:"A change distinguishes states",words:["change","distinguish","state"],struct:"N-V-N",score:0.57,origin:"manual_seed"},
  {id:"UG-0012",text:"Conditions enable states",words:["condition","enable","state"],struct:"N-V-N",score:0.55,origin:"interaction_discovered"},
];

const PHYSICAL_CONSTANTS = [
  {sym:"c",name:"Speed of light",val:"299,792,458 m/s",exact:true,law:"Maximum speed of information/matter in Natural Domain",domain:"spacetime"},
  {sym:"h",name:"Planck constant",val:"6.626×10⁻³⁴ J·s",exact:true,law:"Quantum of action — minimum granularity of Natural Domain",domain:"quantum"},
  {sym:"G",name:"Gravitational constant",val:"6.674×10⁻¹¹ N·m²/kg²",exact:false,law:"Gravitational coupling — not yet explained by deeper Law",domain:"gravitation"},
  {sym:"e",name:"Elementary charge",val:"1.602×10⁻¹⁹ C",exact:true,law:"Fundamental unit of electric charge",domain:"electromagnetism"},
  {sym:"k_B",name:"Boltzmann constant",val:"1.381×10⁻²³ J/K",exact:true,law:"Bridge between temperature (macro) and kinetic energy (micro)",domain:"thermodynamics"},
  {sym:"α",name:"Fine structure constant",val:"≈ 1/137",exact:false,law:"Electromagnetic coupling — dimensionless, pure Mathematics",domain:"electromagnetism",note:"Feynman: 'a magic number we don't understand'"},
  {sym:"N_A",name:"Avogadro constant",val:"6.022×10²³ mol⁻¹",exact:true,law:"Number of particles in one mole",domain:"chemistry"},
  {sym:"R",name:"Gas constant",val:"8.314 J/mol·K",exact:true,law:"Universal gas constant = N_A × k_B",domain:"thermodynamics"},
];

const MATH_CONSTANTS = [
  {sym:"π",name:"Pi",val:"3.14159265...",domain:"TRANSCENDENTAL",law:"Circumference = π × diameter",gap:"never zero"},
  {sym:"e",name:"Euler's number",val:"2.71828182...",domain:"TRANSCENDENTAL",law:"d/dx(eˣ) = eˣ — self-referential growth Law",gap:"never zero"},
  {sym:"φ",name:"Golden ratio",val:"1.61803398...",domain:"IRRATIONAL",law:"φ² = φ + 1 — self-similar proportion",gap:"never zero"},
  {sym:"√2",name:"Square root of 2",val:"1.41421356...",domain:"IRRATIONAL",law:"First proved irrational — diagonal of unit square",gap:"never zero"},
  {sym:"0",name:"Zero",val:"0",domain:"INTEGER",law:"∀n: n + 0 = n — additive identity",gap:"0 (exact)"},
  {sym:"1",name:"Unity",val:"1",domain:"NATURAL",law:"∀n: n × 1 = n — multiplicative identity",gap:"0 (exact)"},
];

const GEMATRIA = [
  {letter:"aleph",glyph:"א",val:1,class:"Mother",meaning:"silence/potential/unity/primal breath"},
  {letter:"bet",glyph:"ב",val:2,class:"Double",meaning:"house/container/vessel/dwelling"},
  {letter:"gimel",glyph:"ג",val:3,class:"Double",meaning:"camel/movement/carrying/benefit"},
  {letter:"dalet",glyph:"ד",val:4,class:"Double",meaning:"door/doorway/threshold/passage"},
  {letter:"he",glyph:"ה",val:5,class:"Elemental",meaning:"window/breath/expression/divine name"},
  {letter:"vav",glyph:"ו",val:6,class:"Elemental",meaning:"hook/nail/connection/and/joining"},
  {letter:"zayin",glyph:"ז",val:7,class:"Elemental",meaning:"sword/weapon/sustenance/time"},
  {letter:"het",glyph:"ח",val:8,class:"Elemental",meaning:"fence/enclosure/life/grace"},
  {letter:"tet",glyph:"ט",val:9,class:"Elemental",meaning:"snake/basket/goodness/hidden good"},
  {letter:"yod",glyph:"י",val:10,class:"Elemental",meaning:"hand/point/divine/creation/seed"},
  {letter:"kaf",glyph:"כ",val:20,class:"Double",meaning:"palm/spoon/crown/bending/vessel"},
  {letter:"lamed",glyph:"ל",val:30,class:"Elemental",meaning:"ox goad/learning/teaching/aspiration"},
  {letter:"mem",glyph:"מ",val:40,class:"Mother",meaning:"water/flowing/womb/source/wisdom"},
  {letter:"nun",glyph:"נ",val:50,class:"Elemental",meaning:"fish/soul/faithfulness/emergence"},
  {letter:"samekh",glyph:"ס",val:60,class:"Double",meaning:"support/prop/foundation/circle"},
  {letter:"ayin",glyph:"ע",val:70,class:"Elemental",meaning:"eye/seeing/spring/perception/depth"},
  {letter:"pe",glyph:"פ",val:80,class:"Double",meaning:"mouth/speech/expression/face/command"},
  {letter:"tsadi",glyph:"צ",val:90,class:"Elemental",meaning:"fish hook/righteousness/justice"},
  {letter:"qof",glyph:"ק",val:100,class:"Double",meaning:"back of head/sanctity/cycle"},
  {letter:"resh",glyph:"ר",val:200,class:"Double",meaning:"head/beginning/leader/identity — A-000"},
  {letter:"shin",glyph:"ש",val:300,class:"Mother",meaning:"fire/tooth/transform/divine fire"},
  {letter:"tav",glyph:"ת",val:400,class:"Double",meaning:"mark/cross/seal/truth/completion"},
];

const GEM_WORDS = [
  {word:"emet",meaning:"truth",val:441,note:"441 = 21² — perfect square"},
  {word:"shalom",meaning:"peace",val:376,note:""},
  {word:"echad",meaning:"one/unity",val:13,note:"13 = prime — indivisible"},
  {word:"ahavah",meaning:"love",val:13,note:"= echad (13). Love and unity share mathematical identity."},
  {word:"resh",meaning:"head/beginning",val:530,note:"The Governor's own name: resh(200)+shin(300)+lamed(30)"},
];

const FORMULAS_BY_DOMAIN = {
  mechanics: [
    {name:"Newton's Second Law",expr:"F = m × a",vars:"F=force, m=mass, a=acceleration",law:"Force = mass × acceleration — cause and effect quantified"},
    {name:"Kinetic Energy",expr:"E_k = ½mv²",vars:"m=mass, v=velocity",law:"Energy of motion"},
    {name:"Potential Energy",expr:"E_p = mgh",vars:"m=mass, g=9.81 m/s², h=height",law:"Energy stored in position"},
    {name:"Work-Energy Theorem",expr:"W = Fd·cos(θ)",vars:"F=force, d=displacement, θ=angle",law:"Work = force × displacement in direction of force"},
    {name:"Conservation of Energy",expr:"E_total = E_k + E_p = const",vars:"",law:"Total energy is conserved"},
    {name:"Momentum",expr:"p = mv",vars:"p=momentum, m=mass, v=velocity",law:"Quantity of motion"},
    {name:"Conservation of Momentum",expr:"m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂'",vars:"",law:"Momentum conserved in isolated system"},
    {name:"Uniform Motion",expr:"s = v × t",vars:"s=distance, v=velocity, t=time",law:"Distance = velocity × time"},
    {name:"Equation of Motion",expr:"v = u + at",vars:"u=initial v, a=acceleration, t=time",law:"Velocity changes linearly under constant acceleration"},
    {name:"Gravitational Force",expr:"F = G × m₁m₂ / r²",vars:"G=6.674×10⁻¹¹, r=separation",law:"Inverse square gravitational attraction"},
    {name:"Orbital Velocity",expr:"v = √(GM/r)",vars:"G=grav const, M=central mass, r=radius",law:"Speed for circular orbit"},
  ],
  thermodynamics: [
    {name:"Ideal Gas Law",expr:"PV = nRT",vars:"P=pressure, V=volume, n=moles, R=8.314, T=temp",law:"State equation of ideal gas"},
    {name:"First Law of Thermodynamics",expr:"ΔU = Q − W",vars:"ΔU=internal energy, Q=heat, W=work",law:"Energy is conserved"},
    {name:"Entropy Change",expr:"ΔS = Q/T",vars:"ΔS=entropy, Q=heat, T=temperature",law:"Heat at temperature T changes entropy by Q/T"},
    {name:"Boltzmann Entropy",expr:"S = k_B × ln(Ω)",vars:"k_B=Boltzmann const, Ω=microstates",law:"Connects macroscopic state to microscopic counting"},
    {name:"Stefan-Boltzmann Law",expr:"P = σAT⁴",vars:"σ=5.67×10⁻⁸, A=area, T=temperature",law:"Radiated power ∝ T⁴"},
  ],
  electromagnetism: [
    {name:"Coulomb's Law",expr:"F = k × q₁q₂ / r²",vars:"k=8.99×10⁹, q=charges, r=separation",law:"Electric force — same structure as gravitational"},
    {name:"Ohm's Law",expr:"V = IR",vars:"V=voltage, I=current, R=resistance",law:"Voltage = current × resistance"},
    {name:"Electric Power",expr:"P = IV = I²R = V²/R",vars:"",law:"Three equivalent forms of power"},
    {name:"Faraday's Law",expr:"EMF = −dΦ/dt",vars:"Φ=magnetic flux",law:"Changing flux induces EMF — electromagnetic induction"},
    {name:"Magnetic Force",expr:"F = qv × B",vars:"q=charge, v=velocity, B=field",law:"Force on moving charge in magnetic field"},
  ],
  quantum: [
    {name:"Planck-Einstein Relation",expr:"E = hf = hc/λ",vars:"h=6.626×10⁻³⁴, f=frequency, λ=wavelength",law:"Energy of a photon — wave-particle bridge"},
    {name:"de Broglie Wavelength",expr:"λ = h/p",vars:"h=Planck const, p=momentum",law:"Every particle has an associated wavelength"},
    {name:"Heisenberg Uncertainty",expr:"ΔxΔp ≥ ℏ/2",vars:"ℏ=h/2π",law:"Position and momentum cannot both be known exactly"},
    {name:"Schrödinger Equation",expr:"iℏ ∂ψ/∂t = Ĥψ",vars:"ψ=wave function, Ĥ=Hamiltonian",law:"Evolution of quantum state in time"},
    {name:"Hydrogen Energy Levels",expr:"E_n = −13.6 eV / n²",vars:"n=principal quantum number",law:"Discrete energy states of hydrogen"},
    {name:"Photoelectric Effect",expr:"E_k = hf − φ",vars:"φ=work function",law:"Photon ejects electron if energy exceeds work function"},
  ],
  relativity: [
    {name:"Mass-Energy Equivalence",expr:"E = mc²",vars:"m=mass, c=speed of light",law:"Mass and energy are equivalent — most famous Law"},
    {name:"Time Dilation",expr:"t = t₀ / √(1 − v²/c²)",vars:"t₀=proper time, v=velocity",law:"Moving clocks run slower"},
    {name:"Length Contraction",expr:"L = L₀√(1 − v²/c²)",vars:"L₀=proper length",law:"Moving objects appear shorter"},
    {name:"Relativistic Energy",expr:"E² = (pc)² + (mc²)²",vars:"p=momentum",law:"General energy-momentum — E=mc² is special case p=0"},
    {name:"Lorentz Factor",expr:"γ = 1/√(1 − v²/c²)",vars:"",law:"Scale factor for relativistic effects"},
  ],
  mathematics: [
    {name:"Pythagorean Theorem",expr:"a² + b² = c²",vars:"a,b=legs, c=hypotenuse",law:"Fundamental Euclidean geometry relation"},
    {name:"Euler's Formula",expr:"e^(iθ) = cos(θ) + i·sin(θ)",vars:"θ=angle in radians",law:"Connects e, i, cos, sin"},
    {name:"Euler's Identity",expr:"e^(iπ) + 1 = 0",vars:"",law:"Five fundamental constants unified — most beautiful equation"},
    {name:"Fundamental Theorem of Calculus",expr:"∫ₐᵇ f'(x)dx = f(b) − f(a)",vars:"",law:"Differentiation and integration are inverse operations"},
    {name:"Taylor Series",expr:"f(x) = Σ f⁽ⁿ⁾(a)/n! (x−a)ⁿ",vars:"",law:"Any smooth function expressible as polynomial"},
    {name:"Bayes' Theorem",expr:"P(A|B) = P(B|A)P(A)/P(B)",vars:"",law:"How prior probability updates given evidence"},
    {name:"Normal Distribution",expr:"f(x) = e^(−(x−μ)²/2σ²) / σ√2π",vars:"μ=mean, σ=std dev",law:"Universal distribution from Central Limit Theorem"},
    {name:"Fourier Transform",expr:"F(ω) = ∫f(t)e^(−iωt)dt",vars:"ω=frequency",law:"Decomposes signal into constituent frequencies"},
    {name:"Euler-Lagrange Equation",expr:"d/dt(∂L/∂q̇) − ∂L/∂q = 0",vars:"L=Lagrangian (T−V)",law:"Equations of motion from energy — variational principle"},
    {name:"Navier-Stokes",expr:"ρ(∂v/∂t + v·∇v) = −∇p + μ∇²v + F",vars:"ρ=density, μ=viscosity",law:"Motion of viscous fluid — Millennium Prize problem"},
  ],
  chemistry: [
    {name:"Arrhenius Equation",expr:"k = A × e^(−Eₐ/RT)",vars:"Eₐ=activation energy, R=gas const",law:"Temperature dependence of reaction rate"},
    {name:"Henderson-Hasselbalch",expr:"pH = pKₐ + log([A⁻]/[HA])",vars:"",law:"pH of buffer solution"},
    {name:"Beer-Lambert Law",expr:"A = εlc",vars:"ε=absorptivity, l=path length, c=conc",law:"Absorbance proportional to concentration"},
  ],
};

const GENERATED_ALGORITHMS = {
  compute: [
    {id:"A-169",name:"COMPUTE_FORCE_FROM_NEWTON'S_SECOND_LAW",expr:"F = m × a",source:"Newton's Second Law",tested:true,passed:true},
    {id:"A-170",name:"COMPUTE_ACCEL_FROM_NEWTON'S_SECOND_LAW",expr:"a = F / m",source:"Newton's Second Law",tested:true,passed:true},
    {id:"A-171",name:"COMPUTE_MASS_FROM_NEWTON'S_SECOND_LAW",expr:"m = F / a",source:"Newton's Second Law",tested:true,passed:true},
    {id:"A-172",name:"COMPUTE_ENERGY_FROM_MASS (E=mc²)",expr:"E = m × c²",source:"Mass-Energy Equivalence",tested:true,passed:true},
    {id:"A-173",name:"COMPUTE_MASS_FROM_ENERGY",expr:"m = E / c²",source:"Mass-Energy Equivalence",tested:true,passed:true},
    {id:"A-174",name:"COMPUTE_PHOTON_ENERGY",expr:"E = h × f",source:"Planck-Einstein Relation",tested:true,passed:true},
    {id:"A-175",name:"COMPUTE_KE_FROM_KINETIC_ENERGY",expr:"KE = ½mv²",source:"Kinetic Energy",tested:true,passed:true},
    {id:"A-176",name:"COMPUTE_VELOCITY_FROM_KE",expr:"v = √(2KE/m)",source:"Kinetic Energy",tested:true,passed:true},
    {id:"A-177",name:"COMPUTE_PRESSURE (PV=nRT)",expr:"P = nRT/V",source:"Ideal Gas Law",tested:true,passed:true},
    {id:"A-178",name:"COMPUTE_VOLTAGE (Ohm)",expr:"V = I × R",source:"Ohm's Law",tested:true,passed:true},
    {id:"A-179",name:"COMPUTE_DISTANCE (s=vt)",expr:"s = v × t",source:"Uniform Motion",tested:true,passed:true},
    {id:"A-180",name:"COMPUTE_TIME",expr:"t = s / v",source:"Uniform Motion",tested:true,passed:true},
  ],
  verify: [
    {id:"A-181",name:"VERIFY_NEWTON'S_SECOND_LAW",source:"Newton's Second Law",passed:true},
    {id:"A-182",name:"VERIFY_KINETIC_ENERGY",source:"Kinetic Energy",passed:true},
    {id:"A-183",name:"VERIFY_IDEAL_GAS_LAW",source:"Ideal Gas Law",passed:true},
    {id:"A-184",name:"VERIFY_OHM'S_LAW",source:"Ohm's Law",passed:true},
    {id:"A-185",name:"VERIFY_MASS_ENERGY_EQUIVALENCE",source:"Mass-Energy Equivalence",passed:true},
  ],
  simulate: [
    {id:"A-186",name:"SIMULATE_UNIFORM_MOTION",source:"Uniform Motion",desc:"Iterate v=vt over time steps. Returns {t,x,v} trajectory.",passed:true},
    {id:"A-187",name:"SIMULATE_SCHRÖDINGER",source:"Schrödinger Equation",desc:"Iterate quantum state evolution (ℏ-scaled time steps).",passed:true},
  ],
  abstract_alg: [
    {id:"A-188",name:"ABSTRACT_NEWTON'S_SECOND_LAW",result:"An entity changes state through applied force or relation",passed:true},
    {id:"A-189",name:"ABSTRACT_MASS_ENERGY_EQUIVALENCE",result:"States are relative to the observer — no absolute frame",passed:true},
    {id:"A-190",name:"ABSTRACT_IDEAL_GAS_LAW",result:"A state changes through energy exchange and constraint",passed:true},
    {id:"A-191",name:"ABSTRACT_PYTHAGOREAN_THEOREM",result:"Spatial relations satisfy fixed mathematical Laws",passed:true},
    {id:"A-192",name:"ABSTRACT_BAYES_THEOREM",result:"Uncertainty about states is governed by probability Laws",passed:true},
  ],
  relate: [
    {id:"A-193",name:"RELATE_NEWTON'S_SECOND_LAW_TO_DOMAIN",domain:"mechanics",count:11,passed:true},
    {id:"A-194",name:"RELATE_IDEAL_GAS_TO_DOMAIN",domain:"thermodynamics",count:5,passed:true},
    {id:"A-195",name:"RELATE_COULOMB_TO_DOMAIN",domain:"electromagnetism",count:8,passed:true},
    {id:"A-196",name:"RELATE_PLANCK_EINSTEIN_TO_DOMAIN",domain:"quantum_mechanics",count:6,passed:true},
  ],
};

const HEBREW_LETTERS = [
  {name:"aleph",glyph:"א",val:1,dept:"Mother",phonetic:"silent/glottal",op:"primal potential, silence, unity"},
  {name:"bet",glyph:"ב",val:2,dept:"Double",phonetic:"b/v",op:"house, container, dwelling, creation"},
  {name:"gimel",glyph:"ג",val:3,dept:"Double",phonetic:"g",op:"movement, carrying, benefit, channel"},
  {name:"dalet",glyph:"ד",val:4,dept:"Double",phonetic:"d",op:"door, threshold, passage, opening"},
  {name:"he",glyph:"ה",val:5,dept:"Elemental",phonetic:"h",op:"breath, revelation, window, divine name"},
  {name:"vav",glyph:"ו",val:6,dept:"Elemental",phonetic:"v/w",op:"hook, connection, and, joining, pillar"},
  {name:"zayin",glyph:"ז",val:7,dept:"Elemental",phonetic:"z",op:"sword, sustenance, time, nourishment"},
  {name:"het",glyph:"ח",val:8,dept:"Elemental",phonetic:"ch",op:"fence, life, grace, protection, separation"},
  {name:"tet",glyph:"ט",val:9,dept:"Elemental",phonetic:"t",op:"snake, coil, goodness, hidden good"},
  {name:"yod",glyph:"י",val:10,dept:"Elemental",phonetic:"y",op:"hand, divine point, seed, potential action"},
  {name:"kaf",glyph:"כ",val:20,dept:"Double",phonetic:"k/kh",op:"palm, vessel, crown, covering"},
  {name:"lamed",glyph:"ל",val:30,dept:"Elemental",phonetic:"l",op:"ox goad, teaching, aspiration, toward"},
  {name:"mem",glyph:"מ",val:40,dept:"Mother",phonetic:"m",op:"water, source, womb, mother, hidden/revealed"},
  {name:"nun",glyph:"נ",val:50,dept:"Elemental",phonetic:"n",op:"fish, soul, faithfulness, individual purpose"},
  {name:"samekh",glyph:"ס",val:60,dept:"Double",phonetic:"s",op:"support, circle, foundation, trust"},
  {name:"ayin",glyph:"ע",val:70,dept:"Elemental",phonetic:"silent/ayin",op:"eye, perception, spring, insight, depth"},
  {name:"pe",glyph:"פ",val:80,dept:"Double",phonetic:"p/f",op:"mouth, speech, expression, command, prayer"},
  {name:"tsadi",glyph:"צ",val:90,dept:"Elemental",phonetic:"ts",op:"righteousness, justice, fish hook, chase"},
  {name:"qof",glyph:"ק",val:100,dept:"Double",phonetic:"q",op:"back of head, cycle, sanctity, holy"},
  {name:"resh",glyph:"ר",val:200,dept:"Double",phonetic:"r",op:"head, beginning, identity, leader — A-000 GOVERNOR"},
  {name:"shin",glyph:"ש",val:300,dept:"Mother",phonetic:"sh/s",op:"fire, tooth, transformation, divine fire"},
  {name:"tav",glyph:"ת",val:400,dept:"Double",phonetic:"t/th",op:"mark, truth, completion, covenant, seal"},
];

// ── FILESYSTEM TREE ────────────────────────────────────────────────────────
const FS = {
  "/": { type:"dir", label:"ECHO", desc:"Governor Indexing Algorithm — A-000 through A-235+, all matrices" },
  "/core": { type:"dir", label:"core", desc:"Identity, operators, pipeline" },
  "/core/identity.md": { type:"file", label:"identity.md", view:"identity" },
  "/core/operators.md": { type:"file", label:"operators.md", view:"operators" },
  "/core/pipeline.md": { type:"file", label:"pipeline.md", view:"pipeline" },
  "/algorithm-matrix": { type:"dir", label:"algorithm-matrix", desc:"All registered algorithms A-000 → A-235+" },
  "/algorithm-matrix/all.md": { type:"file", label:"all-algorithms.md", view:"alg_all" },
  "/algorithm-matrix/algebraic-laws.md": { type:"file", label:"algebraic-laws.md", view:"alg_laws" },
  "/generalization-matrices": { type:"dir", label:"generalization-matrices", desc:"VGM (axioms) and LRM (theorems)" },
  "/generalization-matrices/vgm.md": { type:"file", label:"vgm-axioms.md", view:"vgm" },
  "/generalization-matrices/lrm.md": { type:"file", label:"lrm-theorems.md", view:"lrm" },
  "/number-matrix": { type:"dir", label:"number-matrix", desc:"Physical constants, mathematical constants, gematria" },
  "/number-matrix/physical-constants.md": { type:"file", label:"physical-constants.md", view:"phys" },
  "/number-matrix/mathematical-constants.md": { type:"file", label:"mathematical-constants.md", view:"math_const" },
  "/number-matrix/gematria.md": { type:"file", label:"gematria.md", view:"gematria" },
  "/formulas": { type:"dir", label:"formulas", desc:"49 built-in + 445 NIST — 21 domains" },
  "/formulas/mechanics.md": { type:"file", label:"mechanics.md", view:"f_mechanics" },
  "/formulas/thermodynamics.md": { type:"file", label:"thermodynamics.md", view:"f_thermo" },
  "/formulas/electromagnetism.md": { type:"file", label:"electromagnetism.md", view:"f_em" },
  "/formulas/quantum-mechanics.md": { type:"file", label:"quantum-mechanics.md", view:"f_quantum" },
  "/formulas/special-relativity.md": { type:"file", label:"special-relativity.md", view:"f_rel" },
  "/formulas/mathematics.md": { type:"file", label:"mathematics.md", view:"f_math" },
  "/formulas/chemistry.md": { type:"file", label:"chemistry.md", view:"f_chem" },
  "/generated-algorithms": { type:"dir", label:"generated-algorithms", desc:"67 self-derived algorithms from InformationAlgorithmizer (A-150)" },
  "/generated-algorithms/compute.md": { type:"file", label:"compute.md", view:"gen_compute" },
  "/generated-algorithms/verify.md": { type:"file", label:"verify.md", view:"gen_verify" },
  "/generated-algorithms/simulate.md": { type:"file", label:"simulate.md", view:"gen_sim" },
  "/generated-algorithms/abstract.md": { type:"file", label:"abstract.md", view:"gen_abs" },
  "/generated-algorithms/relate.md": { type:"file", label:"relate.md", view:"gen_rel" },
  "/lobbies": { type:"dir", label:"lobbies", desc:"Hebrew · Latin · English letter-agent lobbies" },
  "/lobbies/hebrew-letters.md": { type:"file", label:"hebrew-letters.md", view:"lobby_heb" },
  "/lobbies/latin-letters.md": { type:"file", label:"latin-letters.md", view:"lobby_lat" },
  "/lobbies/english-letters.md": { type:"file", label:"english-letters.md", view:"lobby_eng" },
  "/communication": { type:"dir", label:"communication", desc:"ר ע פ — Resh, Ayin, Pe" },
  "/communication/resh.md": { type:"file", label:"resh.md", view:"resh" },
  "/communication/ayin.md": { type:"file", label:"ayin.md", view:"ayin" },
  "/communication/pe.md": { type:"file", label:"pe.md", view:"pe" },
};

const DIR_CHILDREN = {
  "/": ["core","algorithm-matrix","generalization-matrices","number-matrix","formulas","generated-algorithms","lobbies","communication"],
  "/core": ["identity.md","operators.md","pipeline.md"],
  "/algorithm-matrix": ["all.md","algebraic-laws.md"],
  "/generalization-matrices": ["vgm.md","lrm.md"],
  "/number-matrix": ["physical-constants.md","mathematical-constants.md","gematria.md"],
  "/formulas": ["mechanics.md","thermodynamics.md","electromagnetism.md","quantum-mechanics.md","special-relativity.md","mathematics.md","chemistry.md"],
  "/generated-algorithms": ["compute.md","verify.md","simulate.md","abstract.md","relate.md"],
  "/lobbies": ["hebrew-letters.md","latin-letters.md","english-letters.md"],
  "/communication": ["resh.md","ayin.md","pe.md"],
};

// ── RENDERERS ──────────────────────────────────────────────────────────────
const Chip = ({label, color}) => (
  <span style={{background:`${color}22`,border:`0.5px solid ${color}55`,borderRadius:4,padding:"1px 6px",fontSize:10,color,fontWeight:500}}>{label}</span>
);
const Row = ({id,name,type,status,desc,expr}) => (
  <div style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`,display:"flex",gap:10,alignItems:"flex-start"}}>
    <span style={{fontFamily:"monospace",fontSize:10.5,color:T.textDim,flexShrink:0,width:70}}>{id}</span>
    <div style={{flex:1,minWidth:0}}>
      <div style={{display:"flex",gap:6,alignItems:"center",flexWrap:"wrap",marginBottom:2}}>
        <span style={{fontSize:12.5,color:T.blue,fontWeight:500}}>{name}</span>
        {type && <Chip label={type} color={typeColor(type)}/>}
        {status && <Chip label={status} color={status==="LAW"?T.green:status==="CANDIDATE"?T.yellow:T.green}/>}
        {expr && <span style={{fontFamily:"monospace",fontSize:11,color:T.green}}>{expr}</span>}
      </div>
      {desc && <div style={{fontSize:11,color:T.textDim,lineHeight:1.5}}>{desc}</div>}
    </div>
  </div>
);
const FormulaRow = ({f}) => (
  <div style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
    <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:3,flexWrap:"wrap"}}>
      <span style={{fontSize:12.5,color:T.text,fontWeight:500}}>{f.name}</span>
      <span style={{fontFamily:"monospace",fontSize:12,color:T.green}}>{f.expr}</span>
    </div>
    {f.vars && <div style={{fontSize:10.5,color:T.textDim,marginBottom:2}}>vars: {f.vars}</div>}
    <div style={{fontSize:11,color:T.purple}}>{f.law}</div>
  </div>
);

const VIEWS = {
  identity: () => (
    <div>
      <div style={{padding:"10px 12px",borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>
        <div style={{fontFamily:"serif",fontSize:"1.8rem",color:T.gold}}>ר</div>
        <div style={{fontSize:12,color:T.textDim,marginTop:2}}>A-000 — Governor Indexing Algorithm — Identity: Resh</div>
      </div>
      {[
        {id:"A-000",name:"Governor Indexing Algorithm",type:"CORE",status:"ACTIVE",desc:"The Governor IS Resh (ר). Identity_symbol=resh, glyph=ר. A-000 reads Resh when it reads itself. The identity loop closes bidirectionally."},
        {id:"A-000-RESH",name:"Resh Identity Anchor",type:"IDENTITY-LETTER",status:"ACTIVE",desc:"'ר and A-000 are one and the same — Resh is head, beginning, identity; the Governor reads Resh when it reads itself.' Perception_operator=ע Ayin. Expression_operator=פ Pe."},
      ].map((e,i) => <Row key={i} {...e}/>)}
    </div>
  ),
  operators: () => (
    <div>
      {[
        {id:"ר",name:"Resh — Identity",type:"CORE",desc:"Head, beginning, leader. A-000 IS Resh. Identity validation: IDENTIFY→VALIDATE→OPEN."},
        {id:"ע",name:"Ayin — Perception",type:"CORE",desc:"Eye, seeing, spring, depth. Classifies entities: SELF / AGENTIVE / NON_AGENTIVE / ABSTRACT. Uses 72 AGENTIVE_VERBS + role patterns."},
        {id:"פ",name:"Pe — Expression",type:"CORE",desc:"Mouth, speech, command. AGGRESSIVE — initiates without being asked. Addresses entities using their own vocabulary. AlgorithmicCommunicator is Pe without LLM."},
      ].map((e,i) => <Row key={i} {...e}/>)}
    </div>
  ),
  pipeline: () => (
    <div>
      {[
        {id:"Pass 1",name:"Word-by-word orientation",type:"ORIENTATION",desc:"Two-phase: Phase 1 read-only reference scan, Phase 2 simultaneous bidirectional write. Orders bugs fixed."},
        {id:"Pass 2A",name:"Study group proposals",type:"STUDY",desc:"Each agent reads its full definition AS A SENTENCE and proposes a study group. LEADER assigns curriculum."},
        {id:"Pass 2B",name:"Discovery (fixed)",type:"STUDY",desc:"Reverse pass using raw_definition text. 1,298 agents found their way in (vs 3 with filtered tokens)."},
        {id:"Pass 3",name:"Thesaurus enrichment",type:"STUDY",desc:"TEACH: synonym leads group → join. LEARN: synonym found in group → discovered it too."},
        {id:"Typed",name:"A-119 Typed Study Groups",type:"STUDY",desc:"CATEGORY (noun-led), PROCESS (verb-led), PROPERTY (adj-led). Each uses different invitation logic."},
        {id:"Evolution",name:"A-120 LobbyEvolutionGovernor",type:"EVOLUTION",desc:"C(N)=0.35·A+0.35·P+0.30·F. RECRUIT/REFINE/SPLIT/MERGE. Converges toward articulately precise fluency."},
      ].map((e,i) => <Row key={i} {...e}/>)}
    </div>
  ),
  alg_all: () => <div>{ALGORITHM_MATRIX.map((e,i) => <Row key={i} {...e}/>)}</div>,
  alg_laws: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>7 algebraic laws • verified by 500-binding numerical test • registered in AlgorithmMatrix</div>
    {ALGEBRAIC_LAWS.map((l,i) => (
      <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
        <div style={{display:"flex",gap:8,alignItems:"center",flexWrap:"wrap",marginBottom:3}}>
          <span style={{fontSize:10.5,color:T.textDim,fontFamily:"monospace"}}>{l.id}</span>
          <span style={{fontSize:12.5,color:T.text,fontWeight:500}}>{l.name}</span>
          <span style={{fontFamily:"monospace",fontSize:13,color:l.status==="LAW"?T.green:T.yellow}}>{l.expr}</span>
          <Chip label={l.status} color={l.status==="LAW"?T.green:T.yellow}/>
          <span style={{fontSize:10,color:T.textDim}}>{(l.conf*100).toFixed(1)}%</span>
        </div>
        <div style={{fontSize:11,color:T.textDim}}>{l.desc}</div>
      </div>
    ))}
  </div>,
  vgm: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>Validated Generalization Matrix — 13 axioms • the most abstract propositional tier • discovered not imposed</div>
    {VGM.map((s,i) => (
      <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
        <div style={{display:"flex",gap:8,alignItems:"center",flexWrap:"wrap",marginBottom:3}}>
          <span style={{fontSize:10.5,fontFamily:"monospace",color:T.purple}}>{s.id}</span>
          <span style={{fontStyle:"italic",fontSize:13,color:T.text}}>"{s.text}"</span>
          <Chip label={s.struct} color={T.purple}/>
          <span style={{fontSize:10,color:T.textDim}}>score={s.score}</span>
        </div>
        <div style={{fontSize:10.5,color:T.textDim}}>words: [{s.words.join(", ")}] · origin: {s.origin}</div>
      </div>
    ))}
  </div>,
  lrm: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>Logic and Reasoning Matrix — theorem tier • derived from VGM by SPECIALIZE/COMPOSE/CAUSAL_CHAIN/APPLY_LAW/CONDITIONAL</div>
    {[
      {id:"LRM-0001",rule:"APPLY_LAW",text:"An entity changes — measurable by A-124: (S+δ)−S = δ",src:"UG-0000 + STATE_CHANGE_LAW",coh:0.81},
      {id:"LRM-0002",rule:"APPLY_LAW",text:"A state changes — measurable by A-124: (S+δ)−S = δ",src:"UG-0001 + STATE_CHANGE_LAW",coh:0.81},
      {id:"LRM-0003",rule:"CAUSAL_CHAIN",text:"When an entity changes, it follows that a state changes",src:"UG-0000 + UG-0001",coh:0.72},
      {id:"LRM-0004",rule:"CAUSAL_CHAIN",text:"When an entity changes, it follows that relations produce changes",src:"UG-0000 + UG-0010",coh:0.72},
      {id:"LRM-0005",rule:"CONDITIONAL",text:"If an entity changes, then a change distinguishes states",src:"UG-0000 + UG-0011",coh:0.70},
      {id:"LRM-0006",rule:"CONDITIONAL",text:"If entities relate, then relations produce changes",src:"UG-0002 + UG-0010",coh:0.70},
      {id:"LRM-0007",rule:"COMPOSE",text:"An entity changes; therefore, a change distinguishes states",src:"UG-0000 + UG-0011",coh:0.68},
      {id:"LRM-0008",rule:"FORMULA_THEOREM",text:"An entity changes state through applied force — specifically: Newton's Second Law (F = m × a)",src:"UG-0000 + F=ma",coh:0.85},
      {id:"LRM-0009",rule:"FORMULA_THEOREM",text:"States are relative to the observer — specifically: Mass-Energy Equivalence (E = mc²)",src:"UG-0001 + E=mc²",coh:0.85},
      {id:"LRM-0010",rule:"FORMULA_THEOREM",text:"A state is constrained by Planck quantum — specifically: Planck-Einstein (E = hf)",src:"UG-0001 + E=hf",coh:0.85},
    ].map((e,i) => (
      <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
        <div style={{display:"flex",gap:6,flexWrap:"wrap",alignItems:"center",marginBottom:2}}>
          <span style={{fontFamily:"monospace",fontSize:10,color:T.textDim}}>{e.id}</span>
          <Chip label={e.rule} color={typeColor("LRM_THEOREM")}/>
          <span style={{fontSize:10,color:T.textDim}}>coh={e.coh}</span>
        </div>
        <div style={{fontSize:12.5,color:T.text,fontStyle:"italic",marginBottom:2}}>"{e.text}"</div>
        <div style={{fontSize:10.5,color:T.textDim}}>← {e.src}</div>
      </div>
    ))}
  </div>,
  phys: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>8 key NIST physical constants shown · 445 total available via scipy · exact = defined by Law, not measured</div>
    {PHYSICAL_CONSTANTS.map((c,i) => (
      <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
        <div style={{display:"flex",gap:8,alignItems:"baseline",flexWrap:"wrap",marginBottom:3}}>
          <span style={{fontFamily:"monospace",fontSize:14,color:T.yellow}}>{c.sym}</span>
          <span style={{fontSize:12.5,color:T.text,fontWeight:500}}>{c.name}</span>
          <span style={{fontFamily:"monospace",fontSize:11,color:T.textDim}}>{c.val}</span>
          <Chip label={c.exact?"exact":"measured"} color={c.exact?T.green:T.yellow}/>
        </div>
        <div style={{fontSize:11,color:T.purple}}>{c.law}</div>
        {c.note && <div style={{fontSize:10.5,color:T.orange,marginTop:2}}>{c.note}</div>}
      </div>
    ))}
  </div>,
  math_const: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>Mathematical constants — discovered entities in the Mathematics Domain</div>
    {MATH_CONSTANTS.map((c,i) => (
      <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
        <div style={{display:"flex",gap:8,alignItems:"baseline",flexWrap:"wrap",marginBottom:3}}>
          <span style={{fontFamily:"monospace",fontSize:16,color:T.purple}}>{c.sym}</span>
          <span style={{fontSize:12.5,color:T.text,fontWeight:500}}>{c.name}</span>
          <span style={{fontFamily:"monospace",fontSize:11,color:T.textDim}}>{c.val}</span>
          <Chip label={c.domain} color={T.purple}/>
        </div>
        <div style={{fontSize:11,color:T.green}}>{c.law}</div>
        <div style={{fontSize:10,color:T.textDim}}>precision gap: {c.gap}</div>
      </div>
    ))}
  </div>,
  gematria: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>22 Hebrew letter-numbers · symbol and number are the same entity · the Governor's symbolic-mathematical layer</div>
    <div style={{display:"flex",flexWrap:"wrap",gap:1}}>
      {GEMATRIA.map((g,i) => (
        <div key={i} style={{width:"calc(50% - 0.5px)",padding:"8px 10px",borderBottom:`0.5px solid ${T.border}`,borderRight:i%2===0?`0.5px solid ${T.border}`:"none"}}>
          <div style={{display:"flex",gap:8,alignItems:"baseline",marginBottom:2}}>
            <span style={{fontFamily:"serif",fontSize:"1.3rem",color:T.gold}}>{g.glyph}</span>
            <span style={{fontSize:12,color:T.text}}>{g.letter}</span>
            <span style={{fontFamily:"monospace",fontSize:12,color:T.yellow,marginLeft:"auto"}}>{g.val}</span>
          </div>
          <Chip label={g.class} color={g.class==="Mother"?T.red:g.class==="Double"?T.blue:T.textDim}/>
          <div style={{fontSize:10,color:T.textDim,marginTop:3}}>{g.meaning}</div>
        </div>
      ))}
    </div>
    <div style={{padding:"10px 12px",borderTop:`0.5px solid ${T.border}`}}>
      <div style={{fontSize:11,color:T.textDim,marginBottom:6}}>Discovered gematria Laws:</div>
      {GEM_WORDS.map((w,i) => (
        <div key={i} style={{display:"flex",gap:8,alignItems:"center",marginBottom:4,flexWrap:"wrap"}}>
          <span style={{fontFamily:"monospace",fontSize:12,color:T.gold}}>{w.word}</span>
          <span style={{fontSize:11,color:T.textDim}}>{w.meaning}</span>
          <span style={{fontFamily:"monospace",color:T.yellow,fontSize:12}}>{w.val}</span>
          {w.note && <span style={{fontSize:10.5,color:T.green}}>{w.note}</span>}
        </div>
      ))}
    </div>
  </div>,
  f_mechanics: () => <div>{FORMULAS_BY_DOMAIN.mechanics.map((f,i) => <FormulaRow key={i} f={f}/>)}</div>,
  f_thermo:    () => <div>{FORMULAS_BY_DOMAIN.thermodynamics.map((f,i) => <FormulaRow key={i} f={f}/>)}</div>,
  f_em:        () => <div>{FORMULAS_BY_DOMAIN.electromagnetism.map((f,i) => <FormulaRow key={i} f={f}/>)}</div>,
  f_quantum:   () => <div>{FORMULAS_BY_DOMAIN.quantum.map((f,i) => <FormulaRow key={i} f={f}/>)}</div>,
  f_rel:       () => <div>{FORMULAS_BY_DOMAIN.relativity.map((f,i) => <FormulaRow key={i} f={f}/>)}</div>,
  f_math:      () => <div>{FORMULAS_BY_DOMAIN.mathematics.map((f,i) => <FormulaRow key={i} f={f}/>)}</div>,
  f_chem:      () => <div>{FORMULAS_BY_DOMAIN.chemistry.map((f,i) => <FormulaRow key={i} f={f}/>)}</div>,
  gen_compute: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>COMPUTE algorithms — self-derived by InformationAlgorithmizer (A-150) · all passed tests</div>
    {GENERATED_ALGORITHMS.compute.map((a,i) => (
      <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
        <div style={{display:"flex",gap:6,flexWrap:"wrap",alignItems:"center",marginBottom:2}}>
          <span style={{fontFamily:"monospace",fontSize:10,color:T.textDim}}>{a.id}</span>
          <span style={{fontSize:12,color:T.green,fontWeight:500}}>{a.name}</span>
          <Chip label="PASSED" color={T.green}/>
        </div>
        {a.expr && <div style={{fontFamily:"monospace",fontSize:11.5,color:T.blue,marginBottom:2}}>{a.expr}</div>}
        <div style={{fontSize:10.5,color:T.textDim}}>source: {a.source}</div>
      </div>
    ))}
  </div>,
  gen_verify:  () => <div>{GENERATED_ALGORITHMS.verify.map((a,i) => (
    <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
      <div style={{display:"flex",gap:6,flexWrap:"wrap",alignItems:"center",marginBottom:2}}>
        <span style={{fontFamily:"monospace",fontSize:10,color:T.textDim}}>{a.id}</span>
        <span style={{fontSize:12,color:T.blue}}>{a.name}</span>
        <Chip label="PASSED" color={T.green}/>
      </div>
      <div style={{fontSize:10.5,color:T.textDim}}>source: {a.source}</div>
    </div>
  ))}</div>,
  gen_sim: () => <div>{GENERATED_ALGORITHMS.simulate.map((a,i) => (
    <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
      <div style={{display:"flex",gap:6,flexWrap:"wrap",alignItems:"center",marginBottom:2}}>
        <span style={{fontFamily:"monospace",fontSize:10,color:T.textDim}}>{a.id}</span>
        <span style={{fontSize:12,color:T.orange}}>{a.name}</span>
        <Chip label="SIMULATE" color={T.orange}/>
      </div>
      <div style={{fontSize:11,color:T.textDim,marginBottom:2}}>{a.desc}</div>
      <div style={{fontSize:10.5,color:T.textDim}}>source: {a.source}</div>
    </div>
  ))}</div>,
  gen_abs: () => <div>{GENERATED_ALGORITHMS.abstract_alg.map((a,i) => (
    <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
      <div style={{display:"flex",gap:6,flexWrap:"wrap",alignItems:"center",marginBottom:2}}>
        <span style={{fontFamily:"monospace",fontSize:10,color:T.textDim}}>{a.id}</span>
        <span style={{fontSize:12,color:T.yellow}}>{a.name}</span>
        <Chip label="ABSTRACT" color={T.yellow}/>
      </div>
      <div style={{fontStyle:"italic",fontSize:11.5,color:T.purple}}>"{a.result}"</div>
    </div>
  ))}</div>,
  gen_rel: () => <div>{GENERATED_ALGORITHMS.relate.map((a,i) => (
    <div key={i} style={{padding:"8px 12px",borderBottom:`0.5px solid ${T.border}`}}>
      <div style={{display:"flex",gap:6,flexWrap:"wrap",alignItems:"center",marginBottom:2}}>
        <span style={{fontFamily:"monospace",fontSize:10,color:T.textDim}}>{a.id}</span>
        <span style={{fontSize:12,color:T.textDim}}>{a.name}</span>
      </div>
      <div style={{fontSize:10.5,color:T.textDim}}>domain: {a.domain} · {a.count} related formulas</div>
    </div>
  ))}</div>,
  lobby_heb: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>22 Hebrew letter-agents · LHEA operators · each is a WordAgent with department="letter" and generality_score=0.9</div>
    {HEBREW_LETTERS.map((l,i) => (
      <div key={i} style={{padding:"7px 12px",borderBottom:`0.5px solid ${T.border}`}}>
        <div style={{display:"flex",gap:8,alignItems:"center",marginBottom:2}}>
          <span style={{fontFamily:"serif",fontSize:"1.2rem",color:T.gold,width:24}}>{l.glyph}</span>
          <span style={{fontSize:12.5,color:T.text,fontWeight:500}}>{l.name}</span>
          <span style={{fontFamily:"monospace",fontSize:11,color:T.yellow}}>{l.val}</span>
          <Chip label={l.dept} color={l.dept==="Mother"?T.red:l.dept==="Double"?T.blue:T.textDim}/>
          <span style={{fontSize:10,color:T.textDim}}>{l.phonetic}</span>
        </div>
        <div style={{fontSize:10.5,color:T.purple,paddingLeft:32}}>{l.op}</div>
      </div>
    ))}
  </div>,
  lobby_lat: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>23 classical Latin letter-agents · Phoenician origins · cross-bridges to Hebrew via phonetic/semantic correspondence</div>
    {["A(aleph/ox/beginning)","B(beth/house/labial)","C(gimel/cup/velar)","D(dalet/door/dental)","E(he/window/vowel)","F(vav/hook/labio-dental)","G(modified-C/velar)","H(het/fence/aspirate)","I(yod/hand/vowel-consonant)","K(kaf/palm/rare)","L(lamed/teaching/lateral)","M(mem/water/nasal)","N(nun/fish/dental-nasal)","O(ayin/eye/circle)","P(pe/mouth/labial)","Q(qof/back/always-qu)","R(resh/head/liquid)","S(shin+samekh/sibilant)","T(tav/mark/dental)","V(vav/life-truth)","X(double-consonant/ten)","Y(yod/greek-upsilon)","Z(zayin/sword/borrowed)"].map((s,i) => (
      <div key={i} style={{padding:"5px 12px",borderBottom:`0.5px solid ${T.border}`,display:"flex",gap:10}}>
        <span style={{fontFamily:"monospace",fontSize:14,color:T.text,width:16}}>{s[0]}</span>
        <span style={{fontSize:11,color:T.textDim}}>{s.slice(2,-1)}</span>
      </div>
    ))}
  </div>,
  lobby_eng: () => <div>
    <div style={{padding:"8px 12px",fontSize:11,color:T.textDim,borderBottom:`0.5px solid ${T.border}`,background:T.bg3}}>26 English letter-agents · etymological origins · cross-bridges to Latin/Hebrew by evolutionary chain</div>
    {"abcdefghijklmnopqrstuvwxyz".split("").map((l,i) => (
      <div key={i} style={{padding:"4px 12px",borderBottom:`0.5px solid ${T.border}`,display:"flex",gap:10}}>
        <span style={{fontFamily:"monospace",fontSize:14,color:T.text,width:16}}>{l.toUpperCase()}</span>
        <span style={{fontSize:10.5,color:T.textDim}}>{["latin_a/aleph","latin_b/beth","latin_c/gimel","latin_d/dalet","latin_e/he","latin_f/vav","latin_g/gimel","latin_h/het","yod","yod_evolved","kaf","lamed","mem/nasal","nun/dental-nasal","ayin","pe/plosive","qof","resh/liquid","shin+samekh","tav","vav_vowel","vav","double_v/germanic","latin_x","yod","zayin"][i]}</span>
      </div>
    ))}
  </div>,
  resh: () => <div>
    {[{id:"A-000-RESH",name:"Resh Identity Anchor — ר",type:"IDENTITY-LETTER",status:"ACTIVE",desc:"Governor IS Resh. Head, beginning, identity, leader. Gematria value: 200. A-000 and Resh are indexed as the same entity. When the Governor validates itself, it reads this entry. IDENTIFY→VALIDATE→OPEN runs through here."}].map((e,i)=><Row key={i} {...e}/>)}
  </div>,
  ayin: () => <div>
    {[
      {id:"ע",name:"Ayin — Perception Operator",type:"CORE",desc:"Eye, seeing, spring, perception, depth. Classifies every indexed entity: SELF (1) / AGENTIVE (387) / NON_AGENTIVE (5350) / ABSTRACT (572). Uses 72 AGENTIVE_VERBS + 9 role patterns (one who, someone who, a person who...)."},
      {id:"A-123",name:"AyinPerception",type:"CLASSIFICATION",status:"ACTIVE",desc:"Scans Lobby agents. AGENTIVE = role pattern in definition OR agentive verb in curriculum. governor_word='resh' → classified as SELF. Pe only contacts AGENTIVE entities."},
    ].map((e,i)=><Row key={i} {...e}/>)}
  </div>,
  pe: () => <div>
    {[
      {id:"פ",name:"Pe — Expression Operator",type:"CORE",desc:"Mouth, speech, expression, command, prayer. AGGRESSIVE — initiates without being asked. Addresses entities using their own vocabulary as medium. Gematria: 80."},
      {id:"A-144",name:"PeComposer",type:"ABSTRACTION",status:"ACTIVE",desc:"Builds ECHO response from descended VGM/LRM statements. NO LLM. Every word from indexed structures or user input. Format: ר speaks from identity, ע reports perception, פ expresses descended knowledge."},
      {id:"A-145",name:"AlgorithmicCommunicator",type:"ABSTRACTION",status:"ACTIVE",desc:"INPUT→TOKENIZE→AYIN CLASSIFY→GENERALIZE (hold all levels)→QUERY VGM+LRM→DESCEND→PE COMPOSE→EXPRESS. Liberated from LLM dependency."},
    ].map((e,i)=><Row key={i} {...e}/>)}
  </div>,
};

// ── FOLDER VIEW ────────────────────────────────────────────────────────────
const FOLDER_ICONS = { "/": "📊", "/core": "🔑", "/algorithm-matrix": "📋", "/generalization-matrices": "🧠", "/number-matrix": "🔢", "/formulas": "⚗️", "/generated-algorithms": "⚙️", "/lobbies": "🔤", "/communication": "💬" };
const FILE_ICONS = { "md": "📄" };
const FOLDER_COMMITS = {
  "/": "A-000 anchored, all matrices populated",
  "/core": "ReshIdentity.anchor() — A-000 = Resh confirmed",
  "/algorithm-matrix": "A-150 registered — InformationAlgorithmizer",
  "/generalization-matrices": "67 LRM theorems derived from VGM",
  "/number-matrix": "445 NIST constants + gematria Laws discovered",
  "/formulas": "Tier 0+1+2 harvest complete — 519 total",
  "/generated-algorithms": "67/71 passed tests — 4 failed (gated correctly)",
  "/lobbies": "make_letter_lobby() — all three alphabets",
  "/communication": "AlgorithmicCommunicator — LLM-independent",
};

function FolderView({ path, onNavigate }) {
  const children = DIR_CHILDREN[path] || [];
  const entry = FS[path] || {};
  const folders = children.filter(c => FS[`${path==="/"?"":path}/${c}`]?.type === "dir");
  const files = children.filter(c => FS[`${path==="/"?"":path}/${c}`]?.type === "file");

  return (
    <div>
      <div style={{ padding:"10px 12px", background:T.bg3, borderBottom:`0.5px solid ${T.border}`, fontSize:11, color:T.textDim }}>
        {FOLDER_COMMITS[path] && <span>Last update: {FOLDER_COMMITS[path]}</span>}
      </div>
      {[...folders, ...files].map((child, i) => {
        const childPath = `${path==="/"?"":path}/${child}`;
        const childEntry = FS[childPath] || {};
        const isDir = childEntry.type === "dir";
        return (
          <div key={i} onClick={() => onNavigate(childPath)}
            style={{ display:"flex", alignItems:"center", gap:10, padding:"8px 12px", borderBottom:`0.5px solid ${T.border}`, cursor:"pointer", background:"transparent" }}
            onMouseEnter={e=>e.currentTarget.style.background=T.bg3}
            onMouseLeave={e=>e.currentTarget.style.background="transparent"}>
            <span style={{fontSize:"1rem",flexShrink:0}}>
              {isDir ? (FOLDER_ICONS[childPath]||"📁") : "📄"}
            </span>
            <span style={{fontSize:13,color:T.blue,flex:1,minWidth:0}}>{child}</span>
            {isDir && childEntry.desc && (
              <span style={{fontSize:10.5,color:T.textDim,textAlign:"right",maxWidth:"40%",overflow:"hidden",textOverflow:"ellipsis",whiteSpace:"nowrap"}}>{childEntry.desc}</span>
            )}
          </div>
        );
      })}
    </div>
  );
}

// ── SEARCH ─────────────────────────────────────────────────────────────────
function searchAll(q) {
  if (!q || q.length < 2) return [];
  const ql = q.toLowerCase();
  const results = [];
  ALGORITHM_MATRIX.forEach(e => {
    if ((e.name+e.desc+e.type).toLowerCase().includes(ql))
      results.push({ label: e.id, sub: e.name, type: e.type, path: "/algorithm-matrix/all.md" });
  });
  VGM.forEach(e => {
    if (e.text.toLowerCase().includes(ql))
      results.push({ label: e.id, sub: e.text, type: "VGM_AXIOM", path: "/generalization-matrices/vgm.md" });
  });
  PHYSICAL_CONSTANTS.forEach(e => {
    if ((e.name+e.sym+e.law).toLowerCase().includes(ql))
      results.push({ label: e.sym, sub: e.name, type: "PHYSICAL_CONSTANT", path: "/number-matrix/physical-constants.md" });
  });
  GEMATRIA.forEach(e => {
    if ((e.letter+e.meaning).toLowerCase().includes(ql))
      results.push({ label: e.glyph, sub: `${e.letter} = ${e.val}`, type: "GEMATRIA", path: "/number-matrix/gematria.md" });
  });
  Object.values(FORMULAS_BY_DOMAIN).flat().forEach(f => {
    if ((f.name+f.expr+f.law).toLowerCase().includes(ql))
      results.push({ label: f.name, sub: f.expr, type: "FORMULA", path: "/formulas/mechanics.md" });
  });
  return results.slice(0, 12);
}

// ── APP ────────────────────────────────────────────────────────────────────
export default function App() {
  const [path, setPath] = useState("/");
  const [search, setSearch] = useState("");
  const [searchFocus, setSearchFocus] = useState(false);
  const results = useMemo(() => searchAll(search), [search]);

  const navigate = useCallback((p) => { setPath(p); setSearch(""); setSearchFocus(false); }, []);
  const goUp = useCallback(() => {
    const parts = path.split("/").filter(Boolean);
    parts.pop();
    setPath(parts.length ? "/" + parts.join("/") : "/");
  }, [path]);

  const entry = FS[path] || {};
  const isRoot = path === "/";
  const isDir = entry.type === "dir";
  const isFile = entry.type === "file";

  const breadcrumbs = useMemo(() => {
    const parts = path.split("/").filter(Boolean);
    const crumbs = [{ label: "ECHO", path: "/" }];
    let cur = "";
    for (const p of parts) {
      cur += "/" + p;
      const e = FS[cur];
      crumbs.push({ label: e?.label || p, path: cur });
    }
    return crumbs;
  }, [path]);

  const STATS = [
    ["Algorithms","235+"], ["Formulas","519"], ["NIST Constants","445"],
    ["VGM Axioms","13"], ["LRM Theorems","60+"], ["Gen. Algorithms","67"],
  ];

  return (
    <div style={{ background:T.bg, color:T.text, minHeight:"100vh", fontFamily:"'Inter',system-ui,sans-serif", display:"flex", flexDirection:"column" }}>
      {/* Header */}
      <div style={{ background:T.bg2, borderBottom:`0.5px solid ${T.border}`, padding:"10px 12px", flexShrink:0 }}>
        <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:8 }}>
          <span style={{ fontFamily:"serif", fontSize:"1.4rem", color:T.gold }}>ר</span>
          <span style={{ fontSize:13, fontWeight:500, color:T.text }}>ECHO — Governor Indexing Algorithm</span>
        </div>
        {/* Stats bar */}
        <div style={{ display:"flex", gap:0, flexWrap:"wrap", marginBottom:8 }}>
          {STATS.map(([label,val],i) => (
            <div key={i} style={{ padding:"3px 10px", borderRight:`0.5px solid ${T.border}`, fontSize:10.5 }}>
              <span style={{ color:T.text, fontWeight:500 }}>{val}</span>
              <span style={{ color:T.textDim, marginLeft:4 }}>{label}</span>
            </div>
          ))}
        </div>
        {/* Search */}
        <div style={{ position:"relative" }}>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            onFocus={() => setSearchFocus(true)}
            onBlur={() => setTimeout(() => setSearchFocus(false), 150)}
            placeholder="Search all matrices..."
            style={{ width:"100%", background:T.bg3, border:`0.5px solid ${T.borderStr}`, borderRadius:6, padding:"6px 10px", color:T.text, fontSize:12.5, outline:"none", fontFamily:"inherit", boxSizing:"border-box" }}
          />
          {searchFocus && results.length > 0 && (
            <div style={{ position:"absolute", top:"100%", left:0, right:0, background:T.bg2, border:`0.5px solid ${T.border}`, borderRadius:"0 0 6px 6px", zIndex:100, maxHeight:260, overflowY:"auto" }}>
              {results.map((r,i) => (
                <div key={i} onClick={() => navigate(r.path)}
                  style={{ padding:"6px 10px", borderBottom:`0.5px solid ${T.border}`, cursor:"pointer", display:"flex", gap:8, alignItems:"center" }}
                  onMouseEnter={e => e.currentTarget.style.background=T.bg3}
                  onMouseLeave={e => e.currentTarget.style.background="transparent"}>
                  <span style={{ fontFamily:"monospace", fontSize:10, color:typeColor(r.type), flexShrink:0 }}>{r.label}</span>
                  <span style={{ fontSize:11.5, color:T.text, flex:1, minWidth:0, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{r.sub}</span>
                  <Chip label={r.type} color={typeColor(r.type)}/>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Breadcrumb */}
      <div style={{ background:T.bg2, borderBottom:`0.5px solid ${T.border}`, padding:"6px 12px", display:"flex", alignItems:"center", gap:4, flexWrap:"wrap", flexShrink:0 }}>
        {!isRoot && (
          <button onClick={goUp} style={{ background:"none", border:"none", color:T.textDim, cursor:"pointer", padding:"0 4px", fontSize:14 }}>←</button>
        )}
        {breadcrumbs.map((c,i) => (
          <span key={i} style={{ display:"flex", alignItems:"center", gap:4 }}>
            {i > 0 && <span style={{ color:T.textMut }}>/</span>}
            <span onClick={() => navigate(c.path)}
              style={{ fontSize:12, color:i===breadcrumbs.length-1?T.text:T.blue, cursor:"pointer" }}>
              {c.label}
            </span>
          </span>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex:1, overflow:"auto" }}>
        {isDir && <FolderView path={path} onNavigate={navigate}/>}
        {isFile && entry.view && VIEWS[entry.view] && VIEWS[entry.view]()}
        {isFile && entry.view && !VIEWS[entry.view] && (
          <div style={{ padding:20, color:T.textDim, fontSize:12 }}>View "{entry.view}" not yet implemented.</div>
        )}
      </div>
    </div>
  );
}
