from django.urls import path

from . import views

urlpatterns = [
    path('list', views.list_all_events, name='list-all-events'),
    path('create', views.create_event, name='create-event'),
    path('<int:id>', views.show_event, name='show-event'),
    path('<int:id>/vote', views.add_vote, name='add-vote'),
    path('<int:id>/results', views.show_results, name='show-results'),
    path('<int:id>/delete', views.delete_event, name='delete-event')
]