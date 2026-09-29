"""
Translator: Yaoundé Pidgin / "franc-anglais" -> standard English or French
CS4110 - Compiler Construction

Two layers:
  1. VERIFIED  - hand-checked translations of the collected statements (the exam corpus).
  2. AUTOMATIC - a rule-based engine for new sentences. It uses the lexical analyzer's
     token types, then rewrites Pidgin aspect markers into standard tense:
        dey + V  -> progressive       done/don + V -> present perfect
        go + V   -> future            no fit + V   -> cannot
        make we/you/I ... -> let's / please / so that I can
     Words that are not in the lexicon are kept unchanged and reported in Translator.unknown,
     so any input is translated (never rejected).
"""

import re
from typing import Dict, List, Optional, Tuple

from lexical_analyzer import LexicalAnalyzer, Token, TokenType

# ---------------------------------------------------------------------------
# 1. Verified translations (collected corpus)
# ---------------------------------------------------------------------------
# Filled by statements.py from corpus.py (30 statements) plus the statements you add in the app
VERIFIED: Dict[str, Dict[str, str]] = {}


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().strip('"')).lower()


_VERIFIED_INDEX: Dict[str, Dict[str, str]] = {}


def rebuild_verified_index() -> None:
    _VERIFIED_INDEX.clear()
    _VERIFIED_INDEX.update({_norm(k): v for k, v in VERIFIED.items()})

# ---------------------------------------------------------------------------
# 2. Lexicon
# ---------------------------------------------------------------------------
# nouns: word -> (english, french, gender m/f, plural?)
NOUNS = {
    "taxi": ("taxi", "taxi", "m", False), "light": ("power", "courant", "m", False),
    "internet": ("internet", "Internet", "m", False), "modem": ("modem", "modem", "m", False),
    "generator": ("generator", "groupe électrogène", "m", False), "money": ("money", "argent", "m", False),
    "francs": ("francs", "francs", "m", True), "tomatoes": ("tomatoes", "tomates", "f", True),
    "chop": ("food", "nourriture", "f", False), "price": ("price", "prix", "m", False),
    "road": ("road", "route", "f", False), "car": ("car", "voiture", "f", False),
    "mud": ("mud", "boue", "f", False), "rain": ("rain", "pluie", "f", False),
    "petrol": ("petrol", "essence", "f", False), "pump": ("pump", "pompe", "f", False),
    "tank": ("tank", "réservoir", "m", False), "lecture": ("lecture", "cours", "m", False),
    "prof": ("professor", "prof", "m", False), "class": ("class", "classe", "f", False),
    "exam": ("exam", "examen", "m", False), "beer": ("beer", "bière", "f", False),
    "semester": ("semester", "semestre", "m", False), "network": ("network", "réseau", "m", False),
    "quarter": ("neighbourhood", "quartier", "m", False), "quartier": ("neighbourhood", "quartier", "m", False),
    "checkpoint": ("checkpoint", "contrôle", "m", False), "document": ("documents", "papiers", "m", True),
    "documents": ("documents", "papiers", "m", True), "front": ("front", "devant", "m", False),
    "transport": ("transport", "transport", "m", False), "traffic": ("traffic", "embouteillages", "m", True),
    "bendskin": ("bendskin", "bendskin", "m", False), "morning": ("morning", "matin", "m", False),
    "kilometers": ("kilometres", "kilomètres", "m", True), "kontri": ("country", "pays", "m", False),
    "junction": ("junction", "carrefour", "m", False), "madam": ("madam", "madame", "f", False),
    "paper": ("paper", "papier", "m", False), "pas": ("pas", "pas", "m", False), "message": ("message", "message", "m", False),
    "candle": ("candle", "bougie", "f", False), "shoe": ("shoe", "chaussure", "f", False),
    "gutter": ("gutter", "caniveau", "m", False), "station": ("station", "station", "f", False),
    "suya": ("suya", "suya", "m", False), "roadblock": ("roadblock", "barrage", "m", False),
    "officer": ("officer", "agent", "m", False), "shop": ("shop", "boutique", "f", False),
    "notes": ("notes", "notes", "f", True), "assignment": ("assignment", "devoir", "m", False),
    "egg": ("egg", "œuf", "m", False), "litre": ("litre", "litre", "m", False), "one": ("one", "un", "m", False),
    "another": ("another", "autre", "m", False),
    "njangi": ("savings group", "tontine", "f", False), "moto": ("motorbike", "moto", "f", False), "airtime": ("airtime", "crédit", "m", False),
    "phone": ("phone", "téléphone", "m", False), "balance": ("credit", "crédit", "m", False),
    "ticket": ("ticket", "billet", "m", False), "driver": ("driver", "chauffeur", "m", False),
    "chauffeur": ("driver", "chauffeur", "m", False), "police": ("police", "police", "f", False),
    "time": ("time", "temps", "m", False), "nothing": ("nothing", "rien", "m", False),
    "tomato": ("tomato", "tomate", "f", False), "generators": ("generators", "groupes électrogènes", "m", True),
    "night": ("night", "nuit", "f", False), "food": ("food", "nourriture", "f", False),
    "market": ("market", "marché", "m", False), "bus": ("bus", "bus", "m", False),
    "fuel": ("fuel", "carburant", "m", False), "water": ("water", "eau", "f", False),
    "school": ("school", "école", "f", False), "student": ("student", "étudiant", "m", False),
    "students": ("students", "étudiants", "m", True), "house": ("house", "maison", "f", False),
    "thank": ("thank", "merci", "m", False), "your": ("your", "votre", "m", False),
    "brother": ("brother", "frère", "m", False), "pikin": ("child", "enfant", "m", False),
    "oga": ("boss", "patron", "m", False), "sister": ("sister", "sœur", "f", False), "friend": ("friend", "ami", "m", False),
    "man": ("man", "homme", "m", False), "woman": ("woman", "femme", "f", False), "name": ("name", "nom", "m", False),
    "day": ("day", "jour", "m", False), "church": ("church", "église", "f", False),
    "bread": ("bread", "pain", "m", False), "fish": ("fish", "poisson", "m", False), "meat": ("meat", "viande", "f", False),
    "rice": ("rice", "riz", "m", False), "beans": ("beans", "haricots", "m", True), "plantain": ("plantain", "plantain", "m", False),
    "bag": ("bag", "sac", "m", False), "shoe": ("shoe", "chaussure", "f", False),
    "hospital": ("hospital", "hôpital", "m", False), "office": ("office", "bureau", "m", False), "room": ("room", "chambre", "f", False), "mama": ("Mama", "maman", "f", False),
}
PROPER = {"yaoundé": ("Yaoundé", "Yaoundé"), "carrefour": ("Carrefour", "Carrefour"),
          "mambanda": ("Mambanda", "Mambanda"), "mtn": ("MTN", "MTN"), "mama": ("Mama", "Maman"),
          "brother": ("brother", "frère"), "prof": ("the professor", "le prof"), "ict": ("ICT", "ICT")}
NUMBERS = {"one": ("one", "un"), "two": ("two", "deux"), "three": ("three", "trois"), "four": ("four", "quatre"),
           "five": ("five", "cinq"), "six": ("six", "six"), "seven": ("seven", "sept"), "eight": ("eight", "huit"),
           "nine": ("nine", "neuf"), "ten": ("ten", "dix"), "hundred": ("hundred", "cents"),
           "thousand": ("thousand", "mille")}
