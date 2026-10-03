# Extrasy-Cracker — Crackeador de Hashes Multi-Motor

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Herramienta de cracking de hashes basada en diccionario con tres motores independientes (Python, Go y Bash) para pentesting, CTFs y auditorías de seguridad autorizadas.**

---

## Descripción

Desarrollé Extrasy-Cracker porque necesitaba una herramienta liviana y directa para crackear hashes durante CTFs y pruebas de penetración autorizadas. No quería depender siempre de Hashcat o John the Ripper para tareas simples donde un ataque por diccionario alcanza. Así que construí tres motores distintos —Python, Go y Bash— cada uno pensado para un escenario diferente: el de Python cubre la mayor cantidad de algoritmos con una salida visual clara usando `rich`, el de Go está optimizado para velocidad en procesamiento por lotes, y el de Bash te da un crackeo rápido de MD5 sin dependencias extras.

La idea es que tengas una navaja suiza de cracking por diccionario: elegís el motor que mejor se adapte a lo que necesitás en el momento, sin configuraciones complicadas.

---

## Algoritmos soportados

| Algoritmo       | Python | Go  | Bash |
|-----------------|:------:|:---:|:----:|
| MD5             | ✅     | ✅  | ✅   |
| SHA-1           | ✅     | ✅  | ❌   |
| SHA-256         | ✅     | ✅  | ❌   |
| SHA-384         | ✅     | ❌  | ❌   |
| SHA-512         | ✅     | ✅  | ❌   |
| SHA-3           | ✅     | ❌  | ❌   |
| NTLM            | ✅     | ❌  | ❌   |
| Whirlpool       | ✅     | ❌  | ❌   |
| MySQL           | ✅     | ❌  | ❌   |
| bcrypt          | ✅     | ❌  | ❌   |
| crypt-sha512    | ✅     | ❌  | ❌   |

---

## Requisitos

- **Python 3.8+** con las dependencias listadas en `requirements.txt`
- **Go 1.18+** (para el motor de procesamiento por lotes)
- **Bash** (para el script de crackeo rápido)
- Un **diccionario/wordlist** (por ejemplo, `rockyou.txt`)

---

## Instalación

```bash
git clone https://github.com/44ghost44/Extrasy-Cracker.git
cd Extrasy-Cracker
pip install -r requirements.txt
```

Para compilar el motor Go:

```bash
cd go
go build -o batch_checker batch_checker.go
```

Para el script Bash, solo necesitás darle permisos de ejecución:

```bash
chmod +x bash/quick_md5_crack.sh
```

---

## Uso

### Motor Python (principal)

El motor Python es el más completo. Creé este motor para cubrir la mayor variedad de algoritmos posible, con una salida visual en colores usando la librería `rich`.

```bash
# Desde el directorio raíz
python3 hashcracker.py -H <hash> -t <tipo> -w <wordlist>

# O usando el módulo directamente
python3 python/hash_cracker.py -H <hash> -t <tipo> -w <wordlist>
```

**Ejemplos:**

```bash
# Crackear un hash MD5
python3 hashcracker.py -H 5d41402abc4b2a76b9719d911017c592 -t md5 -w /usr/share/wordlists/rockyou.txt

# Crackear un hash SHA-256
python3 hashcracker.py -H 2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824 -t sha256 -w /usr/share/wordlists/rockyou.txt

# Crackear un hash bcrypt
python3 hashcracker.py -H '$2b$12$LJ3m4ys3Lg...' -t bcrypt -w /usr/share/wordlists/rockyou.txt
```

### Motor Go (lotes de alta velocidad)

Diseñé este motor para cuando tenés que procesar grandes cantidades de hashes. Está optimizado para velocidad pura en MD5, SHA-1, SHA-256 y SHA-512.

```bash
cd go
./batch_checker -hashes <archivo_hashes> -type <tipo> -wordlist <wordlist>
```

**Ejemplo:**

```bash
./batch_checker -hashes hashes.txt -type md5 -wordlist /usr/share/wordlists/rockyou.txt
```

### Motor Bash (crackeo rápido de MD5)

Para cuando necesitás algo instantáneo sin levantar Python ni Go. Solo MD5.

```bash
./bash/quick_md5_crack.sh <hash_md5> <wordlist>
```

**Ejemplo:**

```bash
./bash/quick_md5_crack.sh 5d41402abc4b2a76b9719d911017c592 /usr/share/wordlists/rockyou.txt
```

---

## Comparación de motores

| Característica         | Python                          | Go                          | Bash                        |
|------------------------|--------------------------------|-----------------------------|-----------------------------|
| **Algoritmos**         | 11                             | 4                           | 1 (MD5)                    |
| **Velocidad**          | Media                          | Alta                        | Baja                       |
| **Procesamiento lote** | No                             | Sí                          | No                         |
| **Salida visual**      | Colores con `rich`             | Texto plano                 | Texto plano                |
| **Dependencias**       | Python 3 + `requirements.txt`  | Go compilado                | Solo Bash                  |
| **Caso de uso ideal**  | Uso general, múltiples algoritmos | Lotes grandes, velocidad máxima | Verificación rápida de MD5 |

---

## Limitaciones

- **Solo ataque por diccionario.** No incluye fuerza bruta, reglas ni ataques combinados.
- **No es un reemplazo de Hashcat ni John the Ripper.** Esas herramientas son mucho más potentes y optimizadas para auditorías reales. Construí Extrasy-Cracker como complemento liviano, no como competencia.
- **La efectividad depende de tu wordlist.** Si la contraseña no está en el diccionario, no la vas a encontrar.
- **Requiere un archivo de wordlist externo.**

---

## Aviso legal

Creé esta herramienta **exclusivamente para fines educativos, competencias CTF y pruebas de penetración autorizadas**. Usarla contra sistemas sin autorización explícita es ilegal y va en contra del propósito con el que la desarrollé. Sos el único responsable del uso que le des.

---

## Autor

**Alan Newberry** (alias `44ghost44`)

---

## Licencia

Este proyecto está bajo la [Licencia MIT](LICENSE).
