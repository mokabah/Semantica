"""Hand-written lexical resources used by the rule-based analysers.

Nothing in this module was derived from a corpus or from a trained model. Every entry was
written and reviewed by hand, so coverage is small and deliberate. Words that are absent from
these tables are treated as unknown, and the analysers report uncertainty instead of guessing.
"""

from __future__ import annotations

# --------------------------------------------------------------------------------------
# Function words
# --------------------------------------------------------------------------------------

DETERMINERS = frozenset(
    {
        "the",
        "a",
        "an",
        "this",
        "that",
        "these",
        "those",
        "its",
        "their",
        "his",
        "her",
        "our",
        "my",
        "your",
    }
)

PREPOSITIONS = frozenset(
    {
        "of",
        "in",
        "on",
        "at",
        "for",
        "with",
        "by",
        "from",
        "to",
        "into",
        "about",
        "over",
        "under",
        "between",
        "among",
        "through",
        "during",
        "after",
        "before",
        "against",
        "within",
        "as",
        "than",
    }
)

BE_FORMS: dict[str, int] = {
    "be": 0,
    "am": 1,
    "is": 1,
    "are": 1,
    "was": 2,
    "were": 2,
    "been": 3,
    "being": 4,
}
HAVE_FORMS = frozenset({"have", "has", "had", "having"})
DO_FORMS = frozenset({"do", "does", "did", "doing"})

PRONOUNS = frozenset(
    {"it", "he", "she", "they", "them", "him", "his", "her", "its", "their", "these", "those"}
)

RELATIVIZERS = frozenset({"who", "which", "that", "whom", "whose"})

# --------------------------------------------------------------------------------------
# Negation, quantifiers, degree words
# --------------------------------------------------------------------------------------

#: Tokens that contribute one negation to the parity count.
NEGATION_TOKENS = frozenset(
    {"not", "no", "never", "none", "nobody", "nothing", "neither", "nor", "nowhere"}
)

QUANTIFIER_CLASS: dict[str, str] = {
    "no": "none",
    "none": "none",
    "never": "none",
    "nobody": "none",
    "nothing": "none",
    "few": "few",
    "rarely": "few",
    "seldom": "few",
    "some": "some",
    "sometimes": "some",
    "several": "some",
    "occasionally": "some",
    "many": "many",
    "often": "many",
    "frequently": "many",
    "most": "majority",
    "mostly": "majority",
    "usually": "majority",
    "majority": "majority",
    "generally": "majority",
    "all": "universal",
    "every": "universal",
    "each": "universal",
    "always": "universal",
    "everyone": "universal",
    "everybody": "universal",
    "everything": "universal",
}

#: Ordinal strength used only to report the direction of a quantifier shift.
QUANTIFIER_RANK: dict[str, int] = {
    "none": 0,
    "few": 1,
    "some": 2,
    "many": 3,
    "majority": 4,
    "universal": 5,
    "not_all": 3,
}

#: Words whose addition or removal is flagged for review but is not treated as a hard failure.
DEGREE_WORDS = frozenset(
    {
        "slightly",
        "significantly",
        "strongly",
        "greatly",
        "highly",
        "somewhat",
        "very",
        "extremely",
        "partly",
        "largely",
        "primarily",
        "mainly",
        "directly",
        "indirectly",
        "barely",
        "hardly",
        "substantially",
        "marginally",
        "considerably",
    }
)

#: Exclusivity markers. A mismatch is a meaning change, not a stylistic one.
EXCLUSIVITY_WORDS = frozenset({"only", "solely", "exclusively", "merely", "just"})

# --------------------------------------------------------------------------------------
# Modality
# --------------------------------------------------------------------------------------

MODAL_CLASS: dict[str, str] = {
    "may": "possibility",
    "might": "possibility",
    "could": "possibility",
    "can": "possibility",
    "must": "necessity",
    "will": "prediction",
    "shall": "prediction",
    "should": "advisability",
    "ought": "advisability",
    "would": "ambiguous",
}