ADJ = {"full": ("full", "plein"), "complete": ("complete", "complet"), "hard": ("hard", "difficile"),
       "sweet": ("delicious", "délicieux"), "fresh": ("fresh", "frais"), "good": ("good", "bon"), "scarce": ("scarce", "rare"),
       "crowded": ("crowded", "plein"), "careful": ("careful", "prudent"), "much": ("much", "trop"),
       "tired": ("tired", "fatigué"), "slow": ("slow", "lent"), "cheap": ("cheap", "bon marché"),
       "expensive": ("expensive", "cher"), "wet": ("wet", "mouillé"), "hot": ("hot", "chaud"),
       "cold": ("cold", "froid"), "heavy": ("heavy", "lourd"), "dark": ("dark", "sombre"), "long": ("long", "long"),
       "hungry": ("hungry", "affamé"), "big": ("big", "grand"), "bad": ("bad", "mauvais"), "new": ("new", "nouveau"),
       "cher": ("expensive", "cher"), "down-down": ("down", "en panne")}
ADV = {"plenty": ("a lot", "beaucoup"), "more": ("more", "plus"), "less": ("less", "moins"), "well": ("well", "bien"),
       "quick": ("quickly", "vite"), "never": ("never", "jamais"), "neva": ("never", "jamais"), "neba": ("never", "jamais"), "again": ("again", "encore"), "so": ("so much", "tellement"), "too": ("too", "trop"),
       "just": ("just", "juste"), "even": ("even", "même"), "already": ("already", "déjà"),
       "always": ("always", "toujours"), "now": ("now", "maintenant"), "down": ("down", "en bas"),
       "pass": ("more", "plus"), "ahead": ("ahead", "devant"), "here": ("here", "ici"), "there": ("there", "là"),
       "today": ("today", "aujourd'hui"), "tomorrow": ("tomorrow", "demain"), "soon": ("soon", "bientôt"),
       "late": ("late", "tard"), "early": ("early", "tôt")}
PREP = {"at": ("at", "à"), "for": ("for", "pour"), "in": ("in", "dans"), "on": ("on", "sur"),
        "before": ("before", "avant"), "after": ("after", "après"), "since": ("since", "depuis"),
        "from": ("from", "de"), "with": ("with", "avec"), "to": ("to", "à")}
INTERJ = {"garrr": ("argh", "argh"), "zéro-zéro": ("total blackout", "coupure totale"), "ekiee": ("oh dear", "oh là là"),
          "hmmm": ("hmm", "hmm"), "ok": ("OK", "OK"), "eh": ("oh", "oh"), "ooo": ("", ""),
          "wahala": ("trouble", "souci"), "abeg": ("please", "s'il te plaît"), "ehh": ("oh", "oh"),
          "haba": ("come on", "allons donc"), "chai": ("oh no", "oh non")}
CODE = {"mon dieu": ("my God", "mon Dieu"), "c'est cher": ("that's expensive", "c'est cher"),
        "je wanda": ("I wonder", "je me demande")}
QWORDS = {"how": ("how", "comment"), "why": ("why", "pourquoi"), "what": ("what", "quoi"), "where": ("where", "où"), "wetin": ("what", "quoi"), "who": ("who", "qui"), "when": ("when", "quand")}

# verbs: base -> dict(en=(3sg, pp, ing), fr=(inf, pp, aux, imperative))
EN_IRREG = {  # base: (third, pp, ing)
    "drop": ("drops", "dropped", "dropping"), "tire": ("wears out", "worn out", "wearing out"),
    "try": ("tries", "tried", "trying"), "remain": ("remains", "remained", "remaining"),
    "go": ("goes", "gone", "going"), "take": ("takes", "taken", "taking"), "become": ("becomes", "become", "becoming"),
    "be": ("is", "been", "being"), "sit": ("sits", "sat", "sitting"), "do": ("does", "done", "doing"),
    "buy": ("buys", "bought", "buying"), "see": ("sees", "seen", "seeing"), "know": ("knows", "known", "knowing"),
    "give": ("gives", "given", "giving"), "come": ("comes", "come", "coming"), "say": ("says", "said", "saying"),
    "fall": ("falls", "fallen", "falling"), "cut": ("cuts", "cut", "cutting"), "empty": ("empties", "emptied", "emptying"),
    "sell": ("sells", "sold", "selling"), "eat": ("eats", "eaten", "eating"), "drink": ("drinks", "drunk", "drinking"),
    "tell": ("tells", "told", "telling"), "bring": ("brings", "brought", "bringing"), "leave": ("leaves", "left", "leaving"),
    "sleep": ("sleeps", "slept", "sleeping"), "pay": ("pays", "paid", "paying"), "run": ("runs", "run", "running"),
    "stop": ("stops", "stopped", "stopping"), "hold": ("holds", "held", "holding"), "stand": ("stands", "stood", "standing"),
    "drive": ("drives", "driven", "driving"), "park": ("parks", "parked", "parking"), "hala": ("gives", "given", "giving"),
    "stuck": ("is stuck", "been stuck", "being stuck"), "read": ("reads", "read", "reading"), "fry": ("fries", "fried", "frying"), "tchop": ("eats", "eaten", "eating"), "waka": ("walks", "walked", "walking"),
    "fill": ("fills", "filled", "filling"), "load": ("loads", "loaded", "loading"),
    "start": ("starts", "started", "starting"), "reach": ("reaches", "reached", "reaching"),
}
EN_BASE = {"tchop": "eat", "sabi": "know", "komot": "leave", "tif": "steal", "hala": "give", "waka": "walk", "tire": "wear out", "stuck": "be stuck", "fill": "fill up"}

