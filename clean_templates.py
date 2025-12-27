import os

pdp_path = r'i:\FGBDgithub\Foxy-Glamour-BD\store\templates\store\product_detail.html'

# Clean version of the header blocks
clean_blocks = """{% extends "store/base.html" %}
{% load static %}

{% block title %}{% if product.meta_title %}{{ product.meta_title }}{% else %}{{ product.name }}{% endif %} - Foxy Glamour{% endblock %}

{% block meta_description %}{% if product.meta_description %}{{ product.meta_description }}{% else %}{{ product.description|striptags|truncatewords:20 }}{% endif %}{% endblock %}
{% block meta_keywords %}{% if product.meta_keywords %}{{ product.meta_keywords }}{% else %}jewelry, {{ product.name }}, {{ product.category.name }}{% endif %}{% endblock %}

{% block og_title %}{{ product.name }}{% endblock %}
{% block og_description %}{{ product.description|striptags|truncatewords:30 }}{% endblock %}
{% block og_image %}{% if product.image %}{{ product.image.url }}{% else %}{% static 'img/logo.svg' %}{% endif %}{% endblock %}
{% block og_type %}product{% endblock %}

{% block promo_bar %}{% endblock %}

{% block content %}"""

with open(pdp_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find where the content block starts (it's safe to identify by {% block content %})
split_val = '{% block content %}'
parts = content.split(split_val)

if len(parts) > 1:
    # Keep everything after {% block content %}
    new_content = clean_blocks + parts[1]
    with open(pdp_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully cleaned product_detail.html")
else:
    print("Could not find content block in PDP")