#: Multi-word modal markers, longest first. Matched against lower-cased token sequences.
PHRASE_MODALS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("it", "is", "possible", "that"), "possibility"),
    (("it", "is", "likely", "that"), "probability"),
    (("it", "is", "certain", "that"), "certainty"),
    (("is", "likely", "to"), "probability"),
    (("are", "likely", "to"), "probability"),
    (("is", "unlikely", "to"), "improbability"),
    (("are", "unlikely", "to"), "improbability"),
    (("is", "certain", "to"), "certainty"),
    (("are", "certain", "to"), "certainty"),
    (("is", "bound", "to"), "certainty"),
    (("are", "bound", "to"), "certainty"),
    (("has", "to"), "necessity"),
    (("have", "to"), "necessity"),
    (("had", "to"), "necessity"),
    (("need", "to"), "necessity"),
    (("needs", "to"), "necessity"),
    (("tends", "to"), "tendency"),
    (("tend", "to"), "tendency"),
    (("seems", "to"), "appearance"),
    (("seem", "to"), "appearance"),
    (("appears", "to"), "appearance"),
    (("appear", "to"), "appearance"),
    (("is", "able", "to"), "possibility"),
    (("are", "able", "to"), "possibility"),
)

ADVERB_MODALS: dict[str, str] = {
    "possibly": "possibility",
    "perhaps": "possibility",
    "maybe": "possibility",
    "conceivably": "possibility",
    "probably": "probability",
    "likely": "probability",
    "unlikely": "improbability",
    "certainly": "certainty",
    "definitely": "certainty",
    "undoubtedly": "certainty",
    "surely": "certainty",
    "clearly": "certainty",
    "obviously": "certainty",
    "apparently": "appearance",
    "seemingly": "appearance",
}

#: Ordinal certainty. ``asserted`` is the level of a plain, unmarked statement.
CERTAINTY_LEVEL: dict[str, int] = {
    "improbability": 0,
    "possibility": 1,
    "appearance": 1,
    "tendency": 2,
    "probability": 2,
    "advisability": 2,
    "ambiguous": 2,
    "asserted": 3,
    "prediction": 3,
    "necessity": 4,
    "certainty": 4,
}

# --------------------------------------------------------------------------------------
# Claim strength of predicates (epistemic force of the verb itself)
# --------------------------------------------------------------------------------------

CLAIM_STRENGTH: dict[str, int] = {}
for _lemma in (
    "influence",
    "affect",
    "impact",
    "shape",
    "contribute",
    "relate",
    "associate",
    "correlate",
    "link",
    "connect",
    "suggest",
    "imply",
    "hint",
):
    CLAIM_STRENGTH[_lemma] = 1
for _lemma in (
    "lead",
    "drive",
    "trigger",
    "promote",
    "enable",
    "encourage",
    "foster",
    "indicate",
    "predict",
):
    CLAIM_STRENGTH[_lemma] = 2
for _lemma in (
    "cause",
    "produce",
    "determine",
    "dictate",
    "ensure",
    "guarantee",
    "force",
    "compel",
    "prove",
    "demonstrate",
    "show",
    "reveal",
    "confirm",
    "establish",
):
    CLAIM_STRENGTH[_lemma] = 3
del _lemma

CLAIM_STRENGTH_LABEL = {1: "weak", 2: "moderate", 3: "strong"}

#: Verbs that express a causal relation at predicate level.
CAUSAL_VERBS = frozenset(
    {
        "cause",
        "produce",
        "determine",
        "lead",
        "drive",
        "trigger",
        "force",
        "compel",
        "ensure",
        "result",
    }
)

# --------------------------------------------------------------------------------------
# Verbs
# --------------------------------------------------------------------------------------

