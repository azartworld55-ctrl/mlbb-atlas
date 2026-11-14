# Structured formula format

MLBB Atlas stores formula definitions as JSON expression trees rather than executable strings. This makes calculations reviewable and avoids evaluating untrusted code.

Supported nodes:

- Constant: `{"const": 120}`
- Stat reference: `{"stat": "physical_attack"}`
- Operation: `{"op": "add", "args": [NODE, NODE]}`

Supported operations: `add`, `sub`, `mul`, `div`, `min`, `max`.

Example (illustrative only; **not** a claim about any particular MLBB skill):

```json
{
  "op": "add",
  "args": [
    {"const": 100},
    {
      "op": "mul",
      "args": [{"stat": "physical_attack"}, {"const": 0.8}]
    }
  ]
}
```

With `physical_attack = 200`, the expression returns 260. Real skill formulas must be sourced, tied to a game patch and tested before being added to the production dataset. This evaluator only computes the supplied expression; it does not decide which in-game mitigation, defense or special-case rules apply.


## Calculator API

```http
POST /api/v1/calculator/evaluate
Content-Type: application/json
```

Example request:

```json
{
  "formula_id": "demo-skill",
  "game_patch": "2.2.23",
  "expression": {
    "op": "add",
    "args": [
      {"const": 100},
      {"op": "mul", "args": [{"stat": "physical_attack"}, {"const": 0.8}]}
    ]
  },
  "stats": {"physical_attack": 200}
}
```

The endpoint returns the expression result (260 in this illustrative example), marks it as user-supplied and unverified, and does not infer in-game defense, damage reduction, rounding, or special mechanics. A formula becomes a trustworthy game calculation only after its source, patch, test conditions, and measured behavior have been independently documented.


## Matchup damage mitigation (patch-aware preview)

The matchup endpoint supports physical, magic and true damage. For physical or magic damage, the current preview applies:

1. Target defense reduction: subtract flat defense reduction, then apply percentage defense reduction.
2. Attacker penetration: apply percentage penetration, then subtract flat penetration.
3. Clamp effective defense at the current documented lower bound of -60.
4. Apply the defense multiplier: `120 / (120 + effective_defense)`.
5. Apply the defender's separately entered general damage-reduction percentage.

The combined expression is:

`final = raw × 120/(120 + effective_defense) × (1 - damage_reduction)`

True damage bypasses defense in this preview. It does not apply the separately entered general damage-reduction field because true-damage interactions with specific effects need their own verified handling.

References used for the model:
- MLBBHub damage calculator, which documents the 120 constant and penetration order, with an in-game attribute-panel check: https://mlbbhub.com/damage-calculator
- Mobile Legends Wiki, Physical Defense and Defense Reduction: https://mobile-legends.fandom.com/wiki/Physical_defense and https://mobile-legends.fandom.com/wiki/Defense_reduction
- Mobile Legends Wiki, Damage Reduction: https://mobile-legends.fandom.com/wiki/Damage_reduction

The API only calculates a numeric post-mitigation result for a skill record with exactly one supported base-damage component and at most one supported scaling term. Multi-hit or multi-component skills are not summed automatically. Blue/red buff flags and battle spells remain selectable but are not applied as numeric modifiers until patch-specific values and conditions are verified. Conditional item passives, shields, rounding and skill-specific exceptions are not included.
