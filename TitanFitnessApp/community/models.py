from django.conf import settings
from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_posts',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_comments',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)

    def __str__(self):
        return self.content[:50]


class Like(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_likes',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'post'),
                name='unique_like_per_user_per_post',
            ),
        ]