_REGULAR_VERBS = [
    "influence",
    "affect",
    "impact",
    "shape",
    "contribute",
    "relate",
    "associate",
    "correlate",
    "link",
    "connect",
    "suggest",
    "imply",
    "hint",
    "cause",
    "produce",
    "determine",
    "dictate",
    "ensure",
    "guarantee",
    "force",
    "compel",
    "prove",
    "demonstrate",
    "reveal",
    "confirm",
    "establish",
    "trigger",
    "promote",
    "enable",
    "encourage",
    "discourage",
    "foster",
    "predict",
    "indicate",
    "increase",
    "decrease",
    "reduce",
    "lessen",
    "diminish",
    "improve",
    "worsen",
    "harm",
    "damage",
    "hurt",
    "help",
    "assist",
    "aid",
    "support",
    "oppose",
    "reject",
    "refuse",
    "accept",
    "approve",
    "endorse",
    "deny",
    "allow",
    "permit",
    "forbid",
    "prohibit",
    "prevent",
    "require",
    "need",
    "want",
    "desire",
    "use",
    "utilize",
    "employ",
    "study",
    "examine",
    "analyze",
    "investigate",
    "explain",
    "describe",
    "understand",
    "comprehend",
    "grasp",
    "interpret",
    "perceive",
    "believe",
    "suspect",
    "learn",
    "change",
    "alter",
    "modify",
    "transform",
    "convert",
    "construct",
    "purchase",
    "provide",
    "supply",
    "offer",
    "receive",
    "obtain",
    "acquire",
    "watch",
    "ask",
    "answer",
    "visit",
    "attack",
    "kill",
    "start",
    "finish",
    "stop",
    "begin",
    "continue",
    "follow",
    "precede",
    "depend",
    "rely",
    "motivate",
    "persuade",
    "convince",
    "expect",
    "lack",
    "include",
    "exclude",
    "contain",
    "involve",
    "cover",
    "avoid",
    "publish",
    "release",
    "report",
    "announce",
    "claim",
    "argue",
    "state",
    "mention",
    "note",
    "observe",
    "notice",
    "discover",
    "develop",
    "expand",
    "shrink",
    "strengthen",
    "weaken",
    "destroy",
    "repair",
    "fix",
    "solve",
    "resolve",
    "address",
    "treat",
    "cure",
    "protect",
    "defend",
    "threaten",
    "reward",
    "punish",
    "criticize",
    "praise",
    "blame",
    "accuse",
    "invite",
    "hire",
    "own",
    "possess",
    "keep",
    "arrive",
    "reach",
    "enter",
    "move",
    "carry",
    "send",
    "pass",
    "fail",
    "succeed",
    "play",
    "work",
    "live",
    "talk",
    "call",
    "meet",
    "join",
    "remove",
    "delete",
    "add",
    "install",
    "open",
    "close",
    "cancel",
    "delay",
    "postpone",
    "schedule",
    "review",
    "evaluate",
    "assess",
    "measure",
    "compare",
    "test",
    "check",
    "verify",
    "validate",
    "assert",
    "insist",
    "maintain",
    "allege",
    "speculate",
    "declare",
    "endorse",
    "commence",
    "conclude",
    "halt",
    "cease",
    "boost",
    "foster",
    "raise",
    "lower",
    "clarify",
    "confuse",
    "mislead",
    "inform",
    "educate",
    "entertain",
    "annoy",
    "upset",
    "please",
    "worry",
    "affect",
    "chase",
    "bite",
    "love",
    "hate",
    "like",
    "admire",
    "thank",
    "beat",
    "defeat",
    "marry",
    "fire",
    "attend",
    "inspect",
]

