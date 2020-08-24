from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from .models import Post, Cv
from .forms import PostForm, CvForm

# Create your views here.
def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    return render(request, 'blog/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

@login_required
def post_new(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PostForm(request.POST)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                #post.published_date = timezone.now() #disabled as publishing is now done separately
                post.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = PostForm()
        return render(request, 'blog/post_edit.html', {'form': form})
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

@login_required
def post_edit(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.published_date = timezone.now()
                post.save()
                return redirect('post_detail', pk=post.pk)
        else:
            form = PostForm(instance=post)
        return render(request, 'blog/post_edit.html', {'form': form})
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

@login_required
def post_draft_list(request):
    posts = Post.objects.filter(published_date__isnull=True).order_by('created_date')
    return render(request, 'blog/post_draft_list.html', {'posts': posts})

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)

@login_required
def post_remove(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    return redirect('post_list')

def cv_view(request):
    cv = get_object_or_404(Cv)
    return render(request, 'blog/cv_view.html', {'cv': cv})

@login_required
def cv_update(request):
    if request.user.is_authenticated:
        cv = get_object_or_404(Cv)
        if request.method == "POST":
            form = CvForm(request.POST, instance=cv)
            if form.is_valid():
                cv = form.save(commit=False)
                cv.owner = request.user
                cv.last_updated = timezone.now()
                cv.save()
                return redirect('cv_view')
        else:
            form = CvForm(instance=cv)
        return render(request, 'blog/cv_update.html', {'cv': cv})
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    
    