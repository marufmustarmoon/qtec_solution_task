from rest_framework import serializers
 
from .models import Blog,User,Bookmark


 
        
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    user_type = serializers.ChoiceField(choices=[('author', 'Author'), ('normal', 'Normal User')])

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        user_type = data.get('user_type')

        if not username or not password:
            raise serializers.ValidationError({'detail': 'Username and password are required'})


        return data
    
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password','user_type']
        extra_kwargs = {'password': {'write_only': True}}
    
    


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'blog', 'created_at']