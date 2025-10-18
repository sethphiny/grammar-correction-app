### Categories Checklist

Status legend: [x] Implemented, [~] Partial, [ ] Not implemented

Notes reference internal categories in `backend/services/grammar_checker.py` such as `redundancy`, `awkward_phrasing`, `punctuation`, `grammar`, `dialogue`, `capitalisation`, `tense_consistency`, `spelling`, `parallelism_concision` (experimental), `article_specificity`, `agreement`, and `ambiguous_pronouns`.

### 🧠 Grammar & Structure
- [x] Agreement — `agreement` category for subject–verb agreement rules.
- [x] Ambiguous pronouns — `ambiguous_pronouns` category for pronoun reference clarity.
- [x] Article / Article usage / Specificity — `article_specificity` patterns for a/an/the and specificity.
- [ ] Clause (Dangling Clause) — No dangling modifier detection.
- [ ] Fragment / Sentence Fragment / Formatting — No fragment detection.
- [~] Parallelism / Concision — `parallelism_concision` experimental rules for wordiness/structure.
- [ ] Run-on risk / Layout — No run-on sentence detection.
- [ ] Split line / Broken Dialogue — No split-line detector; see dialogue punctuation below.
- [x] Tense / Tense consistency (past/present) — `tense_consistency` patterns for intra-line shifts.
- [x] Verb phrase — `grammar` rules (e.g., “should of” → “should have”).
- [ ] Word order — No word-order reordering rules.

### ✍️ Style & Clarity
- [x] Awkward phrasing — `awkward_phrasing` list with concise alternatives.
- [~] Clarity — Passive voice flagged via spaCy (if available) and vague terms hints.
- [ ] Contrast — No contrast usage checks.
- [~] Diction / Preposition — Some replacements (e.g., “due to the fact” → “because”, affect/effect); no general preposition audits.
- [~] Generic — Flags vague quantifiers/adjectives (e.g., “a lot of”, “good/bad”).
- [x] Redundancy — `redundancy` extensive tautologies and duplicates.
- [ ] Register — No formality/register checks.
- [ ] Repetition — No repeated-word/phrase detector.
- [x] Tautology — Covered under `redundancy` list.
- [x] Wordiness — Covered by `awkward_phrasing` and `parallelism_concision`.

### 🔤 Punctuation & Mechanics
- [x] Capitalisation (sentence start / common noun / after semicolon) — `capitalisation` patterns (sentence start, days/months, pronoun “I”); semicolon-specific capitalization not explicit.
- [ ] Comma splice — No explicit comma-splice detection.
- [ ] Coordination (spelled “Coordination”) — No coordination conjunction checks.
- [x] Dialogue punctuation / order / quotation setup — `dialogue` patterns (comma inside quotes, tag casing, basic setups).
- [~] Ellipsis — Special-cased to avoid false positives; no validation of correct ellipsis usage.
- [~] Hyphenation — Normalizes hyphenated contractions in sanitizer; no general hyphenation rules.
- [ ] Missing period — Not checked.
- [ ] Number style — Not checked.
- [ ] Possessive — Not checked.
- [~] Quote / Broken Quote — Dialogue-specific checks; no generic unmatched quote validator.
- [x] Quote punctuation — Ensures comma placement inside quotes with tags.
- [x] Spacing — `punctuation` patterns for spaces around punctuation and brackets.

### ✅ Spelling & Usage
- [ ] Compounds — Not checked.
- [x] Grammar — `grammar` patterns (double negatives, verb forms, affect/effect hints, there/their cue).
- [~] Pronoun reference — Capitalization of “I” and a narrow there/their cue; no broad reference resolution.
- [ ] Pronunciation (if meant as “Pronounce,” clarify intent) — Not applicable.
- [x] Spelling — `common_misspellings` list.

### Notes
- Passive voice detection requires spaCy `en_core_web_sm`; when unavailable, passive checks are skipped.
- Many style items are heuristic; the `parallelism_concision` category is explicitly marked experimental.


