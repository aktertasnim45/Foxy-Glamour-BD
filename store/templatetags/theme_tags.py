from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def theme_styles(theme):
    if not theme:
        return ""
    # Create the CSS variable string
    css_vars = (
        f"--primary-color: {theme.primary_color}; "
        f"--text-color: {theme.text_color}; "
        f"--bg-color: {theme.bg_color}; "
        f"--accent-color: {theme.accent_color}; "
        f"--promo-bg: {theme.promo_bg}; "
        f"--btn-bg: {theme.button_bg_color}; "
        f"--btn-text: {theme.button_text_color}; "
        f"--btn-hover-bg: {theme.button_hover_bg_color}; "
        f"--buy-now-bg: {theme.buy_now_bg_color}; "
        f"--buy-now-text: {theme.buy_now_text_color}; "
        f"--buy-now-hover-bg: {theme.buy_now_hover_bg_color}; "
        f"--buy-now-hover-text: {theme.buy_now_hover_text_color};"
    )
    # Return it as a safe string to be rendered in the style attribute
    return mark_safe(f'style="{css_vars}"')
