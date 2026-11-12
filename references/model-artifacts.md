# Formato Visual, Tipografía y Filtraciones de Modelos (Base WP:AISIGNS/S y WP:AIMARKUP)

Esta referencia recopila los errores visuales, de marcado y las fugas de datos internos características de los modelos de IA al generar texto.

---

## 1. Anomalías de Formato Visual y Estilo (`WP:AISIGNS/S`)

### 1.1 Capitalización Tipo Título (*Title Case*)
* **Patrón de IA:** Capitalizar la primera letra de cada palabra importante en subtítulos o encabezados en idiomas donde se usa minúscula estándar (ej. *«El Impacto De La Tecnología En El Mercado Actual»*).
* **Solución humana:** Usar capitalización de oración estándar (*«El impacto de la tecnología en el mercado actual»*).

### 1.2 Saturación de Negritas en Prosa (*Overuse of Boldface*)
* **Patrón de IA:** Marcar en negrita palabras clave o términos centrales en casi cada párrafo o línea, produciendo un aspecto de resumen escolar o temario prefabricado.
* **Solución humana:** Mantener el flujo continuo en texto regular; usar énfasis en negrita solo para encabezados estructurales o avisos puntuales muy contados.

### 1.3 Listas Verticales con Encabezados Integrados (*Inline-Header Vertical Lists*)
* **Patrón de IA:** Compulsión por convertir explicaciones narrativas fluidas en listas con viñetas idénticas donde cada punto abre con un término en negrita seguido de dos puntos:
  * `* **Eficiencia:** Mejora los tiempos de respuesta...`
  * `* **Escalabilidad:** Permite crecer sin fricciones...`
  * `* **Seguridad:** Garantiza la protección integral...`
* **Solución humana:** Integrar los argumentos en prosa fluida y párrafos articulados. Reservar las listas para secuencias de pasos o inventarios de elementos que realmente lo requieran.

### 1.4 Jerarquía de Encabezados Rota
* Repetir el título del documento o del tema como un encabezado H1/H2 al inicio del cuerpo.
* Saltarse niveles jerárquicos (pasar de un H2 directamente a un H4).
* Encabezados vacíos que no tienen contenido propio y solo alojan inmediatamente otros subtítulos debajo.

### 1.5 Emojis Como Formato Estructural
* Usar emojis al principio de títulos, secciones o viñetas (`✨`, `📚`, `🚀`, `💡`, `📌`) para forzar un entusiasmo corporativo artificial.

### 1.6 Tabulación Innecesaria
* Insertar tablas estructuradas de dos o tres columnas para contenidos que se entienden y leen mucho mejor como párrafos convencionales.

### 1.7 Tipografía Rígida de Comillas
* Aparición indiscriminada de comillas curvas dobles (“ ”) o apóstrofes curvas (’ ‘) en entornos de texto plano o de código donde corresponde la comilla recta estándar (`"` y `'`).

---

## 2. Fugas de Sintaxis y Marcado (`WP:AIMARKUP`)

### 2.1 Contaminación de Markdown en Texto Plano o Wiki
* Asteriscos sueltos (`**palabra**`) o almohadillas (`#`, `##`) generados por defecto cuando no se solicitó formato Markdown.
* Separadores temáticos repetitivos (`---` o `----`).
* Enlaces con formato crudo `[texto](url)` cuando el medio requiere enlaces integrados o texto plano.
* Bloques delimitados accidentalmente por triple comilla invertida (` ``` `) o etiquetas `<nowiki></nowiki>`.

### 2.2 Filtraciones de Tokens y Estructuras Internas por Modelo
Ocurren cuando el motor de búsqueda o la memoria del modelo fallan al limpiar su salida:

| Modelo / Plataforma | Token o Rastro Interno Típico |
| :--- | :--- |
| **ChatGPT (OpenAI)** | `contentReference`, `oaicite`, `oai_citation`, `+1`, `turn0search0`, `attributableIndex` |
| **Gemini (Google)** | `[cite: 1]`, `[span_1](start_span)`, etiquetas HTML `<mark>` dispersas |
| **Grok (xAI)** | `grok_card`, `grok_render_citation_card_json` |
| **DeepSeek** | Corchetes lenticulares chinos gruesos (`【` y `】`), símbolos de daga (`†`) |
| **Perplexity** | `attached_file`, `ppl-ai-file-upload` |
| **No clasificados** | Marcadores como `:::writing` |

### 2.3 Marcadores de Posición Olvidados (*Placeholders*)
Textos con campos tipo formulario que el modelo dejó vacíos entre corchetes:
* `[Insertar fecha aquí]`
* `[Nombre de la empresa / persona]`
* `[Añadir enlace o fuente aquí]`
* `[Describa los cambios específicos aquí]`
