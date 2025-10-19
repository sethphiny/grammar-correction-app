### Categories Checklist

Status legend: [x] Implemented, [~] Partial, [ ] Not implemented

Notes reference internal categories in `backend/services/grammar_checker.py` such as `redundancy`, `awkward_phrasing`, `punctuation`, `grammar`, `dialogue`, `capitalisation`, `tense_consistency`, `spelling`, `parallelism_concision` (experimental), `article_specificity`, `agreement`, `ambiguous_pronouns`, `dangling_clause`, `fragment`, `run_on`, `split_line`, `word_order`, `contrast`, `clarity`, `preposition`, `register`, `repetition`, `comma_splice`, `coordination`, `ellipsis`, `hyphenation`, `missing_period`, `number_style`, `possessive`, `broken_quote`, `compounds`, and `pronoun_reference`.

### 🧠 Grammar & Structure
- [x] Agreement — `agreement` category for subject–verb agreement rules.
- [x] Ambiguous pronouns — `ambiguous_pronouns` category for pronoun reference clarity.
- [x] Article / Article usage / Specificity — `article_specificity` patterns for a/an/the and specificity.
- [x] Clause (Dangling Clause) — `dangling_clause` category for dangling modifiers and misplaced clauses.
- [x] Fragment / Sentence Fragment / Formatting — `fragment` category with 10 patterns for incomplete sentences, dependent clauses, participial phrases, prepositional fragments, and relative clause fragments.
- [x] Parallelism / Concision — `parallelism_concision` category with 40+ concision patterns (wordy phrases, nominalizations, redundant intensifiers, passive voice) and 10 parallelism patterns (list verb forms, correlative conjunctions, comparison structures, mixed tenses). Marked experimental due to complexity.
- [x] Run-on risk / Layout — `run_on` category with 8 patterns for run-on sentences: comma splices (with/without transitional words), fused sentences, missing commas before coordinating conjunctions, multiple conjunctions, and very long sentences with multiple clauses.
- [x] Split line / Broken Dialogue — `split_line` category with 10 patterns for improperly split dialogue: unclosed quotes, missing commas in dialogue tags, split dialogue without em-dash, interrupted dialogue, multiple dialogue snippets, attribution splits, and missing punctuation.
- [x] Tense / Tense consistency (past/present) — `tense_consistency` patterns for intra-line shifts.
- [x] Verb phrase — `grammar` rules (e.g., "should of" → "should have").
- [x] Word order — `word_order` category with 12 patterns for word order issues: misplaced adverbs (only, just, even, also), split infinitives, frequency adverb placement, time/place order, double negatives, adjective order, question word order, and "not only...but also" constructions.

### ✍️ Style & Clarity
- [x] Awkward phrasing — `awkward_phrasing` list with concise alternatives.
- [x] Clarity — `clarity` category with 15 patterns for clarity issues: nominalization (make a decision → decide), hedging language, buried verbs, abstract language, double negatives, vague intensifiers, and unclear pronoun references. Comprehensive clarity detection implemented.
- [x] Contrast — `contrast` category with 10 patterns for contrast usage: improper contrast markers, missing punctuation with transitional words, redundant contrast markers, weak contrast expressions, incomplete contrast pairs, ambiguous "while" usage, and informal contrast structures.
- [x] Diction / Preposition — `preposition` category with 18 patterns for preposition and diction errors: time/place prepositions (on Monday, at night), common errors (interested in, depend on), affect/effect usage, redundant prepositions (off of, inside of), and "could of" → "could have" corrections. Fully implemented.
- [x] Generic — `article_specificity` category flags vague quantifiers/adjectives (e.g., "a lot of", "good/bad"), vague words (thing, stuff), and weak descriptors (6 patterns implemented).
- [x] Redundancy — `redundancy` extensive tautologies and duplicates.
- [x] Register — `register` category with 20 patterns for formality/register issues: contractions in formal writing, first/second person in academic text, casual intensifiers, slang/colloquialisms, informal phrasal verbs, text-speak, casual connectors, rhetorical questions, emphatic repetition, and exclamation marks. Comprehensive formality detection implemented.
- [x] Repetition — `repetition` category with 12 patterns for repeated words/phrases: immediate word repetition, repeated articles/conjunctions, word repetition within close proximity, repeated phrases, overused transitions, repeated sentence structures, stuttering effects, repeated intensifiers, and word repetition across sentences. Comprehensive repetition detection implemented.
- [x] Tautology — Covered under `redundancy` list.
- [x] Wordiness — Covered by `awkward_phrasing` and `parallelism_concision`.

