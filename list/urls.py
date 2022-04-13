from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import cache_control
from django.conf import settings

# YOUR urlpatterns here...

urlpatterns = []

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, view=cache_control(no_cache=True, must_revalidate=True)(serve))

urlpatterns += [
    path('', views.home, name='home'),
    path('users/', views.users, name="users"),
    path('reviews/<int:pk>', views.reviews, name="reviews"),
    path('books/', views.allbooks, name="allbooks"),
    path('friends/', views.friends, name="friends"),

    path('login/', auth_views.LoginView.as_view(template_name="login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('signup/', views.signup, name='signup'),

    path('api/addbookdate/', views.post_bookdate_form, name='addbookdate'),
    path('api/delbookdate/', views.delbookdate, name='delbookdate'),
    path('api/delbookdate/<int:pk>', views.delbookdate, name='delbookdate'),
    path('api/delreview/<int:pk>', views.delreview, name="delreview"),
    path('api/setprivate/<value>', views.setprivate, name='setprivate'),
    path('api/send_invite/<username>', views.send_invite, name="send_invite"),
    path('api/accept_invite/<username>', views.accept_invite, name="accept_invite"),
    path('api/decline_invite/<username>', views.decline_invite, name="decline_invite"),

    path('<username>/', views.readonly_list, name='readonlylist'),
]
