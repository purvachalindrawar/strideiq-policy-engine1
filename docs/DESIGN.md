# DESIGN.md

## Rule representation / DSL
- Simple JSON-based condition objects: { field, operator, value } combined with AND/OR.
- Example: { "conds": [{"field":"amount","op":">","value":200}], "actions": ["flag"] }

## Precedence / conflict resolution
- Rules have an explicit integer "priority" (higher overrides lower).
- Tie-breaker: more specific rule (more conditions) wins.

## Caching / Scaling
- Use read-through cache for active policy set.
- Version policies by `policy_version` to ensure consistent evaluation.

## Tradeoffs & Limitations
- Simple DSL (limited operators). Extensible later.
