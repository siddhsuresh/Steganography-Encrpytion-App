import rsa
(pubkey, privkey) = rsa.newkeys(512)
print(pubkey)
print(privkey)

#save the public key to a file
with open('public.pem', 'w+') as f:
    f.write(pubkey.save_pkcs1().decode('utf-8'))

#save the private key to a file
with open('private.pem', 'w+') as f:
    f.write(privkey.save_pkcs1().decode('utf-8'))
