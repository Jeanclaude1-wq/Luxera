from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
from django.db.models import Q

from .models import Hotel, HotelImage, Room, RoomImage, Booking

from datetime import timedelta, date

  
def home(request):
    return render(request, "./hotels/home.html")
    

# ----------------------------------------------------
# HOME – LIST ALL HOTELS (now supports property_type)
# ----------------------------------------------------
def hotel_list(request):
    hotels = Hotel.objects.all().distinct()

    if request.method == "POST":
        search = request.POST.get("search-input", "").strip()
        property_types = request.POST.getlist("property_type")

        minprice = request.POST.get("min-price")
        maxprice = request.POST.get("max-price")

        # ---------------------------
        # Search by hotel name or location
        # ---------------------------
        if search:
            hotels = hotels.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search)
            )

        # ---------------------------
        # Filter by property type
        # ---------------------------
        if property_types:
            hotels = hotels.filter(type__in=property_types)

        # ---------------------------
        # Filter by room price range
        # ---------------------------
        if minprice:
            hotels = hotels.filter(rooms__price_per_night__gte=minprice)

        if maxprice:
            hotels = hotels.filter(rooms__price_per_night__lte=maxprice)

    return render(request, "hotels/hotel_list.html", {"hotels": hotels})


# ----------------------------------------------------
# HOTEL DETAIL – SHOW ROOMS + HOTEL IMAGES
# ----------------------------------------------------
@login_required
def hotel_detail(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = hotel.rooms.all()
    images = hotel.images.all()

    return render(request, 'hotels/hotel_detail.html', {
        'hotel': hotel,
        'rooms': rooms,
        'images': images,
    })


# ----------------------------------------------------
# ROOM DETAIL – SHOW MULTIPLE ROOM IMAGES
# ----------------------------------------------------
@login_required
def room_detail(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    images = room.images.all()
    addtional_images = RoomImage.objects.filter(room=room)

    # Get all accepted bookings for this room that overlap today or future
    bookings = room.bookings.filter(status="accepted", check_out__gte=date.today())

    # Generate list of unavailable dates
    unavailable = []

    for booking in bookings:
        current = booking.check_in
        while current < booking.check_out:  # checkout day becomes available again
            if current >= date.today():
                unavailable.append(current.strftime("%Y-%m-%d"))
            current += timedelta(days=1)

    return render(request, 'hotels/room_detail.html', {
        'room': room,
        'images': images,
        'addtional_images': addtional_images,
        "unavailable_dates": unavailable
    })


# ----------------------------------------------------
# DASHBOARD – HOTEL OWNER MANAGING ROOMS + BOOKINGS
# ----------------------------------------------------
@login_required
def dashboard(request):
    hotel = Hotel.objects.filter(admin=request.user).first()

    if not hotel:
        messages.error(request, "You are not assigned to any hotel.")
        return redirect("hotel_list")

    # Update main hotel info
    if request.method == "POST":
        hotel.name = request.POST.get("name")
        hotel.location = request.POST.get("location")
        hotel.description = request.POST.get("description")

        if "image" in request.FILES:
            hotel.image = request.FILES["image"]

        hotel.save()
        messages.success(request, "Hotel updated successfully!")
        return redirect("dashboard")

    rooms = hotel.rooms.all()
    bookings = Booking.objects.filter(room__hotel=hotel).select_related("user", "room")

    return render(request, "hotels/dashboard.html", {
        "hotel": hotel,
        "rooms": rooms,
        "bookings": bookings,
    })


# ----------------------------------------------------
# ADD ROOM
# ----------------------------------------------------
@login_required
def add_room(request):
    hotel = Hotel.objects.filter(admin=request.user).first()

    if not hotel:
        messages.error(request, "You do not manage any hotel.")
        return redirect("hotel_list")

    if request.method == "POST":
        Room.objects.create(
            hotel=hotel,
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            price_per_night=request.POST.get("price_per_night"),
            image=request.FILES.get("image")
        )

        messages.success(request, "Room added successfully!")
        return redirect("dashboard")

    return render(request, "hotels/add_room.html")


# ----------------------------------------------------
# ADD MULTIPLE ROOM IMAGES
# ----------------------------------------------------
@login_required
def add_room_images(request, room_id):
    room = get_object_or_404(Room, id=room_id, hotel__admin=request.user)

    if request.method == "POST":
        images = request.FILES.getlist("images")
        for img in images:
            RoomImage.objects.create(room=room, image=img)

        messages.success(request, "Room photos uploaded!")
        return redirect("room_detail", room_id=room.id)

    return render(request, "hotels/add_room_images.html", {"room": room})


# ----------------------------------------------------
# ADD MULTIPLE HOTEL IMAGES
# ----------------------------------------------------
@login_required
def add_hotel_images(request):
    hotel = Hotel.objects.filter(admin=request.user).first()

    if not hotel:
        messages.error(request, "You do not manage a hotel.")
        return redirect("hotel_list")

    if request.method == "POST":
        images = request.FILES.getlist("images")
        for img in images:
            HotelImage.objects.create(hotel=hotel, image=img)

        messages.success(request, "Hotel photos uploaded!")
        return redirect("dashboard")

    return render(request, "hotels/add_hotel_images.html", {"hotel": hotel})


# ----------------------------------------------------
# LOGIN
# ----------------------------------------------------
def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            if Hotel.objects.filter(admin=user).exists():
                return redirect("dashboard")
            return redirect("hotel_list")

        messages.error(request, "Invalid username or password.")

    return render(request, "hotels/login.html")


# ----------------------------------------------------
# LOGOUT
# ----------------------------------------------------
def logout_view(request):
    logout(request)
    return redirect("login")


# ----------------------------------------------------
# SIGNUP
# ----------------------------------------------------
def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("signup")

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("hotel_list")

    return render(request, "hotels/signup.html")


# ----------------------------------------------------
# BOOK ROOM — SUPPORT MULTIPLE BOOKINGS per room
# ----------------------------------------------------
@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    if request.method == "POST":
        check_in = request.POST.get("check_in")
        check_out = request.POST.get("check_out")

        if not check_in or not check_out:
            messages.error(request, "Please choose both dates.")
            return redirect("book_room", room_id=room.id)

        ci = datetime.strptime(check_in, "%Y-%m-%d").date()
        co = datetime.strptime(check_out, "%Y-%m-%d").date()

        if ci >= co:
            messages.error(request, "Check-out must be after check-in.")
            return redirect("book_room", room_id=room.id)

        # Check overlapping accepted bookings
        overlap = Booking.objects.filter(
            room=room,
            status="accepted",
            check_out__gt=ci,
            check_in__lt=co,
        ).exists()

        if overlap:
            messages.error(request, "This room is already booked for these dates.")
            return redirect("room_detail", room_id=room.id)

        Booking.objects.create(
            user=request.user,
            room=room,
            check_in=ci,
            check_out=co,
            status="pending",
            payment_status="pending_payment"
        )

        messages.success(request, "Booking request sent!")
        return redirect("my_bookings")

    return render(request, "hotels/book_room.html", {"room": room})


# ----------------------------------------------------
# USER BOOKINGS
# ----------------------------------------------------
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "hotels/my_bookings.html", {"bookings": bookings})


# ----------------------------------------------------
# ADMIN ACCEPT / REJECT BOOKING
# ----------------------------------------------------
@login_required
def update_booking_status(request, booking_id, action):
    hotel = Hotel.objects.filter(admin=request.user).first()

    if not hotel:
        messages.error(request, "You are not assigned to a hotel.")
        return redirect("hotel_list")

    booking = get_object_or_404(Booking, id=booking_id, room__hotel=hotel)

    if action == "accept":
        booking.status = "accepted"
        booking.payment_status = "pending_payment"
        messages.success(request, "Booking accepted. User must now upload payment.")

    elif action == "reject":
        booking.status = "rejected"
        booking.payment_status = "rejected"
        messages.success(request, "Booking rejected.")

    else:
        messages.error(request, "Invalid action.")

    booking.save()
    return redirect("dashboard")


# ----------------------------------------------------
# USER UPLOAD PAYMENT PROOF
# ----------------------------------------------------
@login_required
def upload_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == "POST":
        if "payment_proof" in request.FILES:
            booking.payment_proof = request.FILES["payment_proof"]
            booking.payment_status = "paid"
            booking.save()
            messages.success(request, "Payment uploaded successfully!")
            return redirect("my_bookings")

        messages.error(request, "Please upload an image.")

    return render(request, "hotels/upload_payment.html", {
        "booking": booking
    })
