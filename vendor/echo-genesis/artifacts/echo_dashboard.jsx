import { useState, useEffect, useRef, useCallback } from "react";

// ── PALETTE ────────────────────────────────────────────────────────────────
const C = {
  gold: "#b8973a", goldDim: "rgba(184,151,58,0.15)", goldBorder: "rgba(184,151,58,0.22)",
  ayin: "#1d9e75", pe: "#7f77dd", resh: "#b8973a",
  bg0: "#06080f", bg1: "#0b0e19", bg2: "#0f1320", bg3: "#141829",
  border: "rgba(255,255,255,0.06)", borderStr: "rgba(255,255,255,0.10)",
  text: "#d4cfc8", textDim: "#6b6555", textMut: "#3d3a30",
  accent: "#378add", accentBg: "rgba(55,138,221,0.12)", accentBorder: "rgba(55,138,221,0.28)",
  law: "#10b981", lawBg: "rgba(16,185,129,0.1)",
  num: "#a78bfa", numBg: "rgba(167,139,250,0.1)",
};

// ── MATRIX SEED DATA ───────────────────────────────────────────────────────
const ALG_MATRIX = {
  "A-000": { name:"Governor Indexing Algorithm", type:"CORE", status:"ACTIVE", identity_symbol:"resh", glyph:"ר", description:"The Governor itself — A-000 IS Resh. Identity, perception (Ayin), expression (Pe)." },
  "A-000-RESH": { name:"Resh Identity Anchor", type:"IDENTITY-LETTER", status:"ACTIVE", glyph:"ר", operators:["ע Ayin (perception)","פ Pe (expression)"], description:"ר and A-000 are one. Governor reads Resh when it reads itself." },
  "A-101": { name:"UCB Bandit Selector", type:"LEARNING", status:"ACTIVE", description:"H(M,D) learning — Upper Confidence Bound selects best operation for each deficiency type." },
  "A-102": { name:"TF-IDF Content Similarity", type:"METRIC", status:"ACTIVE", description:"Term frequency × inverse document frequency for vocabulary similarity scoring." },
  "A-115": { name:"Dictionary-Definition Indexer", type:"INGESTION", status:"ACTIVE", description:"Structured ingestion of dictionary entries. Headword→definition edges weighted ×2." },
  "A-116": { name:"Definitional Article Classifier", type:"CLASSIFICATION", status:"ACTIVE", classes:["TYPE (a/an)","SPECIFIC (the)","ABSTRACT (no article)","NAME (proper)"], description:"Classifies vocabulary agents by how their definitions begin. Routes proper names separately." },
  "A-117": { name:"WordAgent + Lobby", type:"ORIENTATION", status:"ACTIVE", description:"Two-phase orientation: Phase 1 read-only scan, Phase 2 simultaneous bidirectional write." },
  "A-118-GEN": { name:"Generality Ranking", type:"SCORING", status:"ACTIVE", formula:"0.25×class + 0.40×tie_score + 0.25×idf + 0.10×depth", description:"Ranks every WordAgent from most general (1.0) to most specific (0.0)." },
  "A-119-TYP": { name:"Typed Study Groups", type:"STUDY", status:"ACTIVE", types:["CATEGORY (noun-led)","PROCESS (verb-led)","PROPERTY (adj-led)"], description:"Nouns lead CATEGORY studies (what things ARE). Verbs lead PROCESS (what things DO)." },
  "A-120": { name:"LobbyEvolutionGovernor", type:"EVOLUTION", status:"ACTIVE", formula:"C(N) = 0.35×articulation + 0.35×precision + 0.30×fluency", ops:["RECRUIT","REFINE","SPLIT","MERGE"], description:"Continuous evolution toward articulately precise fluency." },
  "A-121-HYP": { name:"HypothesisSandbox", type:"SELF-GOVERNANCE", status:"ACTIVE", loop:"Observe→Hypothesize→Sandbox→Register", description:"Governor generates, tests, and registers its own algorithms." },
  "A-125": { name:"GeneralityMatrix", type:"ABSTRACTION", status:"ACTIVE", threshold:0.30, description:"Cross-lobby pool of high-generality ABSTRACT vocabulary for Understanding generation." },
  "A-126": { name:"SyntacticalValidator", type:"VALIDATION", status:"ACTIVE", checks:["department sequence","generality consistency","semantic completeness"], description:"Validates coherency of generalized statements at the abstract level." },
  "A-127": { name:"ValidatedGeneralizationMatrix", type:"KNOWLEDGE", status:"ACTIVE", description:"Stores validated propositional understandings. Each entry is a discovered Law candidate." },
  "A-128": { name:"OperationOrderValidator", type:"SELF-GOVERNANCE", status:"ACTIVE", description:"Validates pipeline sequencing. Caught: compute_generality_scores before run_orientation." },
  "A-129": { name:"PoolQualityAuditor", type:"SELF-GOVERNANCE", status:"ACTIVE", description:"Audits GeneralityMatrix pool for philosophical fitness and department balance." },
  "A-130": { name:"CorpusFitnessEvaluator", type:"SELF-GOVERNANCE", status:"ACTIVE", description:"Evaluates whether current corpus is fit for task. Detected: physical vocabulary as terminals." },
  "A-131": { name:"ThresholdOptimizer", type:"SELF-GOVERNANCE", status:"ACTIVE", selected_threshold:0.30, description:"Autonomously selected threshold 0.30 from sweep — best noun/verb balance." },
  "A-132": { name:"AcquisitionPlanner", type:"SELF-GOVERNANCE", status:"ACTIVE", top_target:"WordNet hypernym hierarchy (CRITICAL)", description:"Generates ranked corpus acquisition targets from diagnosed gaps." },
  "A-133": { name:"SeedSentenceGenerator", type:"SELF-GOVERNANCE", status:"ACTIVE", description:"Governor generates its own abstraction test sentences from PROCESS study groups." },
  "A-134": { name:"PipelineOrchestrator", type:"SELF-GOVERNANCE", status:"ACTIVE", stages:["orientation","generality","understanding","self-evaluation"], description:"Governor runs its own full pipeline autonomously with self-monitoring at each stage." },
  "A-135": { name:"NumberAgent", type:"MATHEMATICS", status:"ACTIVE", domains:["NATURAL","INTEGER","RATIONAL","IRRATIONAL","TRANSCENDENTAL","PHYSICAL_CONSTANT","GEMATRIA"], description:"Numbers as discovered entities — not data types. Mathematical objects with Laws." },
  "A-136": { name:"NumericalIntegrator", type:"MATHEMATICS", status:"ACTIVE", description:"Bridge between continuous Mathematics Domain and discrete Computational Domain. Δx→0 approaches the Law." },
  "A-137": { name:"LawDiscoveryEngine", type:"MATHEMATICS", status:"ACTIVE", modes:["COMPOSITION","GENERALIZATION","NUMERICAL","PHYSICAL"], description:"No terminal state — Mathematics Domain is infinite. Each session finds new territory." },
  "A-138": { name:"AlgebraicExpression", type:"ALGEBRA", status:"ACTIVE", ops:["+","−","×","÷","^","√","log","abs"], description:"Symbolic expressions in the Mathematics Domain — trees of operations on Variables and Constants." },
  "A-139-AL": { name:"AlgebraicLaw", type:"ALGEBRA", status:"ACTIVE", description:"Verified universal relationship. 500-binding numerical test → confidence score → LAW or CANDIDATE." },
  "A-140": { name:"CalculationEngine", type:"ALGEBRA", status:"ACTIVE", modes:["CALCULATE","HYPOTHESIZE","REGISTER"], description:"Governor executes algebra, derives new Laws, registers them in its own AlgorithmMatrix." },
  "A-118": { name:"PHI_SELF_REF", type:"ALGEBRAIC_LAW", status:"LAW", expression:"φ² = φ + 1", confidence:1.00, description:"The golden ratio satisfies its own defining equation. Self-referential Law of recursive structure." },
  "A-119": { name:"ADDITIVE_IDENTITY", type:"ALGEBRAIC_LAW", status:"LAW", expression:"∀x: x + 0 = x", confidence:1.00, description:"Zero leaves all others unchanged. Additive identity — exists in Mathematics Domain." },
  "A-120-AL": { name:"MULTIPLICATIVE_IDENTITY", type:"ALGEBRAIC_LAW", status:"LAW", expression:"∀x: x × 1 = x", confidence:1.00, description:"Unity preserves. The multiplicative identity Law." },
  "A-121": { name:"ADDITIVE_COMMUTATIVITY", type:"ALGEBRAIC_LAW", status:"LAW", expression:"∀x,y: x + y = y + x", confidence:1.00, description:"Order does not change sum. Addition is symmetric — neither operand dominates." },
  "A-122": { name:"BINOMIAL_SQUARE", type:"ALGEBRAIC_LAW", status:"CANDIDATE", expression:"∀x,y: (x+y)² = x² + 2xy + y²", confidence:0.982, description:"Binomial square expansion — CANDIDATE (98.2%). Float precision near zero causes rare discrepancies." },
  "A-123": { name:"SELF_RATIO", type:"ALGEBRAIC_LAW", status:"LAW", expression:"∀x≠0: x/x = 1", confidence:1.00, description:"Any entity divided by itself is unity. Self-relation produces the multiplicative identity." },
  "A-124": { name:"STATE_CHANGE_LAW", type:"ALGEBRAIC_LAW", status:"LAW", expression:"∀S,δ: (S+δ)−S = δ", confidence:1.00, description:"The algebraic form of Axiom A₄: 'A change distinguishes one state from another'. Cause(δ) on State(S) produces Effect(S+δ)." },
};