# (base, third person, past, participle, gerund)
_IRREGULAR_VERBS: tuple[tuple[str, str, str, str, str], ...] = (
    ("lead", "leads", "led", "led", "leading"),
    ("show", "shows", "showed", "shown", "showing"),
    ("find", "finds", "found", "found", "finding"),
    ("think", "thinks", "thought", "thought", "thinking"),
    ("know", "knows", "knew", "known", "knowing"),
    ("teach", "teaches", "taught", "taught", "teaching"),
    ("make", "makes", "made", "made", "making"),
    ("buy", "buys", "bought", "bought", "buying"),
    ("sell", "sells", "sold", "sold", "selling"),
    ("give", "gives", "gave", "given", "giving"),
    ("take", "takes", "took", "taken", "taking"),
    ("get", "gets", "got", "gotten", "getting"),
    ("see", "sees", "saw", "seen", "seeing"),
    ("read", "reads", "read", "read", "reading"),
    ("write", "writes", "wrote", "written", "writing"),
    ("say", "says", "said", "said", "saying"),
    ("tell", "tells", "told", "told", "telling"),
    ("hit", "hits", "hit", "hit", "hitting"),
    ("win", "wins", "won", "won", "winning"),
    ("lose", "loses", "lost", "lost", "losing"),
    ("grow", "grows", "grew", "grown", "growing"),
    ("rise", "rises", "rose", "risen", "rising"),
    ("fall", "falls", "fell", "fallen", "falling"),
    ("build", "builds", "built", "built", "building"),
    ("hold", "holds", "held", "held", "holding"),
    ("leave", "leaves", "left", "left", "leaving"),
    ("bring", "brings", "brought", "brought", "bringing"),
    ("run", "runs", "ran", "run", "running"),
    ("speak", "speaks", "spoke", "spoken", "speaking"),
    ("choose", "chooses", "chose", "chosen", "choosing"),
    ("drive", "drives", "drove", "driven", "driving"),
    ("eat", "eats", "ate", "eaten", "eating"),
    ("drink", "drinks", "drank", "drunk", "drinking"),
    ("sleep", "sleeps", "slept", "slept", "sleeping"),
    ("die", "dies", "died", "died", "dying"),
    ("begin", "begins", "began", "begun", "beginning"),
    ("stop", "stops", "stopped", "stopped", "stopping"),
    ("ban", "bans", "banned", "banned", "banning"),
    ("drop", "drops", "dropped", "dropped", "dropping"),
    ("plan", "plans", "planned", "planned", "planning"),
    ("permit", "permits", "permitted", "permitted", "permitting"),
    ("submit", "submits", "submitted", "submitted", "submitting"),
    ("refer", "refers", "referred", "referred", "referring"),
    ("commit", "commits", "committed", "committed", "committing"),
    ("create", "creates", "created", "created", "creating"),
    ("end", "ends", "ended", "ended", "ending"),
    ("cancel", "cancels", "cancelled", "cancelled", "cancelling"),
)


def _regular_forms(base: str) -> tuple[str, str, str, str, str]:
    if base.endswith(("s", "x", "z", "ch", "sh", "o")):
        third = base + "es"
    elif base.endswith("y") and base[-2] not in "aeiou":
        third = base[:-1] + "ies"
    else:
        third = base + "s"
    if base.endswith("e"):
        past = base + "d"
    elif base.endswith("y") and base[-2] not in "aeiou":
        past = base[:-1] + "ied"
    else:
        past = base + "ed"
    if base.endswith("ie"):
        gerund = base[:-2] + "ying"
    elif base.endswith("e") and not base.endswith("ee"):
        gerund = base[:-1] + "ing"
    else:
        gerund = base + "ing"
    return base, third, past, past, gerund


VERB_PARADIGMS: dict[str, tuple[str, str, str, str, str]] = {}
for _row in _IRREGULAR_VERBS:
    VERB_PARADIGMS[_row[0]] = _row
for _base in _REGULAR_VERBS:
    VERB_PARADIGMS.setdefault(_base, _regular_forms(_base))
del _row, _base

#: surface form -> (lemma, paradigm slot). Slots: 0 base, 1 third, 2 past, 3 participle, 4 gerund.
VERB_FORMS: dict[str, tuple[str, int]] = {}
for _lemma, _paradigm in VERB_PARADIGMS.items():
    for _slot, _form in enumerate(_paradigm):
        VERB_FORMS.setdefault(_form, (_lemma, _slot))
del _lemma, _paradigm, _slot, _form

#: Forms that can head a passive construction ("was criticized").
PARTICIPLE_FORMS: dict[str, str] = {
    _paradigm[3]: _lemma for _lemma, _paradigm in VERB_PARADIGMS.items()
}

# --------------------------------------------------------------------------------------
# Synonym classes. Members of one class are treated as interchangeable in meaning at the
# level of this toolkit. The classes are deliberately conservative and hand-curated; several
# are debatable, which is documented in docs/methodology.md.
# --------------------------------------------------------------------------------------

