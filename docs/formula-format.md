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