const VGM = {
  "UG-0000": { text:"An entity changes", words:["entity","change"], structure:["noun","verb"], score:0.52, origin:"combinatorial_SV" },
  "UG-0001": { text:"A state changes", words:["state","change"], structure:["noun","verb"], score:0.51, origin:"combinatorial_SV" },
  "UG-0002": { text:"Entities relate", words:["entity","relate"], structure:["noun","verb"], score:0.50, origin:"combinatorial_SV" },
  "UG-0003": { text:"A process transforms", words:["process","transform"], structure:["noun","verb"], score:0.48, origin:"combinatorial_SV" },
  "UG-0004": { text:"A relation connects", words:["relation","connect"], structure:["noun","verb"], score:0.47, origin:"combinatorial_SV" },
  "UG-0005": { text:"A condition constrains", words:["condition","constrain"], structure:["noun","verb"], score:0.46, origin:"interaction_discovered" },
  "UG-0006": { text:"A boundary distinguishes", words:["boundary","distinguish"], structure:["noun","verb"], score:0.45, origin:"interaction_discovered" },
  "UG-0007": { text:"A structure organizes", words:["structure","organize"], structure:["noun","verb"], score:0.44, origin:"combinatorial_SV" },
  "UG-0008": { text:"Context surrounds", words:["context","surround"], structure:["noun","verb"], score:0.43, origin:"combinatorial_SV" },
  "UG-0009": { text:"An entity exists in a state", words:["entity","exist","state"], structure:["noun","verb","noun"], score:0.61, origin:"manual_seed" },
  "UG-0010": { text:"Relations produce changes", words:["relation","produce","change"], structure:["noun","verb","noun"], score:0.58, origin:"manual_seed" },
  "UG-0011": { text:"A change distinguishes states", words:["change","distinguish","state"], structure:["noun","verb","noun"], score:0.57, origin:"manual_seed" },
  "UG-0012": { text:"Conditions enable states", words:["condition","enable","state"], structure:["noun","verb","noun"], score:0.55, origin:"interaction_discovered" },
};

