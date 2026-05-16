from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class PredictionHistory(models.Model):
    """预测历史记录"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input_data = models.JSONField()  # 存储输入数据
    result = models.JSONField()  # 存储预测结果
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"