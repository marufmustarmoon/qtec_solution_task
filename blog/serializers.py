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
    
    

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     isAuthor = serializers.BooleanField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'password', 'isAuthor']

#     def create(self, validated_data):
#         username = validated_data.get('username')
#         password = validated_data.get('password')
#         is_author = validated_data.get('isAuthor', False)
#         print(is_author)

#         user, created = User.objects.get_or_create(username=username)
#         print(user)
#         if created:
#             user.set_password(password)
#         else:
#             # If the user already exists, update isAuthor if it's different
#             if user.isAuthor != is_author:
#                 user.isAuthor = is_author
#                 user.save(update_fields=['isAuthor'])

#         return user
    
    


class BlogSerializer(serializers.ModelSerializer):
    author_username = serializers.SerializerMethodField()

    def get_author_username(self, obj):
        return obj.author.username if obj.author else None
    class Meta:
        model = Blog
        fields = '__all__'


class BookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'blog', 'created_at']