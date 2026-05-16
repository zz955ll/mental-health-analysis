from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.contrib.auth.models import User
from .service import send_email_code
from .ml_model import predict_risk, train_model, get_model_status
from .export import export_to_excel, export_to_pdf
from .models import PredictionHistory
import random


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_report(request):
    """导出预测报告"""
    format_type = request.data.get('format', 'excel')
    result = request.data.get('result', {})
    export_data = {
        'risk_level': result.get('risk_level', ''),
        'risk_percentage': result.get('risk_percentage', ''),
        'suggestion': result.get('suggestion', ''),
        'input_data': request.data.get('input_data', {})
    }
    if format_type == 'pdf':
        return export_to_pdf(export_data)
    else:
        return export_to_excel(export_data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_depression(request):
    """预测抑郁风险（需要登录）"""
    try:
        data = request.data
        features = {
            'daily_social_media_hours': float(data.get('daily_social_media_hours', 0)),
            'sleep_hours': float(data.get('sleep_hours', 0)),
            'screen_time_before_sleep': float(data.get('screen_time_before_sleep', 0)),
            'academic_performance': float(data.get('academic_performance', 0)),
            'physical_activity': float(data.get('physical_activity', 0)),
            'stress_level': int(data.get('stress_level', 0)),
            'anxiety_level': int(data.get('anxiety_level', 0)),
            'addiction_level': int(data.get('addiction_level', 0)),
            'age': int(data.get('age', 16)),
            'gender': data.get('gender', 'male'),
            'platform_usage': data.get('platform_usage', 'Both'),
            'social_interaction_level': data.get('social_interaction_level', 'medium')
        }
        result = predict_risk(features)

        # 保存历史记录
        PredictionHistory.objects.create(
            user=request.user,
            input_data=features,
            result=result
        )
        return Response({'code': 200, 'data': result})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'code': 500, 'msg': str(e)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_history(request):
    """获取用户预测历史"""
    limit = int(request.GET.get('limit', 10))
    history = PredictionHistory.objects.filter(user=request.user)[:limit]
    data = []
    for h in history:
        data.append({
            'id': h.id,
            'input_data': h.input_data,
            'result': h.result,
            'risk_level': h.result.get('risk_level', ''),
            'risk_percentage': h.result.get('risk_percentage', ''),
            'created_at': h.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return Response({'code': 200, 'data': data})


@api_view(['POST'])
@permission_classes([AllowAny])
def train_model_api(request):
    """训练模型（管理员接口）"""
    try:
        result = train_model()
        return Response({'code': 200, 'data': result, 'msg': '模型训练成功'})
    except Exception as e:
        return Response({'code': 500, 'msg': str(e)})


@api_view(['GET'])
@permission_classes([AllowAny])
def model_status(request):
    """获取模型状态"""
    return Response({'code': 200, 'data': get_model_status()})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """注册：邮箱 + 验证码 + 密码"""
    email = request.data.get('email')
    password = request.data.get('password')
    code = request.data.get('code')
    if not email or not password or not code:
        return Response({'code': 400, 'msg': '邮箱、密码和验证码不能为空'})
    if len(password) < 6:
        return Response({'code': 400, 'msg': '密码长度不能小于6位'})
    correct_code = cache.get(email)
    if not correct_code or correct_code != code:
        return Response({'code': 400, 'msg': '验证码错误或已过期'})
    if User.objects.filter(username=email).exists():
        return Response({'code': 400, 'msg': '邮箱已注册'})
    user = User.objects.create_user(username=email, email=email, password=password)
    cache.delete(email)
    return Response({'code': 200, 'msg': '注册成功'})


@api_view(['POST'])
@permission_classes([AllowAny])
def send_code(request):
    """发送验证码"""
    to_mail = request.data.get('to_mail')
    if not to_mail:
        return Response({'code': 400, 'msg': '邮箱不能为空'})
    if User.objects.filter(username=to_mail).exists():
        return Response({'code': 400, 'msg': '邮箱已注册，请直接登录'})
    result = send_email_code(to_mail)
    if result['code'] == 200:
        return Response({'code': 200, 'msg': '验证码已发送'})
    else:
        return Response({'code': 500, 'msg': result['msg']})


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """登录：邮箱 + 密码（返回JWT token）"""
    email = request.data.get('email')
    password = request.data.get('password')
    if not email or not password:
        return Response({'code': 400, 'msg': '邮箱和密码不能为空'})
    from django.contrib.auth import authenticate
    user = authenticate(username=email, password=password)
    if not user:
        return Response({'code': 401, 'msg': '邮箱或密码错误'})
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    return Response({
        'code': 200,
        'msg': '登录成功',
        'access': access_token,
        'refresh': str(refresh),
        'user': email
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    """获取当前登录用户信息（需要认证）"""
    user = request.user
    return Response({
        'code': 200,
        'user': user.username,
        'email': user.email,
        'is_authenticated': True
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """退出登录"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception as e:
        pass
    return Response({'code': 200, 'msg': '已退出'})


@api_view(['POST'])
@permission_classes([AllowAny])
def send_login_code(request):
    """发送登录验证码（旧版兼容）"""
    to_mail = request.data.get('to_mail')
    if not to_mail:
        return Response({'code': 400, 'msg': '邮箱不能为空'})
    result = send_email_code(to_mail)
    if result['code'] == 200:
        return Response({'code': 200, 'msg': '验证码已发送'})
    else:
        return Response({'code': 500, 'msg': result['msg']})


@api_view(['POST'])
@permission_classes([AllowAny])
def login_with_code(request):
    """验证码登录（旧版兼容）"""
    email = request.data.get('email')
    code = request.data.get('code')
    if not email or not code:
        return Response({'code': 400, 'msg': '邮箱和验证码不能为空'})
    correct_code = cache.get(email)
    if not correct_code or correct_code != code:
        return Response({'code': 401, 'msg': '验证码错误或已过期'})
    cache.delete(email)
    user, created = User.objects.get_or_create(username=email, email=email)
    if created:
        user.set_unusable_password()
        user.save()
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    return Response({
        'code': 200,
        'msg': '登录成功',
        'access': access_token,
        'refresh': str(refresh),
        'user': email
    })