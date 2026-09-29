---
title: Fase Previa (Pre-engagement, RoE y Alcance)
pubDate: '2026-08-26'
---

La fase previa es la etapa de preparación organizativa y legal esencial antes de realizar el test de penetración. Se establecen los límites, objetivos y marcos legales. Consta de tres componentes fundamentales: **Cuestionario de alcance**, **Reunión previa al test** y **Reunión de lanzamiento**.

## 1. ⚖️ Acuerdos de Confidencialidad y Autorización

Antes de compartir información técnica, debe firmarse un **Non-Disclosure Agreement (NDA)**.

- **Unilateral:** Solo el auditor mantiene la confidencialidad; el cliente puede compartir la información.
- **Bilateral:** Ambas partes mantienen la confidencialidad. Es el más común en pentesting.
- **Multilateral:** Intervienen más de dos partes (ej. redes cooperativas).

**Autorización Legal:** El contrato debe ser firmado exclusivamente por personal autorizado (Alta Dirección / Nivel C). Ejemplos: CEO, CTO, CISO, CSO, CRO, CIO, VP de Auditoría, Gerente de Auditoría o VP/Director de TI/Seguridad.

### 📅 Cronología de Documentación

| Documento | Momento de creación |
| --- | --- |
| **1. NDA** | Después del contacto inicial. |
| **2. Scoping Questionnaire** | Antes de la reunión previa al test. |
| **3. Scoping Document** | Durante la reunión previa al test. |
| **4. Propuesta/Contrato (SoW)** | Durante la reunión previa al test. |
| **5. Rules of Engagement (RoE)** | Antes de la reunión de lanzamiento. *(Nota: Cualquier anexo del cliente con IPs/URLs debe incluirse aquí).* |
| **6. Contractors Agreement** | Antes de la reunión de lanzamiento (Solo para pruebas físicas). |
| **7. Informes** | Durante y después del test. |

> **⚠️ Importante:** Todos estos documentos deben ser revisados y adaptados por un abogado.

---

## 2. 📝 Cuestionario de Alcance (Scoping Questionnaire)

Documento enviado al cliente tras el contacto inicial para dimensionar los servicios requeridos.

**Tipos de evaluación a seleccionar:**

- [ ] Evaluación de vulnerabilidades (Interna / Externa)
- [ ] Test de penetración (Interno / Externo)
- [ ] Evaluación de seguridad inalámbrica, aplicaciones (web/móvil) o seguridad física.
- [ ] Evaluación de ingeniería social o Red Team.

**Información técnica crítica a recopilar:**

- Volumen de activos: Hosts activos, IPs/rangos CIDR, Dominios/subdominios, SSIDs.
- Aplicaciones: Cantidad de apps web/móviles y número de roles si es un test autenticado (estándar, admin, etc.).
- Ingeniería social: Número de usuarios objetivo (phishing/vishing) y si el cliente provee la lista o se usa OSINT.
- Seguridad Física: Número de ubicaciones y dispersión geográfica.
- Red Team: Objetivos específicos y líneas rojas (acciones fuera de alcance).
- Active Directory: ¿Requiere evaluación separada?
- Red interna: ¿Prueba como usuario anónimo o usuario de dominio estándar? ¿Evasión de NAC requerida?
- **Nivel de conocimiento:** Caja negra (*Black box*), Caja gris (*Grey box*) o Caja blanca (*White box*).
- **Nivel de evasión:** No evasivo, híbrido-evasivo (escalada gradual de "ruido") o totalmente evasivo.

---

## 3. 🤝 Reunión Previa al Test (Pre-engagement Meeting)

Se revisa el cuestionario y se discuten las expectativas para redactar la **Propuesta (Contrato/SoW)** y las **Reglas de Enfrentamiento (RoE)**.

### ✅ Lista de control del Contrato (SoW)

