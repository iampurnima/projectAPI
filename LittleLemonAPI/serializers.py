from rest_framework import serializers
from .models import Category, MenuItem,Cart,Order,OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title']
        
class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only = True)
    category = CategorySerializer(read_only = True)
    class Meta:
        model = MenuItem
        fields = '__all__'        #['id','title','price','featured','category','category_id']        
        
        
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart 
        fields = ['id','user','menuitem','quantity','unit_price','price']
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User 
        fields = ['id']   
        

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem 
        fields = ['id','order','menuitem','quantity','unit_price','price']  
                        
class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(read_only = True,many = True)
    class Meta:
        model = Order
        fields = ['id','user','delivery_crew','status','total','date','order_items' ]               