# FR: base -> (infinitive, past participle, auxiliary, imperative-tu, present 3sg override or None)
FR = {
    "drop": ("déposer", "déposé", "avoir", "dépose"), "tire": ("épuiser", "épuisé", "avoir", "épuise"),
    "hala": ("donner", "donné", "avoir", "donne"), "try": ("essayer", "essayé", "avoir", "essaie"),
    "cut": ("couper", "coupé", "avoir", "coupe"), "remain": ("rester", "resté", "être", "reste"),
    "fill": ("remplir", "rempli", "avoir", "remplis"), "go": ("aller", "allé", "être", "va"),
    "waka": ("marcher", "marché", "avoir", "marche"), "take": ("prendre", "pris", "avoir", "prends"),
    "load": ("charger", "chargé", "avoir", "charge"), "start": ("commencer", "commencé", "avoir", "commence"),
    "finish": ("finir", "fini", "avoir", "finis"), "work": ("marcher", "marché", "avoir", "marche"),
    "charge": ("faire payer", "fait payer", "avoir", "fais payer"), "reduce": ("baisser", "baissé", "avoir", "baisse"),
    "browse": ("naviguer", "navigué", "avoir", "navigue"), "relax": ("se détendre", "détendu", "être", "détends-toi"),
    "say": ("dire", "dit", "avoir", "dis"), "come": ("venir", "venu", "être", "viens"),
    "use": ("utiliser", "utilisé", "avoir", "utilise"), "give": ("donner", "donné", "avoir", "donne"),
    "wait": ("attendre", "attendu", "avoir", "attends"), "empty": ("vider", "vidé", "avoir", "vide"),
    "fall": ("tomber", "tombé", "être", "tombe"), "stuck": ("coincer", "coincé", "être", "coince"),
    "restart": ("redémarrer", "redémarré", "avoir", "redémarre"), "become": ("devenir", "devenu", "être", "deviens"),
    "be": ("être", "été", "avoir", "sois"), "sit": ("s'asseoir", "assis", "être", "assieds-toi"),
    "do": ("faire", "fait", "avoir", "fais"), "buy": ("acheter", "acheté", "avoir", "achète"),
    "see": ("voir", "vu", "avoir", "vois"), "know": ("savoir", "su", "avoir", "sache"),
    "reach": ("arriver", "arrivé", "être", "arrive"), "stop": ("arrêter", "arrêté", "avoir", "arrête"),
    "pay": ("payer", "payé", "avoir", "paie"), "drive": ("conduire", "conduit", "avoir", "conduis"),
    "park": ("garer", "garé", "avoir", "gare"), "arrive": ("arriver", "arrivé", "être", "arrive"),
    "move": ("bouger", "bougé", "avoir", "bouge"), "sell": ("vendre", "vendu", "avoir", "vends"),
    "cook": ("cuisiner", "cuisiné", "avoir", "cuisine"), "eat": ("manger", "mangé", "avoir", "mange"),
    "drink": ("boire", "bu", "avoir", "bois"), "call": ("appeler", "appelé", "avoir", "appelle"),
    "send": ("envoyer", "envoyé", "avoir", "envoie"), "ask": ("demander", "demandé", "avoir", "demande"),
    "tell": ("dire", "dit", "avoir", "dis"), "carry": ("porter", "porté", "avoir", "porte"),
    "bring": ("apporter", "apporté", "avoir", "apporte"), "leave": ("partir", "parti", "être", "pars"),
    "stay": ("rester", "resté", "être", "reste"), "open": ("ouvrir", "ouvert", "avoir", "ouvre"),
    "close": ("fermer", "fermé", "avoir", "ferme"), "sleep": ("dormir", "dormi", "avoir", "dors"),
    "cost": ("coûter", "coûté", "avoir", "coûte"), "pick": ("prendre", "pris", "avoir", "prends"),
    "stand": ("rester debout", "resté debout", "être", "reste debout"), "hold": ("tenir", "tenu", "avoir", "tiens"),
    "climb": ("monter", "monté", "être", "monte"), "turn": ("tourner", "tourné", "avoir", "tourne"),
    "run": ("courir", "couru", "avoir", "cours"), "walk": ("marcher", "marché", "avoir", "marche"),
    "show": ("montrer", "montré", "avoir", "montre"), "sabi": ("savoir", "su", "avoir", "sache"),
    "komot": ("sortir", "sorti", "être", "sors"), "tif": ("voler", "volé", "avoir", "vole"),
    "dance": ("danser", "dansé", "avoir", "danse"), "talk": ("parler", "parlé", "avoir", "parle"),
    "look": ("regarder", "regardé", "avoir", "regarde"), "want": ("vouloir", "voulu", "avoir", "veuille"),
    "need": ("avoir besoin de", "eu besoin de", "avoir", "aie besoin de"), "like": ("aimer", "aimé", "avoir", "aime"),
    "love": ("aimer", "aimé", "avoir", "aime"), "help": ("aider", "aidé", "avoir", "aide"),
    "think": ("penser", "pensé", "avoir", "pense"), "queue": ("faire la queue", "fait la queue", "avoir", "fais la queue"),
    "increase": ("augmenter", "augmenté", "avoir", "augmente"), "enter": ("entrer", "entré", "être", "entre"),
    "fry": ("faire frire", "fait frire", "avoir", "fais frire"), "prepare": ("préparer", "préparé", "avoir", "prépare"),
    "block": ("boucher", "bouché", "avoir", "bouche"), "read": ("lire", "lu", "avoir", "lis"), "tchop": ("manger", "mangé", "avoir", "mange"),
}
# 3rd-person singular / plural present for French (regular -er/-re/-ir handled by rule, exceptions here)
FR_PRES = {
    "aller": ("va", "vont"), "être": ("est", "sont"), "faire": ("fait", "font"), "dire": ("dit", "disent"),
    "prendre": ("prend", "prennent"), "venir": ("vient", "viennent"), "devenir": ("devient", "deviennent"),
    "voir": ("voit", "voient"), "savoir": ("sait", "savent"), "boire": ("boit", "boivent"),
    "vendre": ("vend", "vendent"), "attendre": ("attend", "attendent"), "conduire": ("conduit", "conduisent"),
    "dormir": ("dort", "dorment"), "partir": ("part", "partent"), "ouvrir": ("ouvre", "ouvrent"),
    "courir": ("court", "courent"), "tenir": ("tient", "tiennent"), "remplir": ("remplit", "remplissent"),
    "finir": ("finit", "finissent"), "faire payer": ("fait payer", "font payer"), "s'asseoir": ("s'assoit", "s'assoient"),
    "se détendre": ("se détend", "se détendent"), "arriver": ("arrive", "arrivent"),
}
FR_PRES_1S = {"aller": "vais", "être": "suis", "faire": "fais", "dire": "dis", "prendre": "prends", "venir": "viens",
              "voir": "vois", "savoir": "sais", "boire": "bois", "vendre": "vends", "attendre": "attends"}
FR_PRES_1P = {"aller": "allons", "être": "sommes", "faire": "faisons", "dire": "disons", "prendre": "prenons",
              "venir": "venons", "voir": "voyons", "savoir": "savons", "boire": "buvons", "vendre": "vendons",
              "attendre": "attendons", "commencer": "commençons", "manger": "mangeons", "voyager": "voyageons"}
STATE_VERBS = {"stuck"}
NOUN_LIKE = {TokenType.NOUN, TokenType.PROPER_NOUN, TokenType.PRONOUN, TokenType.NUMBER, TokenType.ARTICLE}
PRON_EN = {"yu": ("you", "tu", "2s"), "mi": ("I", "je", "1s"), "wi": ("we", "nous", "1p"),
           "wuna": ("you all", "vous", "2p"), "una": ("you all", "vous", "2p"), "i": ("I", "je", "1s"), "we": ("we", "nous", "1p"), "you": ("you", "tu", "2s"), "they": ("they", "ils", "3p"),
           "it": ("it", "il", "3s"), "she": ("she", "elle", "3s"), "he": ("he", "il", "3s"), "him": ("him", "lui", "3s"), "her": ("her", "elle", "3s"), "it's": ("it's", "c'est", "3s")}
OBJ_EN = {"i": "me", "we": "us", "you": "you", "they": "them"}


POSSESSIVE_FR = {"my": ("mon", "ma", "mes"), "your": ("ton", "ta", "tes"), "our": ("notre", "notre", "nos"),
                 "their": ("leur", "leur", "leurs"), "his": ("son", "sa", "ses")}


