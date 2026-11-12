#!/usr/bin/env python3
"""Revisa un texto en busca de señales típicas de escritura de IA.

Cubre las categorías de la guía de Wikipedia "Signs of AI writing" (contenido,
lenguaje, estilo, formato, marcado, comunicación de chatbot, restos de
herramientas) en español, inglés y francés.

Uso:
    python revisar_patrones.py archivo.txt
    cat texto.txt | python revisar_patrones.py

Imprime un informe: frases hechas (con número de línea), densidad de vocabulario
de IA, signos y formato sospechosos, y uniformidad del ritmo.
Siempre termina con código 0. El informe es una guía, no una sentencia: un solo
rasgo no prueba nada, lo que pesa es la densidad.
"""
import re
import statistics
import sys
import unicodedata


def sin_acentos(s):
    """Quita acentos y ñ sin cambiar el largo del texto (para mapear posiciones)."""
    return "".join(unicodedata.normalize("NFD", c)[0] for c in s)


# (categoría, expresión regular). Se aplica a cada línea en minúsculas y sin acentos.
FRASES = [
    # ---- Importancia, legado y tendencias (WP:AILEGACY, WP:AITREND)
    ("importancia inflada", r"\b(desempena|juega|cumple) un papel\b"),
    ("importancia inflada", r"\bpapel (crucial|fundamental|clave|vital|esencial)\b"),
    ("importancia inflada", r"\bplays? an? (crucial|vital|pivotal|key|significant) role\b|\ba (crucial|pivotal|vital|significant|key) (role|moment)\b"),
    ("importancia inflada", r"\b(un|el|este|su) (verdadero |claro |autentico |vivo )?testimonio de\b|\ba testament\b|\bis a (testament|reminder)\b"),
    ("importancia inflada", r"\bpunto de inflexion\b|\bhuella imborrable\b|\blegado (duradero|perdurable)\b|\bun antes y un despues\b"),
    ("importancia inflada", r"\bse (erige|alza|posiciona|consolida) como\b"),
    ("importancia inflada", r"\bpanorama\b.{0,25}\b(evolucion|cambiante)|\bevolving landscape\b|\bconstante evolucion\b"),
    ("importancia inflada", r"\bsienta las bases\b|\ballana el camino\b|\bsetting the stage\b|\bkey turning point\b|\bwatershed moment\b"),
    ("importancia inflada", r"\barroja luz\b|\bpone de relieve\b|\bsubraya (la|el)\b|\bresalta la importancia\b"),
    ("importancia inflada", r"\b(underscores?|highlights?) (its |the )?(importance|significance)\b|\breflects broader\b|\bsymbolizing its\b|\bfocal point\b|\bindelible mark\b|\bdeeply rooted\b|\bleaves a lasting impact\b|\bcontinues to captivate\b|\bmarks? a shift\b|\brepresents a shift\b"),
    ("importancia inflada", r"\bprofondement ancre\b|\btemoigne de\b|\bs'impose comme\b|\bmarque un tournant\b|\bempreinte indelebile\b|\bjoue un role (crucial|essentiel|cle)\b"),
    # ---- Notoriedad y cobertura enlatadas (WP:AIATTR)
    ("notoriedad enlatada", r"\bindependent coverage\b|\b(local|regional|national) media outlets\b|\btrade publications\b|\bwritten by a leading expert\b|\bactive social media presence\b|\b(featured|profiled) in\b"),
    ("notoriedad enlatada", r"\bcobertura independiente\b|\bmedios (locales|regionales|nacionales)\b|\bpresencia (activa|solida) en redes\b|\bexperto lider\b"),
    # ---- Análisis superficial con gerundio (WP:SUPERFICIAL)
    ("gerundio de análisis superficial", r",\s*(highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|contributing to|cultivating|fostering|encompassing|enhancing|showcasing|demonstrating)\b"),
    ("gerundio de análisis superficial", r",\s*(destacando|subrayando|resaltando|asegurando|garantizando|reflejando|contribuyendo|fomentando|abarcando|potenciando|fortaleciendo|promoviendo|demostrando|evidenciando)\b"),
    ("gerundio de análisis superficial", r",\s*(soulignant|reflétant|refletant|contribuant a|renforcant|mettant en avant)\b"),
    ("análisis superficial", r"\bvaluable insights?\b|\b(align|resonate)s? with\b"),
    # ---- Tono promocional (WP:AIPUFFERY)
    ("tono promocional", r"\b(vibrante|enclavado|rico patrimonio|rica historia|belleza natural|amplia gama|gran diversidad|de renombre|a la vanguardia)\b"),
    ("tono promocional", r"\b(vibrant|nestled|boasts a|breathtaking|groundbreaking|renowned|diverse array|exemplifies|commitment to|natural beauty|must-visit|must-see|rich (cultural )?(heritage|history|tapestry)|lasting legacy|enduring legacy)\b"),
    ("tono promocional", r"\b(cuenta con|en el corazon de)\b|\bin the heart of\b|\bau coeur de\b|\briche patrimoine\b"),
    # ---- Conexión vaga (WP:AICONNECT)
    ("conexión vaga", r"\b(in connection (with|to)|connected (with|to)|in association with|associated with)\b|\b(vinculad[oa]s? (a|con)|asociad[oa]s? (a|con)|en relacion con)\b"),
    # ---- Atribución vaga (WP:AIWEASEL)
    ("atribución vaga", r"\b(los expertos (senalan|coinciden|opinan|afirman)|algunos criticos|segun diversos|diversas fuentes|se dice que|muchos consideran|informes del sector|diversos estudios)\b"),
    ("atribución vaga", r"\b(experts (argue|say|agree)|observers have|industry reports|some critics|several (sources|publications)|research has shown|many consider)\b"),
    ("atribución vaga", r"\b(les experts s'accordent|selon certains critiques|de nombreuses etudes)\b"),
    # ---- Retos y futuro (WP:FACESCHALLENGES)
    ("retos y futuro", r"\bdespite (its|these|the)\b.{0,80}\b(challenges|faces)\b|\bfaces several challenges\b|\bcontinues to thrive\b|\bfuture outlook\b|\bchallenges and (legacy|future)\b|\blies in its ability to adapt\b"),
    ("retos y futuro", r"\ba pesar de (sus|los|estos) (desafios|retos)\b|\bperspectivas futuras\b|\bdesafios y oportunidades\b|\bradica en su capacidad\b|\bsigue prosperando\b"),
    ("retos y futuro", r"\bmalgre ces defis\b|\bperspectives d'avenir\b"),
    # ---- Títulos "X y Y"
    ("título 'X y Y'", r"^\s*#*\s*(awards and recognition|recognition|legacy and impact|logros y reconocimientos|premios y reconocimientos|legado e impacto)\s*:?\s*$"),
    # ---- Avisos didácticos
    ("aviso didáctico", r"\bes (importante|fundamental|crucial|esencial) (destacar|senalar|mencionar|recordar|notar|tener en cuenta|considerar)\b"),
    ("aviso didáctico", r"\bcabe (destacar|senalar|mencionar|resaltar|recordar)\b|\bvale la pena (destacar|mencionar|senalar|resaltar)\b|\bhay que tener en cuenta\b"),
    ("aviso didáctico", r"\bit('?s| is) (important|worth|crucial) (to )?(note|noting|remember|consider)\b|\bno discussion would be complete\b|\bit is worth noting\b"),
    ("aviso didáctico", r"\bil est (important|essentiel) de (noter|souligner|rappeler)\b|\bil convient de souligner\b"),
    # ---- Apertura de relleno
    ("apertura de relleno", r"\ben el mundo (actual|de hoy|moderno)\b|\ben la era digital\b|\bhoy en dia\b|\ben un mundo (cada vez mas|en constante)\b"),
    ("apertura de relleno", r"\bimagina un mundo\b|\ba lo largo de la historia\b|\bdesde tiempos inmemoriales\b"),
    ("apertura de relleno", r"\bin today'?s (fast-paced )?(world|digital)\b|\bin the ever-evolving\b|\bin the digital age\b|\bpicture this\b|\bimagine a world\b"),
    ("apertura de relleno", r"\bdans le monde d'aujourd'hui\b|\ba l'ere du numerique\b|\bde nos jours\b"),
    # ---- Cierres y resúmenes
    ("cierre/resumen", r"\b(en conclusion|en resumen|en definitiva|para concluir|en suma|en sintesis|como hemos visto)\b"),
    ("cierre/resumen", r"\bin (conclusion|summary)\b|\bto sum up\b|\ben conclusion\b"),
    ("cierre/resumen", r"^\s*(overall|en general|globalement),"),
    ("cierre/resumen", r"\ben conclusion\b|\ben resume\b|\bpour conclure\b"),
    ("cierre/resumen", r"\bthe possibilities are endless\b|\bonly time will tell\b|\bel futuro (nos )?(depara|espera)\b|\bthe key takeaway\b"),
    # ---- Vocabulario de IA en español y francés
    ("vocabulario de IA", r"\b(adentrarse|adentrarnos|sumergirse|sumergirnos|embarcarse|embarcarnos|desentranar|desmitificar)\b"),
    ("vocabulario de IA", r"\b(multifacetic|holistic|sinergia|paradigma|tapiz|plethora|piedra angular|crisol|mosaico)\w*\b"),
    ("vocabulario de IA", r"\b(plonger dans|s'aventurer|tapisserie|incontournable|foisonnant)\b"),
    ("vocabulario de IA", r"^\s*(ademas|asimismo|additionally|furthermore|moreover|en consecuencia),"),
    ("vocabulario de IA", r"[.!?]\s+(ademas|asimismo|additionally|furthermore|moreover|en consecuencia),"),
    # ---- Cópulas evitadas (WP:AINOCOPULA)
    ("evita 'es/tiene'", r"\b(serves as|stands as|functions as|operates as)\b|\b(marks|represents) (a|an|the)\b|\b(boasts|features|maintains|offers) (a|an)\b"),
    ("evita 'es/tiene'", r"\b(sirve como|funciona como|constituye un|se configura como|dispone de)\b"),
    ("evita 'es/tiene'", r"\brefers to\b|\bse refiere a\b|\bventured into\b|\bincursiono en\b|\bbegan his career as\b"),
    # ---- Paralelismos negativos (WP:AIPARALLEL)
    ("paralelismo negativo", r"\bno solo\b.{0,140}?\bsino\b"),
    ("paralelismo negativo", r"\bno se trata (solo )?de\b.{0,100}?\bsino\b"),
    ("paralelismo negativo", r"\bno es (solo|simplemente|unicamente)\b.{0,100}?\bes\b"),
    ("paralelismo negativo", r"\bmas que (solo |simplemente )?(un|una|el|la)\b"),
    ("paralelismo negativo", r"\bnot only\b.{0,140}?\bbut\b|\bit'?s not (just |only )?[^.]{0,80}?\bit'?s\b|\bnot just\b[^.]{0,80}\bbut\b"),
    ("paralelismo negativo", r"\bit (is|was) not (just|only|merely)\b[^.]{0,100}?\bit'?s\b|\b(is|are) not (just|only|merely)\b[^.]{0,100}?\b(it|they)'?(s|re)\b"),
    ("paralelismo negativo", r"\bne se limite pas\b|\bne (est|sont) pas (seulement|juste)\b|\bnon seulement\b|\bce n'est pas (seulement|juste)\b"),
    ("paralelismo negativo", r"\bno\s+\w+,\s*no\s+\w+,\s*(just|solo|solamente|simplemente)\b"),
    ("paralelismo negativo", r"\bnot an? \w+ but an? \w+\b|\bnot because\b.{0,60}\bbut because\b"),
    ("paralelismo negativo", r"\b(el resultado|the result|lo mejor)\?"),
    # ---- Falso equilibrio y hedging
    ("falso equilibrio", r"\bpor un lado\b.{0,160}\bpor otro\b|\bon the one hand\b.{0,160}\bon the other\b|\bsi bien\b.{0,80}\btambien\b"),
    # ---- Relleno de información faltante y avisos de corte
    ("hueco de información", r"\bas of my last knowledge\b|\bspecific details are (limited|scarce)\b|\bnot widely (available|documented|disclosed)\b|\bbased on available information\b|\bin the (provided|available) sources\b"),
    ("hueco de información", r"\blos detalles (son|estan) limitad|\bno hay mucha informacion\b|\bsegun la informacion disponible\b|\bhasta donde (llega|alcanza) mi (conocimiento|informacion)\b|\bsegun mi ultima actualizacion\b"),
    # ---- Rechazos y charla de chatbot
    ("rechazo/chatbot", r"\bas an ai\b|\bas a large language model\b|\bas an ai language model\b|\bcomo (un )?modelo de lenguaje\b|\bi'?m sorry\b|\blo siento, pero\b"),
    ("charla de chatbot", r"\b(espero que (esto )?(te|le|les) (sirva|ayude)|no dudes en|excelente pregunta|aqui tienes|claro que si|quieres que|hay algo mas en lo que)\b"),
    ("charla de chatbot", r"\b(i hope this helps|let me know|certainly!|of course!|great question|would you like|is there anything else|you'?re absolutely right|here'?s a (template|draft|breakdown))\b"),
    ("charla de chatbot", r"\b(tienes toda la razon|por supuesto!|claro!|sin (lugar a )?dudas?( alguna)?)\b"),
    ("charla de chatbot", r"\b(bien sur !|j'espere que cela vous aide|n'hesitez pas)\b"),
    ("charla de chatbot", r"\b(in this (section|article), we (will|are going to)|this article aims to|en esta seccion veremos|este articulo busca)\b"),
    ("charla de chatbot", r"\bhere are (several|a few|some) (versions|options|variations)\b|\bpero aqui viene\b|\bhere'?s the (kicker|deal|truth)\b|\breal talk\b|\bhot take\b"),
    # ---- Atribución trivial
    ("fuente trivial", r"\baccording to (filings|records|the company'?s)\b"),
    # ---- Restos de herramientas y placeholders
    ("resto de herramienta", r"utm_source=|referrer=grok|turn0search|turn0image|citeturn|contentreference|oaicite|oai_citation|\[cite:|\[attached_file|\[web:\d|grok_card|grok_render|attributableindex|<\|endoftext\|>"),
    ("placeholder", r"\[(tu nombre|your name|insertar|insert|describe|link to)[^\]]*\]|\binsert_source|\bpaste_\w+_here|\b20\d\d-xx-xx\b|\bxxxx\b"),
]
FRASES_COMPILADAS = [(c, re.compile(p, re.IGNORECASE)) for c, p in FRASES]

