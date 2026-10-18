import re
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.filter
def is_liked_by(post, user):
    if not user or not user.is_authenticated:
        return False
    return post.is_liked_by(user)


@register.filter
def is_bookmarked_by(post, user):
    if not user or not user.is_authenticated:
        return False
    return post.is_bookmarked_by(user)


@register.filter
def is_followed_by(target_user, current_user):
    if not current_user or not current_user.is_authenticated or target_user == current_user:
        return False
    return current_user.following_relations.filter(following=target_user).exists()


@register.filter
def render_content(content):
    if not content:
        return ""
    escaped = escape(content)
    # Convert #hashtag to clickable link
    formatted = re.sub(r'#(\w+)', r'<a href="/explore/?q=%23\1" class="hashtag">#\1</a>', escaped)
    # Convert @mentions to profile links
    formatted = re.sub(r'@(\w+)', r'<a href="/profile/\1/" class="hashtag">@\1</a>', formatted)
    return mark_safe(formatted)
