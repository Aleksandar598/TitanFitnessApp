from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from community.forms import CreatePostForm, CreateCommentForm
from community.models import Post, Like, Comment


# Create your views here.
@login_required
def community_view(request):
    if request.method == 'POST':
        post_form = CreatePostForm(request.POST)

        if post_form.is_valid():
            Post.objects.create(
                author=request.user,
                title=post_form.cleaned_data['title'],
                content=post_form.cleaned_data['content'],
            )
            return redirect('community')
    else:
        post_form = CreatePostForm()

    posts = Post.objects.select_related(
        'author',
    ).prefetch_related(
        'comments__author',
        'likes',
    )

    liked_post_ids = set(
        Like.objects.filter(
            author=request.user,
            post__in=posts,
        ).values_list('post_id', flat=True)
    )

    return render(request, 'community/community.html', {
        'post_form': post_form,
        'comment_form': CreateCommentForm(),
        'posts': posts,
        'liked_post_ids': liked_post_ids,
    })

@login_required
@require_POST
def create_comment_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CreateCommentForm(request.POST)

    if form.is_valid():
        Comment.objects.create(
            author=request.user,
            post=post,
            content=form.cleaned_data['content'],
        )
    else:
        messages.error(request, 'Comment cannot be empty.')

    return redirect('community')


@login_required
@require_POST
def toggle_like_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    like = Like.objects.filter(
        author=request.user,
        post=post,
    ).first()

    if like:
        like.delete()
    else:
        Like.objects.create(
            author=request.user,
            post=post,
        )

    return redirect('community')
