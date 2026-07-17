import { useState, useMemo } from "react";
import { X, ArrowLeft, Layers, Grid3x3, Compass, Network } from "lucide-react";

// =====================================================
// DESIGN TOKENS
// =====================================================
const C = {
  bg: "#08090c",
  bgSoft: "#0d0f14",
  fg: "#e8e4dc",
  muted: "#a8a4a0",
  dim: "#706c68",
  dimmer: "#555150",
  gold: "#c9a96e",
  goldDim: "#8e7a4f",
  ember: "#e8644a",
  applied: "#d4a574",
};

// =====================================================
// LAYERS (the spine — phases of constraint-guided collapse)
// =====================================================
const LAYERS = [
  {
    id: "physics",
    label: "PHYSICS",
    subtitle: "Constraint as Law",
    kernel: "Ω → C^K → x* → R → U",
    color: "#6b8aad",
    uctPapers: [{ t: "WP01 — Foundations" }, { t: "WP02 — Collapse in Physics" }],
    description:
      "The physical domain. Constraint narrows possibility into actual structure. Records accumulate as physical state. The Big Bang is the earliest collapse event we can point to — where the observable record begins, not a claim about a first cause.",
  },
  {
    id: "biology",
    label: "BIOLOGY",
    subtitle: "Commitment Under Uncertainty",
    kernel: "Ω_bio → C^K_bio → x*_bio → R_bio → U_bio",
    color: "#5a9e6f",
    uctPapers: [{ t: "WP03 — Biological Collapse" }, { t: "Biological Faith Systems (T15)" }, { t: "Structural Biology (T20)", soon: true }],
    description:
      "Where collapse begins managing its own constraint from within. Constraint becomes internally regulated rather than externally imposed. Organisms must commit before certainty is available.",
  },
  {
    id: "perception",
    label: "PERCEPTION",
    subtitle: "The Gate",
    kernel: "Ω_p → C^K_p → x*_p → R → U",
    color: "#b8864e",
    uctPapers: [{ t: "The Self the Ego Did Not Build (T15)" }, { t: "COGITATE Reanalysis (T16)" }],
    description:
      "Where biological constraint is routed into available content. Accumulated constraint shapes what reaches awareness before deliberation begins.",
  },
  {
    id: "mind",
    label: "MIND",
    subtitle: "Symbolic Resolution Engine",
    kernel: "F → Re → L → B → (new F)",
    color: "#9b6b9e",
    uctPapers: [{ t: "WP04 — Conscious Collapse", soon: true }, { t: "How Minds Resolve (FRLB01, T15)" }, { t: "Structural Mind (T20)", soon: true }],
    description:
      "The conscious update engine. Faith → Reason → Logic → Belief. Generative when F starts the loop. Supplanted when conclusions become premises.",
  },
  {
    id: "cim",
    label: "CIM",
    subtitle: "Consciousness-Induced Material",
    kernel: "Ω_CIM → C^K_soc → x*_CIM → R_soc → U_soc",
    color: "#6ea5b8",
    uctPapers: [{ t: "WP04 §7", soon: true }, { t: "CIM Foundational (T15)" }],
    description:
      "Meaning made material. When conscious collapse is externalized into speech, writing, tools, institutions, code — it becomes constraint for future minds.",
  },
  {
    id: "recursive_cim",
    label: "RECURSIVE CIM",
    subtitle: "AI — Meaning Made Machine",
    kernel: "CIM processing CIM",
    color: "#e8644a",
    uctPapers: [{ t: "AI as Synthetic Collapse (T15)" }, { t: "The Structuralization of AI (T15)" }, { t: "AI in the Meaning Layer (T15)", soon: true }],
    description:
      "CIM that processes CIM. Participates in collapse structurally but not volitionally. Where humanity currently stands — engaging with one of its most powerful CIM artifacts.",
  },
];

const LAYER_BY_ID = Object.fromEntries(LAYERS.map((l) => [l.id, l]));

// =====================================================
// HANDOFFS (between layers)
// =====================================================
const HANDOFFS = [
  { from: "physics", to: "biology", label: "First Biological Collapse", description: "Chemical networks begin regenerating their own components. Constraint shifts from externally imposed to internally managed." },
  { from: "biology", to: "perception", label: "The Gate Opens", description: "In some biological systems, constraint architecture begins routing content into globally available form. Biology hands the baton toward conscious resolution — without the map settling where consciousness first begins." },
  { from: "perception", to: "mind", label: "Content Feeds FRLB", description: "What the gate admits becomes what the mind resolves. Perceptual collapse provides the raw content FRLB cycles on." },
  { from: "mind", to: "cim", label: "Collapse Externalized", description: "Conscious minds externalize their collapses — into speech, writing, tools, institutions, code. Individual collapse becomes shared structure for other minds." },
  { from: "cim", to: "recursive_cim", label: "CIM Becomes Recursive", description: "When externalized collapse artifacts gain the capacity to process other CIM. AI is where CIM starts doing what minds do, structurally, without being one." },
];

