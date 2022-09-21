from django.urls import include, path

from users.views import SubcribeApiView, SubcribeListAPIView

urlpatterns = [
    path('users/<int:id>/subscribe/', SubcribeApiView.as_view(),
         name='subscribe'),
    path('users/subscriptions/', SubcribeListAPIView.as_view(),
         name='subscription'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