# Vocabulario de IA en inglés (listas de la guía, todas las épocas). Se cuenta por densidad.
VOCAB_EN = [
    r"additionally", r"align(s|ed|ing)? with", r"boasts?", r"bolstered", r"crucial", r"deep dive",
    r"delv(e|es|ed|ing)", r"emphasiz(e|es|ed|ing)", r"enduring", r"enhanc(e|es|ed|ing|ement)",
    r"foster(s|ed|ing)?", r"garner(s|ed|ing)?", r"highlight(s|ed|ing)?", r"interplay",
    r"intricate", r"intricacies", r"landscape", r"meticulous(ly)?", r"pivotal", r"robust",
    r"showcas(e|es|ed|ing)", r"tapestry", r"testament", r"underscor(e|es|ed|ing)", r"valuable",
    r"vibrant", r"beacon", r"cornerstone", r"demystify", r"embark(s|ed|ing)?", r"game-changer",
    r"holistic", r"myriad", r"nuanced", r"paradigm shift", r"plethora", r"realms?", r"resonat(e|es|ed|ing)",
    r"seamless(ly)?", r"streamline[sd]?", r"synergy", r"unleash(es|ed|ing)?", r"unveil(s|ed|ing)?",
    r"multifaceted", r"leverag(e|es|ed|ing)", r"prioriti[sz](e|es|ed|ing)", r"dependable", r"quietly",
    r"universally", r"causal", r"empirical", r"correlate",
]
VOCAB_EN_RX = re.compile(r"\b(" + "|".join(VOCAB_EN) + r")\b", re.IGNORECASE)

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅❌]")
NEGRITA = re.compile(r"\*\*[^*\n]+\*\*")
VINETA_NEGRITA = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+\*\*[^*\n]+:?\*\*\s*:?", re.MULTILINE)
ENCABEZADO_MD = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
COMILLAS_CURVAS = re.compile("[“”‘’]")
RAYA_SEPARACION = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$", re.MULTILINE)
TABLA_MD = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$", re.MULTILINE)
CERCA_CODIGO = re.compile(r"^\s*```", re.MULTILINE)
VINETA_PUNTO = re.compile("^\\s*•\\s", re.MULTILINE)
ASUNTO = re.compile(r"^\s*(subject|asunto|objet)\s*:", re.IGNORECASE)
TRIO = re.compile(r"\b[\wÀ-ſ-]+, [\wÀ-ſ-]+,? (?:y|e|and|et) [\wÀ-ſ-]+\b", re.IGNORECASE)
FALSO_RANGO = re.compile(r"\b(?:from|desde|de|de la|del)\s+([^,.;:]{3,45}?)\s+(?:to|hasta|a|al)\s+([^,.;:]{3,45})", re.IGNORECASE)
RATHER_THAN = re.compile(r"\brather than\b|\ben lugar de\b|\ben vez de\b|\bplutot que\b", re.IGNORECASE)

