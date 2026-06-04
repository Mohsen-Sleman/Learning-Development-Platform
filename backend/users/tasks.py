from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from users.models import User,RoleChoices
from courses.models import Enrollment,TrackEnrollment
from datetime import timedelta
@shared_task
def send_otp_email_task(email,otp_code) :

    send_mail(
                'Activate Your Account',
                f'Welcome! Your verification code is: {otp_code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],          
                fail_silently=False,
            )
    
@shared_task
def send_weekly_report() :
    total_students = User.objects.filter(role = RoleChoices.STUDENT).count()

    one_week_ago = timezone.now() - timedelta(days=7)
    
    # Using last_login permanently because there is no creation time field for the user
    new_students = User.objects.filter(role=RoleChoices.STUDENT, last_login__gte=one_week_ago).count() 

    number_of_enrollment_in_courses = Enrollment.objects.count()
    number_of_enrollment_in_tracks = TrackEnrollment.objects.count()
    total_enrollments = number_of_enrollment_in_courses + number_of_enrollment_in_tracks

    best_course_enrollment = Enrollment.objects.values('course__name').annotate(total = Count('course')).order_by('-total').first()
    most_common_course_title = best_course_enrollment['course__name'] if best_course_enrollment else None
    most_common_course_count = best_course_enrollment['total'] if best_course_enrollment else 0


    best_track_enrollment = TrackEnrollment.objects.values('track__name').annotate(total = Count('track')).order_by('-total').first()
    most_common_track_title = best_track_enrollment['track__name'] if best_track_enrollment else None
    most_common_track_count = best_track_enrollment['total'] if best_track_enrollment else 0

    context = {
        'total_students': total_students,
        'new_students': new_students,
        'total_enrollments': total_enrollments,
        'course_title': most_common_course_title,
        'course_count': most_common_course_count,
        'track_title': most_common_track_title,
        'track_count': most_common_track_count,
    }

    html_message = render_to_string('weekly_report.html', context)

    email = EmailMessage(
        subject='[Learning Platform] Weekly Performance Report',
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.ADMIN_EMAIL], 
    )
    email.content_subtype = "html" 
    email.send(fail_silently=False)