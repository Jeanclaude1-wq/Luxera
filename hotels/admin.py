from django.contrib import admin
from .models import Hotel, HotelImage, Room, RoomImage, Booking


# -----------------------
# HOTEL ADMIN
# -----------------------
class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'type', 'admin')
    list_filter = ('type', 'location')
    search_fields = ('name', 'location', 'admin__username')
    inlines = [HotelImageInline]  # allows uploading multiple images inside hotel admin


# -----------------------
# ROOM ADMIN
# -----------------------
class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'price_per_night', 'is_available')
    list_filter = ('hotel', 'is_available')
    search_fields = ('name', 'hotel__name')
    inlines = [RoomImageInline]  # allows uploading room images inside room admin


# -----------------------
# BOOKING ADMIN
# -----------------------
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'room', 'check_in', 'check_out',
        'status', 'payment_status', 'created_at'
    )
    list_filter = ('status', 'payment_status', 'room', 'check_in', 'check_out')
    search_fields = ('user__username', 'room__name', 'room__hotel__name')