def _fr_conjugate(verb: str, person: str) -> str:
    """Present tense (only the persons the translator needs)."""
    inf = FR[verb][0] if verb in FR else verb
    if person == "3p":
        if inf in FR_PRES:
            return FR_PRES[inf][1]
        return inf[:-2] + "ent" if inf.endswith("er") else inf
    if person == "1p":
        return FR_PRES_1P.get(inf, inf[:-2] + "ons" if inf.endswith("er") else inf)
    if person == "1s":
        if inf in FR_PRES_1S:
            return FR_PRES_1S[inf]
        return inf[:-2] + "e" if inf.endswith("er") else inf
    if person == "2s":
        if inf in FR_PRES_1S:
            return FR_PRES_1S[inf] if not inf.endswith("er") and inf not in ("aller", "être") else {"aller": "vas", "être": "es"}.get(inf, FR_PRES_1S[inf])
        return inf[:-2] + "es" if inf.endswith("er") else inf
    if inf in FR_PRES:
        return FR_PRES[inf][0]
    return inf[:-2] + "e" if inf.endswith("er") else inf


PAST_EN = {"go": "went", "eat": "ate", "see": "saw", "come": "came", "give": "gave", "take": "took", "sit": "sat",
           "say": "said", "buy": "bought", "know": "knew", "tell": "told", "bring": "brought", "leave": "left",
           "drink": "drank", "run": "ran", "pay": "paid", "sell": "sold", "fall": "fell", "sleep": "slept",
           "drive": "drove", "stand": "stood", "hold": "held", "become": "became", "do": "did", "be": "was",
           "tchop": "ate", "hala": "gave", "sabi": "knew", "cut": "cut", "stuck": "was stuck"}


def _en_forms(base: str) -> Tuple[str, str, str]:
    if base in EN_IRREG:
        return EN_IRREG[base]
    third = base + ("es" if base.endswith(("s", "sh", "ch", "x")) else "s")
    pp = base + ("d" if base.endswith("e") else "ed")
    ing = (base[:-1] if base.endswith("e") else base) + "ing"
    return third, pp, ing


def _en_base(base: str) -> str:
    return EN_BASE.get(base, base)


def _be(person: str, lang: str) -> str:
    if lang == "en":
        return {"1s": "am", "3s": "is"}.get(person, "are")
    return {"1s": "suis", "2s": "es", "3s": "est", "1p": "sommes", "3p": "sont"}.get(person, "est")


def _have(person: str, lang: str) -> str:
    if lang == "en":
        return "has" if person == "3s" else "have"
    return {"1s": "ai", "2s": "as", "3s": "a", "1p": "avons", "3p": "ont"}.get(person, "a")


# ---------------------------------------------------------------------------
# Expressions (idioms): translated by SENSE, not word by word.
# key = the clause in lower case without punctuation
# value = (English, French, English as a question, French as a question)  - question forms used when the
#         clause ends with "?" (None = same as the statement)
# ---------------------------------------------------------------------------
IDIOMS: Dict[str, Tuple[str, str, object, object]] = {
    "you dey ok": ("you are alright", "tu vas bien", "are you alright", "tu vas bien"),
    "you dey dey ok so": ("you really are fine", "tu vas vraiment bien", "are you normal", "tu es normal"),
    "you dey ok so": ("you are fine, then", "tu vas bien, alors", "are you sure you are alright", "tu es sûr que ça va"),
    "you dey craze": ("you are crazy", "tu es fou", "are you crazy", "tu as perdu la tête"),
    "you don craze": ("you have gone crazy", "tu es devenu fou", "have you gone crazy", "tu as perdu la tête"),
    "you don mad": ("you have gone mad", "tu es devenu fou", "have you gone mad", "tu as perdu la tête"),
    "how you dey": ("how are you", "comment vas-tu", None, None),
    "how you di do": ("how are you", "comment vas-tu", None, None),
    "how body": ("how are you", "comment ça va", None, None),
    "how far": ("what's up", "quoi de neuf", None, None),
    "i dey": ("I am fine", "je vais bien", None, None),
    "i dey fine": ("I am fine", "je vais bien", None, None),
    "i dey ok": ("I am alright", "ça va", None, None),
    "i dey come": ("I am coming, I'll be right back", "j'arrive", None, None),
    "wetin dey happen": ("what is going on", "qu'est-ce qui se passe", None, None),
    "wetin happen": ("what happened", "qu'est-ce qui s'est passé", None, None),
    "wetin be dis": ("what is this", "qu'est-ce que c'est", None, None),
    "wetin be that": ("what is that", "qu'est-ce que c'est", None, None),
    "wetin you dey do": ("what are you doing", "qu'est-ce que tu fais", None, None),
    "wetin you want": ("what do you want", "qu'est-ce que tu veux", None, None),
    "no wahala": ("no problem", "pas de problème", None, None),
    "e no easy": ("it is not easy", "ce n'est pas facile", None, None),
    "e don do": ("that is enough", "ça suffit", None, None),
    "na so": ("that is how it is", "c'est comme ça", None, None),
    "na wa": ("wow, that is something", "eh ben dis donc", None, None),
    "i no sabi": ("I don't know", "je ne sais pas", None, None),
    "i don tire": ("I am tired of it", "j'en ai marre", None, None),
    "wait small": ("wait a moment", "attends un instant", None, None),
    "abeg": ("please", "s'il te plaît", None, None),
    "thank you": ("thank you", "merci", None, None),
}


