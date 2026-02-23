# Crypto-Toolkit
A Python cryptography toolkit with Caesar, Vigenère, AES, TripleDES, SHA-256 and RSA encryption support (CLI based).

# 🔐 Shoaib Crypto Toolkit

A Python-based cryptography toolkit that provides both classical and modern encryption algorithms through a simple command-line interface (CLI).
This project is designed for learning cryptography concepts and understanding how different encryption techniques work in real-world security systems.

# 🚀 Features

- Caesar Cipher (Encrypt / Decrypt)
- Vigenère Cipher (Encrypt / Decrypt)
- AES Encryption / Decryption
- TripleDES Encryption / Decryption
- SHA-256 Hash Generator
- RSA Key Generation
- RSA Encryption / Decryption
- Command Line Interface (CLI)
- Beginner Friendly
- Works in Online Compilers

---

# 🔑 Cryptographic Methods Explained

This toolkit includes both **classical encryption methods** and **modern cryptographic algorithms** used in cybersecurity.

---

## 1️⃣ Caesar Cipher

### 📌 What it is
Caesar Cipher is one of the oldest and simplest encryption techniques. It shifts letters in the message by a fixed number.

### ⚙ How it works
Each letter is replaced by another letter a fixed number of positions down the alphabet.

Example:
```
HELLO → Shift 3 → KHOOR
```

### 🎯 Usage
- Learning basic encryption
- Understanding substitution ciphers
- Educational purposes

### 🔐 Security Level
❌ Very weak and easy to break.

---

## 2️⃣ Vigenère Cipher

### 📌 What it is
Vigenère Cipher is an improved version of Caesar Cipher that uses a keyword to encrypt text.

### ⚙ How it works
- Each letter is shifted using a repeating keyword.
- Different letters use different shifts.

Example:
```
Text: HELLO
Key: KEY
```

### 🎯 Usage
- Classical cryptography study
- Understanding polyalphabetic encryption

### 🔐 Security Level
⚠ Moderate but breakable.

---

## 3️⃣ AES Encryption (Advanced Encryption Standard)

### 📌 What it is
AES is a modern symmetric encryption algorithm widely used for securing sensitive data.

### ⚙ How it works
- Uses same key for encryption and decryption
- Uses 256-bit encryption in this project
- Converts plaintext into unreadable ciphertext
- Uses password-based key generation

### 🎯 Real-world usage
- Secure messaging applications
- File encryption
- Banking systems
- WiFi security
- Data protection systems

### 🔐 Security Level
✅ Very strong and industry standard.

---

## 4️⃣ TripleDES (DES)

### 📌 What it is
TripleDES is an improved version of DES encryption that encrypts data three times.

### ⚙ How it works
- Uses symmetric key encryption
- Applies encryption three times for extra security
- Older but historically important

### 🎯 Usage
- Legacy systems
- Older banking security

### 🔐 Security Level
⚠ Old technology (mostly replaced by AES).

---

## 5️⃣ SHA-256 Hashing

### 📌 What it is
SHA-256 is a cryptographic hash function that converts data into a fixed-length string.

### ⚙ How it works
- One-way process (cannot reverse)
- Same input always produces same output
- Detects data changes

Example:
```
Hello → 185f8db32271fe25...
```

### 🎯 Usage
- Password storage
- Blockchain technology
- Data verification
- Digital signatures

### 🔐 Security Level
✅ Very strong.

---

## 6️⃣ RSA Encryption (Public-Key Cryptography)

### 📌 What it is
RSA is an asymmetric encryption algorithm that uses two keys.

### 🔑 Keys Used
- Public Key → Encrypt data
- Private Key → Decrypt data

### ⚙ How it works
- Uses mathematical factorization
- Generates secure key pairs
- Only private key can decrypt encrypted data

### 🎯 Real-world usage
- HTTPS websites
- Secure communication
- Digital certificates
- Secure email systems

### 🔐 Security Level
✅ Very strong.

---

# 🛠 Technologies Used

- Python 3
- Cryptography Library (optional)
- PyCryptodome Library (optional)

---

# 📦 Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/crypto-toolkit-python.git
cd crypto-toolkit-python
```

Install required packages (optional but recommended):

```bash
pip install cryptography pycryptodome
```

---

# ▶️ How to Run

```bash
python main.py
```

Follow the menu instructions.

---

# 📌 Notes

- AES and TripleDES require `cryptography` library.
- RSA requires `pycryptodome`.
- If libraries are not installed, basic features still work.
- Designed for learning and educational purposes.

---

# 📚 Learning Purpose

This project helps understand:

- Cryptography fundamentals
- Encryption techniques
- Data security concepts
- Python security programming

---

# 📄 License

This project is open-source and free to use.

---

# 👨‍💻 Author

Developed by **Shoaib**
