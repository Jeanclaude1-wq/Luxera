from .models import Booking
from django.shortcuts import redirect



def cancel_reservation(request):
    if request.method == "POST":
        reservation_id = request.POST['reservation_id']
        reservation = Booking.objects.get(pk=reservation_id)
        reservation.status = "Canceled"
        reservation.save()

        return redirect("/my-bookings/")

    else:
        return redirect("1")
