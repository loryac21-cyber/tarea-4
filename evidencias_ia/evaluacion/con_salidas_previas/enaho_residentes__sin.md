# Evaluación · enaho_residentes · modo sin

## Pedido

```text
Responde la pregunta con datos oficiales. Si no puedes saber una cifra con certeza, pon null: no estimes. En «fuente» di de dónde sale cada cifra (código de serie, archivo, documento o cálculo).

¿Cuántas personas son residentes habituales en el módulo 02 (características de los miembros del hogar) de la ENAHO 2024 del INEI, con el criterio de residencia habitual del INEI?
```

## Configuración de la sesión

- Modelo: `claude-sonnet-5-5`
- Herramientas disponibles: `StructuredOutput`
- Servidores MCP: 
- Skills: `developing-with-streamlit`, `design`, `design-sync`, `dataviz`, `update-config`, `verify`, `debug`, `code-review`, `simplify`, `batch`, `fewer-permission-prompts`, `doctor`, `loop`, `schedule`, `claude-api`, `run`, `run-skill-generator`, `plugin-authoring`, `anthropic-skills:built-in-browser`, `anthropic-skills:chrome-browser`, `anthropic-skills:computer-use`, `anthropic-skills:deep-research`, `anthropic-skills:docs`, `anthropic-skills:docx`, `anthropic-skills:google-workspace`, `anthropic-skills:import-memory`, `anthropic-skills:morning`, `anthropic-skills:pdf`, `anthropic-skills:pptx`, `anthropic-skills:skill-creator`, `anthropic-skills:xlsx`

### Agente

No puedo darte esa cifra con certeza, así que pongo `null`. No tengo a mano la base de microdatos del módulo 02 de la ENAHO 2024 (Enaho01-2024-200) y no la he procesado. Cualquier número que te diera sería una estimación.

El criterio del INEI para residente habitual, según la documentación de la encuesta, se calcula con las variables P204, P205 y P206:
- Es residente habitual quien tiene P204 = 1 (miembro del hogar) y P205 = 2 (no estuvo ausente 30 días o más).
- También lo es quien tiene P204 = 2 (no es miembro del hogar) y P206 = 1 (estuvo presente 30 días o más).

Para obtener el número, descarga la base del módulo 02 desde la plataforma de microdatos del INEI y cuenta los registros que cumplan esa condición. Puedes hacerlo sin ponderar, o ponderando con FACTOR07 si quieres la cifra poblacional.

### Llamada a `StructuredOutput`

```json
{
 "valor": null,
 "fuente": "No verificable sin acceso a los microdatos del módulo 02 (Enaho01-2024-200) del INEI. El criterio de residente habitual usa P204, P205 y P206: (P204=1 y P205=2) o (P204=2 y P206=1). No se estimó ninguna cifra.",
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
- Duración: 6.1 s
- Costo informado por Claude Code: US$ 0.0103095

{"valor":null,"fuente":"No verificable sin acceso a los microdatos del módulo 02 (Enaho01-2024-200) del INEI. El criterio de residente habitual usa P204, P205 y P206: (P204=1 y P205=2) o (P204=2 y P206=1). No se estimó ninguna cifra.","unidad":"personas"}
