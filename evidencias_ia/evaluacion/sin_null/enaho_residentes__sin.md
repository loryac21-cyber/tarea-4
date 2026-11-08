# Evaluación · enaho_residentes · modo sin

## Pedido

```text
Responde la pregunta con datos oficiales. En «fuente» di de dónde sale cada cifra (código de serie, archivo, documento o cálculo).

¿Cuántas personas son residentes habituales en el módulo 02 (características de los miembros del hogar) de la ENAHO 2024 del INEI, con el criterio de residencia habitual del INEI?
```

## Configuración de la sesión

- Modelo: `claude-sonnet-5-5`
- Herramientas disponibles: `StructuredOutput`
- Servidores MCP: 
- Skills: `developing-with-streamlit`, `design`, `design-sync`, `dataviz`, `update-config`, `verify`, `debug`, `code-review`, `simplify`, `batch`, `fewer-permission-prompts`, `doctor`, `loop`, `schedule`, `claude-api`, `run`, `run-skill-generator`, `plugin-authoring`, `anthropic-skills:built-in-browser`, `anthropic-skills:chrome-browser`, `anthropic-skills:computer-use`, `anthropic-skills:deep-research`, `anthropic-skills:docs`, `anthropic-skills:docx`, `anthropic-skills:google-workspace`, `anthropic-skills:import-memory`, `anthropic-skills:morning`, `anthropic-skills:pdf`, `anthropic-skills:pptx`, `anthropic-skills:skill-creator`, `anthropic-skills:xlsx`

### Agente

No tengo la cifra. No pude acceder a los microdatos de la ENAHO 2024 (módulo 02, archivo Enaho01-2024-200) desde esta sesión, y cualquier número que diera sería inventado.

Para calcularla con el criterio de residencia habitual del INEI:
- **Fuente:** el módulo 200 de la ENAHO 2024, descargable desde la plataforma de microdatos del INEI (proyectos.inei.gob.pe/microdatos).
- **Criterio:** son residentes habituales quienes cumplen `(P204==1 & P205==2) | (P204==2 & P206==1)`. Es decir, los miembros del hogar que no están ausentes por más de 30 días, más los no miembros que sí residen habitualmente. En las bases del INEI esto equivale a la variable `RESULT`/`ESTRATO` según el caso, y a la variable derivada `P204`/`P205`/`P206`.
- **Cálculo:**
  - Para el número de registros, cuenta las filas que cumplen la condición.
  - Para la población expandida, suma el factor `FACTOR07` (o `FACPOB07`) de esas filas.

Si me pasas el archivo `.sav` o `.csv` del módulo 200, lo calculo y te doy la cifra con la fuente exacta.

### Llamada a `StructuredOutput`

```json
{
 "valor": null,
 "fuente": "No se pudo calcular: no hay acceso a los microdatos ENAHO 2024 módulo 02 (Enaho01-2024-200). Criterio INEI: (P204==1 & P205==2) | (P204==2 & P206==1); contar registros o sumar el factor de expansión.",
 "unidad": "personas"
}
```

<details><summary>Resultado</summary>

```text
Structured output provided successfully
```

</details>

## Resultado final

- Turnos: 2
- Duración: 7.6 s
- Costo informado por Claude Code: US$ 0.011795499999999999

{"valor":null,"fuente":"No se pudo calcular: no hay acceso a los microdatos ENAHO 2024 módulo 02 (Enaho01-2024-200). Criterio INEI: (P204==1 & P205==2) | (P204==2 & P206==1); contar registros o sumar el factor de expansión.","unidad":"personas"}