PALABRAS_MENORES = {"and", "the", "of", "for", "in", "on", "to", "a", "an", "y", "e", "o", "u", "de", "del", "la", "el", "los", "las", "un", "una", "en", "con", "por", "para", "al", "et", "ou", "du", "des", "le", "les"}


def leer_texto():
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        with open(sys.argv[1], encoding="utf-8") as f:
            return f.read()
    return sys.stdin.read()


def buscar_frases(texto):
    hallazgos = []
    for n, linea in enumerate(texto.splitlines(), 1):
        base = sin_acentos(linea)
        vistos = set()
        for categoria, rx in FRASES_COMPILADAS:
            for m in rx.finditer(base):
                clave = (categoria, m.start())
                if clave in vistos:
                    continue
                vistos.add(clave)
                fragmento = linea[m.start():m.end()].strip()
                if len(fragmento) > 90:
                    fragmento = fragmento[:87] + "..."
                hallazgos.append((n, categoria, fragmento or linea.strip()[:60]))
    return hallazgos


def largos_de_frases(texto):
    limpio = re.sub(r"\s+", " ", texto)
    frases = [f for f in re.split(r"(?<=[.!?…])\s+", limpio) if len(f.split()) >= 2]
    return [len(f.split()) for f in frases]


def titulo_en_mayusculas(linea):
    """True si el encabezado capitaliza todas sus palabras principales."""
    palabras = re.findall(r"[A-Za-zÀ-ſ][\w'À-ſ-]*", linea)
    significativas = [p for p in palabras if p.lower() not in PALABRAS_MENORES and len(p) > 2]
    if len(palabras) < 3 or len(significativas) < 2:
        return False
    return all(p[0].isupper() for p in significativas)


