from django import forms
from .models import Comment, Post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ["post"]
        labels = {
            "user_name": "Your Name",
            "user_email": "Your Email",
            "text": "Your Comment"
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ["slug"] # We will auto-generate the slug in the view
