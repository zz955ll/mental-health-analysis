"""
邮件发送服务模块
"""

import random
import smtplib
from email.mime.text import MIMEText
from django.core.cache import cache


def send_email_code(to_mail):
    """
    发送邮箱验证码
    参数: to_mail - 接收邮箱
    返回: {'code': 200, 'msg': '发送成功'} 或 {'code': 500, 'msg': '错误信息'}
    """
    if not to_mail:
        return {'code': 400, 'msg': '邮箱不能为空'}

    from_mail = "3414987943@qq.com"
    code = str(random.randint(1000, 9999))

    # 邮件内容
    msg = MIMEText(f"您的验证码为：{code}，有效期为1分钟。", "plain", "utf-8")
    msg['from'] = from_mail
    msg['to'] = to_mail
    msg['subject'] = "心理健康系统 - 登录验证码"

    try:
        # 发送邮件
        smtp = smtplib.SMTP_SSL("smtp.qq.com", 465)
        smtp.login(from_mail, "lcyxqcalknecdbgj")  # 授权码
        smtp.sendmail(from_mail, to_mail, msg.as_string())
        smtp.close()

        # 存储验证码到缓存，有效期60秒
        cache.set(to_mail, code, timeout=60)

        print(f"验证码：{code} 已发送至 {to_mail}")
        return {'code': 200, 'msg': '发送成功'}

    except Exception as e:
        print(f"发送失败: {e}")
        return {'code': 500, 'msg': str(e)}


def check_code(email, code):
    """
    验证验证码是否正确
    返回: True/False
    """
    correct_code = cache.get(email)
    if not correct_code:
        return False
    return code == correct_code


def get_code(email):
    """
    获取缓存中的验证码（用于调试）
    """
    return cache.get(email)