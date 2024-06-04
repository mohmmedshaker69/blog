from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics', null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    @property
    def total_likes(self):
        # likes = Like.objects.filter(post=self, kind='like')
        return self.likes.filter(kind='like').count()
    
    @property
    def total_unlikes(self):
        unlikes = Like.objects.filter(post=self, kind='unlike')
        return unlikes.count()
    
    @property
    def total_comments(self):
        return Comment.objects.filter(post=self).count()

    def __str__(self):
        return self.title
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return (self.body, self.name)
    
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    kind = models.CharField(choices=[('like', 'Like'), ('unlike', 'Unlike')], max_length=10)

    def __str__(self):
        return f'{self.user.username} {self.kind} {self.post.title}'