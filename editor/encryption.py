
import os
import base64
from typing import Union
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from cryptography.hazmat.primitives import serialization, hashes

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_private_key(size:int=2048) -> RSAPrivateKey:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=size
    )
    return private_key

def extract_public_key(private_key:RSAPrivateKey) -> RSAPublicKey:
    return private_key.public_key()

def serialize_pem_private_key(private_key:RSAPrivateKey, password:bytes=None,
                                    file_path:Union[str, Path]=None) -> bytes:
    enc_alg = serialization.NoEncryption()
    if password is not None:
        enc_alg = serialization.BestAvailableEncryption(password)
        
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc_alg
    )
    
    if file_path is not None:
        with open(file_path, 'wb') as file:
            file.write(pem)
    
    return pem
    
def serialize_pem_public_key(public_key:RSAPublicKey, file_path:Union[str, Path]=None) -> bytes:
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    if file_path is not None:
        with open(file_path, 'wb') as file:
            file.write(pem)
        
    return pem

def load_pem_private_key(private_key_path:Union[str, Path], password:bytes=None) -> RSAPrivateKey:
    with open(private_key_path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=password,
        )
    return private_key
    
def load_pem_public_key(public_key_path:Union[str, Path]) -> RSAPublicKey:
    with open(public_key_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read()
        )
    return public_key

def rsa_encrypt(message:bytes, public_key:RSAPublicKey):
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext
    
def rsa_decrypt(ciphertext:bytes, private_key:RSAPrivateKey) -> bytes:
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

def generate_salt(length:int=24) -> bytes:
    return os.urandom(length)

def derive(data:bytes, salt:bytes, length:int=32, iterations=400000) -> bytes:
    # pbkdf with secure parameters
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=length,
        salt=salt,
        iterations=iterations,
    )
    # Secure Hash with no collisions thanks to unique salt (must be unique per password)
    salted_hash = kdf.derive(data) 
    # Make the hash url friendly
    salted_hash = base64.urlsafe_b64encode(salted_hash) 
    
    return salted_hash

def generate_rsa_key_pairs(private_key_password:str=None):
    password = None
    if private_key_password is not None:
        password = private_key_password.encode()
    # Generamos claves y las guardamos en un fichero
    private_key_path = 'private_key'
    public_key_path = 'public_key'
    private_key = generate_private_key()
    public_key = extract_public_key(private_key)
    # Comprobamos que las claves son validas
    msg = b'Hola buenas'
    ciphertext = rsa_encrypt(msg, public_key)
    deciphered_text = rsa_decrypt(ciphertext, private_key)
    if msg != deciphered_text: 
        print("[!] Las claves no son validas")
        exit(1)
    else:
        print(" + Las claves son validas")
        print(f"     => Mensage desencriptado = '{deciphered_text.decode()}'")
    # Comprobamos que las claves guardadas en los ficheros son validas
    serialize_pem_private_key(private_key, file_path=private_key_path, password=password)
    serialize_pem_public_key(public_key, file_path=public_key_path)
    private_key_recovered = load_pem_private_key(private_key_path, password=password)
    public_key_recovered = load_pem_public_key(public_key_path)
    # Comprobamos que las claves recuperadas son validas
    msg = b'Hola buenas'
    ciphertext = rsa_encrypt(msg, public_key_recovered)
    deciphered_text = rsa_decrypt(ciphertext, private_key_recovered)
    if msg != deciphered_text: 
        print("[!] Las claves recuperadas no son validas")
        exit(1)
    else:
        print(" + Las claves recuperadas son validas")
        print(f"     => Mensage desencriptado = '{deciphered_text.decode()}'")
    

# Creamos el par de claves publica/privada y comprobamos que todo sea correcto 
if __name__ == "__main__":
    password = None
    generate_rsa_key_pairs(private_key_password=password)