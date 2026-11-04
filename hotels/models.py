from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# ==========================
#  HOTEL MODEL
# ==========================
class Hotel(models.Model):

    PROPERTY_TYPES = [
        ("Hotel", "Hotel"),
        ("Apartment", "Apartment"),
        ("Guesthouse", "Guesthouse"),
        ("Resort", "Resort"),
    ]

    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    # ✔ Correct type field
    type = models.CharField(max_length=50, choices=PROPERTY_TYPES, default="Hotel")

    image = models.ImageField(upload_to='hotel_images/', blank=True, null=True)
    admin = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


# ==========================
#  MULTIPLE HOTEL IMAGES
# ==========================
class HotelImage(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hotel_images/')

    def __str__(self):
        return f"Image for {self.hotel.name}"


# ==========================
#  ROOM MODEL
# ==========================
class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='room_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} — {self.hotel.name}"


# ==========================
#  MULTIPLE ROOM IMAGES
# ==========================
class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')

    def __str__(self):
        return f"Image for {self.room.name}"


# ==========================
#  BOOKING MODEL
# ==========================
class Booking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("Canceled", "Canceled"),
    ]

    PAYMENT_CHOICES = [
        ("pending_payment", "Pending Payment"),
        ("paid", "Paid"),
        ("rejected", "Payment Rejected"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')

    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="pending_payment")

    payment_proof = models.ImageField(upload_to='payment_proofs/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} → {self.room.name}"


    def get_total_price(self):
        """
        Calculate total price based on number of nights.
        """
        if self.check_out <= self.check_in:
            raise ValidationError("Check-out date must be after check-in date.")

        nights = (self.check_out - self.check_in).days
        return nights * self.room.price_per_night