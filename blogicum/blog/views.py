from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.db import models

from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from django.contrib.auth.decorators import login_required

from .models import Post, Category, Comment
from .forms import CorrectUserChangeForm, PostForm, CommentForm
from .utils import get_full_name

from datetime import datetime


User = get_user_model()


class HomePageView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.select_related(
            'category',
            'author',
            'location'
        ).filter(
            category__is_published=True,
            is_published=True,
            pub_date__date__lt=datetime.now(),
        ).annotate(
            comment_count=models.Count('comment')
        ).order_by('-pub_date')


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        return get_object_or_404(
            Post.objects.select_related('category', 'author', 'location'),
            id=self.kwargs['id'],
            category__is_published=True,
            is_published=True,
            pub_date__date__lt=datetime.now(),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comment.select_related('author')
        )
        return context


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    ordering = '-pub_date'
    paginate_by = 10

    def get_queryset(self):
        category = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return Post.objects.select_related(
            'category',
            'author',
            'location'
        ).filter(
            category=category,
            is_published=True,
            pub_date__date__lt=datetime.now(),
        ).annotate(
            comment_count=models.Count('comment')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug']
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'data': self.request.POST or None,
            'files': self.request.FILES or None
        })
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.author != request.user:
            return redirect('blog:post_detail', pk=obj.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'data': self.request.POST or None,
            'files': self.request.FILES or None
        })
        return kwargs

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.id})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_queryset(self):
        return super().get_queryset().filter(author=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class ProfileView(ListView):
    template_name = 'blog/profile.html'
    context_object_name = 'page_obj'
    paginate_by = 10

    def get_queryset(self):
        self.profile = get_object_or_404(
            User.objects.all(),
            username=self.kwargs['username']
        )

        return Post.objects.select_related(
            'category',
            'author',
            'location',
        ).filter(author=self.profile).annotate(
            comment_count=models.Count('comment')
        ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['profile'] = self.profile
        context['profile'].get_full_name = get_full_name(
            self.profile.first_name,
            self.profile.last_name
        )
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = CorrectUserChangeForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


@login_required
def add_comment(request, id):
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id)


@login_required
def edit_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'

    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(
        Comment, id=comment_id, post=post, author=request.user)

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, template_name, {
        'form': form,
        'post': post,
        'comment': comment
    })


@login_required
def delete_comment(request, post_id, comment_id):
    template_name = 'blog/comment.html'

    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(
        Comment, id=comment_id, post=post, author=request.user)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)

    return render(request, template_name, {
        'post': post,
        'comment': comment
    })
