from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import random
import json
import os
from src.setting import *
from src.accesskey import *

def generate_verification_code(length=6):
    return ''.join(random.choices('0123456789', k=length))

async def code_sender(phonenumber: str):
    print("code_sender")
    PhoneNumber = phonenumber
    code = generate_verification_code(6)
    acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, template_code)

    # 创建CommonRequest实例
    request = CommonRequest()

    # 设置请求参数,下面这5行其实不用动
    request.set_accept_format('json')  # 设置API响应格式的方法
    request.set_domain('dysmsapi.aliyuncs.com')  # 设置API的域名的方法
    request.set_method('POST')  # 设置API请求方法
    request.set_version('2017-05-25')  # 设置API版本号
    request.set_action_name('SendSms')  # 设置API操作名

    # 设置短信模板参数
    request.add_query_param('PhoneNumbers', PhoneNumber)
    request.add_query_param('SignName', SIGN_NAME)
    request.add_query_param('TemplateCode', template_code)
    # request.add_query_param('TemplateParam', '{"code":"123456"}')
    template_param = {"code": code}
    request.add_query_param('TemplateParam', json.dumps(template_param))
    # 发送短信请求并获取返回结果
    response = acs_client.do_action_with_exception(request)

    print(response)

    return code

