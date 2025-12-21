from .models import Category, Theme, HeroSection

def categories(request):
    return {
        'categories': Category.objects.filter(parent=None)
    }

def active_theme(request):
    theme = Theme.objects.filter(is_active=True).first()
    return {'active_theme': theme}

def active_hero(request):
    """Provides the active hero section configuration to all templates."""
    hero = HeroSection.objects.filter(is_active=True).first()
    return {'active_hero': hero}
