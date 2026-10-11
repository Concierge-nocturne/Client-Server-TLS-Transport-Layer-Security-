# 🔒 Secure Client-Server UDP File Transfer with Simulated TLS & ARQ

A Python-based client-server application that demonstrates reliable, encrypted data transmission over **UDP (User Datagram Protocol)**. The project simulates key transport and security layer mechanisms, including a **TCP-like 3-way handshake**, a **TLS session key exchange**, and a **Stop-and-Wait ARQ** reliability protocol with symmetric encryption via Fernet (AES-128 + HMAC-SHA256).

---

## 📑 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture & Workflow](#system-architecture--workflow)
- [Technologies & Libraries](#technologies--libraries)
- [Protocol Specification](#protocol-specification)
- [Installation & Setup](#installation--setup)
- [Security & Architectural Notes](#security--architectural-notes)

---

## 📖 Overview

Standard UDP is connectionless and does not guarantee message delivery, order, or confidentiality. This project builds a reliable and secure application-layer protocol on top of UDP sockets by introducing:

1. **Connection-oriented Handshake**: Verifies both endpoints are reachable before sending payloads.
2. **Session Key Negotiation (Simulated TLS)**: Establishes a shared symmetric encryption key for the session.
3. **Stop-and-Wait ARQ**: Implements sequence numbering, positive acknowledgments (`ACK`), and retransmission on timeout to guarantee packet delivery.
4. **End-to-End Encryption**: Encrypts all data in transit using authenticated symmetric cryptography (`Fernet`).
5. **Multi-Client Concurrency**: Spawns dedicated threads on the server to handle concurrent client file requests.

---

## ✨ Key Features

- **Simulated 3-Way Handshake**: Implements the classic `SYN` → `SYN-ACK` → `ACK` exchange over UDP.
- **Simulated TLS Handshake**: Generates a dynamic cryptographic session key using `Fernet` and exchanges it during connection establishment.
- **Reliable Stop-and-Wait ARQ Protocol**:
  - Sequence numbering (`seq_num`) attached to every packet.
  - Per-packet acknowledgment (`ACK<seq>`).
  - Timeout handling (`2.0s`) with automatic retransmission upon packet loss.
- **Multi-Threaded Server**: Uses Python's `threading` module to serve multiple clients simultaneously with different source files.
- **File Reconstruction**: Reconstructs decrypted payloads line by line and outputs a local file (`copia_cliente_tls.txt`).

---

### Detailed Workflow:
1. **Handshake Phase**: The client sends a `SYN` packet to server port `20001`. The server replies with `SYN-ACK`, and the client finalizes with `ACK`.
2. **Secure Session Setup**: Upon receiving `ACK`, the server generates a new Fernet key, stores the client session state, and transmits `TLS-AES|<clave>` back to the client. A worker thread is spawned to handle transmission.
3. **Encrypted Line-by-Line Transmission**: The server reads the assigned text file, prefixes each line with its sequence number (`seq|line`), encrypts the string with Fernet, and transmits it over UDP.
4. **Acknowledgment & Retransmission**: The server waits up to 2 seconds for `ACK{seq}`. If no ACK is received before timeout, the packet is resent.
5. **Termination & Storage**: When transmission completes, the server sends an encrypted `FIN` packet. The client decrypts all received lines, writes them to `copia_cliente_tls.txt`, and safely terminates the connection.

---

## 🧰 Technologies & Libraries

| Technology / Library | Purpose | Description |
| :--- | :--- | :--- |
| **Python 3.x** | Core Language | Runtime and programming logic. |
| **`socket`** (Standard Library) | Network Communication | Handles low-level UDP socket management (`AF_INET`, `SOCK_DGRAM`). |
| **`threading`** (Standard Library) | Concurrency | Allows the server to manage multiple client transfers concurrently without blocking. |
| **`cryptography.fernet`** | Cryptographic Security | Symmetric authenticated encryption using **AES-128 in CBC mode** with **HMAC-SHA256** for message integrity and authenticity. |
| **`base64`** | Key Encoding | Standard Base64 URL-safe encoding for encryption keys. |

---

## 📡 Protocol Specification

### Control Packets
- `SYN`: Initiated by client to request a connection.
- `SYN-ACK`: Server response acknowledging connection request.
- `ACK`: Client response completing 3-way handshake.
- `TLS-AES|<Key>`: Server response distributing the symmetric Fernet key.
- `FIN`: Encrypted termination flag signaling end-of-file.

### Data Packets
- **Data Payload**: `Fernet.encrypt("<seq_number>|<text_line>")`
- **Acknowledgment**: `ACK<seq_number>` (e.g., `ACK0`, `ACK1`)

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher installed on your machine.
- `pip` package manager.

### 2. Clone Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 3. Install Required Dependencies
The project uses the `cryptography` package:
```bash
pip install cryptography
```

---

## 🔒 Security & Architectural Notes

- **Educational Simulation**: This project demonstrates the architectural concepts of TLS and ARQ. In real-world TLS, session keys are negotiated using asymmetric cryptography (e.g., Diffie-Hellman / RSA) and validated via X.509 Digital Certificates to prevent Man-in-the-Middle (MITM) attacks.
- **Authenticated Encryption**: `Fernet` guarantees that ciphertext cannot be altered or tampered with without detection, using 128-bit AES in CBC mode with PKCS7 padding and HMAC-SHA256 for message integrity.
- **Reliability over UDP**: While UDP provides lightweight, low-overhead transport, implementing Stop-and-Wait ARQ at the application level recovers from packet loss and reordering.
