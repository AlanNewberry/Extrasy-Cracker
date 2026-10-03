import argparse
import hashlib
import sys
import os
import time
import shutil
import multiprocessing
from rich.console import Console
from rich.table import Table

console = Console()


def detect_algo(hash_str):
    h = hash_str.strip()
    if h.startswith("$2a$") or h.startswith("$2b$") or h.startswith("$2y$"):
        return "bcrypt"
    if h.startswith("$6$"):
        return "crypt-sha512"
    hl = h.lower()
    if len(hl) == 32 and all(c in "0123456789abcdef" for c in hl):
        return "md5/ntlm"
    if len(hl) == 40 and all(c in "0123456789abcdef" for c in hl):
        return "sha1"
    if len(hl) == 64 and all(c in "0123456789abcdef" for c in hl):
        return "sha256"
    if len(hl) == 96 and all(c in "0123456789abcdef" for c in hl):
        return "sha384"
    if len(hl) == 128 and all(c in "0123456789abcdef" for c in hl):
        return "sha512"
    return "unknown"


def hash_word(word, algo, salt=None):
    word_bytes = word.encode("utf-8", errors="ignore")
    if algo == "md5":
        return hashlib.md5(word_bytes).hexdigest()
    elif algo == "sha1":
        return hashlib.sha1(word_bytes).hexdigest()
    elif algo == "sha256":
        return hashlib.sha256(word_bytes).hexdigest()
    elif algo == "sha384":
        return hashlib.sha384(word_bytes).hexdigest()
    elif algo == "sha512":
        return hashlib.sha512(word_bytes).hexdigest()
    elif algo == "ntlm":
        try:
            import hashlib as _hl
            return _hl.new("md4", word.encode("utf-16le")).hexdigest()
        except Exception:
            return None
    elif algo == "crypt-sha512" and salt:
        try:
            import crypt
            return crypt.crypt(word, salt)
        except Exception:
            return None
    return None


