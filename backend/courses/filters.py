import django_filters
from django.db.models import Q
from courses.models import Course,Track,Enrollment,TrackEnrollment


class SearchFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='filter_by_name')

    def filter_by_name(self, queryset, name, value):
        keywords = [word for word in value.split() if word.strip()]

        query = Q()
        for word in keywords:
            query |= Q(**{f"{self.search_field}__icontains" : word})
            
        return queryset.filter(query)

class CourseFilter(SearchFilter) :
    search_field = 'name'
    class Meta :
        model = Course
        fields=['instructor', 'difficulty_level']


class TrackFilter(SearchFilter) :
    search_field = 'name'
    class Meta :
        model = Track
        fields=[]

class EnrollmentCourseFilter(SearchFilter) :
    search_field = 'course__name'
    class Meta :
        model = Enrollment
        fields=[]

class EnrollmentTrackFilter(SearchFilter) :
    search_field = 'track__name'
    class Meta :
        model = TrackEnrollment
        fields=[]