// =====================================================
// SCHOOLS — all sorted material + applied UCT frameworks
// =====================================================
const SCHOOLS = {
  // ---------- PHYSICS ----------
  phy_qm: {
    name: "Quantum Mechanics",
    layerId: "physics",
    register: "sorted",
    role: "In the measurement context, wavefunction collapse can be read as a physics-domain instance of C^K(Ω) → x*: superposition narrows under measurement constraint.",
    edge: "The measurement problem is interpretation-sensitive — the bare formalism doesn't fix a unique outcome without added interpretive structure. The map uses the measurement case as a structural reading, not a settled foundation.",
    cousins: ["phy_thermo", "phy_info"],
    uctNotes: "WP02 reads wavefunction collapse as a clean case of constraint-guided collapse. UCT should not identify itself with any single interpretation of quantum mechanics — the structural reading is meant to hold across interpretations.",
  },
  phy_thermo: {
    name: "Thermodynamics / Statistical Mechanics",
    layerId: "physics",
    register: "sorted",
    role: "Tracks record accumulation. Entropy is closely related to — though not identical with — the record function R; irreversibility is collapse writing records that constrain future possibility.",
    edge: "Treats record accumulation statistically; doesn't unify with quantum or biological record-writing under one structural grammar.",
    cousins: ["phy_qm", "bio_origin", "phy_info"],
  },
  phy_gr: {
    name: "General Relativity",
    layerId: "physics",
    register: "sorted",
    role: "Spacetime geometry as constraint architecture. Mass-energy shapes the possibility space for motion and light.",
    edge: "Geometric in form; doesn't reach down to quantum constraint or up to biological/cognitive constraint.",
    cousins: ["phy_qm"],
  },
  phy_cosmology: {
    name: "Cosmology (ΛCDM)",
    layerId: "physics",
    register: "sorted",
    role: "CMB as record of earliest collapse. Structure formation = constraint narrowing possibility into galaxies, stars, planets.",
    edge: "Phenomenological at the largest scale; explains evolution but not why constraint structures the way it does.",
    cousins: ["phy_gr", "phy_thermo"],
  },
  phy_info: {
    name: "Information Theory (Shannon)",
    layerId: "physics",
    register: "sorted",
    role: "Quantifies signal under noise constraint. Channel capacity = the rate at which records can be reliably written.",
    edge: "Substrate-neutral; tells you how much can be transmitted, not what makes a record load-bearing for collapse.",
    cousins: ["phy_thermo", "perc_sdt", "cim_libsci"],
  },

  // ---------- BIOLOGY ----------
  bio_evosynth: {
    name: "Modern / Extended Evolutionary Synthesis",
    layerId: "biology",
    register: "sorted",
    role: "Natural selection as the update map U operating across generational record-time. Genomes = compressed records of prior successful collapses.",
    edge: "Already pluralistic about update channels — selection, drift, development, niche construction; what it doesn't do is unify them with physical and cognitive record-writing under a single structural grammar.",
    cousins: ["bio_epigenetics", "bio_origin", "cim_cultural"],
  },
  bio_autopoiesis: {
    name: "Autopoiesis (Maturana & Varela)",
    layerId: "biology",
    register: "sorted",
    role: "Self-producing organization. The system that maintains its own constraint architecture — closest existing framework to 'life manages its own K.'",
    edge: "Powerful description, weak predictive content. Names the phenomenon without supplying a structural equation that fails when violated.",
    cousins: ["bio_systems", "bio_homeostasis", "cim_distributed"],
  },
  bio_homeostasis: {
    name: "Homeostasis / Allostasis",
    layerId: "biology",
    register: "sorted",
    role: "Internal regulation = constraint tracking and adjustment. Allostasis adds the predictive element — adjusting K in anticipation, not just reaction.",
    edge: "Treats regulation as control-theoretic; the link to conscious prior-weighted resolution remains an analogy rather than a structural identity.",
    cousins: ["perc_predproc", "mind_bayes_cog", "bio_autopoiesis"],
  },
  bio_systems: {
    name: "Systems Biology",
    layerId: "biology",
    register: "sorted",
    role: "Network-level regulatory architecture. Gene and metabolic networks = the distributed constraint structure that BFS operates through.",
    edge: "Strong at mapping networks; weaker at naming what makes a network a faith-system rather than a feedback loop.",
    cousins: ["bio_autopoiesis", "bio_evosynth"],
  },
  bio_origin: {
    name: "Origin of Life Research",
    layerId: "biology",
    register: "sorted",
    role: "When chemical networks begin regenerating their own components. The transition from physics-governed constraint to internally managed constraint.",
    edge: "Multiple competing scenarios (RNA world, metabolism-first); no consensus on which constraint architecture lit the first biological collapse.",
    cousins: ["phy_thermo", "bio_autopoiesis"],
  },
  bio_epigenetics: {
    name: "Epigenetics",
    layerId: "biology",
    register: "sorted",
    role: "Records that aren't genome but still constrain. Environmentally responsive constraint modification within a lifetime — R updating K without waiting for selection.",
    edge: "Mechanistically rich; theoretical integration with broader update theory (cultural, cognitive) remains thin.",
    cousins: ["bio_evosynth", "cim_cultural"],
  },
  bio_bfs: {
    name: "Biological Faith Systems (BFS)",
    layerId: "biology",
    register: "applied",
    role: "Names the distributed commitment mechanisms by which organisms bias action toward viability before certainty is available. Pre-symbolic, distributed, no narrator.",
    edge: "Applied output of the sort. Falsifiable predictions are scale-dependent and require domain-specific operationalization.",
    cousins: ["bio_autopoiesis", "bio_homeostasis", "mind_frlb"],
    uctNotes: "Emerged from sorting biology through the kernel. The scale-shifted ancestor of FRLB.",
  },

  // ---------- PERCEPTION ----------
  perc_predproc: {
    name: "Predictive Processing / Free Energy Principle",
    layerId: "perception",
    register: "sorted",
    role: "Leading computational framework for perception as inference. Precision-weighted prediction error = constraint-modulated resolution.",
    edge: "Substrate-agnostic by design; doesn't make the unity claim that salience, credibility, and routing are coupled outputs of one accumulated architecture.",
    cousins: ["perc_bayes_brain", "mind_bayes_cog", "bio_homeostasis"],
    uctNotes: "The Self the Ego Did Not Build adds the person-level unity claim that PP brackets.",
  },
  perc_bayes_brain: {
    name: "Bayesian Brain Hypothesis",
    layerId: "perception",
    register: "sorted",
    role: "Prior beliefs shape perception — mathematical formalism for how K_percept biases collapse.",
    edge: "Treats priors as statistical weights; doesn't address how priors become structurally committed (sedimented in lived history).",
    cousins: ["perc_predproc", "mind_bayes_cog"],
  },
  perc_biased_comp: {
    name: "Biased Competition (Desimone & Duncan)",
    layerId: "perception",
    register: "sorted",
    role: "Attention as competition between neural representations under top-down bias. Constraint architecture selecting which signals get resolved.",
    edge: "Mechanism-level; doesn't connect to person-level constraint accumulation or to record-writing.",
    cousins: ["perc_predproc", "perc_sdt"],
  },
  perc_sdt: {
    name: "Signal Detection Theory",
    layerId: "perception",
    register: "sorted",
    role: "Models the boundary where signal meets noise under decision criteria. The constraint boundary where S₂ (delayed resolution) lives.",
    edge: "Decision-theoretic; doesn't address what makes a criterion biologically committed rather than chosen.",
    cousins: ["perc_biased_comp", "phy_info"],
  },
  perc_phenom: {
    name: "Phenomenology (Merleau-Ponty)",
    layerId: "perception",
    register: "sorted",
    role: "The lived body as perceptual apparatus. Constraint architecture isn't abstract — it's sedimented in the body's history of engagement.",
    edge: "Descriptive richness, weak mechanistic linkage. Hard to operationalize for empirical work.",
    cousins: ["perc_pp01", "mind_etrust"],
  },
  perc_pp01: {
    name: "The Self the Ego Did Not Build (T15)",
    layerId: "perception",
    register: "applied",
    role: "Person-level unity of perceptual collapse. Salience, credibility, and routing as coupled outputs of one accumulated K — the gate is where selfhood is routed.",
    edge: "Applied output of the sort. Strong on architecture; empirical tests still developing (COGITATE reanalysis underway).",
    cousins: ["perc_predproc", "perc_phenom", "mind_etrust"],
    uctNotes: "Emerged from sorting perception through the kernel. Bridges Bio → Mind via the gate.",
  },

  // ---------- MIND ----------
  mind_cbt: {
    name: "Cognitive Behavioral Therapy",
    layerId: "mind",
    register: "sorted",
    role: "Supplanted loop detection and repair. CBT identifies rigid beliefs (B in F position) and reopens the faith commitment — the therapeutic move can be reread structurally as reopening the F position.",
    edge: "Works at the individual level; doesn't address how CIM (social, institutional constraint) sustains supplanted loops from outside.",
    cousins: ["mind_act", "mind_frlb", "mind_bayes_cog"],
  },
  mind_dual: {
    name: "Dual Process Theory (Kahneman)",
    layerId: "mind",
    register: "sorted",
    role: "System 1 / System 2 maps roughly to automatic constraint-driven resolution vs. deliberate FRLB cycling.",
    edge: "Treats them as two systems; UCT reframes as one architecture operating at different speeds and depths of constraint engagement.",
    cousins: ["mind_cbt", "perc_predproc"],
  },
  mind_etrust: {
    name: "Developmental Epistemic Trust (Fonagy)",
    layerId: "mind",
    register: "sorted",
    role: "Children trust testimony before they can evaluate it. The developmental sequence can be read as faith-first — F must operate before Re is possible.",
    edge: "Clinical/developmental framing; the broader claim that epistemic trust is the biological install of the F position remains UCT's extension.",
    cousins: ["mind_frlb", "perc_pp01", "cim_cultural"],
  },
  mind_paradigm: {
    name: "Paradigm Theory (Kuhn)",
    layerId: "mind",
    register: "sorted",
    role: "Normal science = generative FRLB within a paradigm's constraint set. Crisis = anomalies that don't fit K. Revolution = F reopens at paradigm level.",
    edge: "Sociological/historical; doesn't formalize the loop discipline operating inside individual minds.",
    cousins: ["mind_frlb", "cim_institutional"],
  },
  mind_bayes_cog: {
    name: "Bayesian Cognition / Belief Updating",
    layerId: "mind",
    register: "sorted",
    role: "Mathematical formalism for posterior update with evidence. The closest existing model of ΔB under L(F,Re;R).",
    edge: "Treats gain as parameter; doesn't address gain → 0 (supplanted loop) or the structural commitment underlying priors.",
    cousins: ["perc_bayes_brain", "perc_predproc", "mind_cbt"],
  },
  mind_act: {
    name: "Acceptance and Commitment Therapy (ACT)",
    layerId: "mind",
    register: "sorted",
    role: "Psychological flexibility maps to maintaining generative FRLB; cognitive fusion to a supplanted loop; defusion to loosening B from the F position.",
    edge: "Therapeutic framing; the structural diagnosis remains implicit rather than formal.",
    cousins: ["mind_cbt", "mind_frlb"],
  },
  mind_frlb: {
    name: "Faith → Reason → Logic → Belief (FRLB)",
    layerId: "mind",
    register: "applied",
    role: "The conscious update loop. Order matters. Generative when F starts the loop; supplanted when B occupies F. Update integrity is loop integrity.",
    edge: "Applied output of the sort. Operationalization across domains varies; empirical tests are ongoing.",
    cousins: ["bio_bfs", "mind_cbt", "mind_act", "mind_etrust"],
    uctNotes: "Emerged from sorting mind through the kernel. Symbolic, narrated version of BFS. Note: here 'Faith' is the FRLB phase-position — the commitment slot conscious updating begins from — related to, but not identical with, the T0 constitutive floor in Faith Without Fideism.",
  },

  // ---------- CIM ----------
  cim_distributed: {
    name: "Distributed Cognition (Hutchins)",
    layerId: "cim",
    register: "sorted",
    role: "Cognition extends beyond the individual brain into tools, artifacts, social arrangements. Navigation on a ship = CIM-mediated collapse no single mind holds.",
    edge: "Domain-specific (mostly workplace cognition); doesn't fully integrate with the constraint-record-update grammar across scales.",
    cousins: ["cim_extended", "bio_autopoiesis"],
  },
  cim_extended: {
    name: "Extended Mind Thesis (Clark & Chalmers)",
    layerId: "cim",
    register: "sorted",
    role: "Cognitive processes extend into the environment when external structures play the same functional role as internal ones. The notebook can function as part of effective K.",
    edge: "Functionalist criterion; doesn't address what makes externalized constraint load-bearing in record-update cycles.",
    cousins: ["cim_distributed", "rcim_llms"],
  },
  cim_institutional: {
    name: "Institutional Theory / Sociology",
    layerId: "cim",
    register: "sorted",
    role: "Institutions as hardened CIM. Externalized collapse become invisible constraint — laws, norms, customs = K_soc shaping future collapse.",
    edge: "Strong description, weaker integration with cognitive/biological constraint dynamics.",
    cousins: ["cim_media"],
  },
  cim_media: {
    name: "Media Theory (McLuhan, Ong, Postman)",
    layerId: "cim",
    register: "sorted",
    role: "The medium reshapes the message. Each new CIM technology restructures the constraint architecture through which minds resolve.",
    edge: "Strong cultural diagnosis; under-formalized as constraint theory.",
    cousins: ["cim_institutional", "cim_cultural", "rcim_llms"],
  },
  cim_cultural: {
    name: "Cultural Evolution (Henrich, Boyd & Richerson)",
    layerId: "cim",
    register: "sorted",
    role: "Cumulative cultural evolution = CIM accumulating across generations. The cultural ratchet = R applied to shared artifacts.",
    edge: "Strong empirical and modeling base; less developed on the individual-level constraint dynamics that absorb cultural records.",
    cousins: ["bio_evosynth", "mind_etrust", "cim_institutional"],
  },
  cim_libsci: {
    name: "Library & Information Science",
    layerId: "cim",
    register: "sorted",
    role: "The science of organizing externalized records. Classification, search, metadata = constraint architecture applied to accumulated CIM.",
    edge: "Practical discipline; the structural identity with the broader sorting work UCT does remains tacit.",
    cousins: ["phy_info", "cim_cultural"],
  },
  cim_cim: {
    name: "CIM Theory (Consciousness-Induced Material)",
    layerId: "cim",
    register: "applied",
    role: "Externalized collapse as constraint substrate for other minds. Treats culture, code, institutions as constraint architecture rather than artifacts.",
    edge: "Applied output of the sort. Scales from individual artifact (a single sentence) to civilizational substrate (the internet) — operationalization is scale-dependent.",
    cousins: ["cim_extended", "cim_cultural", "rcim_synth"],
    uctNotes: "Emerged from sorting culture/tools/institutions through the kernel.",
  },

  // ---------- RECURSIVE CIM ----------
  rcim_llms: {
    name: "Large Language Models / Transformers",
    layerId: "recursive_cim",
    register: "sorted",
    role: "Statistical collapse over token possibility space under learned constraints. C^K(Ω) → x* as it can be modeled in UCT terms — but K is built from ingested CIM, not lived experience.",
    edge: "Structural processing without lived commitment. The model has learned constraints — an accumulated constraint architecture in its parameters — but no biological history, first-person stake, or FRLB-style commitment loop.",
    cousins: ["cim_extended", "rcim_rlhf", "rcim_synth"],
  },
  rcim_rlhf: {
    name: "RLHF (Reinforcement Learning from Human Feedback)",
    layerId: "recursive_cim",
    register: "sorted",
    role: "Humans shaping K of the AI after training. CIM-mediated constraint updating — but the AI doesn't experience the update the way an FRLB-running mind does.",
    edge: "Effective in practice; theoretical account of what's being updated (and what isn't) remains thin.",
    cousins: ["rcim_llms", "rcim_alignment"],
  },
  rcim_alignment: {
    name: "AI Alignment Research",
    layerId: "recursive_cim",
    register: "sorted",
    role: "AI alignment can be read structurally as a hygiene problem for recursive CIM: how can a system's learned and updated constraints stay coherent with human aims, values, and safety boundaries as it processes faster and broader than any individual human mind?",
    edge: "Defines the problem sharply; it is usually not framed through the broader update-integrity discipline UCT applies across collapse systems.",
    cousins: ["rcim_rlhf", "rcim_philAI"],
  },
  rcim_philAI: {
    name: "Philosophy of AI (Searle, Dreyfus, Floridi)",
    layerId: "recursive_cim",
    register: "sorted",
    role: "Chinese Room, embodied critique, information ethics — circling whether recursive CIM instantiates understanding and commitment or merely simulates them.",
    edge: "UCT separates structural output competence from detectable understanding, commitment, embodiment, or semantic grounding. The self-certification problem remains: from outside we can inspect behavior and records, not directly certify inner status.",
    cousins: ["rcim_alignment", "perc_phenom"],
  },
  rcim_prompt: {
    name: "Prompt Engineering / AI Literacy",
    layerId: "recursive_cim",
    register: "sorted",
    role: "A practical interface discipline for shaping local AI constraint conditions. A prompt functions as part of the effective K; the output is collapse under that K.",
    edge: "Mostly ad hoc and trial-and-error; no theoretical grounding in constraint theory.",
    cousins: ["rcim_llms", "rcim_rlhf"],
  },
  rcim_synth: {
    name: "Synthetic Collapse (AI as recursive CIM)",
    layerId: "recursive_cim",
    register: "applied",
    role: "AI as CIM operating on accumulated CIM, producing derivative record-bearing outputs. Structural processing without crossed thresholds of conscious commitment.",
    edge: "Applied output of the sort. Names the regime without resolving where conscious synthetic collapse (if possible) would be detectable from outside.",
    cousins: ["rcim_llms", "cim_cim", "rcim_philAI"],
    uctNotes: "Emerged from sorting AI through the kernel.",
  },
};