### 🔤 Punctuation & Mechanics
- [x] Capitalisation (sentence start / common noun / after semicolon) — `capitalisation` patterns (sentence start, days/months, pronoun "I"); semicolon-specific capitalization not explicit.
- [x] Comma splice — `comma_splice` category with 10 patterns for comma splice detection: classic independent clause splices, splices with transitional adverbs (however, therefore), splices with "then", demonstrative pronouns, expletive constructions, possessive pronouns, transitional phrases, and serial comma splices. Comprehensive comma splice detection.
- [x] Coordination (spelled "Coordination") — `coordination` category with 10 patterns for coordinating conjunction usage: missing commas before FANBOYS with independent clauses, unnecessary commas with compound predicates, Oxford comma usage, overuse of "and", sentence starters, parallel structure in coordination, correlative conjunctions, and list coordination. Comprehensive coordination checks.
- [x] Dialogue punctuation / order / quotation setup — `dialogue` patterns (comma inside quotes, tag casing, basic setups).
- [x] Ellipsis — `ellipsis` category with 8 patterns for ellipsis usage: four-dot errors, two-dot errors, spacing issues, informal sentence starts, overuse detection, redundant punctuation, style advisory for formal writing, and spaced dots. Comprehensive ellipsis validation implemented.
- [x] Hyphenation — `hyphenation` category with 10 patterns for hyphenation rules: compound adjectives before nouns, -ly adverb errors, compound numbers, fractions, prefix vowel collisions, self/ex prefixes, age expressions, number+noun compounds, and suspended hyphenation. Comprehensive hyphenation checking implemented.
- [x] Missing period — `missing_period` category with 8 patterns for missing end punctuation: capital after comma, missing periods between sentences, comma instead of period, missing question marks, missing exclamation marks, and abbreviation periods. Comprehensive end punctuation detection.
- [x] Number style — `number_style` category with 10 patterns for number formatting: sentence-start digits, small number spelling, large number commas, inconsistent formatting, percentage symbols, ordinal numbers, currency decimals, leading zeros, Roman numerals, and time format consistency. Comprehensive number style checking.
- [x] Possessive — `possessive` category with 12 patterns for possessive forms: its/it's confusion, your/you're errors, their/they're/there confusion, whose/who's errors, plural possessives, inanimate object possessives, double possessives, and apostrophe errors. Comprehensive possessive checking.
- [x] Quote / Broken Quote — `broken_quote` category with 8 patterns for unmatched quotes: unclosed quotes, mixed quote styles, duplicate quotes, missing quotes in dialogue, unnecessary quotes, smart/straight quote mixing, and nested quote errors. Comprehensive quote validation implemented.
- [x] Quote punctuation — Ensures comma placement inside quotes with tags.
- [x] Spacing — `punctuation` patterns for spaces around punctuation and brackets.

### ✅ Spelling & Usage
- [x] Compounds — `compounds` category with 50+ compound word rules: one-word compounds (anybody, homework), two-word corrections (a lot, at least), and hyphenated compounds (self-esteem, decision-making, up-to-date). Comprehensive compound word detection.
- [x] Grammar — `grammar` patterns (double negatives, verb forms, affect/effect hints, there/their cue).
- [x] Pronoun reference — `pronoun_reference` category with 15 patterns for pronoun reference resolution: vague "it"/"this"/"that", pronoun-antecedent agreement, who/whom case, subject/object case errors, reflexive pronouns, that/which usage, their/there/they're confusion, capitalization of "I", and pronoun shifts. Comprehensive pronoun reference checking implemented.
- [x] Spelling — `common_misspellings` list.

### Notes
- Passive voice detection requires spaCy `en_core_web_sm`; when unavailable, passive checks are skipped.
- Many style items are heuristic; the `parallelism_concision` category is explicitly marked experimental.


