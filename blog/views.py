from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView
from django.utils.text import slugify
from .models import Post
from .forms import CommentForm, PostForm

class StartingPageView(ListView):
    template_name = "blog/index.html"
    model = Post
    context_object_name = "posts"

    def get_queryset(self):
        # Fetches the base queryset and slices the first 3
        queryset = super().get_queryset()
        data = queryset.order_by("-date")[:3]
        return data

class AllPostsView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    context_object_name = "collection"
    ordering = ["-date"]

class PostDetailView(View):
    # The underscore indicates this is an internal/private helper method
    def _get_context(self, post, comment_form):
        return {
            "post": post,
            "post_tags": post.tags.all(),
            "comment_form": comment_form,
            "comments": post.comments.all().order_by("-id")
        }

    def get(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        # Calling the internal helper
        context = self._get_context(post, CommentForm())
        return render(request, "blog/post-detail.html", context)

    def post(self, request, slug):
        post = get_object_or_404(Post, slug=slug)
        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect("post-detail-page", slug=slug)

        # Calling the internal helper to re-render with errors
        context = self._get_context(post, comment_form)
        return render(request, "blog/post-detail.html", context)

class ReadLaterView(View):
    def get(self, request):
        # Retrieve the list of post IDs from the user's session; default to an empty list if it doesn't exist
        stored_posts = request.session.get("stored_posts", [])
        context = {}

        if len(stored_posts) == 0:
            context["posts"] = []
            context["has_posts"] = False
        else:
            # Fetch all Post objects whose primary keys match any ID in our session list
            posts = Post.objects.filter(id__in=stored_posts)
            context["posts"] = posts
            context["has_posts"] = True

        return render(request, "blog/stored-posts.html", context)


    def post(self, request):
        # Get the current list of IDs from the session to prepare for modification
        stored_posts = request.session.get("stored_posts", [])
        post_id = int(request.POST["post_id"])

        # Toggle logic: Add the ID if it's new, or remove it if the user clicked "Remove"
        if post_id not in stored_posts:
            stored_posts.append(post_id)
        else:
            stored_posts.remove(post_id)

        # Save the updated list back into the session dictionary
        request.session["stored_posts"] = stored_posts
        
        # Redirect the user back to the page they came from, or the home page as a fallback
        return redirect(request.POST.get("next", "/"))

class CreatePostView(View):
    def get(self, request):
        form = PostForm()
        return render(request, "blog/create-post.html", {"form": form})

    def post(self, request):
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.slug = slugify(post.title)
            post.save()
            form.save_m2m()  # Required to save many-to-many relationships (tags)

            return redirect("starting-page")
        
        return render(request, "blog/create-post.html", {"form": form})