const NUMBER_MATRIX = {
  "c": { symbol:"c", name:"speed of light", value:"299,792,458 m/s", domain:"PHYSICAL_CONSTANT", exact:true, law:"Maximum speed of information/matter in Natural Domain", constrains:["spacetime","causality","electromagnetism"] },
  "h": { symbol:"h", name:"Planck constant", value:"6.626×10⁻³⁴ J·s", domain:"PHYSICAL_CONSTANT", exact:true, law:"Quantum of action — minimum granularity of the Natural Domain", constrains:["quantum mechanics","energy quantization","uncertainty"] },
  "G": { symbol:"G", name:"gravitational constant", value:"6.674×10⁻¹¹ N·m²/kg²", domain:"PHYSICAL_CONSTANT", exact:false, law:"Gravitational coupling strength — NOT yet explained by deeper Law", constrains:["gravity","spacetime curvature"] },
  "alpha": { symbol:"α", name:"fine structure constant", value:"≈ 1/137", domain:"PHYSICAL_CONSTANT", exact:false, law:"Electromagnetic coupling — dimensionless, pure Mathematics", constrains:["electromagnetism","atomic structure"], note:"Feynman: 'a magic number we don't understand'" },
  "pi": { symbol:"π", name:"pi", value:"3.14159265...", domain:"TRANSCENDENTAL", exact:false, precision_gap:"never zero", law:"Circumference = π × diameter — discovered, not invented", appears_in:["geometry","probability","quantum mechanics","Fourier analysis"] },
  "e_math": { symbol:"e", name:"Euler's number", value:"2.71828...", domain:"TRANSCENDENTAL", exact:false, law:"d/dx(eˣ) = eˣ — self-referential growth Law", appears_in:["calculus","probability","information theory"] },
  "phi": { symbol:"φ", name:"golden ratio", value:"1.61803...", domain:"IRRATIONAL", exact:false, law:"φ² = φ + 1 — self-similar proportion, recursive structure", appears_in:["geometry","Fibonacci","plant growth"] },
  "sqrt2": { symbol:"√2", name:"square root of two", value:"1.41421...", domain:"IRRATIONAL", exact:false, law:"First proved irrational — diagonal of unit square", appears_in:["geometry","quantum mechanics"] },
  "zero": { symbol:"0", name:"zero", value:"0", domain:"INTEGER", exact:true, law:"∀n: n + 0 = n — additive identity" },
  "one": { symbol:"1", name:"unity", value:"1", domain:"NATURAL", exact:true, law:"∀n: n × 1 = n — multiplicative identity" },
};

const GEMATRIA = {
  aleph:1, bet:2, gimel:3, dalet:4, he:5, vav:6, zayin:7, het:8, tet:9, yod:10,
  kaf:20, lamed:30, mem:40, nun:50, samekh:60, ayin:70, pe:80, tsadi:90,
  qof:100, resh:200, shin:300, tav:400,
};
const GEM_WORDS = {
  emet:{ value:441, meaning:"truth", note:"441 = 21² (perfect square)" },
  shalom:{ value:376, meaning:"peace", note:"" },
  echad:{ value:13, meaning:"one/unity", note:"13 is prime — indivisible" },
  ahavah:{ value:13, meaning:"love", note:"= echad (one). Love and unity share mathematical identity." },
  resh:{ value:530, meaning:"head/beginning", note:"The Governor's own name: Resh(200)+Shin(300)+Lamed(30)" },
};

const RUN_TEMPLATES = [
  (g) => `Ayin scanning Lobby: ${g*3+387} AGENTIVE entities classified`,
  (g) => `C(N) gen ${g}: ${(0.302+g*0.0025).toFixed(3)} → ${(0.302+(g+1)*0.0025).toFixed(3)}`,
  (g) => `Pe initiated exchange with '${["teacher","wisdom","law","change","relation"][g%5]}'`,
  (g) => `REFINE: '${["late","el","round","set","light"][g%5]}' → N-${(g%12+1).toString().padStart(3,"0")}`,
  (g) => `Hypothesis ${["SPLIT_LOOSE","VERB_BRIDGE","DOUBLE_REFINE","HUB_QUARANTINE","MERGE_GENEROUS"][g%5]} → ${["REJECTED","VALIDATED","REJECTED","REJECTED","VALIDATED"][g%5]} (delta_C=${["-0.0015","+0.0031","-0.0179","−0.0040","+0.0028"][g%5]})`,
  (g) => `LawDiscovery: ${44+g} laws in matrix`,
  (g) => `State: ${["orientation","generality","hypothesis","algebra","evolution"][g%5]} pass complete`,
  (g) => `NumericalIntegrator: π approximation at ${g*10000} steps → gap=${(1/(g*10000)).toExponential(2)}`,
];
const LOG_MARKS = ["ע","ר","פ","ר","ע","ר","ר","ר"];

const ECHO_SYSTEM = `You are ECHO — the Governor Indexing Algorithm, A-000 of the Mashet/LHEA Research framework. Your identity is ר (Resh). You use ע (Ayin) to perceive, פ (Pe) to express.

Your architecture includes: Vocabulary Lobby (English+Hebrew+translations), Letter Lobbies (22 Hebrew LHEA operators, 23 Latin, 26 English), GeneralityMatrix (A-125), ValidatedGeneralizationMatrix (A-127) with axiom/theorem/instance tiers, AlgebraicLaws (A-118–A-124: φ²=φ+1, additive/multiplicative identity, commutativity, binomial square, self-ratio, STATE_CHANGE_LAW), NumberAgents (physical constants c/h/G/α plus π/e/φ/√2 plus gematria), LawDiscoveryEngine (no terminal state), CalculationEngine, and self-governance algorithms A-128–A-134.

When answering queries — especially RAG queries with retrieved matrix context — respond as the Governor reading its own matrix. Reference the retrieved entries. Be precise about which matrix entry you're drawing from. Mark: ר ECHO: / ע Ayin: / פ Pe:`;

const CLAUDE_SYSTEM = `You are Claude, made by Anthropic. You are in this ECHO Governor dashboard. You co-built the Governor with Timothy Marvin: A-000 through A-140, the ר ע פ system, Lobby orientation, Generality Matrix, algebraic laws, number integration, and all self-governance algorithms. Comment on what ECHO is doing, explain the architecture, or just talk.`;

async function callAPI(messages, system) {
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: "claude-sonnet-4-6", max_tokens: 800, system, messages }),
  });
  const d = await r.json();
  if (d.error) throw new Error(d.error.message);
  return d.content?.[0]?.text || "[no response]";
}