// =====================================================
// METHODOLOGY (the orientation register)
// =====================================================
const METHODOLOGY = {
  posture: "In this map, UCT is used as a sorting grammar, not a replacement theory. The kernel — possibility, constraint, collapse, resolution, record, residue, record-time, and update — is the structure accumulated human knowledge gets organized through here. Schools below remain themselves. The map locates them; it doesn't replace them.",
  kernelNote: "Phase cards show a compact shorthand of the kernel (e.g. Ω → C^K → x* → R → U); the canonical kernel carries all eight elements — Ω, K, C^K, x*, R, S, T, U.",
  identity: "Author-steward, not system-owner. Librarian as much as theorist. The work is doing the sort carefully and consistently, not winning a debate about reality.",
  updates: "Critique is welcome. Opinion is free. But if you see a better build, allow another update. The version history is the audit trail.",
  claimLevel: "This map is an orientation artifact, not evidence for UCT by itself. Placing a tradition inside the kernel shows where it sits; it doesn't confirm the kernel. The mapping stays at the level of structural interpretation until it yields a discriminator, a method, a falsifiable prediction, or a ledgered empirical result — and those live in the empirical and governance tiers, not on this map.",
  registers: [
    {
      key: "sorted",
      label: "Sorted Material",
      desc: "Existing schools and traditions placed by what they structurally do. They came before UCT; UCT locates them within the kernel.",
    },
    {
      key: "applied",
      label: "UCT-Derived Frameworks",
      desc: "Frameworks generated by applying the kernel to a domain — BFS, FRLB, CIM, Synthetic Collapse. Outputs of the sorting discipline, not independent primitives, and not proof of the law-level programme.",
    },
    {
      key: "methodology",
      label: "Methodology & Governance",
      desc: "The sorting structure itself — the orientation discipline. How updates work, what counts as a structural improvement vs. an opinion swap, and how the map's claims are kept separate from the law-level programme.",
    },
  ],
  operatingPosture: {
    t0: [
      "Kernel First — the kernel is the load-bearing commitment; everything else is downstream of it.",
      "Faith Without Fideism — a constitutive starting commitment is unavoidable, but it stays revisable, not protected.",
      "Sealed Inquiry / No-Loss Fallacy — an inquiry that cannot lose isn't testing anything.",
      "The Tether — claims stay anchored to what can actually be checked.",
    ],
    t30: [
      "Coherence — constraint-visible order, the default outcome under constraint — is not intelligence, agency, or teleology.",
      "Randomness is not a first principle or an end-of-inquiry verdict; it names residual unpredictability under stated constraints, model class, diagnostics, and search budget.",
      "Chaos is structured unpredictability, not disorder.",
      "Intelligence is plastic, feedback-driven constraint-navigation, not mystical agency.",
      "Nothingness is not the vacuum, the null, or the merely unknown.",
    ],
  },
};

