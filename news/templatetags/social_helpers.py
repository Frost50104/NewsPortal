from django import template
from django.contrib.sites.models import Site

try:
    # allauth is optional in some environments, guard import
    from allauth.socialaccount.models import SocialApp
except Exception:  # pragma: no cover
    SocialApp = None

register = template.Library()


@register.simple_tag(takes_context=True)
def social_app_configured(context, provider):
    """
    Returns True if a django-allauth SocialApp for the given provider exists
    and is attached to the current Site. Safe to use even if allauth is not
    installed or misconfigured — it will simply return False.
    Usage in template:
        {% load social_helpers %}
        {% if social_app_configured 'yandex' %}
            ... show login link ...
        {% endif %}
    """
    if SocialApp is None:
        return False
    try:
        current_site = Site.objects.get_current()
        return SocialApp.objects.filter(provider=provider, sites=current_site).exists()
    except Exception:
        # Any issues (e.g., migrations pending) — do not break templates
        return False
