# test
from django.contrib import admin
from rest_framework.authtoken.views import obtain_auth_token

from . import views
from django.urls import path, re_path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.urls import path
from config.views import CustomUserDetailView

schema_view = get_schema_view(
   openapi.Info(
      title="WishJob API",
      default_version='v1',
      description="API documentation for WishJob project",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="your-email@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('users/', include('users.urls')),
    path('jobfair/', include('jobfair.urls')),
    path('myPage/', include('myPage.urls')),
    path('company/', include('company.urls')),

    path('api-token-auth/', obtain_auth_token),

    path('user/json/<str:email>/', CustomUserDetailView.as_view(), name='user_json'),

]