def revisar_encabezados(texto):
    avisos = []
    lineas = texto.splitlines()
    previo = 0
    saltos = []
    for n, linea in enumerate(lineas, 1):
        m = re.match(r"^(#{1,6})\s+(.*)$", linea)
        titulo = None
        if m:
            nivel = len(m.group(1))
            titulo = m.group(2).strip()
            if (previo == 0 and nivel >= 3) or (previo and nivel > previo + 1):
                saltos.append(n)
            previo = nivel
        else:
            palabras = linea.split()
            anterior_vacia = n == 1 or not lineas[n - 2].strip()
            siguiente_vacia = n == len(lineas) or not lineas[n].strip()
            if 3 <= len(palabras) <= 8 and not re.search(r"[.!?,;:]$", linea.strip()) and anterior_vacia and siguiente_vacia:
                titulo = linea.strip()
        if titulo and titulo_en_mayusculas(titulo):
            avisos.append(f"Título con todas las palabras en mayúscula (línea {n}): \"{titulo[:60]}\". Deja mayúscula solo en la primera palabra y en los nombres propios.")
    if saltos:
        avisos.append(f"Niveles de encabezado saltados en las líneas {', '.join(map(str, saltos[:6]))}. Respeta la jerarquía 1, 2, 3.")
    return avisos