class Translator:
    def __init__(self):
        self.lexer = LexicalAnalyzer()
        self.unknown: List[str] = []

    # -- public ------------------------------------------------------------
    def translate(self, text: str, lang: str = "en") -> Tuple[str, str]:
        """Return (translation, method) where method is 'verified' or 'automatic'."""
        lang = "fr" if lang.lower().startswith("f") else "en"
        hit = _VERIFIED_INDEX.get(_norm(text))
        if hit:
            return hit[lang], "verified"
        return self._auto(text, lang), "automatic"

    # -- automatic engine --------------------------------------------------
    def _auto(self, text: str, lang: str) -> str:
        self.unknown = []
        self.lang = lang
        tokens = [t for t in self.lexer.tokenize(text) if t.type != TokenType.EOF]
        clauses: List[Tuple[List[Token], str]] = []
        cur: List[Token] = []
        for t in tokens:
            if t.type in (TokenType.CONNECTOR, TokenType.PUNCTUATION):
                if cur:
                    clauses.append((cur, t.value if t.value in ",.!?" else ("," if t.value in ("and", "but", "or") else "")))
                    if t.value in ("but", "and", "or"):
                        clauses[-1] = (clauses[-1][0], ",")
                        cur = [t]
                        continue
                    cur = []
                elif t.value in ",.!?" and clauses:
                    clauses[-1] = (clauses[-1][0], t.value)
            else:
                cur.append(t)
        if cur:
            clauses.append((cur, ""))
        pieces = []
        for toks, sep in clauses:
            s = self._clause(toks, lang, sep)
            if s:
                pieces.append((s, sep))
        out = ""
        for i, (s, sep) in enumerate(pieces):
            out += s
            if sep in ("!", "?") and lang == "fr":
                out += " " + sep
            else:
                out += sep
            if i < len(pieces) - 1 and sep not in ("",):
                out += " "
            elif i < len(pieces) - 1:
                out += " "
        out = out.strip()
        out = re.sub(r"\s+([,.])", r"\1", out)
        out = re.sub(r"\b(well|quickly|vite|bien) \1\b", r"\1", out)
        out = re.sub(r"\b(worn|wear|wears|wearing|fill|fills|filled) (out|up) (me|us|it|you|them|him|her)\b", r"\1 \3 \2", out)
        if lang == "fr":
            out = re.sub(r"\btrop trop\b", "trop", out)
            for a, b in ((r"\bà le\b", "au"), (r"\bà les\b", "aux"), (r"\bde le\b", "du"), (r"\bde les\b", "des")):
                out = re.sub(a, b, out)
        if out and out[-1] not in ".!?" and not (lang == "fr" and out.endswith((" !", " ?"))):
            out += "."
        out = re.sub(r"([.!?]) +([a-zà-ÿ])", lambda m: m.group(1) + " " + m.group(2).upper(), out)
        if out:
            out = out[0].upper() + out[1:]
        return out

    # helpers ---------------------------------------------------------------
    def _word(self, tok: Token, lang: str) -> str:
        i = 0 if lang == "en" else 1
        v = tok.value.lower()
        if tok.type == TokenType.PROPER_NOUN:
            return PROPER.get(v, (tok.value, tok.value))[i]
        if tok.type == TokenType.NUMBER:
            return NUMBERS.get(v, (tok.value, tok.value))[i]
        if tok.type == TokenType.ADJECTIVE:
            return ADJ.get(v, (v, v))[i]
        if tok.type == TokenType.ADVERB:
            return ADV.get(v, (v, v))[i]
        if tok.type == TokenType.PREPOSITION:
            return PREP.get(v, (v, v))[i]
        if tok.type == TokenType.INTERJECTION:
            return INTERJ.get(v, (v, v))[i]
        if tok.type == TokenType.CODE_MIXED:
            return CODE.get(re.sub(r"\s+", " ", v), (v, v))[i]
        if tok.type == TokenType.QUESTION_WORD:
            return QWORDS.get(v, (v, v))[i]
        if tok.type == TokenType.NOUN:
            if v in NOUNS:
                return NOUNS[v][i]
            if not tok.value[:1].isupper():
                self.unknown.append(tok.value)
            return tok.value
        return tok.value

    def _person(self, subj: List[Token]) -> str:
        if not subj:
            return "3s"
        first = subj[-1] if subj[-1].type == TokenType.PRONOUN else subj[0]
        if first.type == TokenType.PRONOUN:
            return PRON_EN.get(first.value.lower(), ("", "", "3s"))[2]
        last = subj[-1].value.lower()
        if last in NOUNS:
            if getattr(self, "lang", "en") == "en":
                if NOUNS[last][0].endswith("s") or last == "police":
                    return "3p"
            elif NOUNS[last][3]:
                return "3p"
        return "3s"

    def _np(self, toks: List[Token], lang: str, obj: bool = False, mode: str = "subj") -> str:
        """Translate a noun phrase (article / numbers / nouns / pronoun)."""
        if not toks:
            return ""
        if len(toks) == 1 and toks[0].type == TokenType.PRONOUN:
            v = toks[0].value.lower()
            if lang == "en":
                return OBJ_EN.get(v, PRON_EN.get(v, (v,))[0]) if obj else PRON_EN.get(v, (toks[0].value,))[0]
            return {"i": "moi" if obj else "je", "you": "toi" if obj else "tu", "we": "nous",
                    "they": "eux" if obj else "ils"}.get(v, PRON_EN.get(v, ("", v))[1])
        art = None
        body = []
        for t in toks:
            if t.type == TokenType.ARTICLE and art is None and not body:
                art = {"dis": "this", "dat": "that"}.get(t.value.lower(), t.value.lower())
            else:
                body.append(t)
        words = [self._word(t, lang) for t in body]
        head = body[-1].value.lower() if body else ""
        entry = NOUNS.get(head)
        if lang == "en":
            phrase = " ".join(words)
            if art in ("the", "this", "that", "these", "those", "a", "an", "my", "your", "our", "their", "his"):
                if art in ("a", "an"):
                    art = "an" if phrase[:1].lower() in "aeiou" else "a"
                if entry and head in ("light", "traffic", "internet"):
                    art = "the" if art in ("the", None) else art
                phrase = f"{art} {phrase}"
            elif mode != "frag" and entry and not entry[3] and body and body[0].type == TokenType.NOUN and head in ("light", "network", "road", "class", "pump", "taxi", "car", "lecture", "bendskin", "prof", "police") and len(body) == 1:
                phrase = f"the {phrase}"
            return phrase
        # French
        if not entry:
            return " ".join(words)
        gender, plural = entry[2], entry[3]
        name = " ".join(w for w in words)
        vowel = name[:1].lower() in "aeiouhéèêàâîôû"
        if art in ("the",):
            d = "les" if plural else ("l'" if vowel else ("le" if gender == "m" else "la"))
            return d + ("" if d.endswith("'") else " ") + name
        if art in ("this", "that", "these", "those"):
            d = "ces" if plural else ("cet" if gender == "m" and vowel else ("ce" if gender == "m" else "cette"))
            return f"{d} {name}"
        if art in POSSESSIVE_FR:
            m, f, pl = POSSESSIVE_FR[art]
            d = pl if plural else (m if gender == "m" or vowel else f)
            return f"{d} {name}"
        if art in ("a", "an"):
            return ("des " if plural else ("un " if gender == "m" else "une ")) + name
        if body and body[0].value.lower() == "your":
            return ("vos " if plural else "votre ") + " ".join(words[1:])
        if body and body[0].type in (TokenType.PROPER_NOUN, TokenType.NUMBER):
            return name
        if mode == "frag":
            return name
        if mode == "obj":   # bare object: partitive / indefinite plural
            if plural:
                return "des " + name
            if head in ("money", "food", "petrol", "water", "fuel", "rain", "mud"):
                return ("de l'" + name) if vowel else (("du " if gender == "m" else "de la ") + name)
            return ("un " if gender == "m" else "une ") + name
        d = "les" if plural else ("l'" if vowel else ("le" if gender == "m" else "la"))
        return d + ("" if d.endswith("'") else " ") + name

    def _split_np(self, toks: List[Token]) -> Tuple[List[Token], List[Token]]:
        """Split leading noun phrase tokens from the rest."""
        i = 0
        while i < len(toks) and toks[i].type in NOUN_LIKE:
            i += 1
        return toks[:i], toks[i:]

    def _comps(self, toks: List[Token], lang: str, agree: Tuple[str, bool] = ("m", False)) -> str:
        """Complements: NPs, prepositional phrases, adverbs, adjectives, particles."""
        out: List[str] = []
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.type in NOUN_LIKE:
                j = i
                while j < len(toks) and toks[j].type in NOUN_LIKE:
                    j += 1
                prev_prep = i > 0 and toks[i - 1].type == TokenType.PREPOSITION
                out.append(self._np(toks[i:j], lang, obj=True, mode="prep" if prev_prep else "obj"))
                i = j
            elif t.type == TokenType.PIDGIN_MARKER:
                v = t.value.lower()
                if v == "small":
                    out.append("a little" if lang == "en" else "un peu")
                elif v == "am":
                    out.append("it" if lang == "en" else "le")
                elif v == "me":
                    out.append("me" if lang == "en" else "moi")
                i += 1
            elif t.type == TokenType.PREPOSITION:
                v = t.value.lower()
                if v == "for" and i + 1 < len(toks) and toks[i + 1].value.lower() == "front":
                    out.append("at the front" if lang == "en" else "devant")
                    i += 2
                    continue
                if v == "for" and i + 1 < len(toks) and toks[i + 1].value.lower() in ("quarter", "quartier"):
                    out.append("in the" if lang == "en" else "dans le")
                    i += 1
                    continue
                if v == "since" and i + 1 < len(toks) and toks[i + 1].value.lower() == "morning":
                    out.append("since morning" if lang == "en" else "depuis ce matin")
                    i += 2
                    continue
                out.append(self._word(t, lang))
                i += 1
            elif t.type == TokenType.NEGATION:
                out.append("no" if lang == "en" else "pas de")
                i += 1
            else:
                w = self._word(t, lang)
                if w and lang == "fr" and t.type == TokenType.ADJECTIVE and w not in ("trop", "en panne"):
                    if agree[0] == "f" and not w.endswith("e"):
                        w += "e"
                    if agree[1] and not w.endswith("s"):
                        w += "s"
                if w:
                    out.append(w)
                i += 1
        return " ".join(x for x in out if x)

    # clause ------------------------------------------------------------------
    def _idiom(self, toks: List[Token], lang: str, sep: str = ""):
        """Translate an expression by its sense. Returns None when the clause is not a known expression."""
        words = [t.value.lower() for t in toks if t.type not in (TokenType.PUNCTUATION, TokenType.CONNECTOR)]
        entry = IDIOMS.get(" ".join(words))
        if not entry:
            return None
        en, fr, enq, frq = entry
        if sep == "?":
            en = enq or en
            fr = frq or fr
        return en if lang == "en" else fr

    def _clause(self, toks: List[Token], lang: str, sep: str = "") -> str:
        hit = self._idiom(toks, lang, sep)
        if hit is not None:
            return hit
        # emphatic "dey dey" -> one "dey"
        squeezed = []
        for t in toks:
            if squeezed and t.type == TokenType.PIDGIN_VERB and squeezed[-1].type == TokenType.PIDGIN_VERB                     and t.value.lower() == squeezed[-1].value.lower() == "dey":
                continue
            squeezed.append(t)
        toks = squeezed
        toks = [t for t in toks if not (t.type == TokenType.PIDGIN_MARKER and t.value.lower() == "na")]
        if not toks:
            return ""
        # leading interjection / code-mixed particles
        lead: List[str] = []
        while toks and toks[0].type in (TokenType.INTERJECTION, TokenType.CODE_MIXED):
            if toks[0].type == TokenType.CODE_MIXED and toks[0].value.lower().startswith("je") and len(toks) > 1:
                break
            w = self._word(toks[0], lang)
            if w:
                lead.append(w)
            toks = toks[1:]
        trail: List[str] = []
        while toks and toks[-1].type == TokenType.INTERJECTION:
            w = self._word(toks[-1], lang)
            if w:
                trail.insert(0, w)
            toks = toks[:-1]
        if [t.value.lower() for t in toks] == ["thank", "you"]:
            body = "thank you" if lang == "en" else "merci"
        else:
            body = self._body(toks, lang) if toks else ""
        parts = [p for p in lead + [body] + trail if p]
        return ", ".join(parts) if lead and not body else " ".join(parts)

    def _body(self, toks: List[Token], lang: str) -> str:
        t0 = toks[0]
        # "Je wanda why ..." (indirect question)
        if t0.type == TokenType.CODE_MIXED and len(toks) > 1:
            return self._word(t0, lang) + " " + self._body(toks[1:], lang)
        if t0.type == TokenType.QUESTION_WORD:
            return self._question(toks, lang)
        if t0.type == TokenType.SUBJUNCTIVE:
            return self._subjunctive(toks[1:], lang, start=True)
        # split at a mid-clause "make"
        for k, t in enumerate(toks):
            if t.type == TokenType.SUBJUNCTIVE and k > 0:
                main = self._body(toks[:k], lang)
                sub = self._subjunctive(toks[k + 1:], lang, start=False)
                return f"{main} {sub}"
        if t0.type == TokenType.VERB:
            return self._imperative(toks, lang)
        if t0.type == TokenType.NEGATION and len(toks) >= 1 and all(t.type != TokenType.VERB for t in toks):
            return self._comps(toks, lang)
        if t0.type == TokenType.PREPOSITION:
            return self._prep_clause(toks, lang)
        subj, rest = self._split_np(toks)
        if not rest:
            return self._np(subj, lang, mode="frag")
        return self._declarative(subj, rest, lang)

    def _prep_clause(self, toks: List[Token], lang: str) -> str:
        prep = toks[0].value.lower()
        subj, rest = self._split_np(toks[1:])
        if prep in ("after", "before") and rest and rest[0].type == TokenType.VERB:
            v = rest[0].value.lower()
            if v == "finish":
                if lang == "en":
                    return f"{PREP[prep][0]} {self._np([Token(TokenType.ARTICLE, 'the', 0, 0)] + subj, lang)} is over"
                return f"{PREP[prep][1]} {self._np([Token(TokenType.ARTICLE, 'the', 0, 0)] + subj, lang)}"
        return self._comps(toks, lang)

    def _question(self, toks: List[Token], lang: str) -> str:
        qw = self._word(toks[0], lang)
        rest = toks[1:]
        if not rest:
            return qw
        if toks[0].value.lower() == "how" and rest[0].value.lower() == "much":
            tail = self._comps(rest[1:], lang)
            return (f"how much {tail}" if lang == "en" else f"c'est combien {tail}").strip()
        # "How you dey" -> "How are you"
        subj, after = self._split_np(rest)
        if subj and after and after[0].type == TokenType.PIDGIN_VERB and after[0].value.lower() == "dey" and len(after) == 1:
            return (f"{qw} are you" if lang == "en" else f"{qw} vas-tu") if toks[0].value.lower() == "how" else f"{qw} {self._np(subj, lang)}"
        if subj and after:
            person = self._person(subj)
            s, aux, tail = self._verb_group(subj, after, lang, split=True)
            if aux:
                subj_s = self._np(subj, lang)
                if lang == "en":
                    return f"{qw} {aux} {subj_s} {tail}".strip()
                return f"{qw} est-ce que {s}".strip()
            return f"{qw} {self._declarative(subj, after, lang)}"
        if subj is not None and not after:
            return f"{qw} {self._comps(rest, lang)}".strip()
        return f"{qw} {self._comps(rest, lang)}".strip()

    def _imperative(self, toks: List[Token], lang: str) -> str:
        verbs = []
        i = 0
        while i < len(toks) and toks[i].type == TokenType.VERB:
            verbs.append(toks[i].value.lower())
            i += 1
        rest = self._comps(toks[i:], lang)
        if lang == "en":
            vs = " and ".join(_en_base(v) for v in verbs)
            if verbs[0] in ("hala",):
                vs = "give"
            out = f"{vs} {rest}".strip()
            out = re.sub(r"\b(drop|fill up) me\b", lambda m: f"{m.group(1)} me", out)
            return out
        vs = " ".join(FR[v][3] if v in FR else v for v in verbs[:1])
        if len(verbs) > 1:
            vs += " " + " ".join(FR[v][0] if v in FR else v for v in verbs[1:])
        out = f"{vs} {rest}".strip()
        return re.sub(r"^(\S+) (moi|le|la|les|lui)\b", r"\1-\2", out)

    def _subjunctive(self, toks: List[Token], lang: str, start: bool) -> str:
        subj, rest = self._split_np(toks)
        who = subj[0].value.lower() if subj else ""
        vp = self._infinitive_vp(rest, lang)
        if lang == "en":
            if start:
                if who == "we":
                    return f"let's {vp}"
                if who == "you":
                    return f"please {vp}"
                if who == "i":
                    return f"let me {vp}"
                return f"let {self._np(subj, lang)} {vp}"
            subj_s = self._np(subj, lang)
            return f"so {subj_s} can {vp}"
        if start:
            first, _, remainder = vp.partition(" ")
            if who == "we":
                if first == "aller" and not remainder:
                    return "allons-y"
                return f"{_fr_conjugate_1p(first)} {remainder}".strip()
            return f"veuillez {vp}" if who == "you" else f"que {self._np(subj, lang)} {vp}"
        return f"pour que {self._np(subj, lang)} puisse {vp}"

    def _infinitive_vp(self, toks: List[Token], lang: str) -> str:
        verbs = []
        i = 0
        while i < len(toks) and toks[i].type in (TokenType.VERB, TokenType.PIDGIN_VERB, TokenType.NEGATION):
            verbs.append(toks[i])
            i += 1
        rest = self._comps(toks[i:], lang)
        words = []
        for v in verbs:
            b = v.value.lower()
            if v.type == TokenType.VERB:
                words.append(_en_base(b) if lang == "en" else (FR[b][0] if b in FR else b))
            elif v.type == TokenType.NEGATION:
                words.append("not" if lang == "en" else "ne pas")
        return (" ".join(words) + " " + rest).strip()

    def _declarative(self, subj: List[Token], rest: List[Token], lang: str) -> str:
        s, aux, tail = self._verb_group(subj, rest, lang, split=False)
        return s

    def _verb_group(self, subj: List[Token], rest: List[Token], lang: str, split: bool):
        """Return (sentence, aux_for_inversion, remainder)."""
        person = self._person(subj)
        subj_s = self._np(subj, lang)
        i = 0
        neg = False
        aux = None
        if i < len(rest) and rest[i].type == TokenType.NEGATION:
            neg = True
            i += 1
        if i < len(rest) and rest[i].type == TokenType.PIDGIN_VERB:
            aux = rest[i].value.lower()
            i += 1
        verbs: List[str] = []
        while i < len(rest) and rest[i].type == TokenType.VERB:
            verbs.append(rest[i].value.lower())
            i += 1
        comps_toks = rest[i:]
        subj_key = subj[-1].value.lower() if subj else ""
        ent = NOUNS.get(subj_key)
        comps = self._comps(comps_toks, lang, agree=(ent[2] if ent else "m", bool(ent and ent[3])))
        first = verbs[0] if verbs else None

        def fmt(auxs: str, main: str, inv_aux: Optional[str] = None):
            sent = " ".join(x for x in (subj_s, auxs, main, comps) if x).strip()
            return sent, inv_aux, " ".join(x for x in (main, comps) if x).strip()

        en = lang == "en"
        # special idioms
        if first == "fall" and subj_key == "rain" and aux == "dey":
            return ("it is raining " + comps).strip() if en else ("il pleut " + comps).strip(), None, ""
        if first in ("cut", "go") and subj_key == "light" and aux in ("done", "don"):
            main = "gone out" if en else "coupé"
            a = _have(person, lang) if en else _be(person, lang)
            return fmt(a, main, a)
        if first == "do" and aux == "dey":
            a = _be(person, lang)
            main = "acting up" if en else "fait des siennes"
            return fmt(a if en else "", main if en else main, a) if en else (f"{subj_s} {main} {comps}".strip(), None, "")
        if first == "empty" and aux in ("done", "don"):
            a = _have(person, lang) if en else _be(person, lang)
            main = "run empty" if en else "vide"
            return fmt(a, main, a)
        if first == "say":
            if comps_toks and comps_toks[0].type in (TokenType.VERB,):
                pass
            if len(verbs) > 1:
                vs = " and ".join(_en_base(v) for v in verbs[1:]) if en else " ".join(FR[v][0] if v in FR else v for v in verbs[1:])
                joined = f"to {vs}" if en else f"de {vs}"
                return fmt("said" if en else "a dit", joined, None)
            return fmt("", ("say there is" if en else "on dit qu'il y a"), None)
        if first == "stuck":
            a = _be(person, lang)
            return fmt(a, "stuck" if en else "coincé" + ("e" if subj_key in NOUNS and NOUNS[subj_key][2] == "f" else ""), a)
        # aspect handling
        if aux == "di":
            aux = "dey"
        if aux in ("bin", "wan", "mos") and verbs:
            b = " ".join(_en_base(x) if en else (FR[x][0] if x in FR else x) for x in verbs)
            if aux == "bin":
                if en:
                    v0 = verbs[0]
                    past = PAST_EN.get(v0, _en_forms(v0)[1])
                    rest_v = " ".join(_en_base(x) for x in verbs[1:])
                    return fmt("", (past + " " + rest_v).strip(), None)
                entry = FR.get(verbs[0])
                a = _have(person, lang) if not entry or entry[2] == "avoir" else _be(person, lang)
                pp = entry[1] if entry else verbs[0]
                return f"{subj_s} {a} {pp} {comps}".strip(), None, ""
            if aux == "wan":
                if en:
                    return fmt("wants to" if person == "3s" else "want to", b, None)
                return f"{subj_s} {dict(zip(('1s', '2s', '3s', '1p', '2p', '3p'), ('veux', 'veux', 'veut', 'voulons', 'voulez', 'veulent'))).get(person, 'veut')} {b} {comps}".strip(), None, ""
            if en:
                return fmt("must", b, None)
            return f"{subj_s} {dict(zip(('1s', '2s', '3s', '1p', '2p', '3p'), ('dois', 'dois', 'doit', 'devons', 'devez', 'doivent'))).get(person, 'doit')} {b} {comps}".strip(), None, ""
        if aux == "dey" and not verbs:
            a = _be(person, lang)
            if not comps:
                return f"{subj_s} {a} fine".strip() if en else f"{subj_s} {a} bien".strip(), a, ""
            if comps.startswith(("for ", "pour ")):
                comps_fixed = ("at " + comps[4:]) if en else ("à " + comps[5:])
                return f"{subj_s} {a} {comps_fixed}".strip(), a, ""
            return fmt(a, "", a)
        if aux == "dey":
            v = verbs[0]
            if en:
                a = _be(person, lang) + (" not" if neg else "")
                ing = _en_forms(v)[2]
                extra = ""
                if len(verbs) > 1:
                    extra = "to " + " ".join(_en_base(x) for x in verbs[1:])
                return fmt(a, f"{ing} {extra}".strip(), a)
            a = _be(person, lang)
            inf = FR[v][0] if v in FR else v
            de = "d'" if inf[:1] in "aeiouhéè" else "de "
            return (f"{subj_s} {a} en train {de}{inf} {comps}".strip(), a, "")
        if aux in ("done", "don"):
            if not verbs:
                if comps_toks and comps_toks[0].type in (TokenType.ADJECTIVE, TokenType.ADVERB):
                    a = _be(person, lang)
                    return fmt(a, "", a)
                return fmt("is" if en else "est", "over" if en else "terminé", None)
            v = verbs[0]
            if en:
                a = _have(person, lang)
                if v == "try" and len(verbs) > 1:
                    main = "tried to " + " ".join(_en_base(x) for x in verbs[1:])
                    return fmt(a, main, a)
                if v in ("become",):
                    return fmt(a, "become", a)
                if v == "fall" and subj_key == "rain":
                    return f"it has rained {comps}".strip(), a, ""
                return fmt(a, _en_forms(v)[1], a)
            entry = FR.get(v)
            aux_fr = entry[2] if entry else "avoir"
            a = _have(person, lang) if aux_fr == "avoir" else _be(person, lang)
            if v == "try" and len(verbs) > 1:
                return f"{subj_s} {a} essayé de {' '.join(FR[x][0] if x in FR else x for x in verbs[1:])} {comps}".strip(), a, ""
            pp = entry[1] if entry else v
            if aux_fr == "être" and person == "3p":
                pp += "s"
            return f"{subj_s} {a} {pp} {comps}".strip(), a, ""
        if aux == "fit":
            if verbs:
                b = " ".join(_en_base(x) if en else (FR[x][0] if x in FR else x) for x in verbs[:1])
                if en:
                    return fmt("can't" if neg else "can", b, "can't" if neg else "can")
                return f"{subj_s} {'ne peux pas' if person in ('1s', '2s') and neg else ('ne peut pas' if neg else 'peut')} {b} {comps}".strip(), None, ""
            return fmt("can't" if neg else "can", "", None) if en else (f"{subj_s} {'ne peut pas' if neg else 'peut'} {comps}".strip(), None, "")
        # "never": no do-support in English, ne ... jamais in French
        pre_never = [t for t in rest[:1] if t.type == TokenType.ADVERB and t.value.lower() in ("never", "neva", "neba")]
        if not aux and pre_never and len(rest) > 1 and rest[1].type == TokenType.VERB:
            v = rest[1].value.lower()
            comps = self._comps(rest[2:], lang)
            if en:
                verb_s = _en_forms(v)[0] if person == "3s" else _en_base(v)
                return " ".join(x for x in (subj_s, "never", verb_s, comps) if x), None, ""
            return " ".join(x for x in (subj_s, "ne", _fr_conjugate(v, person), "jamais", comps) if x), None, ""
        # no aux
        if first == "go" and len(verbs) == 1 and comps_toks and comps_toks[0].type in NOUN_LIKE:
            ent2 = NOUNS.get(comps_toks[-1].value.lower())
            if en:
                return f"{subj_s} will go to the {comps}".strip() if False else f"{subj_s} {'goes' if person == '3s' else 'go'} to the {comps}".strip(), None, ""
            g = ent2[2] if ent2 else "m"
            name = re.sub(r"^(le |la |l'|un |une |du |de la |de l')", "", comps)
            prep = "à l'" if name[:1] in "aeiouhéè" else ("au " if g == "m" else "à la ")
            return f"{subj_s} {_fr_conjugate('go', person)} {prep}{name}".strip(), None, ""
        if first == "go":
            if len(verbs) > 1:
                b = " ".join(_en_base(x) if en else (FR[x][0] if x in FR else x) for x in verbs[1:])
                if en:
                    return fmt("will", b, "will")
                return f"{subj_s} {_fr_conjugate('go', person)} {b} {comps}".strip(), None, ""
            if en:
                return fmt("will", "go", "will")
            return f"{subj_s} {_fr_conjugate('go', person)} aller {comps}".strip(), None, ""
        if not verbs:
            if neg:
                return f"{subj_s} {'is not' if en else 'n’est pas'} {comps}".strip(), None, ""
            if comps_toks and comps_toks[0].type in (TokenType.ADJECTIVE, TokenType.ADVERB, TokenType.PREPOSITION):
                a = _be(person, lang)
                return fmt(a, "", a)
            return f"{subj_s} {comps}".strip(), None, ""
        v = verbs[0]
        if v == "try" and len(verbs) > 1:
            tries = _en_forms(v)[0] if person == "3s" else "try"
            main = tries + " to " + " ".join(_en_base(x) for x in verbs[1:]) if en else f"{_fr_conjugate('try', person)} de {' '.join(FR[x][0] if x in FR else x for x in verbs[1:])}"
            return fmt("", main, None) if en else (f"{subj_s} {main} {comps}".strip(), None, "")
        if en:
            b = _en_base(v)
            if neg:
                return fmt("doesn't" if person == "3s" else "don't", b, "doesn't" if person == "3s" else "don't")
            third = _en_forms(v)[0]
            if v == "charge":
                third = "charges"
            verb_s = third if person == "3s" else b
            if len(verbs) > 1:
                verb_s += " " + " ".join(_en_base(x) for x in verbs[1:])
            return fmt("", verb_s, None)
        fr = _fr_conjugate(v, person)
        if len(verbs) > 1:
            fr += " " + " ".join(FR[x][0] if x in FR else x for x in verbs[1:])
        if neg:
            fr = "ne " + fr.split(" ", 1)[0] + " pas" + (" " + fr.split(" ", 1)[1] if " " in fr else "")
        return f"{subj_s} {fr} {comps}".strip(), None, ""


