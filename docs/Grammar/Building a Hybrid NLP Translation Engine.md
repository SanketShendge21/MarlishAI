# **Architecting Marlish.AI: A 7-Layer Hybrid NLP and ML Framework for Code-Mixed Indian Conversational Translation**

The engineering of a real-time translation engine capable of interpreting noisy, code-mixed Indian conversational text requires a fundamental departure from traditional machine translation models. Pure neural architectures frequently fail when confronted with the morphological richness, inconsistent phonetic transliterations, and deep cultural slang embedded in Hinglish and Marlish.1 Conversely, strict rule-based systems are too brittle to accommodate the dynamic evolution of internet linguistics.3 The optimal solution is a 7-layer hybrid architecture that systematically processes input through normalization, tokenization, phrase matching, context resolution, grammar repair, machine learning enhancement, and output beautification.4 The following research details the architectural blueprint, linguistic heuristics, and algorithmic logic required to construct this system.

## **Language Grammar Rules**

The foundational challenge in translating Indian languages to English lies in managing profound syntactic divergence. The contrastive grammar between Hindi, Marathi, and English necessitates robust, programmable rules rather than abstract linguistic theory. Implementing these rules within the Grammar Repair and Context Resolution layers is critical for transforming raw conversational input into fluent English.

The most prominent syntactic difference is word order. English operates on a Subject-Verb-Object (SVO) framework, whereas Hindi, Marathi, Hinglish, and Marlish natively employ a Subject-Object-Verb (SOV) structure.6 In an SVO language, the verb acts as the medial pivot, driving the action forward. In SOV languages, the verb is positioned at the absolute end of the clause, anchoring the entire semantic payload.8 Consequently, any engineering approach must prioritize dependency parsing to isolate the terminal verb cluster and relocate it to the post-subject position.

Beyond word order, verb conjugation and tense formation present severe computational complexities. Hindi and Marathi are highly inflected languages, meaning verbs change forms based on tense, gender, number, and person.9 English relies predominantly on auxiliary verbs (is, am, are, was, were, will) to convey these temporal and aspectual shifts.

The tables below map the core grammatical behaviors across the target languages, providing deterministic transformation logic for the translation engine.

| Grammatical Feature | Hindi / Hinglish Rule | Marathi / Marlish Rule | English Rule | Engineering Transformation Logic |
| :---- | :---- | :---- | :---- | :---- |
| **Sentence Structure** | Subject-Object-Verb (SOV). Example: *Main ghar ja raha hu.* 11 | Subject-Object-Verb (SOV). Example: *Mi ghari jaat aahe.* 7 | Subject-Verb-Object (SVO). Example: *I am going home.* | Parse SOV input, extract the terminal Verb Phrase (VP), and insert it immediately after the initial Subject Noun Phrase (NP). |
| **Simple Present** | Root \+ *ta/te/ti* \+ *hai/hu*. Example: *Khelta hai* 12 | Root \+ *to/te/taat*. Example: *Khelto* 13 | Base Verb (+s/es). Example: *Plays* | Map terminal indicative suffixes directly to the English simple present base verb. Detect gender/number to apply pluralization. |
| **Present Continuous** | Root \+ *raha/rahi/rahe* \+ *hai/hu*. Example: *Khel raha hai* | Root \+ *at* \+ *aahe*. Example: *Khelat aahe* 13 | *is/am/are* \+ Verb-ing. Example: *is playing* | Detect auxiliary clusters (*raha hai* / *at aahe*), map to *is/am/are*, and apply the gerund *\-ing* suffix to the English root. |
| **Simple Past** | Root \+ *ya/aa/ee/e*. Example: *Khela* / *Gaya* 14 | Root \+ *la/li/le*. Example: *Khelala* / *Gela* 13 | Verb-ed or irregular past. Example: *Played* / *Went* | Identify past tense morphological markers and map to the English simple past dictionary format. |
| **Future Tense** | Root \+ *unga/ega/egi*. Example: *Khelega* 14 | Root \+ *in/el/til*. Example: *Khelil* 13 | *will* \+ Base Verb. Example: *will play* | Extract future tense suffixes and insert the auxiliary modal *will* before the translated English root verb. |
| **Negation Placement** | *Nahi* / *Na* placed immediately before the verb. Example: *Nahi khelta* | *Nahi* / *Nako* placed as a post-verbal suffix or particle. Example: *Khelat nahi* | *do not* / *does not* placed before the verb. Example: *does not play* | Identify negation tokens, extract them, and insert the appropriate *do/does/did not* construct before the English main verb. |
| **Question Formation** | *Kya* / *Kyu* / *Kaise* placed in-situ (before object or verb). Example: *Tu kya kar raha hai?* | *Kay* / *Kasa* placed in-situ. Example: *Tu kay karat aahes?* | Wh-word moved to sentence front \+ auxiliary inversion. Example: *What are you doing?* | Extract in-situ interrogative tokens, move them to index 0, and invert the subject and auxiliary verb in the SVO output. |
| **Gender Agreement** | Verbs and adjectives inflect for Masculine (*\-aa*) and Feminine (*\-ee*). 9 | Verbs and adjectives inflect for Masculine, Feminine, and Neuter. 7 | Gender-neutral verbs and adjectives. (Except third-person pronouns). | Strip gender inflection suffixes from Indic verbs and adjectives during translation, as English lacks verb gender agreement. |
| **Adposition Usage** | Postpositions (attached after nouns). Example: *Ghar mein* | Postpositions. Example: *Gharat* (Ghar \+ aat) 15 | Prepositions (attached before nouns). Example: *In the house* | Identify postpositional particles, extract them, translate to English prepositions, and place them *before* the associated Noun Phrase. 15 |

