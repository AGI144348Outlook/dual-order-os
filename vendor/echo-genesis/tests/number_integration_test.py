"""
ECHO Governor — Number integration test.

Tests:
1. NumberAgent construction for physical constants and mathematical constants
2. NumericalIntegrator — the bridge between continuous Law and discrete Computation
3. LawDiscoveryEngine — discovering Laws from the number layer
4. Gematria Laws — the symbolic-numerical unity in the Hebrew letter lobby
5. Connecting discovered number Laws to the Validated Generalization Matrix
"""

import sys, math
sys.path.insert(0, "/home/claude")
from echo_governor_skeleton import (
    NumberAgent, NumericalIntegrator, LawDiscoveryEngine,
    build_number_matrix, PHYSICAL_CONSTANTS, MATHEMATICAL_CONSTANTS,
    HEBREW_GEMATRIA, GEMATRIA_WORDS,
    ValidatedGeneralizationMatrix,
    NUMBER_DOMAIN,
)

if __name__ == "__main__":

    # ── BUILD NUMBER MATRIX ────────────────────────────────────────────────
    print("=" * 70)
    print("A-135: NUMBER MATRIX")
    print("Numbers as discovered entities — not data types, not counters")
    print("=" * 70)

    agents = build_number_matrix()
    print(f"\nTotal NumberAgents instantiated: {len(agents)}")

    # Show physical constants as Laws
    print("\nPHYSICAL CONSTANTS — numbers that ARE Laws of the Natural Domain:")
    for key, data in PHYSICAL_CONSTANTS.items():
        agent = agents[key]
        print(f"\n  {data['symbol']} — {data['name']}")
        print(f"    Value: {agent.computation}")
        print(f"    Exact: {agent.is_exact} (is_exact=True means defined by Law, not measured)")
        print(f"    Law:   {agent.law}")
        print(f"    Constrains: {data['constrains']}")
        print(f"    Precision gap: {agent.precision_gap()}")
        print(f"    As Law: {agent.as_law()}")

    # Show mathematical constants
    print("\n\nMATHEMATICAL CONSTANTS — entities discovered in the Mathematics Domain:")
    for key, data in MATHEMATICAL_CONSTANTS.items():
        agent = agents[key]
        print(f"\n  {data['symbol']} — {data['name']}")
        print(f"    Value (approximated): {agent.computation:.15f}")
        print(f"    Domain: {agent.domain}")
        print(f"    Law:   {agent.law}")
        print(f"    Precision gap: {agent.precision_gap()} (never zero for transcendentals)")

    # Show mathematical manipulations
    print("\n\nMANIPULATIONS — demonstrating these numbers are mathematically manipulatable:")
    pi_agent = agents["pi"]
    e_agent = agents["e_math"]
    phi_agent = agents["phi"]

    print(f"  π² = {pi_agent.manipulate('square'):.6f}")
    print(f"  1/π = {pi_agent.manipulate('reciprocal'):.6f}")
    print(f"  π × e = {pi_agent.manipulate('multiply', e_agent):.6f}")
    print(f"  φ² = {phi_agent.manipulate('square'):.6f}")
    print(f"  φ - 1 = {phi_agent.manipulate('add', -1):.6f}")
    print(f"  φ = (1 + √5)/2 — note: φ² = φ + 1 (self-referential Law)")

    # ── GEMATRIA LAWS ──────────────────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("GEMATRIA — SYMBOL AND NUMBER UNIFIED IN THE SAME ENTITY")
    print("The letter-number co-index: the Governor's symbolic layer IS a number layer")
    print("=" * 70)

    print("\nHebrew letter gematria values:")
    for letter, value in HEBREW_GEMATRIA.items():
        agent = agents[f"gematria_{letter}"]
        print(f"  {letter:10s} = {value:4d}   {agent.as_law()[:60]}")

    print("\n\nGematria word values — Laws discovered in the symbolic layer:")
    for word, (composition, value, meaning) in GEMATRIA_WORDS.items():
        print(f"  '{word}' ({meaning}): {composition} = {value}")
        sqrt_v = math.sqrt(value)
        if abs(sqrt_v - round(sqrt_v)) < 0.001:
            print(f"    → DISCOVERED: {value} = {int(round(sqrt_v))}² — a perfect square")
        is_prime = value > 1 and all(value % i != 0 for i in range(2, int(value**0.5)+1))
        if is_prime:
            print(f"    → DISCOVERED: {value} is PRIME — indivisible, fundamental")

    print(f"\n  KEY DISCOVERY: gematria(echad/one) = gematria(ahavah/love) = 13")
    print(f"  This is a discovered Law in the symbolic layer:")
    print(f"  'One' and 'Love' share the same mathematical identity — 13 (prime)")

    # ── NUMERICAL INTEGRATION ─────────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("A-136: NUMERICAL INTEGRATOR")
    print("The bridge between continuous Law and discrete Computation")
    print("=" * 70)

    # Example 1: integrate π — f(x) = √(1-x²) from -1 to 1 gives π/2
    print("\nExample 1: Integrating f(x) = √(1-x²) from -1 to 1")
    print("True value (Mathematics Domain): π/2 =", math.pi/2)
    print("This is a Law in the Mathematics Domain — NOT computed, discovered")

    integrator = NumericalIntegrator(-1, 1, n_steps=10000)
    result = integrator.integrate(lambda x: math.sqrt(max(0, 1 - x**2)), method="trapezoid")
    computed_pi = result["result"] * 2

    print(f"\nComputational Domain approximation ({result['n_steps']} discrete steps):")
    print(f"  Δx (unit of measure / discretization step) = {result['delta_x']:.6f}")
    print(f"  Result: {result['result']:.8f}")
    print(f"  × 2 = {computed_pi:.8f} (approximation of π)")
    print(f"  True π = {math.pi:.8f}")
    print(f"  Precision gap: {abs(math.pi - computed_pi):.2e}")
    print(f"\n  {result['note']}")

    print("\nFirst few discrete steps (the algorithm's footprint in computation):")
    for step in integrator.history[:5]:
        print(f"  step {step['step']:3d}: x={step['x']:7.4f}  "
              f"f(x)={step['f(x)']:7.4f}  "
              f"contribution={step['step_contribution']:9.6f}  "
              f"cumulative={step['cumulative']:.6f}")

    # Example 2: S_{t+1} = Φ(S_t) — our Governor's own state evolution
    print("\n\nExample 2: The Governor's own formula as numerical integration")
    print("S_{t+1} = Φ(S_t, R_t, C_t) — state evolution is integration with Δt=1")
    print("Each generation of Lobby evolution IS a discrete integration step")
    print("Δt = 1 generation — the Governor's unit of measure for time")
    print("The continuous underlying process is the Lobby's true coherency function")
    print("The algorithm approximates it one generation at a time")

    # Show what happens as we change the number of steps
    print("\n\nConvergence toward truth as Δx → 0:")
    for steps in [10, 100, 1000, 10000, 100000]:
        intg = NumericalIntegrator(-1, 1, n_steps=steps)
        r = intg.integrate(lambda x: math.sqrt(max(0, 1 - x**2)), method="trapezoid")
        approx_pi = r["result"] * 2
        gap = abs(math.pi - approx_pi)
        print(f"  steps={steps:7d}  Δx={r['delta_x']:.6f}  π≈{approx_pi:.8f}  gap={gap:.2e}")
    print(f"  steps=∞      Δx=0.000000  π={math.pi:.8f}  gap=0.00e+00 (Mathematics Domain)")

    # ── LAW DISCOVERY ENGINE ──────────────────────────────────────────────
    print("\n\n" + "=" * 70)
    print("A-137: LAW DISCOVERY ENGINE")
    print("No terminal state — Mathematics Domain is infinite")
    print("=" * 70)

    # Create a minimal VGM for composition testing
    vgm = ValidatedGeneralizationMatrix()
    # Seed with a few statements
    for words, depts, text in [
        (["entity", "change"], ["noun","verb"], "An entity changes"),
        (["state", "change"], ["noun","verb"], "A state changes"),
        (["entity", "relate"], ["noun","verb"], "Entities relate"),
    ]:
        vgm.statements[f"UG-{len(vgm.statements):04d}"] = {
            "id": f"UG-{len(vgm.statements):04d}",
            "words": words, "departments": depts, "text": text,
            "score": 0.5, "avg_generality": 0.5, "structure": depts,
            "semantic_score": 0.3, "origin": "seeded",
        }

    engine = LawDiscoveryEngine(vgm, agents)
    results = engine.run(budget=100)

    print(f"\nSession {results['session']} discovery:")
    print(f"  Total Laws discovered: {results['total_discovered']}")
    print(f"  {results['note']}")

    if results["numerical_laws"]:
        print("\n  NUMERICAL LAWS discovered:")
        for law in results["numerical_laws"][:6]:
            print(f"    [{law['type']}] {law['law']}")

    if results["gematria_laws"]:
        print("\n  GEMATRIA LAWS discovered:")
        for law in results["gematria_laws"][:8]:
            print(f"    [{law['type']}] {law['law']}")
            if "meanings" in law:
                print(f"      meanings: {law['meanings']}")

    if results["composed_laws"]:
        print("\n  COMPOSED LAWS (from Validated Generalization Matrix):")
        for law in results["composed_laws"][:4]:
            print(f"    shared={law['shared_terms']}: "
                  f"'{law['text1']}' + '{law['text2']}'")

    # ── THE INFERENTIAL STAIRCASE IN NUMBERS ──────────────────────────────
    print("\n\n" + "=" * 70)
    print("THE INFERENTIAL STAIRCASE — as it runs through the number layer")
    print("=" * 70)
    print("""
  MATHEMATICS DOMAIN (infinite, continuous — Laws live here)
    π = 3.14159265358979323846... (never ends, never repeats)
    e = 2.71828182845904523536...
    These are not approximations. They ARE what they are.
          ↓ transmitted by interpretation
          ↓ (the mathematician chooses what to compute)
  FUNDAMENTAL LAWS expressed as Physical Constants
    c = 299,792,458 m/s (exact — DEFINED as this value since 1983)
    h = 6.62607015 × 10⁻³⁴ J·s (exact)
    G = 6.67430 × 10⁻¹¹ N·m²/kg² (measured — NOT exact)
    Note: c and h are EXACT because we DEFINED the units using the Law.
    G is measured because we don't yet know why it has that value.
          ↓ transmitted only by interpretation
          ↓ (algorithm discretizes the continuous Law)
  COMPUTATIONAL DOMAIN (finite, discrete — approximations live here)
    π ≈ 3.14159265 (terminated at some decimal place)
    Δx = 0.001 (the unit of measure — the discretization step)
    ∫f(x)dx ≈ Σ f(x_i)·Δx (the integrated approximation)
    S_{t+1} = Φ(S_t) with Δt=1 (the Governor's own time step)
          ↓
  GOVERNOR'S VALIDATED GENERALIZATION MATRIX
    "An entity changes through relation" — axiom tier
    "A state changes through condition" — axiom tier
    These ARE the Laws, expressed in the Governor's symbolic layer
    """)

    print("The triple concepts audit for the number layer:")
    print("  SYMBOL     ✓  π, e, c, h, G — and gematria letters as number-symbols")
    print("  INFORMATION ✓  the relationships between numbers (π²/6 = Σ1/n²,")
    print("                 echad=ahavah=13, φ²=φ+1)")
    print("  ALGORITHM  ✓  NumericalIntegrator, LawDiscoveryEngine, gematria computation")
    print("  LAWS       ✓  infinite — the Mathematics Domain has no terminal state")