def _fr_conjugate_1p(inf: str) -> str:
    return FR_PRES_1P.get(inf, inf[:-2] + "ons" if inf.endswith("er") else inf)


_default = Translator()


def translate_ex(text: str, lang: str = "en") -> Dict[str, object]:
    """Like translate() but also returns the words that are not in the lexicon."""
    result, method = _default.translate(text, lang)
    unknown = [] if method == "verified" else sorted(set(w.lower() for w in _default.unknown))
    return {"text": result, "method": method, "unknown": unknown}


def translate(text: str, lang: str = "en") -> Tuple[str, str]:
    """Translate `text` to English ('en') or French ('fr'). Returns (translation, 'verified'|'automatic')."""
    return _default.translate(text, lang)


def main():
    import sys
    text = " ".join(sys.argv[1:]) or "The light done cut again"
    for lang in ("en", "fr"):
        result, method = translate(text, lang)
        print(f"[{lang}] ({method}) {result}")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Built-in vocabulary snapshot + user dictionary hook (see userdict.py)
# ---------------------------------------------------------------------------
BUILTIN_WORDS = (set(NOUNS) | set(PROPER) | set(NUMBERS) | set(ADJ) | set(ADV) | set(PREP) | set(INTERJ) | set(CODE)
                 | set(QWORDS) | set(FR) | set(PRON_EN)
                 | {"dey", "di", "done", "don", "fit", "wan", "mos", "bin", "no", "make", "na", "am", "me", "small",
                    "the", "a", "an", "this", "that", "these", "those", "dis", "dat", "my", "your", "our", "their", "his",
                    "and", "but", "or"})
BUILTIN_IDIOMS = set(IDIOMS)
USER_ADDED = {"IDIOMS": set(), "NOUNS": set(), "PROPER": set(), "ADJ": set(), "ADV": set(), "INTERJ": set(), "FR": set(),
              "EN_IRREG": set(), "EN_BASE": set(), "PAST_EN": set()}


def reload_user_dictionary() -> int:
    import userdict
    return userdict.apply()


import sys as _sys
if "statements" not in _sys.modules:   # statements applies itself when imported first
    import statements  # noqa: F401
if "userdict" not in _sys.modules:   # userdict applies itself when imported first
    import userdict  # noqa: F401  (its module-level apply() loads data/user_dictionary.json)
