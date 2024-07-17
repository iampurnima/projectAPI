from rest_framework import generics
from .models import Category,MenuItem,Cart,Order,OrderItem
from .serializers import MenuItemSerializer,CategorySerializer,CartSerializer,OrderSerializer,OrderItemSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes,throttle_classes
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import UserRateThrottle
from rest_framework.permissions import IsAdminUser
#from .throttles import TenCallsPerMinute
from django.contrib.auth.models import User,Group
from rest_framework.views import APIView
from rest_framework import status
from .permissions import IsManager
from django.utils import timezone

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class MenuItemListView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer 

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    
# @api_view()
# def secret(request):
#     return Response({"Message":"Some secret message"})    #anyone can see this end points 

@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({"Message":"Some secret message"}) #This time only authenticated user can see the endpoint and this end point can test in insomnia 


#users roles 

@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    return Response({"Message":"Only manager should see this"}) # after checking of this end points in insomnia both user and manager can see the end point 


# to fix this and make only manager  can access this end point 

@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter().exists(): #using this line developer can check which groups the current authenticated user belongs to and then check if the manage group exists in that list
        return Response({"Message":"Only manager should see this"})
    else:
        return Response({"Message":"You are not authorized"},403)
    
    
#in this way we can protect any end points from unauthorized access in drf     


@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message":"successfull"})

#throttle some end points for the authenticated users to 10 calls per minute 


@api_view()
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])#TenCallsPerMinute
def throttle_check_auth(request):
    return Response({"Message":"message for the logged in users only "})



#making end point for the super admin that end point is used to assign users to the manager group or ermove them from it . this end point only access by the super admin 

# @api_view(['POST'])
# @permission_classes([IsAdminUser])
# def managers(request):
#     return Response({"Message":"Ok"}) # this end point should accept one post field "username" if the user name is present find the user and add to the gropu  so import user and group at the top 

@api_view(['POST'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data['username']
    return Response({"Message":"Ok"})
    if username:
        user = get_object_or_404(User,username = username)
        managers = Group.objects.get(name = "Manager")
        if request.method =='POST':
            managers.user_set.add(user)
        elif request.method =='DELETE':
            managers.user_set.remove(user)    
        return Response({"message":"Ok"})
    return Response({"message":"error"},status.HTTP_400_BAD_REQUEST)

class CartView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        user = request.user
        cart_items = Cart.objects.filter(user = user)
        serializer = CartSerializer(cart_items,many = True)
        return Response(serializer.data)
    def post(self,request):
        user = request.user
        data = request.data.copy()
        data['user'] = user.id
        serializer = CartSerializer(data=data)
        serialized_item = CartSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
      
    def delete(self,request):
        user = request.user
        Cart.objects.filter(user = user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CustomerOrderView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        user = request.user
        orders = Order.objects.filter(user = user)
        serializer = OrderSerializer(orders,many = True )
        return Response(serializer.data)
    
    def post(self, request):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        
        order = Order.objects.create(user=user, total=0, date=timezone.now().date())
        total = 0
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            total += item.price
        
        order.total = total
        order.save()
        cart_items.delete()
        
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    
class CustomerOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, orderId):
        user = request.user
        try:
            order = Order.objects.get(id=orderId, user=user)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class ManagerOrderView(APIView):
    permission_classes = [IsAuthenticated]  # Add a custom permission for Manager

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class ManagerOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Add a custom permission for Manager
    
    def put(self, request, orderId):
        try:
            order = Order.objects.get(id=orderId)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        if 'delivery_crew' in data:
            order.delivery_crew_id = data['delivery_crew']
        if 'status' in data:
            order.status = data['status']
        
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    
    def delete(self, request, orderId):
        try:
            order = Order.objects.get(id=orderId)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DeliveryCrewOrderView(APIView):
    permission_classes = [IsAuthenticated]  # Add a custom permission for Delivery Crew
    
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(delivery_crew=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class DeliveryCrewOrderDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Add a custom permission for Delivery Crew
    
    def patch(self, request, orderId):
        user = request.user
        try:
            order = Order.objects.get(id=orderId, delivery_crew=user)
        except Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        data = request.data
        if 'status' in data:
            order.status = data['status']
            order.save()
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
class ManagerGroupView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        managers = User.objects.filter(groups__name='Manager')
        manager_data = [{"id": manager.id, "username": manager.username, "email": manager.email} for manager in managers]
        return Response(manager_data, status=status.HTTP_200_OK)

    def post(self, request):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            manager_group = Group.objects.get(name='Manager')
            user.groups.add(manager_group)
            return Response({"status": "user added to manager group"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Manager group not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            manager_group = Group.objects.get(name='Manager')
            user.groups.remove(manager_group)
            return Response({"status": "user removed from manager group"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Manager group not found"}, status=status.HTTP_404_NOT_FOUND)
class ManagerGroupDetailView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, userId):
        try:
            user = User.objects.get(id=userId)
            group = Group.objects.get(name='Manager')
            user.groups.remove(group)
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

class DeliveryCrewGroupView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        delivery_crew = User.objects.filter(groups__name='DeliveryCrew')
        delivery_crew_data = [{'id': member.id, 'username': member.username} for member in delivery_crew]
        return Response(delivery_crew_data)

    def post(self, request):
        user_id = request.data.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            group = Group.objects.get(name='DeliveryCrew')
            user.groups.add(group)
            return Response(status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)

class DeliveryCrewGroupDetailView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def delete(self, request, userId):
        try:
            user = User.objects.get(id=userId)
            group = Group.objects.get(name='DeliveryCrew')
            user.groups.remove(group)
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=status.HTTP_404_NOT_FOUND)
        

class MenuItemListView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['POST']:
            self.permission_classes = [IsAuthenticated, IsManager]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def post(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().post(request, *args, **kwargs)

class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsManager]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def delete(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name='Manager').exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().patch(request, *args, **kwargs)
        