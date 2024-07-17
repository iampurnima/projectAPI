from django.urls import path, include
from . import views
from rest_framework.authtoken.views import obtain_auth_token #for token generation from endpoints

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='categories-list'),
    path('categories/<int:pk>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('menu-items/', views.MenuItemListView.as_view(), name='menu-items-list'),
    path('menu-items/<int:pk>/', views.MenuItemDetailView.as_view(), name='menu-item-detail'),
    path('secret/',views.secret),
    path('api-token-auth/',obtain_auth_token),# this end point only accept http post call
    path('manager-view/',views.manager_view),
    path('throttle-check/',views.throttle_check),
    path('throttle-check-auth',views.throttle_check_auth),
    path('groups/manager/users',views.managers), #Test this end point with user token and admin token ans see the result in insomnia with post call, 
    path('cart/menu-items/',views.CartView.as_view()),
    path('orders/',views.CustomerOrderView.as_view()),
    path('orders/<int:orderId>',views.CustomerOrderDetailView.as_view()),
    path('manager/orders/',views.ManagerOrderView.as_view()),
    path('manager/orders/<int:orderId>',views.ManagerOrderDetailView.as_view()),
    path('delivery/orders',views.DeliveryCrewOrderView.as_view()),
    path('delivery/orders/<int:orderId>',views.DeliveryCrewOrderDetailView.as_view()),
    path('groups/manager/users/',views.ManagerGroupView.as_view()),
    path('groups/manager/users/<int:userId>',views.ManagerGroupDetailView.as_view()),
    path('groups/delivery-crew/users',views.DeliveryCrewGroupView.as_view()),
    path('group/delivery-crew/users/<int:userId>',views.DeliveryCrewGroupView.as_view()),
    path('api/menu-items',views. MenuItemListView.as_view()),
    path('api/menu-items/<int:pk>',views. MenuItemDetailView.as_view()),
]