SYNONYM_CLASSES: tuple[frozenset[str], ...] = tuple(
    frozenset(group.split())
    for group in (
        "influence affect impact",
        "associate link connect relate",
        "cause produce",
        "determine dictate",
        "ensure guarantee",
        "force compel",
        "promote encourage foster",
        "suggest imply hint",
        "show demonstrate reveal",
        "prove establish",
        "understand interpret comprehend grasp",
        "use utilize employ",
        "buy purchase",
        "begin start commence",
        "end finish conclude",
        "stop halt cease",
        "help assist aid",
        "need require",
        "want desire",
        "get obtain acquire",
        "build construct",
        "fix repair",
        "reduce decrease lessen diminish",
        "increase boost raise",
        "harm damage hurt",
        "allow permit",
        "forbid prohibit ban",
        "reject refuse",
        "say state declare",
        "examine inspect",
        "people individuals persons humans",
        "child kid",
        "children kids",
        "doctor physician",
        "doctors physicians",
        "student pupil",
        "students pupils",
        "customer client",
        "customers clients",
        "scientist researcher",
        "scientists researchers",
        "expert specialist",
        "experts specialists",
        "teenager adolescent",
        "teenagers adolescents",
        "company firm business",
        "car automobile",
        "error mistake",
        "problem issue",
        "result outcome",
        "goal aim objective",
        "behavior behaviour conduct",
        "big large",
        "small little",
        "fast quick rapid",
        "important significant",
        "harmful damaging detrimental",
        "beneficial advantageous",
        "smart intelligent",
        "easy simple",
        "difficult hard",
    )
)

#: Pairs of words that express opposite meanings. Matching is done on class representatives.
ANTONYM_PAIRS: tuple[tuple[str, str], ...] = (
    ("increase", "decrease"),
    ("increase", "reduce"),
    ("rise", "fall"),
    ("raise", "lower"),
    ("grow", "shrink"),
    ("expand", "shrink"),
    ("improve", "worsen"),
    ("support", "oppose"),
    ("accept", "reject"),
    ("approve", "reject"),
    ("approve", "deny"),
    ("confirm", "deny"),
    ("allow", "forbid"),
    ("win", "lose"),
    ("begin", "end"),
    ("start", "stop"),
    ("open", "close"),
    ("buy", "sell"),
    ("give", "take"),
    ("help", "harm"),
    ("benefit", "harm"),
    ("strengthen", "weaken"),
    ("include", "exclude"),
    ("succeed", "fail"),
    ("encourage", "discourage"),
    ("praise", "criticize"),
    ("true", "false"),
    ("possible", "impossible"),
    ("legal", "illegal"),
    ("safe", "dangerous"),
    ("safe", "unsafe"),
    ("positive", "negative"),
    ("good", "bad"),
    ("high", "low"),
    ("large", "small"),
    ("more", "less"),
    ("before", "after"),
    ("above", "below"),
    ("advantage", "disadvantage"),
    ("success", "failure"),
    ("same", "different"),
    ("early", "late"),
    ("easy", "difficult"),
    ("hot", "cold"),
    ("fast", "slow"),
    ("strong", "weak"),
    ("effective", "ineffective"),
    ("agree", "disagree"),
    ("trust", "distrust"),
    ("beneficial", "harmful"),
    ("increase", "lower"),
    ("accelerate", "slow"),
    ("rich", "poor"),
    ("happy", "sad"),
    ("true", "untrue"),
    ("likely", "unlikely"),
    ("important", "unimportant"),
    ("present", "absent"),
    ("accurate", "inaccurate"),
    ("reliable", "unreliable"),
    ("healthy", "unhealthy"),
    ("friend", "enemy"),
    ("hire", "fire"),
    ("cause", "prevent"),
    ("allow", "prevent"),
    ("lead", "follow"),
)

#: Sets of mutually exclusive alternatives. Two different members are a substitution.
EXCLUSIVE_SETS: tuple[frozenset[str], ...] = tuple(
    frozenset(group.split())
    for group in (
        "red blue green yellow black white orange purple brown grey gray pink",
        "monday tuesday wednesday thursday friday saturday sunday",
        "january february march april june july august september october november december",
        "north south east west",
        "spring summer autumn fall winter",
        "morning afternoon evening night",
        "first second third fourth fifth sixth",
        "daily weekly monthly yearly annually",
        "man woman",
        "boy girl",
    )
)