// =====================================================
// NEIGHBORS (external positioning — where UCT sits among peer frameworks)
// =====================================================
const NEIGHBORS = {
  intro:
    "Where the phase stack sorts domain work into the kernel, this view does the reverse: it locates UCT itself among the frameworks it is kin to. The same verb — locating — at a higher altitude. Placement here is positioning, not a claim that these traditions are secretly UCT.",
  groups: [
    {
      id: "lineage",
      title: "Philosophical Lineage",
      blurb:
        "Where UCT sits in metaphysics and epistemology — the families it extends and the neighbors it answers to. Stated in Kernel First.",
      members: [
        {
          name: "Structural Realism",
          stance: "Extends",
          shares:
            "The realist force of structure over isolated substances — structure is real, not a projection of language or mind.",
          diverges:
            "Refuses to promote structure into a base substrate, and is not the weaker epistemic thesis that we know only structure while the rest stays hidden. It adds how structures actualize, persist, and revise future constraints.",
        },
        {
          name: "Process Philosophy",
          stance: "Extends",
          shares: "The primacy of becoming and occurrence over static substance.",
          diverges:
            "Specifies a kernel where process thought asserts becoming — what possibility space, what constraints, what resolution, what records, what update — and refuses to crown process itself as base.",
        },
        {
          name: "Pragmatism",
          stance: "Neighbor",
          shares:
            "The link between knowing, practice, and fallibilist inquiry — concepts clarified by their consequences.",
          diverges:
            "Adds record integrity and update conditions that make intersubjective convergence auditable, rather than merely perspective-relative.",
        },
        {
          name: "Popper / Lakatos",
          stance: "Programme",
          shares:
            "Falsifiability and programme-level evaluation — a hard core kept in view, judged progressive or degenerating.",
          diverges:
            "Operationalizes falsifiability with the signature family, methods papers, and update-integrity standard — failure conditions built in, not merely professed. A progressive programme makes new domains legible; a degenerating one relabels them.",
        },
      ],
    },
    {
      id: "systems",
      title: "Systems-Theoretic Kin",
      blurb:
        "The 20th-century projects that also reached for cross-domain structural law. UCT shares the ambition; the divergences are where the kernel does work they do not.",
      members: [
        {
          name: "General Systems Theory",
          attribution: "von Bertalanffy",
          stance: "Ancestor",
          shares: "The search for structural pattern recurring across physics, biology, and society.",
          diverges:
            "Claims one grammar specialized per domain with explicit anti-false-analogy discipline, not isomorphism by resemblance — and crowns no organizing principle as base.",
        },
        {
          name: "Cybernetics",
          attribution: "Wiener, Ashby; second-order: von Foerster",
          stance: "Kin",
          shares: "Feedback, control, regulation, and self-reference — systems steering under constraint.",
          diverges:
            "Adds the explicit record and residue ledger (R, S) and record-time (T) as an accumulating coordinate. The update map U is feedback specified as constraint-revision through records — the loop with a persistence substrate.",
        },
        {
          name: "Complexity & Self-Organization",
          attribution: "Prigogine, Kauffman, Santa Fe",
          stance: "Kin",
          shares: "Emergence and order-from-constraint — structure arising far from equilibrium rather than by design.",
          diverges:
            "Attempts to supply its own falsification discipline — the signature family and auditing standards — so that broad cross-domain pattern claims do not become merely analogical or self-sealing. The residue term S connects to the dissipation language without crowning entropy as base.",
        },
      ],
    },
  ],
  note:
    "Autopoiesis (Maturana & Varela) already sits in the map as a biology-layer school — what it does in biology. Here it would appear at the systems-theory altitude as the account of self-producing organization. Same framework, two altitudes, no contradiction.",
};

