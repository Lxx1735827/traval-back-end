import hashlib
import os
import binascii


def generate_password_hash(password):
    """
    使用 PBKDF2 生成密码的衍生密钥和盐

    :param password: 明文密码（string）
    :return: (salt, derived_key) 盐和衍生密钥
    """
    salt = os.urandom(16)  # 生成 16 字节的随机盐
    iterations = 1000  # 迭代次数
    dklen = 32  # 衍生密钥的长度，32 字节即 256 位

    # 使用 hashlib 库的 pbkdf2_hmac 函数来实现 PBKDF2
    derived_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations, dklen)

    return salt, derived_key, iterations


def verify_password(input_password, stored_salt, stored_derived_key, stored_iterations):
    """
    验证用户输入的密码与存储的密码是否匹配

    :param input_password: 用户输入的密码（string）
    :param stored_salt: 存储的盐（bytes）
    :param stored_derived_key: 存储的衍生密钥（bytes）
    :param stored_iterations: 存储的迭代次数（int）
    :return: 是否匹配（bool）
    """
    # 确保输入密码是字节类型
    input_password_bytes = input_password.encode('utf-8')  # 将字符串转为字节

    # 如果 stored_salt 和 stored_derived_key 是十六进制字符串，先解码为字节
    if isinstance(stored_salt, str):
        stored_salt = bytes.fromhex(stored_salt)
    if isinstance(stored_derived_key, str):
        stored_derived_key = bytes.fromhex(stored_derived_key)

    # 使用存储的盐、迭代次数对输入密码进行 PBKDF2 处理
    derived_key = hashlib.pbkdf2_hmac('sha256', input_password_bytes, stored_salt, stored_iterations,
                                      len(stored_derived_key))

    # 比较生成的衍生密钥与存储的衍生密钥
    return derived_key == stored_derived_key



if __name__ == "__main__":
    # 用户注册时的操作
    password = "mypassword"  # 假设用户输入的密码是 "mypassword"
    salt, derived_key, iterations = generate_password_hash(password)

    # 假设用户登录时输入的密码是 "mypassword"
    input_password = "mypassword"

    # 从数据库中获取存储的盐、衍生密钥和迭代次数
    stored_salt = salt # 假设从数据库中读取的盐
    stored_derived_key = derived_key  # 假设从数据库中读取的衍生密钥
    stored_iterations = iterations  # 假设从数据库中读取的迭代次数
    print(type(derived_key))

    # 验证密码是否正确
    is_valid = verify_password(input_password, stored_salt, stored_derived_key, stored_iterations)
    print(is_valid)
    if is_valid:
        print("密码验证通过！")
    else:
        print("密码错误！")