NUMBER_WORDS: dict[str, str] = {
    "zero": "0",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "sixty": "60",
    "seventy": "70",
    "eighty": "80",
    "ninety": "90",
    "hundred": "100",
    "thousand": "1000",
    "million": "1000000",
    "half": "0.5",
}

# --------------------------------------------------------------------------------------
# Evaluative polarity (pragmatic layer)
# --------------------------------------------------------------------------------------

POSITIVE_WORDS = frozenset(
    {
        "good",
        "great",
        "excellent",
        "beneficial",
        "helpful",
        "effective",
        "successful",
        "safe",
        "useful",
        "valuable",
        "positive",
        "improve",
        "benefit",
        "help",
        "wonderful",
        "reliable",
        "healthy",
        "accurate",
        "advantageous",
        "praise",
        "success",
        "advantage",
    }
)
NEGATIVE_WORDS = frozenset(
    {
        "bad",
        "poor",
        "harmful",
        "dangerous",
        "ineffective",
        "useless",
        "negative",
        "terrible",
        "awful",
        "risky",
        "unsafe",
        "failure",
        "worse",
        "worsen",
        "harm",
        "damage",
        "criticize",
        "unreliable",
        "unhealthy",
        "inaccurate",
        "disadvantage",
        "detrimental",
        "damaging",
    }
)

# --------------------------------------------------------------------------------------
# Attribution
# --------------------------------------------------------------------------------------

REPORTING_VERB_CLASS: dict[str, str] = {}
for _lemma in ("say", "state", "report", "announce", "mention", "note", "write", "tell", "declare"):
    REPORTING_VERB_CLASS[_lemma] = "neutral"
for _lemma in (
    "find",
    "show",
    "demonstrate",
    "prove",
    "reveal",
    "confirm",
    "discover",
    "establish",
    "observe",
):
    REPORTING_VERB_CLASS[_lemma] = "finding"
for _lemma in ("claim", "allege", "assert", "insist", "maintain"):
    REPORTING_VERB_CLASS[_lemma] = "distancing"
for _lemma in ("suggest", "believe", "think", "suspect", "argue", "speculate", "imply", "indicate"):
    REPORTING_VERB_CLASS[_lemma] = "tentative"
del _lemma

#: Reporting verbs that may introduce a clause without the complementiser "that".
BARE_REPORTING_VERBS = frozenset(
    {"say", "state", "claim", "allege", "announce", "report", "mention", "declare", "tell"}
)

PASSIVE_REPORT_CLASS: dict[str, str] = {
    "reported": "neutral",
    "said": "neutral",
    "stated": "neutral",
    "claimed": "distancing",
    "alleged": "distancing",
    "believed": "tentative",
    "thought": "tentative",
    "suggested": "tentative",
    "known": "finding",
    "shown": "finding",
}

ADVERBIAL_ATTRIBUTION: dict[str, str] = {
    "reportedly": "neutral",
    "allegedly": "distancing",
    "supposedly": "distancing",
}

# --------------------------------------------------------------------------------------
# Discourse
# --------------------------------------------------------------------------------------

DISCOURSE_MARKERS: dict[str, str] = {
    "however": "contrast",
    "nevertheless": "contrast",
    "nonetheless": "contrast",
    "in contrast": "contrast",
    "on the other hand": "contrast",
    "but": "contrast",
    "yet": "contrast",
    "whereas": "contrast",
    "moreover": "addition",
    "furthermore": "addition",
    "also": "addition",
    "in addition": "addition",
    "additionally": "addition",
    "for example": "exemplification",
    "for instance": "exemplification",
    "therefore": "result",
    "thus": "result",
    "hence": "result",
    "consequently": "result",
    "as a result": "result",
    "similarly": "similarity",
    "likewise": "similarity",
}

# --------------------------------------------------------------------------------------
# Misc function-word groups used when selecting content words
# --------------------------------------------------------------------------------------

FILLER_WORDS = frozenset({"how", "way", "manner", "extent", "and", "also", "then", "there"})

AMBIGUITY_ABBREVIATIONS = frozenset(
    {"mr", "mrs", "ms", "dr", "prof", "vs", "etc", "e.g", "i.e", "u.s", "st", "no", "fig", "inc"}
)
