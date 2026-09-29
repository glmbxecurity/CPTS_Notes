---
title: Codificación, Descompilación y Bases
pubDate: 2026-05-22
---

## ¿Qué es la Codificación?
La **codificación** es el proceso de transformar datos de un formato a otro para facilitar su transporte o almacenamiento. A diferencia del cifrado, **no requiere una clave**; cualquier persona que conozca el método puede revertirlo. Es fundamental en el manejo de payloads y el análisis de archivos.

---

## 🔢 1. Bases Comunes

### Base64 (Muy usada en Web y Emails)
```bash
# Codificar texto
echo -n 'texto_original' | base64

# Decodificar texto
echo -n 'dGV4dG8=' | base64 -d
```

### Hexadecimal (Base16)
Común en el análisis de binarios y protocolos de red.
```bash
# Convertir texto a Hex
echo -n 'hello' | xxd -p

# Convertir Hex a texto
echo -n '68656c6c6f' | xxd -p -r
```

### URL Encoding
Sustituye caracteres especiales por `%HH` para enviarlos de forma segura por HTTP.
*   **Ejemplo:** ` ` (espacio) ➔ `%20`, `'` ➔ `%27`.

---

## 🧩 2. Lenguajes Esotéricos (Típicos de CTFs)
Si encuentras un archivo con caracteres repetitivos y sin sentido, podrías estar ante un lenguaje esotérico.

*   **Brainfuck:** Usa solo 8 caracteres: `> < + - . , [ ]`.
    *   [Decodificador Brainfuck](https://www.dcode.fr/brainfuck-language)
*   **Ook!:** Una variante de Brainfuck que usa solo tres palabras: `Ook.`, `Ook?`, `Ook!`.
    *   [Decodificador Ook!](https://www.dcode.fr/ook-language)

---

## 🛠️ 3. Ingeniería Inversa Básica
Consiste en analizar un programa ejecutable para entender su lógica o extraer secretos sin tener el código fuente original.

### Ghidra (NSATool)
Es la herramienta líder gratuita para descompilar binarios (EXE, ELF).
1.  **Nuevo Proyecto:** Crea un espacio de trabajo.
2.  **Importar:** Arrastra el binario al proyecto.
3.  **Analizar:** Doble clic en el binario y pulsa "Yes" cuando pregunte si quieres analizarlo.
4.  **Decompiler Window:** A la derecha verás el código fuente en C (aproximado) que generó el binario.

> **Tip:** Usa siempre la herramienta online **CyberChef** ("The Cyber Swiss Army Knife") para manipular bases y codificaciones de forma visual y rápida.