- [ ] **NDA:** Acuerdos de confidencialidad y penalizaciones.
- [ ] **Objetivos:** Hitos principales y secundarios a alcanzar.
- [ ] **Alcance:** Definición exacta de dominios, IPs, hosts y sistemas en el scope.
- [ ] **Tipo de test:** Definición técnica y justificación del enfoque elegido.
- [ ] **Metodologías:** Marcos de trabajo (OSSTMM, OWASP, PTES, etc.).
- [ ] **Ubicaciones:** Remoto (VPN) o presencial/interno.
- [ ] **Estimación de tiempo:** Fechas de inicio/fin y ventanas de ejecución para explotación y movimientos laterales (horario laboral vs. fuera de horario).
- [ ] **Terceros:** Permisos por escrito y confirmados de proveedores cloud o ISPs afectados.
- [ ] **Pruebas evasivas:** Definición de técnicas de evasión de sistemas de seguridad autorizadas.
- [ ] **Riesgos:** Precauciones acordadas ante posibles caídas.
- [ ] **Limitaciones/Restricciones:** Sistemas de producción intocables (Blacklist).
- [ ] **Manejo de información:** Cumplimiento normativo requerido (HIPAA, PCI, NIST, etc.).
- [ ] **Contacto:** Nombre, cargo, correos, teléfonos y cadena de escalada.
- [ ] **Líneas de comunicación:** Canales oficiales (Mail, llamadas, reuniones).
- [ ] **Informes:** Estructura, requisitos del cliente y necesidad de presentación ejecutiva.
- [ ] **Condiciones de pago:** Precios y términos comerciales.

### ✅ Lista de control: Reglas de Enfrentamiento (RoE)

- [ ] **Partes y Contacto:** Identificación del Contratista, Pentesters y todos los datos de contacto.
- [ ] **Bases Técnicas:** Propósito, Objetivos, Alcance (IPs, dominios, CIDR), Metodologías y Objetivos/Banderas específicas a capturar.
- [ ] **Logística:** Líneas de comunicación, estimación de fechas, horario diario permitido y ubicaciones/conexiones de red.
- [ ] **Seguridad Operacional:** Manejo de evidencias (cifrado), manejo de información de cliente, manejo de copias de seguridad.
- [ ] **Gestión de crisis:** Procedimiento y reporte de incidentes, protocolo de interrupción del test.
- [ ] **Gobernanza:** Reuniones de estado (frecuencia), tipo de informe final y fechas para repetición de pruebas (*re-test*).
- [ ] **Legal:** Descargos de responsabilidad (daños/pérdida de datos) y Permiso firmado para probar.

---

## 4. 🚀 Reunión de Lanzamiento (Kick-off Meeting)

Reunión final (presencial o remota) con los puntos de contacto, personal técnico y pentesters antes de iniciar.

- **Aclaraciones clave:** Por norma general NO se hacen pruebas de Denegación de Servicio (DoS). Se advierte sobre el ruido en logs, alarmas y el riesgo de bloqueo accidental de cuentas por fuerza bruta.
- **Protocolo de Parada y Notificación de Emergencia:** El test se detiene y se avisa de inmediato si:
    1. Se halla una vulnerabilidad crítica (ej. RCE no autenticada, SQLi masiva).
    2. Un sistema deja de responder.
    3. Se encuentra material o actividad ilegal.
    4. Se detecta un atacante real externo previo (*breach*).

---

## 🚨 5. Acuerdo de Contratistas (Contractor's Agreement)

Obligatorio para pruebas físicas (Evaluación de edificios, ingeniería social presencial). Actúa como un salvoconducto legal ante la intervención de autoridades o personal de seguridad no avisado.

### ✅ Lista de control para Evaluaciones Físicas

- [ ] Introducción y Propósito.
- [ ] Identificación del Contratista y Pentesters.
- [ ] Objetivo y Contactos de emergencia.
- [ ] Direcciones físicas exactas (Nombre del edificio, pisos, IDs de salas).
- [ ] Componentes físicos dentro del alcance.
- [ ] Cronograma detallado.
- [ ] **Notarización y Permiso explícito firmado.**
