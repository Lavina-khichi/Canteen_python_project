"""
URL configuration for canteen project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from canteen_app import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',views.index, name="home"),
    path('register',views.user_reg, name="register"),
    path('login',views.user_login, name="login"),
    path('logout',views.user_logout, name="logout"),
    path('menu',views.menu_page, name="menu"),
    path('add_to_cart/<int:menu_item_id>',views.add_to_cart, name="add_to_cart"),
    path('cart',views.cart_page, name="cart"),
    path('pay_online/<int:order_id>',views.pay_online, name="pay_online"),
    path('pay_card/<int:order_id>',views.pay_card, name="pay_card"),
    path('order',views.order_page, name="order"),
    path('repeat_order/<int:order_id>/', views.repeat_order, name='repeat_order'),
    path('book_table',views.book_table, name="book_table"),
    path('cancel_reservation/<int:res_id>',views.cancel_reservation, name="cancel_res"),
    path('check_reservations',views.check_reservations_page, name="check_reservations"),
    path('admin/', admin.site.urls),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
