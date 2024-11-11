byte_str = "0909093c904692b25f904692b296bc3e88c390c28a44816092838a8c816088c392838a8c3c2f904692b25f904692b296bc3e0d0a"

# Decode the byte string
byte_str = bytes.fromhex(byte_str)
print(byte_str)
print(byte_str.decode("shift-jis"))