To convert an Indian SOV structure into an English SVO structure reliably, the engine must employ chunking and Part-of-Speech (POS) tagging. For example, the Hinglish input "main ghar ja raha hu" must be tokenized and tagged: \[main\] (Pronoun/Subject) \+ \[ghar\] (Noun/Object) \+ \[ja raha hu\] (Verb Phrase/Action). The programmable transformation rule executes a structural swap, resulting in \`\` \+ \[Verb Phrase/Action\] \+ \[Noun/Object\], mapping exactly to "I am going home." Similarly, for Marathi, "mi ghari jaat aahe" is parsed as \[mi\] (Subject) \+ \[ghari\] (Object \+ Postposition) \+ \[jaat aahe\] (Verb Phrase), which translates via the same logic to "I am going to the house."

## **Hinglish/Marlish Behavior**

Standard NMT models fail spectacularly when processing Hinglish and Marlish because these are not standardized dialects; they are highly fluid, code-mixed communicative modalities born out of digital convenience.16 Users operating in these formats do not adhere to formal linguistic constraints, resulting in a chaotic blend of transliteration paradigms, phonetic spellings, aggressive abbreviations, and intra-sentential language switching.1 To achieve high-fidelity translations, the Tokenization and Normalization layers must systematically decode this specific behavior.

Transliteration from Devanagari to the Latin script introduces immense phonetic variation. The Devanagari script is strictly phonetic, but the Latin alphabet is not, leading users to improvise spellings based on auditory perception. Vowel dropping, specifically schwa deletion, is highly prevalent.18 Words that end with an inherent vowel sound in written Hindi are routinely truncated in Hinglish. Furthermore, users exhibit varying preferences for vowel representation; the long "ee" sound is transcribed interchangeably as "i", "ee", or even "y".19 Consequently, the Hindi word for "how" can appear as "kaise", "kese", "kese", or "kse".

This phonetic instability is compounded by extreme abbreviative behavior optimized for rapid typing. Chat linguistics routinely omit vowels entirely from high-frequency functional words. The verb "kar" (to do) becomes "kr", the auxiliary "hai" (is) becomes "h", and the continuous marker "raha" becomes "rha".20 The translation engine cannot rely on static dictionary lookups to resolve these tokens; it requires an active phonetic resolution algorithm.

Code-mixing behavior in Hinglish and Marlish is not merely lexical borrowing; it is deep structural integration.1 A user might attach a Hindi postposition to an English noun, or apply an English plural suffix to a Marathi root.

| Behavioral Anomaly | Hinglish / Marlish Example | Canonical Meaning | NLP Engine Handling Strategy |
| :---- | :---- | :---- | :---- |
| **Vowel Omission (Short-hand)** | kr, h, rha, bht | kar, hai, raha, bohot | Implement a high-frequency abbreviation mapping dictionary in the Tokenization Layer prior to syntactic analysis. |
| **Phonetic Vowel Substitution** | kese, kaise, kse | kaise (how) | Utilize Soundex or Double Metaphone algorithms to map acoustically similar strings to a canonical root. 22 |
| **Intra-sentential Code-Switching** | aaj ka task complete krna h | Today's task needs to be completed | Deploy a language identification classifier per token. Tag aaj ka (Hindi), task complete (English), krna h (Hinglish short-hand). |
| **Morphological Hybridization** | friends log / tension mat le | Group of friends / Do not worry | Separate native roots from foreign suffixes. Treat log as a plural marker for the English noun friends. 23 |
| **Contextual Slang Integration** | scene kya hai / bhaari kaam | What is the plan? / Epic work | Process via the Phrase Matching layer to prevent literal SOV-SVO translation. Maps whole bigrams/trigrams to English idioms. 1 |

The meaning of a code-mixed sentence frequently diverges entirely from its literal translation due to semantic shifts. The Hinglish input "kya kar raha hai" translates literally to "What doing is?", but structurally means "What are you doing?". The omission of the pronoun "tu" (you) is a common pro-drop behavior in conversational Indian dialects. The engine must computationally infer the missing subject from the verb ending (raha hai implies second or third-person singular) and inject the missing "you" into the English output. Similarly, "scene kya hai" literally means "What is the visual setting?", but functions sociolinguistically as "What's the plan?".24 The Phrase Matching Layer must intercept these specific bigrams before they reach the literal translation module.

## **Ambiguity Resolution**

Ambiguity resolution is a critical operational requirement within the Context Resolution Layer. In highly ambiguous languages like Hindi and Marathi, solitary lexical tokens frequently harbor multiple, mutually exclusive meanings. The absence of diacritics in romanized Hinglish and Marlish further exacerbates this issue.25 To extract the correct semantic intent, the engine must employ Word Sense Disambiguation (WSD) techniques utilizing context-based rules, positional heuristics, and syntactic dependency parsing.26

The temporal adverb "kal" exemplifies profound lexical ambiguity, as it serves as the signifier for both "yesterday" and "tomorrow".28 A literal translation engine operating on isolated unigrams cannot resolve this. The Context Resolution Layer must implement a look-ahead and look-behind heuristic that scans the terminal verb phrase of the SOV structure. If the dependency parser detects past-tense auxiliary markers such as tha, thi, the, or gaya, the WSD module deterministically maps "kal" to "yesterday".29 Conversely, if the terminal verbs exhibit future-tense markers like ga, gi, ge, jayega, or imperative/intent markers like milte hai (let us meet), "kal" is mapped to "tomorrow."

The term "bhai" requires relational versus vocative disambiguation. Literally translating to "brother," its conversational utility has shifted dramatically. In informal chat, it acts as a vocative particle analogous to "bro," "dude," or "mate." The disambiguation rule logic dictates that if "bhai" is preceded by a possessive pronoun (mera bhai \- my brother) or acts as the strict syntactic subject of an action (bhai ne khana khaya \- brother ate food), it resolves to "brother." However, if "bhai" operates as an isolated token at the absolute beginning or end of a sentence boundary, lacking a dependency link to the core verb (kya kar raha hai bhai), it resolves to the conversational "bro."

Borrowing from English, the word "scene" requires domain-specific contextual disambiguation. When transliterated into Hinglish, "scene" rarely refers to a theatrical setting. It has been repurposed as a slang term for "plan," "situation," or "event."

| Ambiguous Token | Contextual Trigger / Heuristic Rule | Disambiguated Output | Engineering Implementation Logic |
| :---- | :---- | :---- | :---- |
| **kal** | POS Tag of terminal verb \= PAST (e.g., tha, ya) | yesterday | if sentence.terminal\_verb.tense \== 'PAST': return 'yesterday' |
| **kal** | POS Tag of terminal verb \= FUTURE (e.g., ga, ge) | tomorrow | if sentence.terminal\_verb.tense \== 'FUTURE' or 'IMPERATIVE': return 'tomorrow' |
| **bhai** | Preceded by possessive pronoun (mera, uska) | brother | if preceding\_token.pos \== 'PRP$': return 'brother' |
| **bhai** | Position \= Index 0 or Index \-1; No direct verb dependency | bro / dude | if token.is\_vocative() or token.position in \[start, end\]: return 'bro' |
| **scene** | Collocated with interrogatives (kya) or temporal markers (raat ko) | plan / situation | if bigram matches \['scene', 'kya'\] or \['kya', 'scene'\]: return 'plan' |
| **accha** | Terminal position with interrogative punctuation (?) | is that so? / really? | if token.position \== end and punctuation \== '?': return 'really?' |
| **accha** | Preceding a noun phrase | good / nice | if following\_token.pos \== 'NOUN': return 'good' |

Implementing these rules requires a hybrid approach utilizing both rule-based Part-of-Speech (POS) tagging and n-gram statistical probability.30 By analyzing the bigram and trigram patterns surrounding the ambiguous token, the engine calculates the conditional probability of a specific definition, ensuring the final English sentence reflects the user's authentic intent.

## **Sentence Transformation Rules**

The transition from Indian conversational inputs to natural English outputs mandates severe structural reordering. The Sentence Transformation Rules govern the mechanics of converting the native Subject-Object-Verb (SOV) topology into the target Subject-Verb-Object (SVO) topology. This process cannot rely on naive word-to-word translation; it requires robust syntactic chunking and dependency parsing to reconstruct the sentence architecture dynamically.31

The fundamental transformation logic dictates the extraction and repositioning of the Verb Phrase (VP). In an input such as "I home go" (generated from a direct lexical mapping of "Main ghar jaata hu"), the parser identifies "I" as the Subject Noun Phrase (NP), "home" as the Object Noun Phrase (NP), and "go" as the Verb Phrase (VP). The transformation engine executes a structural swap, shifting the terminal VP to the medial position, rendering the syntactically valid SVO output: "I go home."

Crucially, this transformation must also address the conversion of postpositions to prepositions. Indian languages utilize markers appended after the noun to indicate spatial, temporal, or logical relationships (e.g., *mein* for in, *par* for on, *se* for from).15 The engine must decouple these postpositional markers, translate them into English prepositions, and prepend them to the relevant noun phrase. For example, the Hinglish phrase "table par" (table on) must be chunked, inverted, and output as "on the table." Marathi utilizes bound morphemes (suffixes) rather than distinct postpositional words; "gharat" means "in the house" (ghar \+ aat).15 The NLP tokenizer must split the root "ghar" from the locative suffix "aat", process the morphological translation, and prepend the English preposition "in" to the translated noun.

| Indian Linguistic Structure | Example (Hinglish/Marlish) | Naive Literal Translation | Programmable SVO Restructuring Logic | Clean English Output |
| :---- | :---- | :---- | :---- | :---- |
| **\[Object\]\[Verb\]** | Main office ja raha hu | I office going am. | Move terminal VP (am going) to post-subject position. | I am going to the office. |
| **\[Noun\]\[Postposition\]** | Delhi se | Delhi from. | Extract postposition (se), translate to preposition (from), prepend to NP. | from Delhi. |
| \*\*\*\* | Gharat (Ghar \+ aat) | House-in. | Morphologically split noun and locative suffix. Prepend preposition. | in the house. |
| **\[Adverb\]\[Verb\]** | Jaldi aao | Quickly come. | Invert sequence for imperative phrases: \[Verb\]\[Adverb\]. | Come quickly. |
| **\[Verb\]** | Kahan hai? | Where is? | Apply Wh-movement: \[Aux Verb\]. | Where are you? |

Handling pro-drop behavior during this transformation is mathematically complex. Indian chat frequently omits the subject entirely, relying on context. If a user types "kahan hai?" (where is?), the engine detects an incomplete syntax tree missing a subject NP. Based on conversational heuristics, interrogatives lacking a subject default to the second person. The engine automatically injects the pronoun "you" and the corresponding plural auxiliary "are" to fulfill the English SVO requirement, outputting "where are you?" rather than the broken "where is?"

## **Grammar Repair Templates**

Conversational data is inherently noisy and routinely defies formal syntactic structures. Users generate fragmented clauses, misaligned auxiliary chains, and grammatically incomplete thoughts. To prevent the translation engine from outputting literal, broken English, the Grammar Repair Layer applies specific rule-based templates. This layer acts as a deterministic safety net, utilizing pattern matching to intercept malformed outputs and map them to clean, pre-verified English grammatical templates.33

When the translation pipeline produces an intermediate string that violates standard English grammar rules, the repair module matches the anomaly against a repository of known error patterns. Once a match is identified, the elements of the broken sentence are slotted into a corrected structural mold.

| Anomalous Input Pattern | Recognized Linguistic Error | Repair Template Mapping | Raw Output Example | Corrected English Translation |
| :---- | :---- | :---- | :---- | :---- |
| \[Pronoun\]\[Aux Verb\] | Inverted Interrogative Syntax | \[Aux Verb\]\[Pronoun\] | "you where are" | "Where are you?" |
| \[Pronoun\]\[Noun\]\[Verb\] | SOV failure / Missing Preposition | \[Pronoun\]\[Aux Verb\]\[Verb\]\[Preposition\]\[Noun\] | "I home go" | "I am going home." |
| \[Verb\]\[Aux\] | Missing Imperative Subject | Let's \[Verb\] | "kal milte hai" | "Let's meet tomorrow." |
| \[Noun\]\[Verb\] | In-situ Interrogative Failure | \[Verb\]\[Article\]\[Noun\] | "plan kya hai" | "What is the plan?" |
| \[Verb\]\[Negation\] | Improper Negation Placement | \[Pronoun\]\[Verb\] | "jaana nahi" | "I will not go." / "Do not go." |
| \[Adjective\]\[Noun\]\[Hai\] | Missing Copula Subject | \[Article\]\[Noun\] is \[Adjective\] | "mast movie hai" | "The movie is awesome." |

The engineering logic driving this layer relies on highly efficient Regular Expressions (Regex) and Conditional Random Fields (CRF) for pattern detection.35 For instance, if the system detects the sequence \[Pronoun\]\[Aux Verb\], a simple rule logic is triggered:

Python

if sequence.matches(PRP \+ WP \+ VBP):  
    reorder\_to(WP \+ VBP \+ PRP)  
    append("?")

This ensures that "you what doing" is instantly repaired to "what are you doing?". Reusable templates drastically reduce computational overhead compared to passing every fractured sentence through a heavy neural network for grammar correction.5 By employing template substitution, the system guarantees high-speed, deterministic repair of the most common conversational errors encountered in Indian chat environments.

## **Typo Handling Rules**

The informal nature of texting guarantees a continuous influx of typographical errors, repeated characters, and phonetic misspellings. If these errors reach the semantic processing layers, they will be classified as out-of-vocabulary (OOV) tokens, causing translation failure.36 The Typo Handling module within the Normalization Layer executes critical pre-processing to sanitize the data stream before tokenization.

The most prevalent noise in chat text is character repetition, used stylistically to convey emotion or emphasis (e.g., "kyaaa", "pleeease", "jaaaldii").37 Standard dictionary lookups fail on these tokens. The engine must implement a strict normalization algorithm that evaluates the length of the string and the position of the repeating characters to truncate them safely without destroying valid words.37

**Rule Logic for Repeated Characters:**

1. **Length Validation:** If the total string length is less than 4 characters (e.g., "hmm", "yee"), truncate all repeating characters to a single instance. Short strings with repeats are almost universally abbreviations or interjections.  
2. **Positional Truncation:** If the string length exceeds 4 characters:  
   * If the repetition occurs at the absolute beginning or the absolute end of the string (e.g., "rhaaa"), truncate the repeated sequence to a single character.  
   * If the repetition occurs in the middle of the string (e.g., "pleeease"), truncate the sequence to exactly two characters.37  
3. **Dictionary Validation:** Pass the truncated string through an in-vocabulary (IV) check. If "pleease" becomes "please", the dictionary validates it. If "jaaaaldi" becomes "jaaldi", it fails the dictionary check and triggers the secondary truncation phase, reducing the double characters to a single character ("jaldi").37

| Typo/Noise Category | Chat Input Example | Normalization Rule / Algorithm | Cleaned Output |
| :---- | :---- | :---- | :---- |
| **Trailing Repetitions** | kyaaa, rhaaa | regex: /(.)\\1+$/ ![][image1] Truncate to 1 character. | kya, rha |
| **Internal Repetitions** | ghaaari, bhaaaari | regex: /(.)\\1{2,}/ ![][image1] Truncate to 2 characters, test dictionary. | ghaari ![][image1] ghari |
| **Phonetic Vowel Swaps** | ghri, kaise, kese | Apply Soundex/Double Metaphone to match phonetic root. 22 | ghari, kaise |
| **Missing Vowels** | tmrw, plz, bht | Map against a static abbreviation lookup dictionary. | tomorrow, please, bohot |

Phonetic typos demand a different algorithmic approach. Because users spell words based on auditory approximations rather than orthographic rules, the system must utilize algorithms like Levenshtein distance combined with phonetic hashing.38 If a user types "ghri" instead of "ghari", the system calculates the edit distance. If the distance is low and the phonetic hash matches the canonical Hinglish dictionary entry, the token is successfully replaced. This ensures that the engine processes standardized text, drastically reducing perplexity in the machine learning models downstream.39

## **Slang Mapping**

A core objective of Marlish.AI is understanding what the user means, rather than performing a sterile, literal translation. Code-mixed Indian chat relies heavily on cultural slang that carries nuanced sociological connotations.16 The Slang Mapping protocol operates within the Phrase Matching Layer to intercept known idioms and apply context-aware English equivalents that preserve the conversational tone.

The system utilizes a dedicated slang dictionary structured as key-value pairs, mapped against specific conversational triggers. Direct translation of these terms strips them of their intended meaning. For example, "jugaad" literally translates to "provision" or "arrangement," but culturally means a "hack," "workaround," or "quick fix".40

A critical architectural decision involves determining *when* to retain slang and *when* to normalize it. This is dictated by the desired output tone. Since the engine is designed for informal chat, it must avoid over-formalizing the text. The term "bro" (derived from the vocative use of "bhai" or "bhau") should be retained in the output to preserve the casual atmosphere, rather than translating it strictly to "brother".41

| Original Slang Token | Literal Translation | Conversational English Mapping | Implementation Logic / Context Trigger |
| :---- | :---- | :---- | :---- |
| bhai / bhau | Brother | bro / dude | Retain as slang if used as a vocative particle at sentence boundaries. 41 |
| scene | Visual setting | plan / situation | Map to "plan" if interrogative markers (kya) are present. 1 |
| timepass | Passing time | casual fun / killing time | Map idiomatically based on verb collocation. |
| jugaad | Arrangement | workaround / hack | Direct dictionary substitution for informal contexts. 40 |
| jhakaas / bhaari | Superb / Heavy | awesome / epic | Map Marathi adjectives directly to casual English equivalents. 42 |
| pakka | Cooked / Solid | for sure / definitely | Map as an adverbial confirmation token. 41 |

The rule logic dictates that if a slang term is identified, the system bypasses the neural translation generation for that specific phrase.

Python

if phrase in slang\_dictionary:  
    output\_token \= slang\_dictionary\[phrase\].get\_informal\_translation()  
    bypass\_nmt(phrase)

This precise mapping guarantees that the vibrant, expressive nature of Hinglish and Marlish is accurately conveyed in the final English output, avoiding the robotic dissonance characteristic of legacy translation engines.

## **Beautification Rules**

The Output Beautification Layer acts as the final polishing mechanism before the translated string is presented to the user. Raw translations, even when grammatically perfect, often lack the fluidity and rhythm of natural human conversation.43 By applying post-processing linguistic rules, the engine injects a casual tone, corrects capitalization, and systematically restores appropriate punctuation.44

The most effective method for converting robotic text into conversational English is the systemic application of contraction rules.45 In verbal communication, native speakers rarely enunciate full auxiliary phrases. The beautification algorithm scans the finalized English string and applies a regex-based substitution protocol to contract recognized noun-auxiliary and verb-negation pairs.

| Raw Structural Output | Robotic Translation | Applied Beautification Rule | Conversational English Output |
| :---- | :---- | :---- | :---- |
| \[Noun\]\[is\]\[Article\]\[Noun\] | "What is the plan?" | Apply contraction: what is ![][image1] what's | "What's the plan?" |
| \[Pronoun\]\[Not\]\[Verb\] | "Do not worry." | Apply contraction: do not ![][image1] don't | "Don't worry." |
| \[Pronoun\]\[Verb\] | "I will go." | Apply contraction: I will ![][image1] I'll | "I'll go." |
| \[Vocative\]\[Phrase\] | "Bro what is the plan" | Insert vocative comma separator. | "Bro, what's the plan?" |
| \[Interrogative\]\[Phrase\] | "Where are you" | Detect Wh-word, append ? terminal punctuation. | "Where are you?" |

Punctuation restoration is equally critical. Code-mixed chat inputs generally lack terminal punctuation. The beautification engine utilizes syntactic cues to deduce the sentence type. If the sentence initiates with an interrogative pronoun (Who, What, Where, When, Why, How) or an inverted auxiliary (Is, Are, Do, Does), the rule logic automatically appends a question mark ?.47 If the sentence begins with an imperative verb ("Tell me," "Come here"), it appends a period .. Furthermore, when the system detects a vocative slang token ("bro," "dude") at the beginning of the string, it inserts a comma immediately following the token to enforce natural pacing. These targeted heuristic improvements ensure the final output mimics authentic human texting behavior.

## **Rule Priority Strategy**

A highly effective translation engine cannot rely solely on deterministic rules or entirely on probabilistic machine learning; it must leverage a hybrid architecture.4 Rule-based systems provide absolute structural accuracy and precision for known grammatical patterns but fail when encountering novel linguistic constructions. Conversely, Neural Machine Translation (NMT) models excel at contextual fluency but hallucinate wildly when processing the chaotic, low-resource inputs typical of Hinglish and Marlish.4 The Rule Priority Strategy defines the hierarchical execution and conflict resolution parameters between these systems.

To orchestrate this, the engine employs a tiered prioritization matrix driven by confidence scoring:

1. **Tier 1: Explicit Dictionary & Phrase Mapping (Highest Priority).**  
   Hardcoded rules for slang, abbreviations, and fixed idiomatic expressions supersede all other logic. If the input contains "scene kya hai," the system immediately maps this to "what's the plan" and bypasses the neural network. This prevents the ML model from attempting a literal translation.  
2. **Tier 2: Structural Grammar Rules (Secondary Priority).** The deterministic SOV-to-SVO restructuring algorithms and grammar repair templates form the rigid backbone of the translation. The system mathematically guarantees that the subject, verb, and object are positioned correctly before applying any probabilistic generation.49  
3. **Tier 3: ML Contextual Enhancement (Tertiary Priority).**  
   The neural layer is engaged to handle out-of-vocabulary terms, complex multi-clause sentences, and nuanced semantic smoothing that fall outside the bounds of the hardcoded rules.

**Conflict Resolution and Confidence Scoring:** When the RBMT output and the NMT output diverge, the engine utilizes a perplexity-based confidence scoring module.49 Perplexity measures how "surprised" the neural model is by the sequence of words.

* If the NMT generates an output with high statistical confidence (low perplexity), it indicates the neural model has effectively grasped the context, and the NMT output overrides the rigid rule-based structure.51  
* If the input is highly anomalous, resulting in low neural confidence (high perplexity), the system rejects the ML output to prevent hallucination and falls back on the deterministic, safe rule-based translation.4 This recursive feedback loop guarantees operational stability in a real-time environment.

## **Implementation Notes**

Deploying Marlish.AI as a real-time, low-latency engine requires meticulous architectural pipelining. The 7 layers must execute sequentially, ensuring that each module passes sanitized, structured data to the next. Below is the technical guidance for implementing this pipeline in a production environment.

**1\. Sequential Pipeline Execution:** The engine operates strictly sequentially. Raw text is ingested into the **Normalization Layer**, where rapid regex functions and Levenshtein distance calculations normalize repeated characters and phonetic typos. The sanitized string passes to the **Tokenization and Phrase Matching Layer**, where bigram dictionaries execute ![][image2] time-complexity lookups for slang and idioms.52 The tokenized array is handed to the **Context Resolution Layer**, utilizing fast POS-taggers to disambiguate tokens like "kal." The structured data is then processed by the **Grammar Repair Layer**, applying SOV-to-SVO transformations via syntactic tree manipulation. The intermediate string is evaluated by the **ML Enhancement Layer** using the confidence scoring algorithm, and finally, the **Beautification Layer** applies regex-based contractions.

**2\. Rule Logic Example (If/Else Pattern):**

Implementing the "kal" disambiguation requires localized POS tagging.

Python

def resolve\_ambiguity(token, sentence\_tree):  
    if token \== "kal":  
        terminal\_verb \= get\_terminal\_verb(sentence\_tree)  
        if terminal\_verb.tense in:  
            return "yesterday"  
        elif terminal\_verb.tense in:  
            return "tomorrow"  
    return token

**3\. Handling Edge Cases:**

A primary edge case involves highly fragmented inputs lacking a terminal verb (e.g., "kal party mein"). The grammar repair layer must implement fallback heuristics. If no verb is detected, the engine infers a state of being and injects a copula (is/are/am). The phrase maps to the template \[In/At\]\[Noun\] ![][image1] "At the party tomorrow."

**4\. Real-Time System Constraints:** To maintain real-time responsiveness (sub-200ms latency), heavy neural models cannot be invoked for every sub-process. The architecture mandates that the Normalization, Tokenization, Phrase Matching, and Grammar Repair layers execute entirely via compiled, highly optimized rule-based algorithms (Regex, hash-maps, dependency parsing libraries). The ML Enhancement layer is only engaged for final fluency checks and complex ambiguity resolution, utilizing lightweight, quantized models tailored specifically for code-mixed inference.53 This ensures Marlish.AI translates informal chat rapidly, accurately, and with deep contextual awareness.

#### **Works cited**

1. Interpreting Hinglish Conversations | by Sayan Biswas | inspiringbrilliance \- Medium, accessed May 6, 2026, [https://medium.com/inspiredbrilliance/interpreting-hinglish-conversations-79dab7cabd47](https://medium.com/inspiredbrilliance/interpreting-hinglish-conversations-79dab7cabd47)  
2. Natural Language Processing on Hinglish | by Kopal Sharma, accessed May 6, 2026, [https://kopalsharma19.medium.com/natural-language-processing-on-hinglish-9479e1d3d339](https://kopalsharma19.medium.com/natural-language-processing-on-hinglish-9479e1d3d339)  
3. How Rule-Based Machine Translation Works: A Deep Dive, accessed May 6, 2026, [https://reverieinc.com/blog/how-rule-based-machine-translation-works-a-deep-dive/](https://reverieinc.com/blog/how-rule-based-machine-translation-works-a-deep-dive/)  
4. Hybrid Machine Translation \- Omniscien Technologies, accessed May 6, 2026, [https://omniscien.com/machine-translation/hybrid-machine-translation/](https://omniscien.com/machine-translation/hybrid-machine-translation/)  
5. Building a Multilingual Grammar Correction Model with NLP | by Vaishnavi Chavan, accessed May 6, 2026, [https://medium.com/@2021.vaishnavi.chavan/building-a-multilingual-grammar-correction-model-with-nlp-021674a1358d](https://medium.com/@2021.vaishnavi.chavan/building-a-multilingual-grammar-correction-model-with-nlp-021674a1358d)  
6. Hindi Sentence Structure: SOV Explained \- Hindi Check, accessed May 6, 2026, [https://www.hindicheck.in/blogs/hindi-sentence-structure-sov-explained](https://www.hindicheck.in/blogs/hindi-sentence-structure-sov-explained)  
7. Marathi grammar \- Wikipedia, accessed May 6, 2026, [https://en.wikipedia.org/wiki/Marathi\_grammar](https://en.wikipedia.org/wiki/Marathi_grammar)  
8. Hindi Sentence Structures Explained (SOV Format) \- Sariya, accessed May 6, 2026, [https://www.sariya.app/learn/hindi-sentence-structures](https://www.sariya.app/learn/hindi-sentence-structures)  
9. Hindi Sentence Structure And Word Order: A Complete Guide \[2025\] \- Superprof, accessed May 6, 2026, [https://www.superprof.co.in/blog/hindi-sentence-structure-and-word-order/](https://www.superprof.co.in/blog/hindi-sentence-structure-and-word-order/)  
10. Marathi Verb Forms and Tense System Rules Study Usage Impact Lit \- College Manzil, accessed May 6, 2026, [https://collegemanzil.com/study-materials/marathi-verb-forms-and-tense-system-rules-study-usage-impact-lit-fd9129c8](https://collegemanzil.com/study-materials/marathi-verb-forms-and-tense-system-rules-study-usage-impact-lit-fd9129c8)  
11. Master Hindi Basics: Essential Grammar Rules Simplified, accessed May 6, 2026, [https://www.orchidsinternationalschool.com/blog/basics-of-hindi-grammar](https://www.orchidsinternationalschool.com/blog/basics-of-hindi-grammar)  
12. Hindi grammar Lesson 1- Subject \- Object \- Verb RULE \- YouTube, accessed May 6, 2026, [https://www.youtube.com/watch?v=Tt4ALGhEm8E](https://www.youtube.com/watch?v=Tt4ALGhEm8E)  
13. Inflection rules for Marathi to English in rule based machine translation \- Semantic Scholar, accessed May 6, 2026, [https://pdfs.semanticscholar.org/72ba/61dd3c5df371cbf46eefbf27a1201229a59d.pdf](https://pdfs.semanticscholar.org/72ba/61dd3c5df371cbf46eefbf27a1201229a59d.pdf)  
14. The Basics of Hindi Verb Tenses with Examples \- Superprof, accessed May 6, 2026, [https://www.superprof.com/blog/hindi-tenses/](https://www.superprof.com/blog/hindi-tenses/)  
15. Inflection Rules for Marathi-English Translation | PDF | Preposition And Postposition \- Scribd, accessed May 6, 2026, [https://www.scribd.com/document/584661086/Inflection-rules-for-Marathi-to-English-in-rule-based-machine-translation](https://www.scribd.com/document/584661086/Inflection-rules-for-Marathi-to-English-in-rule-based-machine-translation)  
16. From Hinglish to Tanglish: How Indians Create Unique Language Blends \- TransPerfect, accessed May 6, 2026, [https://www.transperfect.com/blog/hinglish-tanglish-how-indians-create-unique-language-blends](https://www.transperfect.com/blog/hinglish-tanglish-how-indians-create-unique-language-blends)  
17. HiACC: Hinglish adult & children code-switched corpus \- PMC, accessed May 6, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12329218/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12329218/)  
18. Optimizing Transliteration for Hindi/Marathi to English Using only Two Weights \- ACL Anthology, accessed May 6, 2026, [https://aclanthology.org/W12-6103.pdf](https://aclanthology.org/W12-6103.pdf)  
19. Decoding Hinglish: How LLMs Understand Our Daily Chats | by Bholay Nath Singh, accessed May 6, 2026, [https://medium.com/@bholaynathsingh335619/decoding-hinglish-how-llms-understand-our-daily-chats-09c8d5cd77d6](https://medium.com/@bholaynathsingh335619/decoding-hinglish-how-llms-understand-our-daily-chats-09c8d5cd77d6)  
20. Texting Dictionary \- terms used by children online | Internet Matters, accessed May 6, 2026, [https://www.internetmatters.org/resources/text-dictionary/](https://www.internetmatters.org/resources/text-dictionary/)  
21. 100+ Text Abbreviations and How To Use Them \[UPDATED\] \- SlickText, accessed May 6, 2026, [https://www.slicktext.com/blog/2019/02/text-abbreviations-guide/](https://www.slicktext.com/blog/2019/02/text-abbreviations-guide/)  
22. TEXT NORMALIZATION BASED ON ERROR TYPE USING PRE-TRAINED LANGUAGE MODEL \- Purdue University Graduate School research repository, accessed May 6, 2026, [https://hammer.purdue.edu/ndownloader/files/27806907](https://hammer.purdue.edu/ndownloader/files/27806907)  
23. Hindi Slang and Youth Language You Should Know \- Indian Lingua, accessed May 6, 2026, [https://www.indianlinguabooking.in/post/hindi-slang-and-youth-language-you-should-know](https://www.indianlinguabooking.in/post/hindi-slang-and-youth-language-you-should-know)  
24. 10 Hinglish (Hindi \+ English) Phrases That Indians Lovingly Use \- Fodors Travel Guide, accessed May 6, 2026, [https://www.fodors.com/world/asia/india/experiences/news/photos/10-hinglish-hindi-english-phrases-that-indians-lovingly-use](https://www.fodors.com/world/asia/india/experiences/news/photos/10-hinglish-hindi-english-phrases-that-indians-lovingly-use)  
25. LEXICAL AMBIGUITY IN HINDI–MARATHI MACHINE TRANSLATION SYSTEM, accessed May 6, 2026, [http://prakashblog-google.blogspot.com/2008/11/lexical-ambiguity-in-hindimarathi.html](http://prakashblog-google.blogspot.com/2008/11/lexical-ambiguity-in-hindimarathi.html)  
26. The Processing of Lexical Ambiguity: Evidence from Child and Adult Greek \- PMC, accessed May 6, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10881745/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10881745/)  
27. Structural Ambiguity in Hindi \- Language in India, accessed May 6, 2026, [https://www.languageinindia.com/jan2023/madhupriyastructuralambiguityhindifinal.pdf](https://www.languageinindia.com/jan2023/madhupriyastructuralambiguityhindifinal.pdf)  
28. Hindi/Tenses \- Wikibooks, open books for an open world, accessed May 6, 2026, [https://en.wikibooks.org/wiki/Hindi/Tenses](https://en.wikibooks.org/wiki/Hindi/Tenses)  
29. Syntactic and Semantic Predictors of Tense in Hindi: An ERP Investigation \- ResearchGate, accessed May 6, 2026, [https://www.researchgate.net/publication/228659370\_Syntactic\_and\_Semantic\_Predictors\_of\_Tense\_in\_Hindi\_An\_ERP\_Investigation](https://www.researchgate.net/publication/228659370_Syntactic_and_Semantic_Predictors_of_Tense_in_Hindi_An_ERP_Investigation)  
30. Context-Based Bigram Model for POS Tagging in Hindi: A Heuristic Approach \- IDEAS/RePEc, accessed May 6, 2026, [https://ideas.repec.org/a/spr/aodasc/v11y2024i1d10.1007\_s40745-022-00434-4.html](https://ideas.repec.org/a/spr/aodasc/v11y2024i1d10.1007_s40745-022-00434-4.html)  
31. (PDF) Reordering rules for English-Hindi SMT \- ResearchGate, accessed May 6, 2026, [https://www.researchgate.net/publication/309402495\_Reordering\_rules\_for\_English-Hindi\_SMT](https://www.researchgate.net/publication/309402495_Reordering_rules_for_English-Hindi_SMT)  
32. A Domain-Restricted, Rule Based, English-Hindi Machine Translation System Based on Dependency Parsing \- CSE, IIT Bombay, accessed May 6, 2026, [https://www.cse.iitb.ac.in/\~damani/papers/icon14.pdf](https://www.cse.iitb.ac.in/~damani/papers/icon14.pdf)  
33. Grammar Checker Applications in NLP | PDF | Parsing | English Language \- Scribd, accessed May 6, 2026, [https://www.scribd.com/document/926637881/NLP-Applications-Session-3-Grammar-Check-Dr-Chetana-Gavankar](https://www.scribd.com/document/926637881/NLP-Applications-Session-3-Grammar-Check-Dr-Chetana-Gavankar)  
34. Rule-based System for Automatic Grammar Correction Using Syntactic N-grams for English Language Learning (L2) \- ACL Anthology, accessed May 6, 2026, [https://aclanthology.org/W13-3613/](https://aclanthology.org/W13-3613/)  
35. POS tagger model for Hindi Language Using Novel Rule Based Technique.pdf, accessed May 6, 2026, [https://ijaem.net/issue\_dcp/POS%20tagger%20model%20for%20Hindi%20Language%20Using%20Novel%20Rule%20Based%20Technique.pdf](https://ijaem.net/issue_dcp/POS%20tagger%20model%20for%20Hindi%20Language%20Using%20Novel%20Rule%20Based%20Technique.pdf)  
36. A normalization model for repeated letters in social media hate speech text based on rules and spelling correction \- PubMed, accessed May 6, 2026, [https://pubmed.ncbi.nlm.nih.gov/38512966/](https://pubmed.ncbi.nlm.nih.gov/38512966/)  
37. A normalization model for repeated letters in social media hate speech text based on rules and spelling correction \- PMC, accessed May 6, 2026, [https://pmc.ncbi.nlm.nih.gov/articles/PMC10956744/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10956744/)  
38. Spelling Normalization of English Student Writings \- Diva-portal.org, accessed May 6, 2026, [https://www.diva-portal.org/smash/get/diva2:1251763/FULLTEXT01.pdf](https://www.diva-portal.org/smash/get/diva2:1251763/FULLTEXT01.pdf)  
39. A normalization model for repeated letters in social media hate speech text based on rules and spelling correction \- ResearchGate, accessed May 6, 2026, [https://www.researchgate.net/publication/379151353\_A\_normalization\_model\_for\_repeated\_letters\_in\_social\_media\_hate\_speech\_text\_based\_on\_rules\_and\_spelling\_correction](https://www.researchgate.net/publication/379151353_A_normalization_model_for_repeated_letters_in_social_media_hate_speech_text_based_on_rules_and_spelling_correction)  
40. Hindi slang mastery: Sound authentic with 15 must-know phrases \- Preply, accessed May 6, 2026, [https://preply.com/en/blog/hindi-slang-guide/](https://preply.com/en/blog/hindi-slang-guide/)  
41. Learn Marathi Through Slang \- Talkpal AI, accessed May 6, 2026, [https://talkpal.ai/learn-marathi-through-slang/](https://talkpal.ai/learn-marathi-through-slang/)  
42. Marathi Slang: Everyday Marathi phrases that native speakers use, accessed May 6, 2026, [https://www.speakmarathi.com/marathi-slang/](https://www.speakmarathi.com/marathi-slang/)  
43. Tackling long sentence translation: a linguistic perspective \- AUSIT, accessed May 6, 2026, [https://ausit.org/blog/tackling-long-sentence-translation-a-linguistic-perspective/](https://ausit.org/blog/tackling-long-sentence-translation-a-linguistic-perspective/)  
44. NLP Preprocessing: Mastering Punctuation, Contractions, & Special Characters \- YouTube, accessed May 6, 2026, [https://www.youtube.com/watch?v=r\_WQRT0fcDo](https://www.youtube.com/watch?v=r_WQRT0fcDo)  
45. How to Use Contractions: Rules and Examples \- TCK Publishing, accessed May 6, 2026, [https://www.tckpublishing.com/contractions/](https://www.tckpublishing.com/contractions/)  
46. Text Normalization for Natural Language Processing (NLP) | by Diego Lopez Yse \- Medium, accessed May 6, 2026, [https://medium.com/data-science/text-normalization-for-natural-language-processing-nlp-70a314bfa646](https://medium.com/data-science/text-normalization-for-natural-language-processing-nlp-70a314bfa646)  
47. Contractions: 4 Types of Contractions in English Grammar \- 2026 \- MasterClass, accessed May 6, 2026, [https://www.masterclass.com/articles/contraction-grammar-guide](https://www.masterclass.com/articles/contraction-grammar-guide)  
48. Hybrid Translation Models: Optimal Resource Mix, accessed May 6, 2026, [https://translated.com/resources/hybrid-translation-models-optimal-resource-mix](https://translated.com/resources/hybrid-translation-models-optimal-resource-mix)  
49. Hybrid Translation with Classification: Revisiting Rule-Based and Neural Machine Translation \- MDPI, accessed May 6, 2026, [https://www.mdpi.com/2079-9292/9/2/201](https://www.mdpi.com/2079-9292/9/2/201)  
50. Grammar Sharing Techniques for Rule-based Multilingual NLP Systems \- ACL Anthology, accessed May 6, 2026, [https://aclanthology.org/W07-2438.pdf](https://aclanthology.org/W07-2438.pdf)  
51. US20170169015A1 \- Translation confidence scores \- Google Patents, accessed May 6, 2026, [https://patents.google.com/patent/US20170169015A1/en](https://patents.google.com/patent/US20170169015A1/en)  
52. Normalization of Spelling Variations in Code-Mixed Data \- ACL Anthology, accessed May 6, 2026, [https://aclanthology.org/2022.icon-main.33.pdf](https://aclanthology.org/2022.icon-main.33.pdf)  
53. Sample-Efficient Language Model for Hinglish Conversational AI \- arXiv, accessed May 6, 2026, [https://arxiv.org/html/2504.19070v1](https://arxiv.org/html/2504.19070v1)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAXCAYAAADpwXTaAAABWklEQVR4Xo1TOU4EQQzskZBYiUNIRAgEj4DHEBESEJETIkIiREJCsCEf4GPkVLvtdrnHvVAre+zy0TXHlqUA1UmQIy83RmrLUuovRz+Bc06cCNlsn3fFwRjsmE9h3X2x3ZB64r2XjvV5fhJRg45ndIKR9tMkpHQCeSs9Ib/e7bKafq1z25wiYgPuHsGhU3ZtyyPsVK31ltZX/QvsWrsz6BSljCGti17B7UVakQmszJoTVPoRdlclkGqJTuDOdhn+MkNeLjH3CXtDftz2lHKApU+wD2xvhlhyNegTK3JVvvV9w35gz7D90m5Fn9eg16F1vW21G1y+EFzExgBfvv56LFhO4bawq0jTMPMj7ItXVQ9wt1T1MGJaEKC6weHvCM9dkDlDF1cDr4gSlUPuKDCCHtFa+xdnNcribmr25xEHA/ihMcZ8xPotGogIEhO49DlC+Y/ejvB5/gdo+wU99RQaOHkx4AAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAYCAYAAACIhL/AAAADSklEQVR4XqVWTYhOURh+32amKBqMCGMjG5kFMbLAQpJZoKSo2dix9hursbCwkaSUDbOi2KJsTJHETokaEk2EsLETn+e577n3/Nxzvvk0Tz3nnPu87znnPf9XVGqo+DK/uqAy/od/iFalTM221FYMJT3E3HzKlgCtQc0NC8B5/nPWFgfAwbxXXg0xBKfdcDuI8jqwL3VIsAG8AQ7WQmkVPZQBXgYPeKkpeQQaizuQPkf+ABx3fAhOg6PelWhqDqP8CPn6wBhiPngEXFR9xUFgIuQ+pC2Raog8OZqL4Hvoo8noabsO/gQ3mtQYWeAsTCQdLwEPgTfF6n0AV2RnSGSP2CRwi+SgA6h3DYUfkowkaI/L/B28Gss6guQNlBHKgYEB7gc3g7elDpA1vE8NbAt9ivxwaqhxDPzr8hIWgy/AV+BS66VKzoD3JDocLUxKEGABF8C7aLM/NawFP4GvweWJLUQdYNgRg2Jw52qn7PyUAoxdx8R8hmNdsXdEO2IjaCHwXQN+lrgj5MrvvfaZDY6wADVd4mhLbAJnIEQHEZtSp8SWd1ej5vuhnX6PwYVOY6NfwG21UwTXjjJAzcxgDNqCwTpRTeTm5yHohitgR3laHdQC/CiWlwZGfdLNdOYUN7NYBah2rTVwUSsN3Ua3GpyGzzcJ7zplYGoBVr2EvUeRIMAeZ1DluJcUp9FOZVO5MMCzSDoonUis8Qw2cK34LA4wP47cEms/7LdQ+C2lfSTKe5EXLS9qXti1zoQHhzfAWL7PBgiwtMQNmrZSA14GZQB8R4MAKuwEv4KXxJ6rBlU/1QooV+BoaKuNgcAZnJHqSSyCp/edFM4CjW9BvsH1+8u3+KVYkKVxU+fAeIBSp2UQeOJ/KbeH8Y9YoLkHYRz+U5I+d36w2qcWPf9euA9WSnhNOcdWpMrnSTkwXuShni/nwdeDW21idtcapQ7aLQxBeiL24PcO147L+Jo9U8t7gJ/WWHKlZFqZ7UN6R4J9mmmiBHjpeeSnrZyr1lYKyDiaxPSUUQOnon8obNfqJ8F+dFtmQyi7cpx1LTvwBjgJfetsdQOsEvsH4O9WyacgS6aDlqtrtKWXELdYqhbo8VBLFTxaIcflntuJ4f3jmv8AUBt6ebPFJv8AAAAASUVORK5CYII=>