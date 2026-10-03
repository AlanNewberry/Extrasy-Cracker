#!/bin/bash
set -euo pipefail

hashes_file="${1:?Usage: $0 <hashes_file> <dict_file>}"
dict_file="${2:?Usage: $0 <hashes_file> <dict_file>}"

has_tput=$(command -v tput || echo "")
c_red=""; c_green=""; c_yellow=""; c_blue=""; c_magenta=""; c_cyan=""; c_reset=""
if [[ -n "${has_tput}" ]]; then
    c_red=$(tput setaf 1)
    c_green=$(tput setaf 2)
    c_yellow=$(tput setaf 3)
    c_blue=$(tput setaf 4)
    c_magenta=$(tput setaf 5)
    c_cyan=$(tput setaf 6)
    c_reset=$(tput sgr0)
fi

if [[ ! -r "${hashes_file}" ]]; then
    echo "${c_red}Archivo de hashes '${hashes_file}' no existe o no es legible.${c_reset}" >&2
    exit 1
fi
if [[ ! -r "${dict_file}" ]]; then
    echo "${c_red}Archivo diccionario '${dict_file}' no existe o no es legible.${c_reset}" >&2
    exit 1
fi

total=0; cracked=0; notfound=0; unknown=0
declare -A summary_cracked
declare -A summary_notfound
declare -A summary_unknown

while IFS= read -r hash || [[ -n "${hash}" ]]; do
    hash="${hash//[$'\n\r']}"
    [[ -z "${hash}" || "${hash}" =~ ^# ]] && continue
    ((total++))
    found=0

    if [[ "${hash}" =~ ^[a-fA-F0-9]{32}$ ]]; then
        algo="md5"
    elif [[ "${hash}" =~ ^[a-fA-F0-9]{40}$ ]]; then
        algo="sha1"
    elif [[ "${hash}" =~ ^[a-fA-F0-9]{64}$ ]]; then
        algo="sha256"
    elif [[ "${hash}" =~ ^[a-fA-F0-9]{96}$ ]]; then
        algo="sha384"
    elif [[ "${hash}" =~ ^[a-fA-F0-9]{128}$ ]]; then
        algo="sha512"
    elif [[ "${hash}" =~ ^\$2[aby]\$ ]]; then
        echo -e "${c_yellow}${hash} : BCRYPT (use hashcat/john)${c_reset}"
        summary_unknown["${hash}"]="BCRYPT"
        ((unknown++))
        continue
    elif [[ "${hash}" =~ ^\$6\$ ]]; then
        algo="crypt-sha512"
    else
        echo -e "${c_magenta}${hash} : UNKNOWN TYPE${c_reset}"
        summary_unknown["${hash}"]="UNKNOWN"
        ((unknown++))
        continue
    fi

    while IFS= read -r word || [[ -n "${word}" ]]; do
        [[ -z "${word}" || "${word}" =~ ^# ]] && continue
        w_hash=""

        if [[ "${algo}" == "md5" ]]; then
            w_hash=$(printf "%s" "${word}" | md5sum | awk '{print $1}')
        elif [[ "${algo}" == "sha1" ]]; then
            w_hash=$(printf "%s" "${word}" | sha1sum | awk '{print $1}')
        elif [[ "${algo}" == "sha256" ]]; then
            w_hash=$(printf "%s" "${word}" | sha256sum | awk '{print $1}')
        elif [[ "${algo}" == "sha384" ]]; then
            w_hash=$(printf "%s" "${word}" | openssl dgst -sha384 | awk '{print $2}')
        elif [[ "${algo}" == "sha512" ]]; then
            w_hash=$(printf "%s" "${word}" | sha512sum | awk '{print $1}')
        elif [[ "${algo}" == "crypt-sha512" ]]; then
            if command -v mkpasswd &>/dev/null; then
                salt="$(echo "${hash}" | awk -F'$' '{print $3}')"
                w_hash=$(mkpasswd -m sha-512 "${word}" "\$6\$${salt}\$")
            else
                echo -e "${c_yellow}${hash} : crypt-sha512 requires mkpasswd${c_reset}"
                summary_unknown["${hash}"]="CRYPT-SHA512 (no mkpasswd)"
                ((unknown++))
                found=2
                break
            fi
        fi

        if [[ -n "${w_hash}" && "${w_hash}" == "${hash}" ]]; then
            echo -e "${c_green}${hash} : ${word} (${algo})${c_reset}"
            summary_cracked["${hash}"]="${word}"
            ((cracked++))
            found=1
            break
        fi
    done <"${dict_file}"

    if [[ "${found}" -eq 0 ]]; then
        echo -e "${c_red}${hash} : NOT FOUND${c_reset}"
        summary_notfound["${hash}"]=1
        ((notfound++))
    fi
done <"${hashes_file}"

echo
echo -e "${c_cyan}Resumen:${c_reset}"
echo -e "${c_green}Crackeados: ${cracked}${c_reset}"
echo -e "${c_red}No encontrados: ${notfound}${c_reset}"
echo -e "${c_magenta}Tipo desconocido: ${unknown}${c_reset}"
echo -e "${c_blue}Total: ${total}${c_reset}"

if [[ "${cracked}" -gt 0 ]]; then
    echo -e "${c_green}Hashes crackeados:${c_reset}"
    for h in "${!summary_cracked[@]}"; do
        echo "${h} : ${summary_cracked[${h}]}"
    done
fi
if [[ "${notfound}" -gt 0 ]]; then
    echo -e "${c_red}Hashes no encontrados:${c_reset}"
    for h in "${!summary_notfound[@]}"; do
        echo "${h}"
    done
fi
if [[ "${unknown}" -gt 0 ]]; then
    echo -e "${c_magenta}Hashes tipo desconocido:${c_reset}"
    for h in "${!summary_unknown[@]}"; do
        echo "${h} : ${summary_unknown[${h}]}"
    done
fi
