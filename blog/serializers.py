from rest_framework import serializers
 
from .models import Blog,User,Bookmark


 
        
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError({'detail': 'Username and password are required'})

        return data
    
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    isAuthor = serializers.BooleanField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'isAuthor']

    def create(self, validated_data):
        isAuthor = validated_data.pop('isAuthor', False)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        user.isAuthor = isAuthor
        user.save()
        return user
    
    


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = '__all__'


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'blog', 'created_at']