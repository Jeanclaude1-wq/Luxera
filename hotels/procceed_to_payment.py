from django.shortcuts import redirect, render
from .models import Booking


def procceed(request):
    if request.method == "POST":
        id = request.POST["reservation_id"]
        get_booking = Booking.objects.get(pk=id)
        return render(request, "./hotels/payment.html", {"booking":get_booking})
    else:
        return redirect("/")