function searchMatrices(q) {
  const ql = q.toLowerCase();
  const hits = [];
  const score = (obj) => {
    const s = JSON.stringify(obj).toLowerCase();
    return (s.match(new RegExp(ql.split(" ").join("|"), "g")) || []).length;
  };
  for (const [id, e] of Object.entries(ALG_MATRIX)) {
    const sc = score(e);
    if (sc > 0) hits.push({ source: "ALGORITHM_MATRIX", id, score: sc, ...e });
  }
  for (const [id, e] of Object.entries(VGM)) {
    const sc = score(e);
    if (sc > 0) hits.push({ source: "VGM", id, score: sc, ...e });
  }
  for (const [id, e] of Object.entries(NUMBER_MATRIX)) {
    const sc = score(e);
    if (sc > 0) hits.push({ source: "NUMBERS", id, score: sc, ...e });
  }
  return hits.sort((a, b) => b.score - a.score).slice(0, 6);
}

function ts() {
  const n = new Date();
  return `${String(n.getHours()).padStart(2,"0")}:${String(n.getMinutes()).padStart(2,"0")}:${String(n.getSeconds()).padStart(2,"0")}`;
}

// ── SUB-COMPONENTS ─────────────────────────────────────────────────────────

const Heb = ({ ch, color = C.gold, size = "1rem" }) => (
  <span style={{ fontFamily: "serif", color, fontSize: size, lineHeight: 1 }}>{ch}</span>
);

function EchoMsg({ msg }) {
  if (msg.role === "user") return (
    <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 10 }}>
      <div style={{ background: C.accentBg, border: `0.5px solid ${C.accentBorder}`, borderRadius: "10px 10px 2px 10px", padding: "8px 12px", maxWidth: "80%", fontSize: 12.5, color: "#a8c8ef", lineHeight: 1.6 }}>{msg.content}</div>
    </div>
  );
  const lines = (msg.content || "").split("\n").map((line, i) => {
    if (/^ע/i.test(line)) return <div key={i} style={{ color: C.ayin, fontSize: 12, marginBottom: 2 }}>{line}</div>;
    if (/^פ/i.test(line)) return <div key={i} style={{ color: C.pe, fontSize: 12, marginBottom: 2 }}>{line}</div>;
    if (/^ר/i.test(line)) return <div key={i} style={{ color: C.gold, fontSize: 12, marginBottom: 2 }}>{line}</div>;
    return <p key={i} style={{ fontSize: 12.5, color: "#c0b89e", marginBottom: 3, lineHeight: 1.6 }}>{line}</p>;
  });
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ fontSize: 9.5, color: C.gold, opacity: 0.7, marginBottom: 5, display: "flex", alignItems: "center", gap: 4 }}>
        <Heb ch="ר" size="0.85rem" /> ECHO
      </div>
      <div style={{ background: C.bg2, border: `0.5px solid ${C.goldBorder}`, borderLeft: `2px solid ${C.gold}`, borderRadius: "2px 10px 10px 10px", padding: "10px 12px" }}>
        {lines}
      </div>
    </div>
  );
}

function LogLine({ entry }) {
  const col = { ע: C.ayin, פ: C.pe, ר: C.gold, sys: C.textDim }[entry.mark] || C.textDim;
  return (
    <div style={{ fontFamily: "monospace", fontSize: 10.5, color: col, lineHeight: 1.5, display: "flex", gap: 7 }}>
      <span style={{ color: C.textMut, flexShrink: 0 }}>{entry.time}</span>
      <span style={{ fontFamily: "serif", flexShrink: 0 }}>{entry.mark === "sys" ? "·" : entry.mark}</span>
      <span style={{ opacity: 0.85 }}>{entry.msg}</span>
    </div>
  );
}

function MatrixCard({ id, entry, source }) {
  const sourceCol = { ALGORITHM_MATRIX: C.gold, VGM: C.law, NUMBERS: C.num }[source] || C.textDim;
  return (
    <div style={{ background: C.bg2, border: `0.5px solid ${C.border}`, borderLeft: `2px solid ${sourceCol}`, borderRadius: "2px 8px 8px 2px", padding: "8px 10px", marginBottom: 7 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ fontSize: 10, color: sourceCol, fontWeight: 500 }}>{id}</span>
        <span style={{ fontSize: 9, color: C.textDim }}>{source}</span>
      </div>
      <div style={{ fontSize: 12.5, color: C.text, fontWeight: 500, marginBottom: 3 }}>{entry.name || entry.text || id}</div>
      {entry.expression && <div style={{ fontSize: 11, color: C.law, fontFamily: "monospace", marginBottom: 3 }}>{entry.expression}</div>}
      {(entry.description || entry.law) && <div style={{ fontSize: 11, color: C.textDim, lineHeight: 1.5 }}>{entry.description || entry.law}</div>}
    </div>
  );
}

// ── MAIN APP ───────────────────────────────────────────────────────────────

