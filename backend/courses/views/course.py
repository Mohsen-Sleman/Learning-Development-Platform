from rest_framework.generics import RetrieveAPIView,CreateAPIView,ListAPIView,UpdateAPIView,DestroyAPIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Q
from users.permissions import IsInstructor
from courses.models import Course,Status
from courses.filters import CourseFilter
from users.models import RoleChoices
from courses.serializers import CourseDetailSerializer,CourseWriteSerializer,CourseListSerializer


class CourseListView(ListAPIView) :
    queryset = Course.objects.filter(status = Status.PUBLISHED).select_related('instructor').only('name','slug','thumbnail','difficulty_level','instructor__id','instructor__full_name')
    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter]
    # filterset_fields = ['instructor',{'difficulty_level': ['in', 'exact']},]
    filterset_class = CourseFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']

class CourseDetailView(RetrieveAPIView) :
    lookup_field = 'slug'
    serializer_class = CourseDetailSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        base_queryset = Course.objects.select_related('instructor').prefetch_related('sections__lessons')
        if user and user.is_authenticated and user.role == RoleChoices.INSTRUCTOR :
            return base_queryset.filter(Q(instructor = user) | Q(status = Status.PUBLISHED))
        return base_queryset.filter(status = Status.PUBLISHED)
    
class CourseCreateView(CreateAPIView) :
    serializer_class = CourseWriteSerializer
    permission_classes = [IsAuthenticated,IsInstructor]
    

    def perform_create(self, serializer):
        serializer.save(instructor = self.request.user)

class CourseUpdateView(UpdateAPIView) :
    lookup_field = 'slug'
    serializer_class = CourseWriteSerializer
    permission_classes = [IsAuthenticated,IsInstructor]
    

    def get_queryset(self):
        return Course.objects.filter(instructor = self.request.user)
    
class CourseDeleteView(DestroyAPIView) :
    lookup_field = 'slug'
    permission_classes = [IsAuthenticated,IsInstructor]
    
    def get_queryset(self):
        return Course.objects.filter(instructor = self.request.user)
