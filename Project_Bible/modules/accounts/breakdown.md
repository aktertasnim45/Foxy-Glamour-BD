# Accounts Module

> User authentication, registration, and account management.

## Overview

The `accounts` app handles:
- User registration
- Login/Logout
- Password changes
- User dashboard with order history

## Files

| File | Purpose | Lines |
|------|---------|-------|
| `views.py` | Register and dashboard views | ~50 |
| `urls.py` | Auth URL patterns | ~30 |
| `models.py` | Empty (uses Django's built-in User) | - |
| `admin.py` | Default User admin | - |

---

## Views

### register

User registration view using `UserCreationForm`.

```python
from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})
```

---

### dashboard

User dashboard showing order history.

```python
from django.contrib.auth.decorators import login_required
from orders.models import Order

@login_required
def dashboard(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'accounts/dashboard.html', {'orders': orders})
```

---

## URL Patterns

```python
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Custom views
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Django's built-in auth views
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Password change
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(template_name='accounts/password_change_form.html'),
         name='password_change'),
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
         name='password_change_done'),
]
```

---

## Templates

### login.html

```django
{% extends "store/base.html" %}

{% block content %}
<div class="auth-form">
    <h2>Login</h2>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Login</button>
    </form>
    <p>Don't have an account? <a href="{% url 'register' %}">Register</a></p>
</div>
{% endblock %}
```

---

### register.html

```django
{% extends "store/base.html" %}

{% block content %}
<div class="auth-form">
    <h2>Register</h2>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit">Create Account</button>
    </form>
    <p>Already have an account? <a href="{% url 'login' %}">Login</a></p>
</div>
{% endblock %}
```

---

### dashboard.html

```django
{% extends "store/base.html" %}

{% block content %}
<div class="dashboard">
    <h2>My Account</h2>
    
    <div class="user-info">
        <p>Welcome, {{ user.username }}!</p>
        <a href="{% url 'password_change' %}">Change Password</a>
        <a href="{% url 'logout' %}">Logout</a>
    </div>
    
    <h3>Order History</h3>
    {% if orders %}
    <table>
        <thead>
            <tr>
                <th>Order #</th>
                <th>Date</th>
                <th>Status</th>
                <th>Total</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td>{{ order.id }}</td>
                <td>{{ order.created|date:"d M Y" }}</td>
                <td>{{ order.status }}</td>
                <td>৳{{ order.get_total_cost }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p>You haven't placed any orders yet.</p>
    {% endif %}
</div>
{% endblock %}
```

---

## Settings Integration

```python
# jewelry_site/settings.py

# Redirect after login/logout
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

---

## Authentication Flow

### Registration
```
1. User visits /accounts/register/
2. Fills out UserCreationForm (username, password1, password2)
3. Form validated and User created
4. Redirect to login page
```

### Login
```
1. User visits /accounts/login/
2. Enters username and password
3. Django authenticates and creates session
4. Redirect to LOGIN_REDIRECT_URL (/)
```

### Order History
```
1. User visits /accounts/dashboard/
2. @login_required checks authentication
3. If not logged in, redirect to login
4. Fetch orders where user = current user
5. Display order list
```

---

## User Model

Uses Django's built-in `django.contrib.auth.models.User`:

| Field | Type | Description |
|-------|------|-------------|
| `id` | AutoField | Primary key |
| `username` | CharField(150) | Unique username |
| `password` | CharField | Hashed password |
| `email` | EmailField | Email (optional) |
| `first_name` | CharField(150) | First name |
| `last_name` | CharField(150) | Last name |
| `is_active` | BooleanField | Account active |
| `is_staff` | BooleanField | Can access admin |
| `is_superuser` | BooleanField | Has all permissions |
| `date_joined` | DateTimeField | Registration date |
| `last_login` | DateTimeField | Last login time |

---

## Password Requirements

Configured in `settings.py`:

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]
```

**Note:** Only minimum length (6 characters) is enforced. Consider adding:
- `CommonPasswordValidator`
- `NumericPasswordValidator`
- `UserAttributeSimilarityValidator`

---

## Integration Points

### With Orders App
- Orders linked via `order.user` ForeignKey
- Dashboard queries `Order.objects.filter(user=request.user)`

### With Store App
- Wishlist requires authentication
- Templates check `{% if request.user.is_authenticated %}`

### With Base Template
- Dynamic navbar based on authentication status:
```django
{% if request.user.is_authenticated %}
    <a href="{% url 'dashboard' %}">My Account</a>
    <a href="{% url 'logout' %}">Logout</a>
{% else %}
    <a href="{% url 'login' %}">Login</a>
    <a href="{% url 'register' %}">Sign Up</a>
{% endif %}
```

---

## Security Considerations

1. **CSRF Protection:** All forms include `{% csrf_token %}`
2. **Password Hashing:** Django uses PBKDF2 by default
3. **Session Security:** Configure `SESSION_COOKIE_SECURE` in production
4. **Login Required:** `@login_required` decorator for protected views

---

## Future Improvements

1. **Social Authentication:** django-allauth for Google/Facebook login
2. **Email Verification:** Require email confirmation
3. **Profile Page:** Edit user details
4. **Password Reset:** Email-based reset flow
5. **Remember Me:** Extended session support
