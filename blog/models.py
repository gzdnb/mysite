from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import User
from read_statistics.models import ReadNumExpandMethod, ReadDetail
from django.contrib.contenttypes.fields import GenericRelation
# Create your models here.



# 博客分类模型
class BlogType(models.Model):
    type_name = models.CharField(max_length=20)

    def __str__(self):
        return self.type_name


# 博客模型
class Blog(models.Model, ReadNumExpandMethod):
    """ *标题*分类*内容*作者*创建时间*最后修改时间* """
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)
    content = RichTextUploadingField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    read_details = GenericRelation(ReadDetail)
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now=True)

    
    


    def __str__(self):
        return "<Blog: %s>" % self.title
    
    # 这里是models的元数据,也可以理解为对数据库基础信息进行管理
    class Meta:
        # ordering字段表示排序,加上-符号表示倒序
        ordering = ['-created_time']

    
