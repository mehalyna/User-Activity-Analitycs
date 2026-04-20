from django.urls import path
from .views import EventCreateView, UserEventsView, DailyReportView

app_name = 'events'

urlpatterns = [
    path('events/', EventCreateView.as_view(), name='event-create'),
    path('users/<str:user_id>/events/', UserEventsView.as_view(), name='user-events'),
    path('reports/daily/', DailyReportView.as_view(), name='daily-report'),
]
