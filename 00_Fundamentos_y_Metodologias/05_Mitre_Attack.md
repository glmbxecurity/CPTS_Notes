---
title: MITRE ATT&CK
pubDate: '2026-06-22'
---

Mientras que metodologías como PTES u OSSTMM ayudan a estructurar y guiar el *proceso* de una auditoría, no catalogan de forma sistemática las tácticas y técnicas específicas que los adversarios reales emplean en sus ataques. Este es precisamente el vacío que cubre **MITRE ATT&CK**.

**ATT&CK** (*Adversarial Tactics, Techniques, and Common Knowledge*), desarrollado y mantenido por la corporación **MITRE**, es una base de conocimiento global sobre el comportamiento de los adversarios, basada enteramente en observaciones del mundo real. No se trata de un marco de pentesting tradicional, sino de una enciclopedia viva sobre cómo operan los actores de amenazas.

---

## La Matriz: Tácticas, Técnicas y Subtécnicas

ATT&CK está estructurado en forma de matriz (una gran tabla de conocimiento):

*   **Tácticas (Las columnas - El "Por qué"):** Son los objetivos de alto nivel del atacante (por qué realiza una acción). La matriz de *Enterprise* cuenta actualmente con 14 tácticas, ordenadas de forma cronológica desde el acceso inicial hasta el impacto final (ej. Acceso Inicial, Ejecución, Persistencia, Escalada de Privilegios, Evasión de Defensas, Acceso a Credenciales, Descubrimiento, Movimiento Lateral, Recopilación, Comando y Control, Exfiltración e Impacto).
*   **Técnicas (Las filas - El "Cómo"):** Son los métodos específicos que utiliza el adversario para alcanzar un objetivo táctico. Por ejemplo, bajo la táctica de *Acceso Inicial* encontramos la técnica de **Explotación de Aplicaciones Expuestas (*Exploit Public-Facing Application*)** (T1190).
*   **Subtécnicas (Variantes del "Cómo"):** Variaciones más granulares de una técnica. Por ejemplo, la técnica de **Phishing** (T1566) se divide en:
    *   *Spearphishing Attachment* (T1566.001) - Phishing dirigido con adjunto malicioso.
    *   *Spearphishing Link* (T1566.002) - Phishing dirigido con enlace malicioso.
    *   *Spearphishing via Service* (T1566.003) - Phishing dirigido a través de un servicio o aplicación externa.

*Nota:* Cada técnica en ATT&CK cuenta con una descripción detallada, ejemplos reales de grupos APT que la utilizan, recomendaciones de detección para los defensores y mitigaciones recomendadas.

---

## Analogía: Procedimiento de Diagnóstico vs. Diccionario Médico

Para entender la relación entre una metodología de pentesting y MITRE ATT&CK, podemos usar la siguiente analogía médica:

*   **PTES (El Procedimiento Diagnóstico):** Es la guía que le dice al médico qué pasos debe seguir durante la exploración del paciente (ej. tomar el pulso, revisar los reflejos, hacer análisis de sangre).
*   **MITRE ATT&CK (El Diccionario Médico):** Proporciona la terminología estandarizada y el catálogo de enfermedades para nombrar y categorizar de forma exacta los síntomas y problemas de salud que el médico observe durante su exploración.

Ambos se complementan: uno guía el proceso de evaluación y el otro estandariza el vocabulario de los hallazgos.

---

## Mapeo de Hallazgos a MITRE ATT&CK: Caso MedGuard Health

Siguiendo el escenario de auditoría a **MedGuard Health** (descrito en el apartado de PTES), así es como se mapean los hallazgos técnicos del reporte con los IDs de técnicas de MITRE ATT&CK:

| Hallazgo en el Pentest | Táctica de ATT&CK | Técnica / Subtécnica de ATT&CK |
| :--- | :--- | :--- |
| Un correo de phishing entrega un payload a la estación de un empleado | **Acceso Inicial** | *Phishing: Spearphishing Attachment* (T1566.001) |
| Se explota un fallo de deserialización de Tomcat en el portal web | **Acceso Inicial** | *Exploit Public-Facing Application* (T1190) |
| Extracción de credenciales de dominio en memoria desde la estación de trabajo | **Acceso a Credenciales** | *OS Credential Dumping* (T1003) |
| Movimiento a un servidor de archivos internos mediante credenciales robadas | **Movimiento Lateral** | *Use Alternate Authentication Material* (T1550) |
| Acceso y lectura de la base de datos de pacientes desde el servidor web de la shell | **Recopilación (*Collection*)** | *Data from Information Repositories* (T1213) |

Al agregar las etiquetas e IDs de técnicas de ATT&CK al informe de pentesting, la conversación con el cliente MedGuard cambia por completo: deja de ser un simple *"parchea esta vulnerabilidad concreta"* y pasa a ser un **"¿tenemos capacidad de detectar este tipo de comportamiento en nuestra infraestructura?"**, permitiendo al equipo de Blue Team refinar reglas EDR/SIEM para toda una clase de amenaza.

---

## Notas Finales

### Puntos Fuertes
*   **Traductor Universal:** Permite que los equipos de pentesting, analistas de SOC, Threat Intelligence y respuesta ante incidentes hablen exactamente el mismo idioma.
*   **Orientación hacia la Detección:** Ayuda a los clientes a validar y robustecer la seguridad en base a comportamientos amplios de amenazas reales, más allá de la simple mitigación de parches de software individuales.

### Desafíos
*   **Curva de Aprendizaje:** Con más de 200 técnicas solo en la matriz de *Enterprise*, dominar y mapear con precisión toda la matriz requiere tiempo y experiencia constante.
*   **No es un Framework de Ejecución:** No indica cómo planificar un pentest ni cómo interactuar legalmente con el cliente; debe usarse como complemento y no como sustituto de guías metodológicas como PTES o WSTG.
