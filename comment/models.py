from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User



# Create your models here.

class Comment(models.Model):
    """  """
    
    # 关联外键
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    
    # 文章id
    object_id = models.PositiveIntegerField()

    # 文章对象
    content_object = GenericForeignKey('content_type', 'object_id')

    # 评论文本
    text = models.TextField()
 
    # 评论时间
    comment_time = models.DateTimeField(auto_now_add=True)
    
    # 评论用户
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)

    # 实现回复评论的功能
    root = models.ForeignKey('self', null=True, related_name="root_comment", on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, related_name="parent_comment", on_delete=models.CASCADE)
    reply_to = models.ForeignKey(User, null=True, related_name="replies", on_delete=models.CASCADE)


    def __str__(self):
        return self.text


    class Meta:
        ordering = ["comment_time"]