def count_words(dict_file):
    count = 0
    with open(dict_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                count += 1
    return count


def crack_one(args):
    hash_line, dict_file, total_words = args
    detected = detect_algo(hash_line)

    if detected == "unknown":
        return (hash_line, "UNKNOWN TYPE", "magenta", 0)

    if detected == "bcrypt":
        msg = "BCRYPT (use hashcat/john)"
        if shutil.which("hashcat") or shutil.which("john"):
            msg = "BCRYPT (use hashcat/john)"
        return (hash_line, msg, "yellow", 0)

    if detected == "crypt-sha512":
        try:
            salt = "$6$" + hash_line.split("$")[2] + "$"
        except Exception:
            salt = None
        tried = 0
        t0 = time.time()
        with open(dict_file, "r", encoding="utf-8", errors="ignore") as f:
            for word in f:
                word = word.strip()
                if not word or word.startswith("#"):
                    continue
                tried += 1
                if tried % 500 == 0:
                    elapsed = time.time() - t0
                    speed = tried / elapsed if elapsed > 0 else 0
                    pct = (tried / total_words * 100) if total_words else 0
                    sys.stderr.write(
                        f"\r  [{hash_line[:16]}...] {tried}/{total_words} "
                        f"({pct:.0f}%) {speed:.0f} h/s"
                    )
                    sys.stderr.flush()
                hashed = hash_word(word, "crypt-sha512", salt)
                if hashed == hash_line:
                    sys.stderr.write("\r" + " " * 72 + "\r")
                    sys.stderr.flush()
                    return (hash_line, f"{word} (crypt-sha512)", "green", tried)
        sys.stderr.write("\r" + " " * 72 + "\r")
        sys.stderr.flush()
        return (hash_line, "NOT FOUND", "red", tried)

    algos = ["md5", "ntlm"] if detected == "md5/ntlm" else [detected]
    tried = 0
    t0 = time.time()
    with open(dict_file, "r", encoding="utf-8", errors="ignore") as f:
        for word in f:
            word = word.strip()
            if not word or word.startswith("#"):
                continue
            tried += 1
            if tried % 5000 == 0:
                elapsed = time.time() - t0
                speed = tried / elapsed if elapsed > 0 else 0
                pct = (tried / total_words * 100) if total_words else 0
                sys.stderr.write(
                    f"\r  [{hash_line[:16]}...] {tried}/{total_words} "
                    f"({pct:.0f}%) {speed:.0f} h/s"
                )
                sys.stderr.flush()
            for algo in algos:
                hashed = hash_word(word, algo)
                if hashed and hashed.lower() == hash_line.lower():
                    sys.stderr.write("\r" + " " * 72 + "\r")
                    sys.stderr.flush()
                    return (hash_line, f"{word} ({algo})", "green", tried)
    sys.stderr.write("\r" + " " * 72 + "\r")
    sys.stderr.flush()
    return (hash_line, "NOT FOUND", "red", tried)


def crack_hashes(hashes_file, dict_file, threads=4):
    hashes = []
    with open(hashes_file, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            hashes.append(line)

    console.print(f"[cyan]Counting wordlist...[/cyan]")
    total_words = count_words(dict_file)
    console.print(f"[cyan]Wordlist: {total_words} words, Hashes: {len(hashes)}[/cyan]")
    console.print()

    results = []
    t_start = time.time()

    with multiprocessing.get_context("spawn").Pool(threads) as pool:
        for result in pool.imap_unordered(
            crack_one, [(h, dict_file, total_words) for h in hashes]
        ):
            results.append(result)
            color = result[2]
            console.print(f"[{color}]{result[0]} : {result[1]}[/{color}]")

    t_elapsed = time.time() - t_start

    cracked = [r for r in results if r[2] == "green"]
    notfound = [r for r in results if r[2] == "red"]
    unknown = [r for r in results if r[2] in ("magenta", "yellow")]
    total_tried = sum(r[3] for r in results)

    console.print()
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Tipo")
    table.add_column("Cantidad")
    table.add_column("Ejemplos", overflow="fold")
    table.add_row(
        "[green]Crackeados[/green]",
        str(len(cracked)),
        "\n".join(f"{r[0]} : {r[1]}" for r in cracked[:3])
        + (" ..." if len(cracked) > 3 else ""),
    )
    table.add_row(
        "[red]No encontrados[/red]",
        str(len(notfound)),
        "\n".join(f"{r[0]}" for r in notfound[:3])
        + (" ..." if len(notfound) > 3 else ""),
    )
    table.add_row(
        "[magenta]Tipo desconocido[/magenta]",
        str(len(unknown)),
        "\n".join(f"{r[0]} : {r[1]}" for r in unknown[:3])
        + (" ..." if len(unknown) > 3 else ""),
    )
    table.add_row("[blue]Total[/blue]", str(len(results)), "")
    console.print(table)

    speed = total_tried / t_elapsed if t_elapsed > 0 else 0
    console.print(
        f"\n[cyan]Time: {t_elapsed:.1f}s, "
        f"Avg speed: {speed:.0f} h/s, "
        f"Cracked: {len(cracked)}/{len(results)}[/cyan]"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Hash cracker (MD5, SHA1, SHA256, SHA384, SHA512, NTLM, bcrypt detect, crypt-sha512)"
    )
    parser.add_argument("--hashes", required=True)
    parser.add_argument("--dict", required=True)
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    if not os.path.isfile(args.hashes):
        console.print(
            f"[red]Archivo de hashes '{args.hashes}' no existe o no es legible.[/red]"
        )
        sys.exit(1)
    if not os.path.isfile(args.dict):
        console.print(
            f"[red]Archivo diccionario '{args.dict}' no existe o no es legible.[/red]"
        )
        sys.exit(1)
    crack_hashes(args.hashes, args.dict, args.threads)
