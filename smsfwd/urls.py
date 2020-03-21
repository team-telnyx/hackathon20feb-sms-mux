from django.urls import path
from . import views

app_name = "smsfwd"

urlpatterns = [
    path("messages/", views.message_list),
    path("team_numbers/", views.teamnum_list),
    path("team_numbers/<pk>/", views.teamnum_detail),
    path("telnyx_webhook/", views.telnyx_webhook, name="telnyx_webhook"),
    path("messaging_profile/", views.msgprof_configure),
    #
    # old names
    path("teamnumbers/", views.teamnum_list),
    path("teamnumbers/<pk>/", views.teamnum_detail),
]
