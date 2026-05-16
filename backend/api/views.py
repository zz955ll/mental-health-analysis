import json
import random
import smtplib
from email.mime.text import MIMEText
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


@csrf_exempt
@require_http_methods(["GET"])
def 发送验证码(request):
    """发送验证码到邮箱"""
    邮箱 = request.GET.get('to_mail')
    if not 邮箱:
        return JsonResponse({'code': 400, 'msg': '请输入邮箱'})

    验证码 = str(random.randint(1000, 9999))
    发件邮箱 = "3414987943@qq.com"
    授权码 = "lcyxqcalknecdbgj"

    try:
        msg = MIMEText(f"您的验证码为：{验证码}，有效期为1分钟。", "plain", "utf-8")
        msg['from'] = 发件邮箱
        msg['to'] = 邮箱
        msg['subject'] = "心理健康分析系统 - 登录验证码"

        smtp = smtplib.SMTP_SSL("smtp.qq.com", 465)
        smtp.login(发件邮箱, 授权码)
        smtp.sendmail(发件邮箱, 邮箱, msg.as_string())
        smtp.close()

        cache.set(验证码, 邮箱, timeout=60)
        print(f"验证码：{验证码} 已发送至 {邮箱}")
        return JsonResponse({'code': 200, 'msg': '验证码发送成功'})

    except Exception as e:
        print(f"发送失败: {e}")
        return JsonResponse({'code': 500, 'msg': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def 用户登录(request):
    """验证码登录"""
    try:
        数据 = json.loads(request.body)
        邮箱 = 数据.get('email')
        验证码 = 数据.get('code')

        if not 邮箱 or not 验证码:
            return JsonResponse({'code': 400, 'msg': '邮箱和验证码不能为空'})

        缓存邮箱 = cache.get(验证码)

        if 缓存邮箱 and 缓存邮箱 == 邮箱:
            cache.delete(验证码)
            return JsonResponse({'code': 200, 'msg': '登录成功', 'user': 邮箱})
        else:
            return JsonResponse({'code': 401, 'msg': '验证码错误或已过期'})

    except Exception as e:
        return JsonResponse({'code': 500, 'msg': str(e)})


@require_http_methods(["GET"])
def 生成分析报告(request):
    """生成数据分析报告"""
    import os
    项目目录 = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    静态目录 = os.path.join(项目目录, 'static')
    报告路径 = os.path.join(静态目录, '报告首页.html')

    if os.path.exists(报告路径):
        return JsonResponse({
            'code': 200,
            'msg': '报告生成成功',
            'dashboard_url': '/static/报告首页.html'
        })
    else:
        return JsonResponse({
            'code': 404,
            'msg': '报告文件不存在，请先运行 main.py 生成图表'
        })


@require_http_methods(["GET"])
def 获取分析数据(request):
    """获取分析数据"""
    return JsonResponse({
        'code': 200,
        'data': {
            'descriptive': {'depression_rate': '2.6%'},
            'correlation': {'sleep_hours': -0.191},
            'factor': {}
        }
    })