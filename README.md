# Extrasy-Cracker - Cracker de Hashes Multi-Motor

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Un cracker de hashes basado en diccionario con tres motores independientes escritos en Python, Go y Bash. Construido para CTFs, entornos de laboratorio y para aprender como funciona el cracking de hashes por dentro.

## Algoritmos soportados

| Algoritmo | Python | Go | Bash |
|-----------|--------|----|------|
| MD5 | Si | Si | Si |
| SHA1 | Si | Si | |
| SHA256 | Si | Si | |
| SHA384 | Si | | |
| SHA512 | Si | Si | |
| SHA3 | Si | | |
| NTLM | Si | | |
| Whirlpool | Si | | |
| MySQL | Si | | |
| bcrypt | Si | | |
| crypt-sha512 | Si | | |

## Instalacion

```bash
git clone https://github.com/AlanNewberry/Extrasy-Cracker.git
cd Extrasy-Cracker
```

Para el motor de Python:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Para el motor de Go, asegurate de tener Go instalado y compila desde el directorio `go/`.

## Uso

### Motor de Python (mas algoritmos)

```bash
python hashcracker.py
```

### Motor de Go (velocidad por lotes)

Compila y ejecuta desde el directorio `go/`.

### Motor de Bash (MD5 rapido)

```bash
bash bash/hashcracker.sh
```

## Comparacion de motores

- **Python** cubre el rango mas amplio de algoritmos, incluyendo bcrypt, NTLM y crypt-sha512. El mejor para uso general.
- **Go** esta optimizado para velocidad de cracking por lotes en los algoritmos principales (MD5, SHA1, SHA256, SHA512).
- **Bash** es un script minimal de un solo archivo para busquedas rapidas de MD5 cuando no hay otra cosa disponible.

## Limitaciones

- Solo basado en diccionario. No soporta ataques de fuerza bruta, basados en reglas ni hibridos.
- No es adecuado para auditorias de passwords en produccion. Usa Hashcat o John the Ripper para evaluaciones del mundo real.
- Requiere un archivo de wordlist externo.

## Aviso legal

Esta herramienta se proporciona exclusivamente para testing de seguridad autorizado, competencias CTF y fines educativos. El uso no autorizado contra sistemas que no son de tu propiedad o para los que no tenes permiso explicito es ilegal. El autor no asume responsabilidad por mal uso.

## Creditos

Desarrollado originalmente por Alan Newberry bajo el alias `44ghost44`.

## Licencia

Este proyecto esta licenciado bajo la MIT License. Ver [LICENSE](LICENSE) para mas detalles.