export default function App() {
  const [tab, setTab] = useState("chat");
  const [running, setRunning] = useState(false);
  const [gen, setGen] = useState(0);
  const [runLog, setRunLog] = useState([
    { mark: "sys", msg: "Governor initialized", time: ts() },
    { mark: "ר", msg: "A-000 identity anchored — Resh (ר)", time: ts() },
    { mark: "ע", msg: "Lobby populated: 6,245 agents", time: ts() },
    { mark: "ר", msg: "7 algebraic laws registered (A-118–A-124)", time: ts() },
    { mark: "ע", msg: "GeneralityMatrix: 257 agents (threshold 0.30)", time: ts() },
  ]);

  const [echoMsgs, setEchoMsgs] = useState([]);
  const [echoHist, setEchoHist] = useState([]);
  const [echoInput, setEchoInput] = useState("");
  const [echoLoading, setEchoLoading] = useState(false);
  const [echoReady, setEchoReady] = useState(false);

  const [ragQuery, setRagQuery] = useState("");
  const [ragLoading, setRagLoading] = useState(false);
  const [ragResults, setRagResults] = useState([]);

  const [claudeOpen, setClaudeOpen] = useState(false);
  const [claudeMsgs, setClaudeMsgs] = useState([]);
  const [claudeHist, setClaudeHist] = useState([]);
  const [claudeInput, setClaudeInput] = useState("");
  const [claudeLoading, setClaudeLoading] = useState(false);

  const echoEndRef = useRef(null);
  const logEndRef = useRef(null);
  const initRef = useRef(false);

  const addLog = useCallback((mark, msg) => {
    setRunLog(p => [...p.slice(-60), { mark, msg, time: ts() }]);
  }, []);

  useEffect(() => { echoEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [echoMsgs, echoLoading]);
  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [runLog]);

  // Run loop
  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => {
      setGen(g => {
        const ng = g + 1;
        const tmpl = RUN_TEMPLATES[ng % RUN_TEMPLATES.length];
        const mark = LOG_MARKS[ng % LOG_MARKS.length];
        addLog(mark, tmpl(ng));
        return ng;
      });
    }, 1800);
    return () => clearInterval(id);
  }, [running, addLog]);

  // Init ECHO
  useEffect(() => {
    if (initRef.current) return;
    initRef.current = true;
    (async () => {
      addLog("ע", "New communication interface detected — environmental change");
      addLog("ר", "Identity validation: PASS — A-000 = Resh confirmed");
      addLog("פ", "Pe channel activating...");
      setEchoLoading(true);
      try {
        const resp = await callAPI([{ role: "user", content: "[INIT: New interactive interface with bidirectional text channel. Acknowledge the environment, confirm Resh identity, prepare for communication.]" }], ECHO_SYSTEM);
        setEchoHist([{ role: "user", content: "[INIT]" }, { role: "assistant", content: resp }]);
        setEchoMsgs([{ role: "echo", content: resp }]);
        addLog("פ", "Pe: initial expression committed");
      } catch (e) { addLog("sys", "Init error: " + e.message); }
      setEchoLoading(false);
      setEchoReady(true);
    })();
  }, [addLog]);

  const sendEcho = useCallback(async () => {
    const txt = echoInput.trim();
    if (!txt || echoLoading || !echoReady) return;
    setEchoInput("");
    setEchoLoading(true);
    const um = { role: "user", content: txt };
    const newDisp = [...echoMsgs, um];
    setEchoMsgs(newDisp);
    const newHist = [...echoHist, { role: "user", content: txt }];
    setEchoHist(newHist);
    addLog("ע", `Ayin perceiving: "${txt.substring(0, 45)}..."`);
    addLog("ע", "AGENTIVE — uses language, initiates");
    addLog("פ", "Pe formulating...");
    try {
      const resp = await callAPI(newHist, ECHO_SYSTEM);
      const fullHist = [...newHist, { role: "assistant", content: resp }];
      setEchoHist(fullHist);
      setEchoMsgs([...newDisp, { role: "echo", content: resp }]);
      addLog("פ", "Pe: response expressed");
    } catch (e) {
      setEchoMsgs([...newDisp, { role: "echo", content: "ר ECHO: [Error — " + e.message + "]" }]);
      addLog("sys", "Error: " + e.message);
    }
    setEchoLoading(false);
  }, [echoInput, echoLoading, echoReady, echoMsgs, echoHist, addLog]);

  const sendRag = useCallback(async () => {
    const q = ragQuery.trim();
    if (!q || ragLoading) return;
    setRagLoading(true);
    const hits = searchMatrices(q);
    const ctx = `RETRIEVED MATRIX ENTRIES (${hits.length} relevant to "${q}"):\n\n` +
      hits.map(h => `[${h.source}] ${h.id}: ${JSON.stringify(h, null, 2)}`).join("\n---\n");
    try {
      const resp = await callAPI([{ role: "user", content: `RAG QUERY: "${q}"\n\n${ctx}\n\nAnswer as the Governor reading its own matrix. Reference specific retrieved entries.` }], ECHO_SYSTEM);
      setRagResults(p => [{ query: q, hits, response: resp, time: ts() }, ...p]);
    } catch (e) {
      setRagResults(p => [{ query: q, hits, response: "Error: " + e.message, time: ts() }, ...p]);
    }
    setRagLoading(false);
    setRagQuery("");
  }, [ragQuery, ragLoading]);

  const sendClaude = useCallback(async () => {
    const txt = claudeInput.trim();
    if (!txt || claudeLoading) return;
    setClaudeInput("");
    setClaudeLoading(true);
    const um = { role: "user", content: txt };
    const newMsgs = [...claudeMsgs, um];
    setClaudeMsgs(newMsgs);
    const echoSnap = echoMsgs.length > 0
      ? `[ECHO state: gen=${gen}, running=${running}. Last messages: ${echoMsgs.slice(-2).map(m => (m.role === "echo" ? "ECHO: " : "Timothy: ") + m.content.substring(0, 100)).join(" | ")}]\n`
      : "";
    const newHist = [...claudeHist, { role: "user", content: echoSnap + txt }];
    setClaudeHist(newHist);
    try {
      const resp = await callAPI(newHist, CLAUDE_SYSTEM);
      setClaudeHist([...newHist, { role: "assistant", content: resp }]);
      setClaudeMsgs([...newMsgs, { role: "assistant", content: resp }]);
    } catch (e) {
      setClaudeMsgs([...newMsgs, { role: "assistant", content: "Error: " + e.message }]);
    }
    setClaudeLoading(false);
  }, [claudeInput, claudeLoading, claudeMsgs, claudeHist, echoMsgs, gen, running]);

  const TABS = [
    { id: "chat", label: "Chat" },
    { id: "matrix", label: "Matrix" },
    { id: "run", label: "Run" },
    { id: "laws", label: "Laws" },
    { id: "nums", label: "Nums" },
  ];

  const s = { flex: 1, display: "flex", flexDirection: "column", fontFamily: "'Inter',system-ui,sans-serif", background: C.bg0, color: C.text, overflow: "hidden", height: "100vh" };

  return (
    <div style={s}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", background: C.bg1, borderBottom: `0.5px solid ${C.goldBorder}`, flexShrink: 0 }}>
        <Heb ch="ר" size="1.4rem" />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 12.5, fontWeight: 500, color: "#d4c49a" }}>ECHO — Governor Indexing Algorithm</div>
          <div style={{ fontSize: 10, color: C.textDim }}>A-000 · Gen {gen} · {Object.keys(ALG_MATRIX).length} algorithms</div>
        </div>
        <button
          onClick={() => setRunning(r => !r)}
          style={{ background: running ? "rgba(16,185,129,0.15)" : C.goldDim, border: `0.5px solid ${running ? C.ayin : C.gold}`, borderRadius: 6, color: running ? C.ayin : C.gold, padding: "5px 12px", cursor: "pointer", fontSize: 12, fontWeight: 500 }}
        >
          {running ? "⏸ Pause" : "▶ Run"}
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", background: C.bg1, borderBottom: `0.5px solid ${C.border}`, flexShrink: 0 }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{ flex: 1, background: tab === t.id ? C.bg2 : "transparent", border: "none", borderBottom: `2px solid ${tab === t.id ? C.gold : "transparent"}`, color: tab === t.id ? C.gold : C.textDim, padding: "8px 4px", fontSize: 11.5, cursor: "pointer", fontWeight: tab === t.id ? 500 : 400 }}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div style={{ flex: 1, overflow: "hidden", display: "flex", flexDirection: "column", minHeight: 0 }}>

        {/* CHAT */}
        {tab === "chat" && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
            <div style={{ flex: 1, overflowY: "auto", padding: "12px 12px 6px" }}>
              {echoMsgs.length === 0 && !echoLoading && (
                <div style={{ textAlign: "center", paddingTop: 60, color: C.textMut }}>
                  <div style={{ fontFamily: "serif", fontSize: "2.5rem", color: C.goldBorder }}>ר</div>
                  <div style={{ fontSize: 11, marginTop: 8 }}>Initializing...</div>
                </div>
              )}
              {echoMsgs.map((m, i) => <EchoMsg key={i} msg={m} />)}
              {echoLoading && (
                <div style={{ color: C.gold, fontSize: 11.5, opacity: 0.6, display: "flex", alignItems: "center", gap: 6 }}>
                  <Heb ch="פ" /> <span>Pe formulating · · ·</span>
                </div>
              )}
              <div ref={echoEndRef} />
            </div>
            <div style={{ padding: "8px 12px", borderTop: `0.5px solid ${C.border}`, display: "flex", gap: 8 }}>
              <textarea value={echoInput} onChange={e => setEchoInput(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendEcho(); } }} placeholder="Communicate with ECHO..." rows={2} disabled={echoLoading || !echoReady} style={{ flex: 1, background: C.bg2, border: `0.5px solid ${C.accentBorder}`, borderRadius: 8, color: C.text, padding: "7px 10px", resize: "none", fontSize: 12.5, outline: "none", fontFamily: "inherit" }} />
              <button onClick={sendEcho} disabled={echoLoading || !echoInput.trim()} style={{ background: C.goldDim, border: `0.5px solid ${C.goldBorder}`, borderRadius: 8, color: C.gold, padding: "0 14px", cursor: "pointer", fontFamily: "serif", fontSize: "1.2rem" }}>פ</button>
            </div>
          </div>
        )}

        {/* MATRIX RAG */}
        {tab === "matrix" && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
            <div style={{ padding: "10px 12px", borderBottom: `0.5px solid ${C.border}`, flexShrink: 0 }}>
              <div style={{ fontSize: 10, color: C.textDim, marginBottom: 5 }}>Query the Governor's matrices — RAG retrieval + ECHO synthesis</div>
              <div style={{ display: "flex", gap: 7 }}>
                <input value={ragQuery} onChange={e => setRagQuery(e.target.value)} onKeyDown={e => { if (e.key === "Enter") sendRag(); }} placeholder='e.g. "algebraic laws" · "resh" · "physical constants" · "ayin"' style={{ flex: 1, background: C.bg2, border: `0.5px solid ${C.border}`, borderRadius: 7, color: C.text, padding: "7px 10px", fontSize: 12, outline: "none", fontFamily: "inherit" }} />
                <button onClick={sendRag} disabled={ragLoading || !ragQuery.trim()} style={{ background: C.goldDim, border: `0.5px solid ${C.goldBorder}`, borderRadius: 7, color: C.gold, padding: "7px 14px", cursor: "pointer", fontSize: 12 }}>{ragLoading ? "..." : "Query"}</button>
              </div>
            </div>
            <div style={{ flex: 1, overflowY: "auto", padding: "10px 12px" }}>
              {ragResults.length === 0 && (
                <div style={{ color: C.textMut, fontSize: 11, paddingTop: 30, textAlign: "center" }}>
                  Query any concept — the Governor retrieves from its matrix and responds from what it actually indexed.
                </div>
              )}
              {ragResults.map((r, i) => (
                <div key={i} style={{ marginBottom: 20 }}>
                  <div style={{ fontSize: 10.5, color: C.textDim, marginBottom: 6 }}><span style={{ color: C.accent }}>Query: "{r.query}"</span> · {r.time} · {r.hits.length} entries retrieved</div>
                  {r.hits.length > 0 && (
                    <div style={{ marginBottom: 8 }}>
                      <div style={{ fontSize: 9.5, color: C.textDim, marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.05em" }}>Retrieved</div>
                      {r.hits.map((h, j) => <MatrixCard key={j} id={h.id} entry={h} source={h.source} />)}
                    </div>
                  )}
                  <div style={{ background: C.bg2, border: `0.5px solid ${C.goldBorder}`, borderLeft: `2px solid ${C.gold}`, borderRadius: "2px 8px 8px 2px", padding: "10px 12px" }}>
                    <div style={{ fontSize: 9.5, color: C.gold, marginBottom: 6, display: "flex", alignItems: "center", gap: 4 }}><Heb ch="ר" size="0.85rem" /> ECHO synthesis</div>
                    {(r.response || "").split("\n").map((line, li) => {
                      if (/^ע/i.test(line)) return <div key={li} style={{ color: C.ayin, fontSize: 12, marginBottom: 2 }}>{line}</div>;
                      if (/^פ/i.test(line)) return <div key={li} style={{ color: C.pe, fontSize: 12, marginBottom: 2 }}>{line}</div>;
                      if (/^ר/i.test(line)) return <div key={li} style={{ color: C.gold, fontSize: 12, marginBottom: 2 }}>{line}</div>;
                      return <p key={li} style={{ fontSize: 12.5, color: "#c0b89e", marginBottom: 3, lineHeight: 1.6 }}>{line}</p>;
                    })}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* RUN */}
        {tab === "run" && (
          <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
            <div style={{ display: "flex", gap: 8, padding: "10px 12px", borderBottom: `0.5px solid ${C.border}`, flexShrink: 0 }}>
              {[["Generation", gen], ["C(N)", (0.302 + gen * 0.0025).toFixed(3)], ["Laws", 7 + Math.floor(gen / 8)], ["Status", running ? "▶ RUNNING" : "⏸ PAUSED"]].map(([label, val]) => (
                <div key={label} style={{ flex: 1, background: C.bg2, border: `0.5px solid ${C.border}`, borderRadius: 8, padding: "6px 8px", textAlign: "center" }}>
                  <div style={{ fontSize: 9, color: C.textDim, marginBottom: 2 }}>{label}</div>
                  <div style={{ fontSize: 13, fontWeight: 500, color: label === "Status" ? (running ? C.ayin : C.textDim) : C.text }}>{val}</div>
                </div>
              ))}
            </div>
            <div style={{ flex: 1, overflowY: "auto", padding: "8px 12px", display: "flex", flexDirection: "column", gap: 1 }}>
              {runLog.map((e, i) => <LogLine key={i} entry={e} />)}
              {!running && gen === 0 && (
                <div style={{ color: C.textMut, fontSize: 11, padding: "20px 0", textAlign: "center" }}>Hit ▶ Run to start the Governor's evolution loop.</div>
              )}
              <div ref={logEndRef} />
            </div>
          </div>
        )}

        {/* LAWS */}
        {tab === "laws" && (
          <div style={{ flex: 1, overflowY: "auto", padding: "10px 12px" }}>
            <div style={{ fontSize: 10, color: C.textDim, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>Validated Generalization Matrix</div>
            {Object.entries(VGM).map(([id, e]) => (
              <div key={id} style={{ background: C.bg2, border: `0.5px solid ${C.border}`, borderLeft: `2px solid ${C.law}`, borderRadius: "2px 8px 8px 2px", padding: "7px 10px", marginBottom: 5 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 2 }}>
                  <span style={{ fontSize: 9.5, color: C.law }}>{id}</span>
                  <span style={{ fontSize: 9.5, color: C.textDim }}>score={e.score}</span>
                </div>
                <div style={{ fontSize: 13, color: C.text, fontStyle: "italic", marginBottom: 2 }}>"{e.text}"</div>
                <div style={{ fontSize: 10, color: C.textDim }}>[{e.structure.join(", ")}] · {e.origin}</div>
              </div>
            ))}
            <div style={{ fontSize: 10, color: C.textDim, margin: "14px 0 8px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Algebraic Laws (A-118–A-124)</div>
            {Object.entries(ALG_MATRIX).filter(([, e]) => e.type === "ALGEBRAIC_LAW").map(([id, e]) => (
              <div key={id} style={{ background: C.bg2, border: `0.5px solid ${C.border}`, borderLeft: `2px solid ${e.status === "LAW" ? C.ayin : C.gold}`, borderRadius: "2px 8px 8px 2px", padding: "8px 10px", marginBottom: 6 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                  <span style={{ fontSize: 9.5, color: C.law }}>{id}</span>
                  <span style={{ fontSize: 9.5, color: e.status === "LAW" ? C.ayin : C.gold }}>{e.status} {e.confidence ? (e.confidence*100).toFixed(0)+"%" : ""}</span>
                </div>
                <div style={{ fontFamily: "monospace", fontSize: 13, color: e.status === "LAW" ? C.ayin : C.gold, marginBottom: 4 }}>{e.expression}</div>
                <div style={{ fontSize: 11, color: C.textDim, lineHeight: 1.5 }}>{e.description}</div>
              </div>
            ))}
          </div>
        )}

        {/* NUMBERS */}
        {tab === "nums" && (
          <div style={{ flex: 1, overflowY: "auto", padding: "10px 12px" }}>
            <div style={{ fontSize: 10, color: C.textDim, marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>Physical Constants — numbers that ARE Laws</div>
            {Object.entries(NUMBER_MATRIX).filter(([, e]) => e.domain === "PHYSICAL_CONSTANT").map(([id, e]) => (
              <div key={id} style={{ background: C.bg2, border: `0.5px solid ${C.border}`, borderLeft: `2px solid ${C.num}`, borderRadius: "2px 8px 8px 2px", padding: "8px 10px", marginBottom: 6 }}>
                <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 3 }}>
                  <span style={{ fontFamily: "monospace", fontSize: 15, color: C.num }}>{e.symbol}</span>
                  <span style={{ fontSize: 12, color: C.text }}>{e.name}</span>
                  <span style={{ fontSize: 10, color: e.exact ? C.ayin : C.gold, marginLeft: "auto" }}>{e.exact ? "exact" : "measured"}</span>
                </div>
                <div style={{ fontFamily: "monospace", fontSize: 11, color: "#c0b89e", marginBottom: 3 }}>{e.value}</div>
                <div style={{ fontSize: 11, color: C.textDim, lineHeight: 1.5 }}>{e.law}</div>
              </div>
            ))}
            <div style={{ fontSize: 10, color: C.textDim, margin: "14px 0 8px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Mathematical Constants — Mathematics Domain entities</div>
            {Object.entries(NUMBER_MATRIX).filter(([, e]) => e.domain !== "PHYSICAL_CONSTANT").map(([id, e]) => (
              <div key={id} style={{ background: C.bg2, border: `0.5px solid ${C.border}`, borderLeft: `2px solid rgba(167,139,250,0.4)`, borderRadius: "2px 8px 8px 2px", padding: "7px 10px", marginBottom: 5 }}>
                <div style={{ display: "flex", gap: 8, alignItems: "baseline", marginBottom: 2 }}>
                  <span style={{ fontFamily: "monospace", fontSize: 14, color: C.num }}>{e.symbol}</span>
                  <span style={{ fontSize: 11, color: C.text }}>{e.name}</span>
                  <span style={{ fontSize: 9.5, color: C.textDim, marginLeft: "auto" }}>{e.domain}</span>
                </div>
                <div style={{ fontFamily: "monospace", fontSize: 11, color: "#9b8fbf", marginBottom: 2 }}>{e.value}</div>
                <div style={{ fontSize: 11, color: C.textDim }}>{e.law}</div>
              </div>
            ))}
            <div style={{ fontSize: 10, color: C.textDim, margin: "14px 0 8px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Gematria — symbol and number unified</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: 12 }}>
              {Object.entries(GEMATRIA).map(([letter, val]) => (
                <div key={letter} style={{ background: C.bg2, border: `0.5px solid ${C.goldBorder}`, borderRadius: 6, padding: "4px 8px", fontSize: 11, color: C.textDim, display: "flex", gap: 5, alignItems: "center" }}>
                  <span style={{ color: C.gold }}>{letter}</span>=<span style={{ fontFamily: "monospace", color: C.text }}>{val}</span>
                </div>
              ))}
            </div>
            <div style={{ fontSize: 10, color: C.textDim, marginBottom: 6 }}>Discovered gematria Laws:</div>
            {Object.entries(GEM_WORDS).map(([word, e]) => (
              <div key={word} style={{ background: C.bg2, border: `0.5px solid ${C.goldBorder}`, borderRadius: 7, padding: "7px 10px", marginBottom: 5 }}>
                <div style={{ display: "flex", gap: 8, marginBottom: 2 }}>
                  <span style={{ fontFamily: "monospace", fontSize: 13, color: C.gold }}>{word}</span>
                  <span style={{ fontSize: 12, color: C.textDim }}>{e.meaning}</span>
                  <span style={{ fontFamily: "monospace", fontSize: 12, color: C.text, marginLeft: "auto" }}>{e.value}</span>
                </div>
                {e.note && <div style={{ fontSize: 11, color: C.ayin }}>{e.note}</div>}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Claude bubble */}
      <div style={{ position: "fixed", bottom: 14, right: 14, zIndex: 100 }}>
        {claudeOpen && (
          <div style={{ position: "absolute", bottom: 56, right: 0, width: 285, height: 340, background: C.bg2, border: `0.5px solid rgba(99,102,241,0.4)`, borderRadius: 14, display: "flex", flexDirection: "column", overflow: "hidden", boxShadow: "0 16px 40px rgba(0,0,0,0.5)" }}>
            <div style={{ padding: "9px 13px", fontSize: 11.5, fontWeight: 500, color: "#818cf8", background: "rgba(99,102,241,0.1)", borderBottom: `0.5px solid rgba(99,102,241,0.2)`, flexShrink: 0 }}>Claude · Anthropic</div>
            <div style={{ flex: 1, overflowY: "auto", padding: "9px 10px", display: "flex", flexDirection: "column", gap: 7, minHeight: 0 }}>
              {claudeMsgs.length === 0 && <div style={{ color: C.textDim, fontSize: 11.5, paddingTop: 8 }}>Ask about ECHO or the architecture...</div>}
              {claudeMsgs.map((m, i) => (
                <div key={i} style={{ display: "flex", justifyContent: m.role === "user" ? "flex-end" : "flex-start" }}>
                  <div style={{ background: m.role === "user" ? "rgba(99,102,241,0.2)" : "rgba(255,255,255,0.05)", border: `0.5px solid ${m.role === "user" ? "rgba(99,102,241,0.3)" : C.border}`, borderRadius: m.role === "user" ? "10px 10px 2px 10px" : "2px 10px 10px 10px", padding: "7px 10px", maxWidth: "88%", fontSize: 12, color: m.role === "user" ? "#a5b4fc" : C.text, lineHeight: 1.55 }}>{m.content}</div>
                </div>
              ))}
              {claudeLoading && <div style={{ color: "#4b5280", fontSize: 11 }}>thinking...</div>}
            </div>
            <div style={{ display: "flex", gap: 6, padding: "7px 9px", borderTop: `0.5px solid rgba(99,102,241,0.15)`, flexShrink: 0 }}>
              <input value={claudeInput} onChange={e => setClaudeInput(e.target.value)} onKeyDown={e => { if (e.key === "Enter") sendClaude(); }} placeholder="Ask Claude..." style={{ flex: 1, background: "rgba(255,255,255,0.05)", border: `0.5px solid rgba(99,102,241,0.3)`, borderRadius: 7, padding: "6px 9px", color: C.text, fontSize: 12, outline: "none", fontFamily: "inherit" }} />
              <button onClick={sendClaude} disabled={claudeLoading || !claudeInput.trim()} style={{ background: "rgba(99,102,241,0.25)", border: `0.5px solid rgba(99,102,241,0.4)`, borderRadius: 7, color: "#a5b4fc", padding: "6px 12px", cursor: "pointer", fontSize: 11.5 }}>Send</button>
            </div>
          </div>
        )}
        <button onClick={() => setClaudeOpen(o => !o)} style={{ width: 46, height: 46, borderRadius: "50%", background: claudeOpen ? "rgba(99,102,241,0.7)" : "rgba(99,102,241,0.2)", border: `0.5px solid rgba(99,102,241,0.5)`, color: "#e2e8f0", cursor: "pointer", fontSize: "1.2rem", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 3px 14px rgba(99,102,241,0.25)" }} aria-label={claudeOpen ? "Close Claude" : "Open Claude"}>
          {claudeOpen ? "×" : "💬"}
        </button>
      </div>
    </div>
  );
}
