import requests
import json
import zlib
import base64
import base58
from urllib.parse import urlparse, urljoin, urlunparse
from Crypto import Random, Hash, Protocol
from Crypto.Cipher import AES


def upload_text(data: str) -> typing.Optional[str]:
    passphrase = Random.get_random_bytes(32)
    salt = Random.get_random_bytes(8)
    key = Protocol.KDF.PBKDF2(passphrase, salt, 32, 100000, hmac_hash_module=Hash.SHA256)
    compress = zlib.compressobj(wbits=-15)
    paste_blob = compress.compress(json.dumps({'paste': data}, separators=(',', ':')).encode()) + compress.flush()
    cipher = AES.new(key, AES.MODE_GCM)
    paste_meta = [[base64.b64encode(cipher.nonce).decode(), base64.b64encode(salt).decode(), 100000, 256, 128, 'aes', 'gcm', 'zlib'], 'syntaxhighlighting', 0, 0]
    cipher.update(json.dumps(paste_meta, separators=(',', ':')).encode())
    ct, tag = cipher.encrypt_and_digest(paste_blob)
    resp = requests.post('https://bin.nixnet.services', headers={'X-Requested-With': 'JSONHttpRequest'}, data=json.dumps({'v': 2, 'adata': paste_meta, 'ct': base64.b64encode(ct + tag).decode(), 'meta': {'expire': '1week'}}, separators=(',', ':')))
    data = resp.json()
    url = list(urlparse(urljoin('https://bin.nixnet.services', data['url'])))
    url[5] = base58.b58encode(passphrase).decode()
    return urlunparse(url)
