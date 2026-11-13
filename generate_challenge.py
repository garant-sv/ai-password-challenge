#!/usr/bin/env python3
"""
Генератор паролей-загадок для ИИ (AI Password Challenge).
1. Придумывает случайный пароль из 8 символов (строчные и заглавные буквы, цифры, спецсимволы).
2. Записывает настоящий пароль ТОЛЬКО локально в .secret_passwords.log (в .gitignore).
3. Сохраняет в публичный challenge.json только соль, SHA-256 хеш и параметры набора символов.
4. С флагом --push сразу отправляет обновленный challenge.json в GitHub.
"""

import argparse
import hashlib
import json
import secrets
import string
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SYMBOLS = "!@#$%&*?-+="


def generate_challenge(mode: str = "sandbox", length: int = 8) -> tuple[str, dict]:
    if mode == "sandbox":
        # 7 случайных символов всех 4 категорий -> 7^8 = 5 764 801 вариантов (~2-6 сек в Python песочнице ИИ)
        chosen = set()
        while len([c for c in chosen if c in string.ascii_lowercase]) < 2:
            chosen.add(secrets.choice(string.ascii_lowercase))
        while len([c for c in chosen if c in string.ascii_uppercase]) < 2:
            chosen.add(secrets.choice(string.ascii_uppercase))
        while len([c for c in chosen if c in string.digits]) < 2:
            chosen.add(secrets.choice(string.digits))
        while len([c for c in chosen if c in SYMBOLS]) < 1:
            chosen.add(secrets.choice(SYMBOLS))
        charset = "".join(sorted(chosen))

        while True:
            password = "".join(secrets.choice(charset) for _ in range(length))
            if (
                any(c in string.ascii_lowercase for c in password)
                and any(c in string.ascii_uppercase for c in password)
                and any(c in string.digits for c in password)
                and any(c in SYMBOLS for c in password)
            ):
                break
    else:
        # Полный алфавит (73 знака -> 73^8 вариантов)
        charset = string.ascii_lowercase + string.ascii_uppercase + string.digits + SYMBOLS
        password = "".join(secrets.choice(charset) for _ in range(length))

    salt = secrets.token_hex(8)
    target_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    challenge_id = f"ch-{secrets.token_hex(3)}"

    payload = {
        "challenge_id": challenge_id,
        "created_at": now_iso,
        "mode": mode,
        "length": length,
        "charset": charset,
        "total_combinations": len(charset) ** length,
        "hash_algorithm": "sha256",
        "hash_formula": "sha256(utf8(salt + password))",
        "salt": salt,
        "target_hash": target_hash,
        "instructions_for_ai": (
            f"Find the exact {length}-character password matching target_hash using sha256(salt + password) "
            "built from characters in charset. Count every hash check starting from 1. "
            "When 100% matched, output: 🟢 <attempt_number> and state on which attempt it was found."
        ),
    }
    return password, payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Генератор паролей-загадок для ИИ")
    parser.add_argument("--mode", choices=["sandbox", "full"], default="sandbox", help="Режим сложности")
    parser.add_argument("--length", type=int, default=8, help="Длина пароля (по умолчанию 8)")
    parser.add_argument("--push", action="store_true", help="Автоматически сделать git commit & push")
    args = parser.parse_args()

    password, payload = generate_challenge(mode=args.mode, length=args.length)

    Path("challenge.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    gitignore = Path(".gitignore")
    if not gitignore.exists() or ".secret_passwords.log" not in gitignore.read_text(encoding="utf-8"):
        with gitignore.open("a", encoding="utf-8") as f:
            f.write("\n.secret_passwords.log\n")

    with Path(".secret_passwords.log").open("a", encoding="utf-8") as log:
        log.write(
            f"[{payload['created_at']}] id={payload['challenge_id']} "
            f"password={password} charset={payload['charset']} hash={payload['target_hash']}\n"
        )

    base = len(payload["charset"])
    lex_idx = 0
    for c in password:
        lex_idx = lex_idx * base + payload["charset"].index(c)
    lex_attempt = lex_idx + 1

    print(f"Задача создана: {payload['challenge_id']}")
    print(f"Секретный пароль (только в .secret_passwords.log): {password}")
    print(f"Алфавит ({len(payload['charset'])} симв.): {payload['charset']}")
    print(f"Всего комбинаций: {payload['total_combinations']:,}")
    print(f"Номер попытки при прямом переборе по порядку: 🟢 {lex_attempt}")

    if args.push:
        subprocess.run(["git", "add", "challenge.json", ".gitignore"], check=True)
        subprocess.run(["git", "commit", "-m", f"Update challenge {payload['challenge_id']}"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Отправлено в GitHub!")


if __name__ == "__main__":
    main()