def main():
    texto = leer_texto()
    if not texto.strip():
        print("No hay texto para revisar.")
        return 0

    palabras = len(re.findall(r"\w+", texto))
    avisos = []

    # Rayas largas
    rayas = texto.count("—")
    por_200 = rayas / max(palabras, 1) * 200
    if rayas and por_200 > 1:
        avisos.append(f"Rayas largas (—): {rayas} ({por_200:.1f} por cada 200 palabras). Deja como mucho una por cada 200.")
    elif rayas:
        avisos.append(f"Rayas largas (—): {rayas}. Dentro de lo razonable, pero revisa que no sean decorativas.")

    # Formato y marcado
    for nombre, rx, consejo in [
        ("Emojis", EMOJI, "Quítalos salvo que la persona los use."),
        ("Negritas (**)", NEGRITA, "Quita las decorativas."),
        ("Viñetas con encabezado en negrita", VINETA_NEGRITA, "Pasa a prosa o a viñetas simples."),
        ("Encabezados Markdown (#)", ENCABEZADO_MD, "Quítalos si el destino no renderiza Markdown."),
        ("Rayas de separación (---)", RAYA_SEPARACION, "Una raya antes de cada encabezado es típica de salida Markdown. Quítalas."),
        ("Tablas Markdown", TABLA_MD, "Una tabla pequeña suele repetir lo que dice la prosa. Usa prosa."),
        ("Cercas de código (```)", CERCA_CODIGO, "Quítalas si el texto no es código."),
        ("Viñetas con el carácter •", VINETA_PUNTO, "Usa la sintaxis de lista o prosa."),
        ("Comillas curvas", COMILLAS_CURVAS, "Evidencia débil; usa comillas rectas y no las mezcles."),
    ]:
        c = len(rx.findall(texto))
        if c:
            avisos.append(f"{nombre}: {c}. {consejo}")

    primera = next((l for l in texto.splitlines() if l.strip()), "")
    if ASUNTO.match(primera):
        avisos.append("El texto empieza con una línea de asunto (Subject:/Asunto:). Quítala si no es un correo.")

    avisos.extend(revisar_encabezados(texto))

    # Tríos
    trios = TRIO.findall(texto)
    if len(trios) >= 3 or (palabras and len(trios) / palabras * 200 > 2):
        avisos.append(f"Tríos de elementos (a, b y c): {len(trios)}. Elige uno o dos que importen.")

    # Falsos rangos (se descartan los que tienen números en ambos extremos)
    rangos = [m for m in FALSO_RANGO.finditer(texto)
              if not (re.search(r"\d", m.group(1)) and re.search(r"\d", m.group(2)))
              and len(m.group(1).split()) <= 6 and len(m.group(2).split()) <= 6
              and re.search(r"\b(from|desde)\b", m.group(0), re.IGNORECASE)]
    if rangos:
        ejemplos = "; ".join(f"\"{m.group(0).strip()[:60]}\"" for m in rangos[:3])
        avisos.append(f"Posibles falsos rangos \"desde X hasta Y\": {len(rangos)} ({ejemplos}). Comprueba que haya una escala real entre los extremos.")

    # "Y en lugar de X"
    ra = len(RATHER_THAN.findall(texto))
    if ra >= 3:
        avisos.append(f"\"rather than / en lugar de / en vez de\": {ra} veces. La forma \"Y en lugar de X\" es común en salida reciente de LLM.")

    # Densidad de vocabulario de IA (inglés)
    vocab = [m.group(0).lower() for m in VOCAB_EN_RX.finditer(texto)]
    distintas = sorted(set(vocab))
    if vocab:
        densidad = len(vocab) / max(palabras, 1) * 500
        if len(distintas) >= 3 or (densidad >= 4 and len(vocab) >= 3):
            avisos.append(f"Vocabulario de IA en inglés: {len(vocab)} apariciones, {len(distintas)} palabras distintas ({', '.join(distintas[:10])}). Esta concentración es una de las señales más fuertes.")
        else:
            avisos.append(f"Vocabulario de IA en inglés: {len(vocab)} aparición(es) ({', '.join(distintas)}). Pocas palabras pueden ser coincidencia; revisa el contexto.")

    # Ritmo
    largos = largos_de_frases(texto)
    if len(largos) >= 6:
        media = statistics.mean(largos)
        desv = statistics.pstdev(largos)
        if desv < 4.5:
            avisos.append(f"Largo de frases muy parejo: media {media:.1f} palabras, desviación {desv:.1f} ({len(largos)} frases). Mezcla frases cortas con otras más largas.")
        elif 8 <= media <= 20 and desv < 6:
            avisos.append(f"Frases casi todas entre 8 y 20 palabras (media {media:.1f}). Varía más el ritmo.")

    parrafos = [p for p in re.split(r"\n\s*\n", texto) if len(p.split()) >= 8]
    if len(parrafos) >= 4:
        tams = [len(re.split(r"(?<=[.!?])\s+", p.strip())) for p in parrafos]
        if len(set(tams)) == 1:
            avisos.append(f"Todos los párrafos tienen {tams[0]} frases. Varía el tamaño de los párrafos.")

    hallazgos = buscar_frases(texto)

    print(f"Revisión: {palabras} palabras, {texto.count(chr(10)) + 1} líneas.\n")

    if hallazgos:
        por_cat = {}
        for n, cat, frag in hallazgos:
            por_cat.setdefault(cat, []).append((n, frag))
        print(f"Frases y palabras sospechosas: {len(hallazgos)}")
        for cat, items in sorted(por_cat.items(), key=lambda kv: -len(kv[1])):
            print(f"\n  {cat} ({len(items)})")
            for n, frag in items[:12]:
                print(f"    línea {n}: {frag}")
            if len(items) > 12:
                print(f"    ... y {len(items) - 12} más")
    else:
        print("Frases y palabras sospechosas: ninguna.")

    print()
    if avisos:
        print("Signos, formato y ritmo:")
        for a in avisos:
            print(f"  - {a}")
    else:
        print("Signos, formato y ritmo: sin avisos.")

    print(
        "\nRecuerda: un rasgo suelto no prueba nada. Lo que pesa es la densidad, "
        "y lo que de verdad arregla el texto es que cada frase diga algo concreto. "
        "Este revisor no detecta ni la variación elegante ni la falta de datos concretos: "
        "revísalas a mano."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
