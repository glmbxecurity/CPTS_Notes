---
title: Metodología PTES
pubDate: '2026-06-22'
---

El **Estándar de Ejecución de Pruebas de Penetración** (PTES, *Penetration Testing Execution Standard*), disponible en [pentest-standard.org](https://www.pentest-standard.org/), fue desarrollado por un grupo de profesionales experimentados en seguridad con un objetivo claro: definir cómo debe ser un pentest real de principio a fin. Mientras que otros marcos de trabajo se centran en *qué* probar o en *cómo* medir los resultados, PTES se enfoca en el **flujo completo de la auditoría**.

PTES se organiza en siete fases secuenciales. Este enfoque resulta extremadamente práctico para auditores junior, ya que responde de forma directa a la pregunta que muchos otros marcos dejan sin responder: *"Tengo un contrato firmado; ¿qué hago ahora el día uno, el día dos y el resto de las jornadas?"*

---

## Las 7 Fases de PTES: Caso de Estudio

Para comprender cómo se aplican las fases de PTES, utilizaremos el escenario de una empresa proveedora de servicios de salud, **MedGuard Health**, que ha contratado un pentest completo de su red corporativa y su portal de registros de pacientes.

### 1. Interacciones Previas al Compromiso (*Pre-engagement Interactions*)
Esta fase comprende todo lo que ocurre antes de realizar la primera prueba técnica. Para el caso de *MedGuard*, se define lo siguiente con su director de TI:
*   **Alcance (*Scope*):** La LAN corporativa (`10.10.0.0/16`), el portal de pacientes en `records.medguard-health.thm` y las redes inalámbricas del edificio de la sede principal.
*   **Reglas de Compromiso (*Rules of Engagement - RoE*):** Ventana de ejecución (solo noches de días laborables para evitar disrupciones en las operaciones clínicas), contactos de emergencia en caso de caída del servicio y la firma de la carta de autorización (o *"carta para salir de la cárcel"* / *Get Out of Jail Free letter*).
*   *Nota:* PTES detalla minuciosamente esta fase porque los malentendidos en el alcance son la principal fuente de problemas legales y profesionales en la industria.

### 2. Recolección de Información (*Intelligence Gathering*)
Consiste en recopilar datos sobre el objetivo utilizando técnicas pasivas y activas:
*   **Reconocimiento Pasivo:** Obtención de correos de empleados de *MedGuard* a través de LinkedIn, descubrimiento de subdominios analizando registros de transparencia de certificados, o revisión de ofertas de empleo antiguas que revelen tecnologías en uso (ej. *"se busca administrador de bases de datos con experiencia en Oracle 19c"*).
*   **Reconocimiento Activo:** Escaneo de puertos y enumeración activa de redes y servicios dentro del alcance acordado.
*   *Nota:* La profundidad de esta fase determina la calidad de los vectores de ataque que se diseñarán a continuación.

### 3. Modelado de Amenazas (*Threat Modeling*)
Con la información obtenida, se identifican los activos de mayor valor y las rutas de ataque más probables.
*   En *MedGuard*, el activo crítico es la base de datos de pacientes.
*   Se identifican dos caminos principales de ataque: comprometer el portal directamente explotando una vulnerabilidad web, o comprometer la estación de trabajo de un empleado de administración y desde ahí pivotar hacia la LAN corporativa interna.
*   *Nota:* Esta fase asegura que las pruebas se dirijan bajo una lógica adversarial realista y no mediante escaneos aleatorios.

### 4. Análisis de Vulnerabilidades (*Vulnerability Analysis*)
Búsqueda sistemática de debilidades que permitan explotar las rutas definidas en el modelado de amenazas:
*   **En el portal de pacientes:** Se detecta que corre sobre una versión obsoleta de *Apache Tomcat* vulnerable a deserialización de objetos.
*   **En la red interna:** Varios equipos de trabajo carecen de actualizaciones críticas del sistema operativo.
*   *Nota:* PTES recalca la necesidad de realizar validaciones manuales junto con el escaneo automático para eliminar falsos positivos.

### 5. Explotación (*Exploitation*)
Ejecución técnica y controlada de exploits sobre los fallos confirmados:
*   **Vector Externo:** Se explota el fallo de deserialización en el Tomcat obsoleto para obtener una consola de comandos (*shell*) en el servidor del portal de pacientes.
*   **Vector Interno:** Se utiliza un ataque de ingeniería social con un pretexto autorizado para desplegar un payload ejecutable en el equipo de un empleado.
*   *Nota:* La explotación en PTES tiene como meta demostrar el impacto real del negocio, no comprometer sistemas de forma masiva sin un propósito claro.

### 6. Post-Explotación (*Post-Exploitation*)
Fase crucial en la que se mide el impacto real del compromiso una vez dentro:
*   **Desde el portal web:** Se pivota hacia la base de datos interna y se confirma el acceso de lectura a los registros médicos de pacientes.
*   **Desde el equipo del empleado:** Se extraen credenciales de dominio cacheadas en memoria y se demuestra el movimiento lateral hacia un servidor de archivos financieros.
*   *Nota:* Aquí se traduce el hallazgo técnico en riesgo de negocio: un reporte indicando *"tuvimos acceso a 50,000 registros médicos"* tiene mucho más impacto ante el cliente que decir *"conseguimos una shell"*.

### 7. Reporte (*Reporting*)
Entrega del informe final estructurado para dos públicos distintos:
*   **Resumen Ejecutivo:** Dirigido a la gerencia de *MedGuard*, comunicando el riesgo general en lenguaje no técnico, destacando la exposición legal regulatoria (ej. leyes de privacidad como HIPAA) y la urgencia de remediarlo.
*   **Reporte Técnico:** Dirigido al equipo de TI, con pasos detallados para reproducir los exploits, capturas de pantalla de evidencia, hosts afectados y recomendaciones de remediación priorizadas.

---

## Notas Finales

### Puntos Fuertes
*   **Estructura práctica integral:** Funciona como un manual operativo paso a paso sobre cómo fluye un proyecto de pentesting real, lo que ayuda a entrenar el instinto de los auditores junior.
*   **Enfoque preventivo y legal:** Detalla con rigor los límites y acuerdos previos para evitar problemas de responsabilidad legal y profesional.

### Desafíos
*   **Falta de actualización técnica reciente:** PTES no se ha actualizado formalmente en varios años, por lo que algunas de sus secciones técnicas y de herramientas están desactualizadas (el auditor debe complementar PTES con metodologías técnicas modernas).
*   **Falta de métricas cuantitativas:** A diferencia de otros estándares como OSSTMM, los resultados de PTES dependen mucho más de la experiencia y el criterio individual del auditor.
