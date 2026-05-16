from django.urls import path
from . import views  # 旧版视图
from . import views_api  # 新版DRF视图

urlpatterns = [
    # ========== 旧版API（兼容原有前端）==========
    path('send-code/', views.发送验证码, name='send_code'),
    path('login/', views.用户登录, name='login'),
    path('generate-report/', views.生成分析报告, name='generate_report'),
    path('get-data/', views.获取分析数据, name='get_data'),

    # ========== 新版API（DRF + JWT）==========
    path('register/', views_api.register, name='register'),
    path('api-send-code/', views_api.send_code, name='api_send_code'),
    path('api-login/', views_api.login, name='api_login'),
    path('user/', views_api.get_user_info, name='user_info'),
    path('api-logout/', views_api.logout, name='api_logout'),
    path('send-login-code/', views_api.send_login_code, name='send_login_code'),
    path('login-with-code/', views_api.login_with_code, name='login_with_code'),

# 在 urlpatterns 中添加
path('predict/', views_api.predict_depression, name='predict'),
path('train-model/', views_api.train_model_api, name='train_model'),
path('model-status/', views_api.model_status, name='model_status'),
path('export/', views_api.export_report, name='export'),
path('history/', views_api.get_history, name='history'),
]