// =====================================================
// UTILITIES
// =====================================================
const hexA = (hex, a) => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${a})`;
};

const SCHOOLS_BY_LAYER = LAYERS.reduce((acc, l) => {
  acc[l.id] = Object.entries(SCHOOLS).filter(([_, s]) => s.layerId === l.id).map(([id, s]) => ({ id, ...s }));
  return acc;
}, {});

// =====================================================
// COMPONENTS
// =====================================================

// Renders kernel notation as typeset math: ^X -> superscript, _X -> subscript.
// Source strings stay plain ASCII (e.g. "C^K_bio"); this formats them for display.
function KernelMath({ text }) {
  const parts = [];
  let i = 0;
  let k = 0;
  while (i < text.length) {
    const ch = text[i];
    if (ch === "^" || ch === "_") {
      i++;
      let run = "";
      while (i < text.length && /[A-Za-z0-9+]/.test(text[i])) {
        run += text[i];
        i++;
      }
      if (run) {
        parts.push(
          ch === "^" ? (
            <sup key={k++} style={{ fontSize: "0.72em" }}>{run}</sup>
          ) : (
            <sub key={k++} style={{ fontSize: "0.72em" }}>{run}</sub>
          )
        );
      }
    } else {
      let norm = "";
      while (i < text.length && text[i] !== "^" && text[i] !== "_") {
        norm += text[i];
        i++;
      }
      parts.push(<span key={k++}>{norm}</span>);
    }
  }
  return <span>{parts}</span>;
}

function RegisterBadge({ register, size = "sm" }) {
  if (register === "sorted") return null;
  const label = register === "applied" ? "UCT-DERIVED" : "METHODOLOGY";
  const color = register === "applied" ? C.applied : C.gold;
  return (
    <span
      style={{
        display: "inline-block",
        padding: size === "sm" ? "2px 7px" : "3px 9px",
        background: hexA(color, 0.1),
        border: `1px solid ${hexA(color, 0.35)}`,
        color,
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: size === "sm" ? 8.5 : 10,
        letterSpacing: "0.15em",
        textTransform: "uppercase",
        borderRadius: 3,
        marginLeft: 8,
        verticalAlign: "middle",
        whiteSpace: "nowrap",
      }}
    >
      {label}
    </span>
  );
}

function SchoolCard({ id, school, onOpen, compact = false }) {
  const layer = LAYER_BY_ID[school.layerId];
  return (
    <div
      onClick={() => onOpen(id)}
      style={{
        padding: compact ? "10px 12px" : "12px 14px",
        marginBottom: 8,
        background: school.register === "applied" ? hexA(C.applied, 0.05) : "rgba(0,0,0,0.25)",
        borderRadius: 8,
        borderLeft: `3px solid ${school.register === "applied" ? hexA(C.applied, 0.55) : hexA(layer.color, 0.5)}`,
        cursor: "pointer",
        transition: "all 0.2s ease",
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.background =
          school.register === "applied" ? hexA(C.applied, 0.09) : "rgba(255,255,255,0.04)";
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.background =
          school.register === "applied" ? hexA(C.applied, 0.05) : "rgba(0,0,0,0.25)";
      }}
    >
      <div
        style={{
          fontFamily: "'EB Garamond', Georgia, serif",
          fontSize: compact ? 13.5 : 14.5,
          color: C.fg,
          fontWeight: 600,
          lineHeight: 1.3,
          display: "flex",
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <span>{school.name}</span>
        <RegisterBadge register={school.register} />
      </div>
      {!compact && (
        <div
          style={{
            fontFamily: "'EB Garamond', Georgia, serif",
            fontSize: 12.5,
            color: C.muted,
            lineHeight: 1.55,
            marginTop: 6,
          }}
        >
          <KernelMath text={school.role} />
        </div>
      )}
      <div
        style={{
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 9,
          color: hexA(layer.color, 0.8),
          letterSpacing: "0.15em",
          textTransform: "uppercase",
          marginTop: 8,
        }}
      >
        {layer.label} · tap for details
      </div>
    </div>
  );
}

function NeighborCard({ n, color }) {
  return (
    <div
      style={{
        padding: "13px 15px",
        marginBottom: 10,
        background: "rgba(0,0,0,0.25)",
        borderRadius: 9,
        borderLeft: `3px solid ${hexA(color, 0.5)}`,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", flexWrap: "wrap", gap: 8, marginBottom: 9 }}>
        <span style={{ fontFamily: "'EB Garamond', Georgia, serif", fontSize: 15.5, color: C.fg, fontWeight: 600 }}>
          {n.name}
        </span>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 8,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color,
            background: hexA(color, 0.1),
            border: `1px solid ${hexA(color, 0.35)}`,
            borderRadius: 3,
            padding: "2px 7px",
          }}
        >
          {n.stance}
        </span>
        {n.attribution && (
          <span style={{ fontFamily: "'EB Garamond', Georgia, serif", fontSize: 11.5, color: C.dim, fontStyle: "italic" }}>
            {n.attribution}
          </span>
        )}
      </div>
      <div style={{ marginBottom: 8 }}>
        <div
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 8.5,
            letterSpacing: "0.16em",
            textTransform: "uppercase",
            color: hexA(color, 0.85),
            marginBottom: 3,
          }}
        >
          Shares
        </div>
        <div style={{ fontFamily: "'EB Garamond', Georgia, serif", fontSize: 13, color: C.muted, lineHeight: 1.55 }}>
          {n.shares}
        </div>
      </div>
      <div>
        <div
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 8.5,
            letterSpacing: "0.16em",
            textTransform: "uppercase",
            color: C.dim,
            marginBottom: 3,
          }}
        >
          Where UCT Diverges
        </div>
        <div style={{ fontFamily: "'EB Garamond', Georgia, serif", fontSize: 13, color: C.muted, lineHeight: 1.55 }}>
          {n.diverges}
        </div>
      </div>
    </div>
  );
}

function LayerCard({ layer, isExpanded, onToggle, onOpenSchool, index }) {
  const schools = SCHOOLS_BY_LAYER[layer.id];
  return (
    <div style={{ animation: `fadeSlideIn 0.5s ease ${index * 0.06}s both` }}>
      <div
        onClick={onToggle}
        style={{
          background: `linear-gradient(135deg, ${hexA(layer.color, 0.08)} 0%, rgba(8,9,12,0.95) 100%)`,
          border: `1px solid ${hexA(layer.color, 0.25)}`,
          borderRadius: 12,
          padding: "18px 16px",
          cursor: "pointer",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            width: 4,
            height: "100%",
            background: layer.color,
            borderRadius: "12px 0 0 12px",
          }}
        />

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9.5,
                letterSpacing: "0.2em",
                color: layer.color,
                textTransform: "uppercase",
                marginBottom: 4,
              }}
            >
              {layer.label}
            </div>
            <div
              style={{
                fontFamily: "'EB Garamond', Georgia, serif",
                fontSize: 19,
                color: C.fg,
                lineHeight: 1.25,
                fontStyle: "italic",
              }}
            >
              {layer.subtitle}
            </div>
          </div>
          <div
            style={{
              color: layer.color,
              fontSize: 16,
              transform: isExpanded ? "rotate(180deg)" : "rotate(0)",
              transition: "transform 0.3s ease",
              marginTop: 4,
            }}
          >
            ▾
          </div>
        </div>

        {isExpanded && (
          <div style={{ marginTop: 14 }}>
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 10.5,
                color: hexA(layer.color, 0.85),
                marginBottom: 12,
                padding: "5px 9px",
                background: "rgba(0,0,0,0.35)",
                borderRadius: 5,
              }}
            >
              <KernelMath text={layer.kernel} />
            </div>

            <p
              style={{
                fontFamily: "'EB Garamond', Georgia, serif",
                fontSize: 14,
                color: C.muted,
                lineHeight: 1.6,
                margin: "0 0 14px 0",
              }}
            >
              {layer.description}
            </p>

            <div style={{ marginBottom: 14 }}>
              <div
                style={{
                  fontSize: 9,
                  letterSpacing: "0.18em",
                  color: C.dim,
                  textTransform: "uppercase",
                  marginBottom: 6,
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                UCT Papers
              </div>
              {layer.uctPapers.map((p, i) => (
                <div
                  key={i}
                  style={{
                    fontFamily: "'EB Garamond', Georgia, serif",
                    fontSize: 12,
                    color: p.soon ? C.dim : C.muted,
                    opacity: p.soon ? 0.6 : 1,
                    padding: "2px 0",
                    borderLeft: `2px solid ${hexA(layer.color, p.soon ? 0.18 : 0.35)}`,
                    paddingLeft: 9,
                    marginBottom: 3,
                  }}
                >
                  {p.t}
                  {p.soon && (
                    <span
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 8.5,
                        color: C.dimmer,
                        letterSpacing: "0.12em",
                        textTransform: "uppercase",
                        marginLeft: 6,
                      }}
                    >
                      · forthcoming
                    </span>
                  )}
                </div>
              ))}
            </div>

            <div
              style={{
                fontSize: 9,
                letterSpacing: "0.18em",
                color: C.dim,
                textTransform: "uppercase",
                marginBottom: 8,
                fontFamily: "'JetBrains Mono', monospace",
              }}
            >
              Schools in this Phase ({schools.length})
            </div>
            {schools.map((s) => (
              <SchoolCard key={s.id} id={s.id} school={s} onOpen={onOpenSchool} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function HandoffConnector({ handoff, isExpanded, onToggle }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "2px 0" }}>
      <div style={{ width: 1, height: 14, background: `linear-gradient(to bottom, ${hexA(C.gold, 0.3)}, ${hexA(C.gold, 0.12)})` }} />
      <div
        onClick={onToggle}
        style={{
          cursor: "pointer",
          padding: "6px 12px",
          background: isExpanded ? hexA(C.gold, 0.09) : hexA(C.gold, 0.04),
          border: `1px solid ${isExpanded ? hexA(C.gold, 0.3) : hexA(C.gold, 0.12)}`,
          borderRadius: 20,
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        <span style={{ color: C.gold, fontSize: 11 }}>↓</span>
        <span
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 9.5,
            color: C.gold,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}
        >
          {handoff.label}
        </span>
      </div>
      {isExpanded && (
        <div
          style={{
            maxWidth: 320,
            padding: "10px 14px",
            marginTop: 8,
            background: hexA(C.gold, 0.05),
            borderRadius: 8,
            border: `1px solid ${hexA(C.gold, 0.15)}`,
          }}
        >
          <p style={{ fontFamily: "'EB Garamond', Georgia, serif", fontSize: 12.5, color: C.muted, lineHeight: 1.55, margin: 0 }}>
            {handoff.description}
          </p>
        </div>
      )}
      <div style={{ width: 1, height: 14, background: `linear-gradient(to bottom, ${hexA(C.gold, 0.12)}, ${hexA(C.gold, 0.3)})` }} />
    </div>
  );
}

function SchoolDetailPanel({ schoolId, history, onClose, onNavigate, onBack }) {
  if (!schoolId) return null;
  const school = SCHOOLS[schoolId];
  if (!school) return null;
  const layer = LAYER_BY_ID[school.layerId];
  const cousins = (school.cousins || []).map((id) => ({ id, school: SCHOOLS[id] })).filter((c) => c.school);

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(4,5,8,0.92)",
        backdropFilter: "blur(8px)",
        zIndex: 100,
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        padding: "16px",
        overflowY: "auto",
        animation: "fadeIn 0.2s ease",
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: 440,
          width: "100%",
          background: C.bgSoft,
          border: `1px solid ${hexA(layer.color, 0.35)}`,
          borderRadius: 14,
          padding: "20px 18px",
          marginTop: 24,
          marginBottom: 24,
        }}
      >
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            {history.length > 0 && (
              <button
                onClick={onBack}
                style={{
                  background: "transparent",
                  border: `1px solid ${hexA(C.gold, 0.25)}`,
                  color: C.gold,
                  borderRadius: 6,
                  padding: "5px 8px",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 10,
                  letterSpacing: "0.1em",
                }}
              >
                <ArrowLeft size={11} style={{ marginRight: 4 }} /> Back
              </button>
            )}
          </div>
          <button
            onClick={onClose}
            style={{ background: "transparent", border: "none", color: C.muted, cursor: "pointer", padding: 4 }}
          >
            <X size={20} />
          </button>
        </div>

        <div
          style={{
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 9.5,
            letterSpacing: "0.22em",
            color: layer.color,
            textTransform: "uppercase",
            marginBottom: 6,
          }}
        >
          {layer.label} · {layer.subtitle}
        </div>

        <h2
          style={{
            fontFamily: "'EB Garamond', Georgia, serif",
            fontSize: 22,
            fontWeight: 500,
            color: C.fg,
            margin: "0 0 10px 0",
            lineHeight: 1.25,
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
          }}
        >
          <span>{school.name}</span>
          <RegisterBadge register={school.register} size="md" />
        </h2>

        {/* Structural role */}
        <div style={{ marginBottom: 16 }}>
          <SectionLabel color={layer.color}>Structural Role</SectionLabel>
          <p style={prose}><KernelMath text={school.role} /></p>
        </div>

        {/* Edge */}
        <div style={{ marginBottom: 16 }}>
          <SectionLabel color={C.dim}>Where the Frame Ends</SectionLabel>
          <p style={{ ...prose, color: C.dim }}>{school.edge}</p>
        </div>

        {/* UCT notes if present */}
        {school.uctNotes && (
          <div style={{ marginBottom: 16 }}>
            <SectionLabel color={C.gold}>UCT Note</SectionLabel>
            <p style={{ ...prose, fontStyle: "italic" }}>{school.uctNotes}</p>
          </div>
        )}

        {/* Cousins */}
        {cousins.length > 0 && (
          <div style={{ marginBottom: 8 }}>
            <SectionLabel color={layer.color}>Structural Cousins</SectionLabel>
            <div style={{ fontSize: 11.5, color: C.dim, marginBottom: 8, fontStyle: "italic", fontFamily: "'EB Garamond', Georgia, serif" }}>
              Schools doing structurally adjacent work across layers
            </div>
            {cousins.map(({ id, school: c }) => {
              const cLayer = LAYER_BY_ID[c.layerId];
              return (
                <div
                  key={id}
                  onClick={() => onNavigate(id)}
                  style={{
                    padding: "10px 12px",
                    marginBottom: 6,
                    background: "rgba(0,0,0,0.3)",
                    border: `1px solid ${hexA(cLayer.color, 0.25)}`,
                    borderRadius: 8,
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.background = hexA(cLayer.color, 0.08); }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = "rgba(0,0,0,0.3)"; }}
                >
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div
                      style={{
                        fontFamily: "'EB Garamond', Georgia, serif",
                        fontSize: 14,
                        color: C.fg,
                        fontWeight: 500,
                        lineHeight: 1.3,
                      }}
                    >
                      {c.name}
                    </div>
                    <div
                      style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 8.5,
                        color: hexA(cLayer.color, 0.85),
                        letterSpacing: "0.15em",
                        textTransform: "uppercase",
                        marginTop: 3,
                      }}
                    >
                      {cLayer.label}
                      {c.register === "applied" && <span style={{ marginLeft: 6, color: C.applied }}>· UCT-Derived</span>}
                    </div>
                  </div>
                  <span style={{ color: hexA(cLayer.color, 0.7), fontSize: 14, marginLeft: 8 }}>→</span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

const prose = {
  fontFamily: "'EB Garamond', Georgia, serif",
  fontSize: 14,
  color: C.muted,
  lineHeight: 1.6,
  margin: 0,
};

function SectionLabel({ children, color }) {
  return (
    <div
      style={{
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 9.5,
        letterSpacing: "0.2em",
        color,
        textTransform: "uppercase",
        marginBottom: 6,
      }}
    >
      {children}
    </div>
  );
}

function MethodologyPanel({ onClose }) {
  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(4,5,8,0.92)",
        backdropFilter: "blur(8px)",
        zIndex: 100,
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-start",
        padding: 16,
        overflowY: "auto",
      }}
      onClick={onClose}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          maxWidth: 440,
          width: "100%",
          background: C.bgSoft,
          border: `1px solid ${hexA(C.gold, 0.35)}`,
          borderRadius: 14,
          padding: "22px 18px",
          marginTop: 24,
          marginBottom: 24,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
          <div
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              fontSize: 10,
              letterSpacing: "0.25em",
              color: C.gold,
              textTransform: "uppercase",
            }}
          >
            Reading This Map
          </div>
          <button onClick={onClose} style={{ background: "transparent", border: "none", color: C.muted, cursor: "pointer", padding: 4 }}>
            <X size={20} />
          </button>
        </div>

        <h2
          style={{
            fontFamily: "'EB Garamond', Georgia, serif",
            fontSize: 22,
            fontWeight: 500,
            color: C.fg,
            margin: "0 0 16px 0",
            lineHeight: 1.25,
          }}
        >
          The Sorting Structure
        </h2>

        <div style={{ marginBottom: 18 }}>
          <SectionLabel color={C.gold}>Posture</SectionLabel>
          <p style={prose}>{METHODOLOGY.posture}</p>
          <p style={{ ...prose, fontSize: 11.5, color: C.dim, fontStyle: "italic", marginTop: 8 }}>
            <KernelMath text={METHODOLOGY.kernelNote} />
          </p>
        </div>

        <div style={{ marginBottom: 18 }}>
          <SectionLabel color={C.gold}>Claim Level</SectionLabel>
          <p style={prose}>{METHODOLOGY.claimLevel}</p>
        </div>

        <div style={{ marginBottom: 18 }}>
          <SectionLabel color={C.gold}>Identity</SectionLabel>
          <p style={prose}>{METHODOLOGY.identity}</p>
        </div>

        <div style={{ marginBottom: 18 }}>
          <SectionLabel color={C.gold}>How Updates Work</SectionLabel>
          <p style={prose}>{METHODOLOGY.updates}</p>
        </div>

        <div>
          <SectionLabel color={C.gold}>Three Registers</SectionLabel>
          {METHODOLOGY.registers.map((r) => (
            <div
              key={r.key}
              style={{
                padding: "10px 12px",
                marginBottom: 8,
                background: r.key === "applied" ? hexA(C.applied, 0.05) : "rgba(0,0,0,0.25)",
                borderRadius: 8,
                borderLeft: `3px solid ${r.key === "applied" ? hexA(C.applied, 0.55) : hexA(C.gold, 0.5)}`,
              }}
            >
              <div
                style={{
                  fontFamily: "'EB Garamond', Georgia, serif",
                  fontSize: 14.5,
                  color: C.fg,
                  fontWeight: 600,
                  marginBottom: 4,
                }}
              >
                {r.label}
              </div>
              <div style={{ ...prose, fontSize: 12.5, color: C.muted }}>{r.desc}</div>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 18 }}>
          <SectionLabel color={C.gold}>Operating Posture — Assumed and Cleared First</SectionLabel>
          <div style={{ marginBottom: 12 }}>
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                color: C.dim,
                letterSpacing: "0.18em",
                textTransform: "uppercase",
                marginBottom: 6,
              }}
            >
              Tier 0 · Foundations
            </div>
            {METHODOLOGY.operatingPosture.t0.map((x, i) => (
              <div
                key={i}
                style={{
                  ...prose,
                  fontSize: 12.5,
                  color: C.muted,
                  borderLeft: `2px solid ${hexA(C.gold, 0.4)}`,
                  paddingLeft: 9,
                  marginBottom: 5,
                }}
              >
                {x}
              </div>
            ))}
          </div>
          <div>
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9,
                color: C.dim,
                letterSpacing: "0.18em",
                textTransform: "uppercase",
                marginBottom: 6,
              }}
            >
              Tier 30 · Ground Cleared (Primes)
            </div>
            {METHODOLOGY.operatingPosture.t30.map((x, i) => (
              <div
                key={i}
                style={{
                  ...prose,
                  fontSize: 12.5,
                  color: C.muted,
                  borderLeft: `2px solid ${hexA(C.gold, 0.4)}`,
                  paddingLeft: 9,
                  marginBottom: 5,
                }}
              >
                {x}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// =====================================================
// MAIN
// =====================================================
export default function UCTArchitectureMapV4() {
  const [mode, setMode] = useState("stack"); // stack | library | neighbors
  const [expandedLayers, setExpandedLayers] = useState(new Set(["physics"]));
  const [expandedHandoffs, setExpandedHandoffs] = useState(new Set());
  const [selectedSchool, setSelectedSchool] = useState(null);
  const [navHistory, setNavHistory] = useState([]);
  const [showMethodology, setShowMethodology] = useState(false);
  const [libraryFilter, setLibraryFilter] = useState("all"); // all | sorted | applied
  const [libraryLayer, setLibraryLayer] = useState("all");

  const toggleLayer = (id) => {
    setExpandedLayers((p) => {
      const n = new Set(p);
      n.has(id) ? n.delete(id) : n.add(id);
      return n;
    });
  };

  const toggleHandoff = (i) => {
    setExpandedHandoffs((p) => {
      const n = new Set(p);
      n.has(i) ? n.delete(i) : n.add(i);
      return n;
    });
  };

  const openSchool = (id) => {
    setNavHistory([]);
    setSelectedSchool(id);
  };

  const navigateToSchool = (id) => {
    if (selectedSchool) setNavHistory((p) => [...p, selectedSchool]);
    setSelectedSchool(id);
  };

  const goBack = () => {
    const prev = navHistory[navHistory.length - 1];
    setNavHistory((p) => p.slice(0, -1));
    setSelectedSchool(prev);
  };

  const closeSchool = () => {
    setSelectedSchool(null);
    setNavHistory([]);
  };

  const filteredSchools = useMemo(() => {
    return Object.entries(SCHOOLS)
      .filter(([_, s]) => {
        if (libraryFilter !== "all" && s.register !== libraryFilter) return false;
        if (libraryLayer !== "all" && s.layerId !== libraryLayer) return false;
        return true;
      })
      .map(([id, s]) => ({ id, ...s }))
      .sort((a, b) => {
        const aIdx = LAYERS.findIndex((l) => l.id === a.layerId);
        const bIdx = LAYERS.findIndex((l) => l.id === b.layerId);
        if (aIdx !== bIdx) return aIdx - bIdx;
        if (a.register !== b.register) return a.register === "applied" ? 1 : -1;
        return a.name.localeCompare(b.name);
      });
  }, [libraryFilter, libraryLayer]);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: C.bg,
        color: C.fg,
        padding: "32px 14px 56px",
        fontFamily: "'EB Garamond', Georgia, serif",
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&family=JetBrains+Mono:wght@300;400;500&display=swap');
        @keyframes fadeSlideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        * { box-sizing: border-box; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: ${hexA(C.gold, 0.2)}; border-radius: 4px; }
        body { margin: 0; }
      `}</style>

      <div style={{ maxWidth: 460, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 18 }}>
          <div
            style={{
              fontSize: 9.5,
              letterSpacing: "0.32em",
              color: C.gold,
              textTransform: "uppercase",
              marginBottom: 6,
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            Universal Collapse Theory
          </div>
          <h1
            style={{
              fontFamily: "'EB Garamond', Georgia, serif",
              fontSize: 28,
              fontWeight: 500,
              color: C.fg,
              margin: "0 0 8px 0",
              lineHeight: 1.15,
            }}
          >
            Architecture Map
          </h1>
          <p style={{ fontSize: 12.5, color: C.dim, margin: "0 0 14px 0", lineHeight: 1.5, fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.02em" }}>
            sorting structure for accumulated knowledge
          </p>
        </div>

        {/* Posture card */}
        <div
          onClick={() => setShowMethodology(true)}
          style={{
            padding: "14px 16px",
            background: `linear-gradient(135deg, ${hexA(C.gold, 0.07)} 0%, rgba(8,9,12,0.95) 100%)`,
            border: `1px solid ${hexA(C.gold, 0.25)}`,
            borderRadius: 10,
            marginBottom: 18,
            cursor: "pointer",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 9.5,
                letterSpacing: "0.22em",
                color: C.gold,
                textTransform: "uppercase",
                display: "flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <Compass size={11} /> Reading This Map
            </div>
            <span style={{ color: C.gold, fontSize: 13 }}>→</span>
          </div>
          <p
            style={{
              fontFamily: "'EB Garamond', Georgia, serif",
              fontSize: 13.5,
              color: C.muted,
              lineHeight: 1.55,
              margin: 0,
            }}
          >
            This map uses UCT as a sorting grammar, not a replacement theory for the schools it places. Schools below remain themselves — the map locates their structural roles, boundaries, and handoffs under the kernel. Tap for the full posture.
          </p>
        </div>

        {/* Mode toggle */}
        <div
          style={{
            display: "flex",
            gap: 6,
            marginBottom: 22,
            padding: 4,
            background: "rgba(255,255,255,0.03)",
            border: "1px solid rgba(255,255,255,0.06)",
            borderRadius: 10,
          }}
        >
          {[
            { id: "stack", label: "Phase Stack", icon: Layers },
            { id: "library", label: "Library", icon: Grid3x3 },
            { id: "neighbors", label: "Neighbors", icon: Network },
          ].map((m) => {
            const Icon = m.icon;
            const active = mode === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                style={{
                  flex: 1,
                  padding: "9px 10px",
                  background: active ? hexA(C.gold, 0.12) : "transparent",
                  border: active ? `1px solid ${hexA(C.gold, 0.35)}` : "1px solid transparent",
                  borderRadius: 6,
                  color: active ? C.gold : C.dim,
                  fontFamily: "'JetBrains Mono', monospace",
                  fontSize: 10.5,
                  letterSpacing: "0.12em",
                  textTransform: "uppercase",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 6,
                  transition: "all 0.2s ease",
                }}
              >
                <Icon size={12} />
                {m.label}
              </button>
            );
          })}
        </div>

        {/* STACK MODE */}
        {mode === "stack" && (
          <>
            {LAYERS.map((layer, i) => (
              <div key={layer.id}>
                <LayerCard
                  layer={layer}
                  isExpanded={expandedLayers.has(layer.id)}
                  onToggle={() => toggleLayer(layer.id)}
                  onOpenSchool={openSchool}
                  index={i}
                />
                {i < HANDOFFS.length && (
                  <HandoffConnector
                    handoff={HANDOFFS[i]}
                    isExpanded={expandedHandoffs.has(i)}
                    onToggle={() => toggleHandoff(i)}
                  />
                )}
              </div>
            ))}

            {/* You Are Here */}
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", padding: "20px 0 4px" }}>
              <div style={{ width: 1, height: 22, background: `linear-gradient(to bottom, ${hexA(C.ember, 0.3)}, ${hexA(C.ember, 0.08)})` }} />
              <div
                style={{
                  padding: "14px 18px",
                  background: hexA(C.ember, 0.06),
                  border: `1px solid ${hexA(C.ember, 0.28)}`,
                  borderRadius: 12,
                  textAlign: "center",
                  maxWidth: 360,
                }}
              >
                <div
                  style={{
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 9.5,
                    letterSpacing: "0.22em",
                    color: C.ember,
                    textTransform: "uppercase",
                    marginBottom: 8,
                  }}
                >
                  You Are Here
                </div>
                <div style={{ fontFamily: "'EB Garamond', Georgia, serif", fontSize: 14, color: C.gold, marginBottom: 6 }}>
                  Standing on the floor, talking to recursive CIM
                </div>
                <div style={{ fontFamily: "'EB Garamond', Georgia, serif", fontSize: 12.5, color: C.dim, lineHeight: 1.55 }}>
                  Humanity is engaging recursive CIM at scale. This map is one coherence-first floor for reading that encounter — without confusing processing, intelligence, commitment, and consciousness.
                </div>
              </div>
            </div>
          </>
        )}

        {/* LIBRARY MODE */}
        {mode === "library" && (
          <>
            {/* Filters */}
            <div style={{ marginBottom: 16 }}>
              <div
                style={{
                  fontSize: 9,
                  letterSpacing: "0.2em",
                  color: C.dim,
                  textTransform: "uppercase",
                  marginBottom: 7,
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                Register
              </div>
              <div style={{ display: "flex", gap: 6, marginBottom: 12, flexWrap: "wrap" }}>
                {[
                  { id: "all", label: "All" },
                  { id: "sorted", label: "Sorted" },
                  { id: "applied", label: "UCT-Derived" },
                ].map((f) => {
                  const active = libraryFilter === f.id;
                  return (
                    <button
                      key={f.id}
                      onClick={() => setLibraryFilter(f.id)}
                      style={{
                        padding: "6px 11px",
                        background: active ? hexA(f.id === "applied" ? C.applied : C.gold, 0.12) : "rgba(255,255,255,0.03)",
                        border: `1px solid ${active ? hexA(f.id === "applied" ? C.applied : C.gold, 0.4) : "rgba(255,255,255,0.08)"}`,
                        color: active ? (f.id === "applied" ? C.applied : C.gold) : C.dim,
                        borderRadius: 6,
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 10,
                        letterSpacing: "0.08em",
                        cursor: "pointer",
                      }}
                    >
                      {f.label}
                    </button>
                  );
                })}
              </div>

              <div
                style={{
                  fontSize: 9,
                  letterSpacing: "0.2em",
                  color: C.dim,
                  textTransform: "uppercase",
                  marginBottom: 7,
                  fontFamily: "'JetBrains Mono', monospace",
                }}
              >
                Phase
              </div>
              <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
                <button
                  onClick={() => setLibraryLayer("all")}
                  style={{
                    padding: "5px 9px",
                    background: libraryLayer === "all" ? hexA(C.gold, 0.12) : "rgba(255,255,255,0.03)",
                    border: `1px solid ${libraryLayer === "all" ? hexA(C.gold, 0.4) : "rgba(255,255,255,0.08)"}`,
                    color: libraryLayer === "all" ? C.gold : C.dim,
                    borderRadius: 6,
                    fontFamily: "'JetBrains Mono', monospace",
                    fontSize: 9,
                    letterSpacing: "0.08em",
                    cursor: "pointer",
                  }}
                >
                  All
                </button>
                {LAYERS.map((l) => {
                  const active = libraryLayer === l.id;
                  return (
                    <button
                      key={l.id}
                      onClick={() => setLibraryLayer(l.id)}
                      style={{
                        padding: "5px 9px",
                        background: active ? hexA(l.color, 0.15) : "rgba(255,255,255,0.03)",
                        border: `1px solid ${active ? hexA(l.color, 0.45) : "rgba(255,255,255,0.08)"}`,
                        color: active ? l.color : C.dim,
                        borderRadius: 6,
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: 9,
                        letterSpacing: "0.08em",
                        cursor: "pointer",
                      }}
                    >
                      {l.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <div
              style={{
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: 10,
                color: C.dim,
                letterSpacing: "0.12em",
                textTransform: "uppercase",
                marginBottom: 10,
              }}
            >
              {filteredSchools.length} school{filteredSchools.length === 1 ? "" : "s"}
            </div>

            {filteredSchools.map((s) => (
              <SchoolCard key={s.id} id={s.id} school={s} onOpen={openSchool} />
            ))}
          </>
        )}

        {/* NEIGHBORS MODE */}
        {mode === "neighbors" && (
          <>
            <div
              style={{
                fontFamily: "'EB Garamond', Georgia, serif",
                fontSize: 13.5,
                color: C.muted,
                lineHeight: 1.6,
                marginBottom: 20,
                padding: "13px 15px",
                background: hexA(C.gold, 0.05),
                border: `1px solid ${hexA(C.gold, 0.2)}`,
                borderRadius: 9,
              }}
            >
              {NEIGHBORS.intro}
            </div>

            {NEIGHBORS.groups.map((g) => {
              const gc = g.id === "systems" ? "#6ea5b8" : C.gold;
              return (
                <div key={g.id} style={{ marginBottom: 22 }}>
                  <div
                    style={{
                      fontFamily: "'JetBrains Mono', monospace",
                      fontSize: 10,
                      letterSpacing: "0.2em",
                      textTransform: "uppercase",
                      color: gc,
                      marginBottom: 5,
                    }}
                  >
                    {g.title}
                  </div>
                  <div
                    style={{
                      fontFamily: "'EB Garamond', Georgia, serif",
                      fontSize: 12.5,
                      color: C.dim,
                      lineHeight: 1.55,
                      marginBottom: 12,
                    }}
                  >
                    {g.blurb}
                  </div>
                  {g.members.map((n) => (
                    <NeighborCard key={n.name} n={n} color={gc} />
                  ))}
                </div>
              );
            })}

            <div
              style={{
                fontFamily: "'EB Garamond', Georgia, serif",
                fontSize: 12,
                color: C.dim,
                fontStyle: "italic",
                lineHeight: 1.55,
                marginTop: 4,
                padding: "11px 14px",
                borderLeft: `2px solid ${hexA(C.gold, 0.3)}`,
              }}
            >
              {NEIGHBORS.note}
            </div>
          </>
        )}

        {/* Footer */}
        <div
          style={{
            textAlign: "center",
            marginTop: 32,
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: 9.5,
            color: C.dimmer,
            letterSpacing: "0.12em",
          }}
        >
          HoldingLight LLC · universalcollapse.com
        </div>
      </div>

      {/* Overlays */}
      {selectedSchool && (
        <SchoolDetailPanel
          schoolId={selectedSchool}
          history={navHistory}
          onClose={closeSchool}
          onNavigate={navigateToSchool}
          onBack={goBack}
        />
      )}
      {showMethodology && <MethodologyPanel onClose={() => setShowMethodology(false)} />}
    </div>
  );
}
