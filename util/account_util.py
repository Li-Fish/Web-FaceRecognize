from time import sleep

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired

from util.fish_logger import log


def generate_auth_token(content, expiration, secret_key):
    s = Serializer(secret_key, expires_in=expiration)
    return s.dumps({'content': content}).decode('utf-8')


def decode_auth_token(token, secret_key):
    s = Serializer(secret_key)
    try:
        data = s.loads(token)
        return data['content']
    except Exception as e:
        log.error(e)
        return None


if __name__ == '__main__':
    a = generate_auth_token(2, content="tst", secret_key="magic")
    b = decode_auth_token(a, "magic")
    print(a)
    print(b)
