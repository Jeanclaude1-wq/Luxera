from django.urls import path
from . import views
from django.conf import settings
from .cancel_reservation import cancel_reservation
from django.conf.urls.static import static
from .procceed_to_payment import procceed

urlpatterns = [

    # HOME
    path('', views.home, name='home'),

    path('listings/', views.hotel_list, name='hotel_list'),

    # HOTEL DETAIL (rooms inside)
    path('hotel/<int:hotel_id>/', views.hotel_detail, name='hotel_detail'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),

    # ADD ROOM (admin)
    path('dashboard/add-room/', views.add_room, name='add_room'),

    # ADD HOTEL PHOTOS (admin)  <-- NEW
    path('dashboard/hotel-images/', views.add_hotel_images, name='add_hotel_images'),

    # AUTH
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # ROOM DETAIL PAGE  <-- Needed for clicking on a room
    path('room/<int:room_id>/', views.room_detail, name='room_detail'),

    # BOOK A ROOM
    path('room/<int:room_id>/book/', views.book_room, name='book_room'),

    # USER BOOKINGS
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel_reservation/', cancel_reservation, name='cancel_reservation'),
    path('proceed_to_payment/', procceed, name='procceed'),

    # ADMIN – ACCEPT / REJECT BOOKING
    path(
        'booking/<int:booking_id>/<str:action>/',
        views.update_booking_status,
        name='update_booking_status'
    ),
    path('dashboard/hotel-images/', views.add_hotel_images, name='add_hotel_images'),
path('dashboard/room/<int:room_id>/images/', views.add_room_images, name='add_room_images'),
path('booking/<int:booking_id>/payment/', views.upload_payment, name='upload_payment'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
