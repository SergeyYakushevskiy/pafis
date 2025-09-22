from __future__ import annotations
import os
import struct
from typing import List, Tuple

_H0: List[int] = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
]

_K: List[int] = [
    0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,
    0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,
    0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
    0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,
    0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,
    0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
    0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,
    0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2
]

def _rotr(x: int, n: int) -> int:
    return ((x >> n) | ((x & 0xffffffff) << (32 - n))) & 0xffffffff

class SHA256:
    def __init__(self) -> None:
        self._h: List[int] = _H0[:]
        self._buf = bytearray()
        self._total = 0  # в байтах

    def _compress(self, block: bytes) -> None:
        w = list(struct.unpack(">16L", block)) + [0]*48
        for i in range(16, 64):
            s0 = _rotr(w[i-15],7) ^ _rotr(w[i-15],18) ^ (w[i-15] >> 3)
            s1 = _rotr(w[i-2],17) ^ _rotr(w[i-2],19) ^ (w[i-2] >> 10)
            w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xffffffff

        a,b,c,d,e,f,g,h = self._h
        for i in range(64):
            S1 = _rotr(e,6) ^ _rotr(e,11) ^ _rotr(e,25)
            ch = (e & f) ^ ((~e) & g)
            t1 = (h + S1 + ch + _K[i] + w[i]) & 0xffffffff
            S0 = _rotr(a,2) ^ _rotr(a,13) ^ _rotr(a,22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            t2 = (S0 + maj) & 0xffffffff

            h,g,f,e,d,c,b,a = g,f,e,(d+t1)&0xffffffff,c,b,a,(t1+t2)&0xffffffff

        self._h[0] = (self._h[0] + a) & 0xffffffff
        self._h[1] = (self._h[1] + b) & 0xffffffff
        self._h[2] = (self._h[2] + c) & 0xffffffff
        self._h[3] = (self._h[3] + d) & 0xffffffff
        self._h[4] = (self._h[4] + e) & 0xffffffff
        self._h[5] = (self._h[5] + f) & 0xffffffff
        self._h[6] = (self._h[6] + g) & 0xffffffff
        self._h[7] = (self._h[7] + h) & 0xffffffff

    def update(self, data: bytes) -> None:
        if not data:
            return
        self._total += len(data)
        self._buf.extend(data)
        while len(self._buf) >= 64:
            self._compress(bytes(self._buf[:64]))
            del self._buf[:64]

    def _snapshot(self) -> Tuple[List[int], bytes, int]:
        return self._h[:], bytes(self._buf), self._total

    def hexdigest(self) -> str:
        h, tail, total = self._snapshot()
        bit_len = (total * 8) & ((1 << 64) - 1)

        pad = bytearray(tail)
        pad.append(0x80)
        while (len(pad) % 64) != 56:
            pad.append(0x00)
        pad.extend(struct.pack(">Q", bit_len))

        def compress_on(state: List[int], block: bytes) -> None:
            w = list(struct.unpack(">16L", block)) + [0]*48
            for i in range(16, 64):
                s0 = _rotr(w[i-15],7) ^ _rotr(w[i-15],18) ^ (w[i-15] >> 3)
                s1 = _rotr(w[i-2],17) ^ _rotr(w[i-2],19) ^ (w[i-2] >> 10)
                w[i] = (w[i-16] + s0 + w[i-7] + s1) & 0xffffffff

            a,b,c,d,e,f,g,hh = state
            for i in range(64):
                S1 = _rotr(e,6) ^ _rotr(e,11) ^ _rotr(e,25)
                ch = (e & f) ^ ((~e) & g)
                t1 = (hh + S1 + ch + _K[i] + w[i]) & 0xffffffff
                S0 = _rotr(a,2) ^ _rotr(a,13) ^ _rotr(a,22)
                maj = (a & b) ^ (a & c) ^ (b & c)
                t2 = (S0 + maj) & 0xffffffff
                hh,g,f,e,d,c,b,a = g,f,e,(d+t1)&0xffffffff,c,b,a,(t1+t2)&0xffffffff

            state[0] = (state[0] + a) & 0xffffffff
            state[1] = (state[1] + b) & 0xffffffff
            state[2] = (state[2] + c) & 0xffffffff
            state[3] = (state[3] + d) & 0xffffffff
            state[4] = (state[4] + e) & 0xffffffff
            state[5] = (state[5] + f) & 0xffffffff
            state[6] = (state[6] + g) & 0xffffffff
            state[7] = (state[7] + hh) & 0xffffffff

        for i in range(0, len(pad), 64):
            compress_on(h, pad[i:i+64])

        return "".join(f"{x:08x}" for x in h)

def sha256_file_hex(path: str, chunk_size: int = 1 << 20) -> str:
    h = SHA256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def pick_file_gui(title: str, filetypes: tuple[tuple[str, str], ...] | None = None) -> str | None:
    try:
        p = input("Введите путь вручную: ").strip()
        return p if p and os.path.isfile(p) else None
    except Exception as e:
        print(f"[!] GUI-диалог недоступен: {e}")
        return None


def read_hash_from_file(path: str) -> str | None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip().lower()
    except Exception:
        return None

def menu():
    target_file: str | None = None
    hash_file: str | None = None

    while True:
        print("\n=== Лабораторная №2: ПРОВЕРКА ЦЕЛОСТНОСТИ ===")
        print("1) Выбрать проверяемый файл (GUI)")
        print("2) Выбрать файл с хешем .sha256 (GUI)")
        print("3) Проверить целостность (сравнить хеши)")
        print("4) Показать текущий SHA-256 файла (без сохранения)")
        print("5) Выход")
        choice = input("Ваш выбор (1-5): ").strip()

        if choice == "1":
            path = pick_file_gui("Выберите проверяемый файл")
            if path:
                target_file = path
                print(f"[✓] Файл выбран: {target_file}")
            else:
                print("[!] Файл не выбран.")

        elif choice == "2":
            path = pick_file_gui("Выберите файл с эталонным хешем (.sha256)",
                                 filetypes=(("SHA256 files", "*.sha256"), ("All files", "*.*")))
            if path:
                hash_file = path
                print(f"[✓] Файл с хешем выбран: {hash_file}")
            else:
                print("[!] Файл с хешем не выбран.")

        elif choice == "3":
            if not target_file:
                print("[!] Сначала выберите проверяемый файл (п.1).")
                continue
            if not hash_file:
                print("[!] Сначала выберите файл с хешем (п.2).")
                continue
            saved = read_hash_from_file(hash_file)
            if not saved:
                print(f"[!] Не удалось прочитать хеш из: {hash_file}")
                continue
            try:
                current = sha256_file_hex(target_file).lower()
                print(f"Текущий SHA-256:  {current}")
                print(f"Эталонный хеш:    {saved}")
                if current == saved:
                    print("[✓] Целостность подтверждена ✅")
                else:
                    print("[×] Целостность нарушена ❌ (хеши отличаются)")
            except Exception as e:
                print(f"[!] Ошибка при вычислении: {e}")

        elif choice == "4":
            if not target_file:
                print("[!] Сначала выберите проверяемый файл (п.1).")
                continue
            try:
                print("SHA-256:", sha256_file_hex(target_file))
            except Exception as e:
                print(f"[!] Ошибка при вычислении: {e}")

        elif choice == "5":
            print("Выход. Проверка завершена.")
            break

        else:
            print("[!] Некорректный ввод. Введите число 1–5.")

if __name__ == "__main__":
    menu()