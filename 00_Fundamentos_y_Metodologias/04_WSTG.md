---
title: Metodología WSTG
pubDate: '2026-06-22'
---

La **Guía de Pruebas de Seguridad Web** (WSTG, *Web Security Testing Guide*) de OWASP (*Open Web Application Security Project*) es un marco de trabajo de ciberseguridad exhaustivo y colaborativo diseñado específicamente para evaluar la seguridad de aplicaciones web y APIs modernas. 

A diferencia del conocido *OWASP Top 10* (que describe los riesgos más críticos en términos generales), el WSTG va mucho más allá: ofrece una metodología detallada con más de 90 casos de prueba estructurados en 12 categorías que cubren toda la superficie de ataque de una aplicación web moderna.

## Las 12 Categorías del WSTG

Cada categoría contiene casos de prueba identificados por códigos (ej. `WSTG-INPV-01` para Cross-Site Scripting reflejado) con guías paso a paso sobre qué probar y cómo hacerlo:

1.  **Recopilación de Información (*Information Gathering - INFO*):** Identificación del motor web, subdominios, tecnologías utilizadas y rutas expuestas.
2.  **Pruebas de Configuración y Gestión del Despliegue (*Configuration and Deployment Management - CONFIG*):** Asegurar que las plataformas, servidores y componentes externos estén configurados de forma segura (ej. cabeceras de seguridad, certificados SSL/TLS).
3.  **Pruebas de Gestión de Identidad (*Identity Management - IDNT*):** Evaluar roles de usuario, procesos de registro y flujos de cuentas.
4.  **Pruebas de Autenticación (*Authentication - ATHN*):** Comprobar la robustez de las contraseñas, políticas de bloqueo, restablecimiento de credenciales y doble factor (2FA).
5.  **Pruebas de Autorización (*Authorization - AUTH*):** Evaluar vulnerabilidades de omisión de control de acceso (como IDOR o escalada de privilegios).
6.  **Pruebas de Gestión de Sesiones (*Session Management - SESS*):** Analizar el ciclo de vida del identificador de sesión, tokens de sesión y cookies de seguridad (`Secure`, `HttpOnly`, `SameSite`).
7.  **Pruebas de Validación de Entradas (*Input Validation - INPV*):** Mitigar inyecciones (SQL, Command Injection), Cross-Site Scripting (XSS), inclusión de archivos y desbordamientos.
8.  **Pruebas de Manejo de Errores (*Error Handling - ERR*):** Asegurar que la aplicación no exponga información técnica sensible a través de mensajes de error o stack traces.
9.  **Pruebas de Criptografía Débil (*Cryptography - CRYP*):** Verificar el uso de algoritmos fuertes, almacenamiento seguro de secretos y transporte cifrado de datos.
10. **Pruebas de Lógica de Negocio (*Business Logic - BUSL*):** Validar si un atacante puede alterar el flujo esperado de la aplicación para su beneficio (ej. saltarse el pago, alterar cantidades o precios).
11. **Pruebas del Lado del Cliente (*Client-Side - CLNT*):** Pruebas enfocadas en el navegador, como inyección de código, manipulación del DOM y CORS.
12. **Pruebas de APIs y Servicios Web (*API Testing - APIT*):** Pruebas específicas para endpoints REST/GraphQL, validación de esquemas y rate limiting.

## El Ciclo de Vida del Desarrollo de Software (SDLC)

El WSTG destaca por su enfoque de **seguridad proactiva e integrada en el SDLC** (Software Development Life Cycle), en lugar de tratar la seguridad como un evento único que ocurre solo al final del desarrollo.

Para entender cómo se aplica, consideremos el ejemplo de una tienda en línea (*ShopSecure Inc.*) que está desarrollando un portal de clientes:

*   **Fase 1: Antes del Desarrollo (Requisitos):** Se definen los requisitos de seguridad y las obligaciones regulatorias desde el principio. Para *ShopSecure*, esto incluye el cumplimiento de la normativa PCI DSS (para procesar pagos) y el establecimiento de acuerdos sobre tiempos de aplicación de parches.
*   **Fase 2: Definición y Diseño (Modelado):** Se analiza la arquitectura de la aplicación en busca de fallos antes de programar. El equipo crea modelos de amenazas para la pasarela de pago, identificando la API de pago como un objetivo crítico y diseñando controles de validación y limitación de tasa (*rate-limiting*) desde el diseño.
*   **Fase 3: Durante el Desarrollo (Vectores de Código):** Se revisa el código mediante walkthroughs y revisiones estáticas. Los desarrolladores evalúan el módulo de autenticación contra los casos de prueba de credenciales de WSTG (`WSTG-ATHN`), encontrando que los tokens de restablecimiento de contraseña no expiraban correctamente.
*   **Fase 4: Durante el Despliegue (Verificación):** Se auditan los controles de seguridad en un entorno de producción controlado (*staging* o preproducción). El equipo realiza un pentest utilizando el WSTG, verificando que se hayan cambiado las credenciales por defecto, que TLS esté bien configurado y que no existan endpoints de depuración abiertos.
*   **Fase 5: Mantenimiento y Operaciones (Monitoreo):** Se mantiene la seguridad tras el lanzamiento con auditorías periódicas, especialmente después de actualizaciones. Si *ShopSecure* añade un sistema de recomendaciones tres meses después, se ejecutan de nuevo las pruebas relevantes del WSTG para garantizar que el cambio no introdujo nuevas vulnerabilidades.

## Notas Finales

### Puntos Fuertes
*   **Cobertura exhaustiva y práctica:** Sus más de 90 casos de prueba proporcionan un mapa concreto y aplicable con pasos detallados y resultados esperados.
*   **Actualización constante:** Es mantenido y enriquecido continuamente por una comunidad de profesionales de la seguridad de todo el mundo, adaptándose a nuevas tecnologías como SPAs o microservicios.
*   **Enfoque basado en riesgos:** Prioriza las vulnerabilidades según su explotabilidad e impacto real, en lugar de limitarse a listarlas.

### Desafíos
*   **Coste de recursos:** Implementar la guía completa de forma manual puede ser inviable para equipos pequeños o con presupuestos ajustados.
*   **Requiere conocimientos especializados:** Varias pruebas (como criptografía avanzada o lógica de negocio compleja) requieren de un analista experimentado.
*   **Peligro de la "mentalidad de checklist":** Existe el riesgo de que los auditores se limiten a completar la lista de forma mecánica, perdiendo la perspectiva de un análisis crítico y de la evaluación de riesgos global de la aplicación.
