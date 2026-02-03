from django.utils import timezone
from datetime import datetime
from django.shortcuts import render,redirect, HttpResponse, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import RegistrationForm, LoginForm
from .models import MenuItem
from .models import OrderItem
from .models import Order
from .models import Cards
from .models import Table
from .models import Reservation
from django.contrib import messages

#To generate QR Code
import qrcode
from io import BytesIO
from django.core.mail import EmailMessage

# Create your views here.
def index(request):
    menu_item_br = MenuItem.objects.filter(category="Breakfast")
    menu_item_lch = MenuItem.objects.filter(category="Lunch")
    sweets = MenuItem.objects.filter(category="Sweets")

    cf=1
    cl=1
    br_item_listf3=[]
    br_item_listl3=[]
    for item in menu_item_br:
        if cf<=3:
            br_item_listf3.append(item)
            cf+=1
        elif cl<=3:
            br_item_listl3.append(item)
            cl=cl+1

    cf=1
    cl=1

    lch_item_listf3=[]
    lch_item_listl3=[]
    for item in menu_item_lch:
        if cf<=3:
            lch_item_listf3.append(item)
            cf+=1
        elif cl<=3:
            lch_item_listl3.append(item)
            cl=cl+1

    menu_items = {"breakfast1": br_item_listf3, "breakfast2": br_item_listl3, "lunch1":lch_item_listf3, "lunch2":lch_item_listl3, "sweets":sweets}
    return render(request, "index.html", menu_items)


def user_reg(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, "register.html", {"form":form})

def user_login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("home")
    else:
        form = LoginForm()
    return render(request, 'login.html', {"form": form})

def user_logout(request):
    logout(request)
    return redirect("home")

def menu_page(request):
    menu_item_br = MenuItem.objects.filter(category="Breakfast")
    menu_item_lch = MenuItem.objects.filter(category="Lunch")
    sweets = MenuItem.objects.filter(category="Sweets")

    cf=1
    cl=1
    br_item_listf3=[]
    br_item_listl3=[]
    for item in menu_item_br:
        if cf<=8:
            br_item_listf3.append(item)
            cf+=1
        elif cl<=8:
            br_item_listl3.append(item)
            cl+=1

    cf=1
    cl=1

    lch_item_listf3=[]
    lch_item_listl3=[]
    for item in menu_item_lch:
        if cf<=8:
            lch_item_listf3.append(item)
            cf+=1
        elif cl<=8:
            lch_item_listl3.append(item)
            cl+=1

    menu_items = {"breakfast1": br_item_listf3, "breakfast2": br_item_listl3, "lunch1":lch_item_listf3, "lunch2":lch_item_listl3, "sweets":sweets}
    return render(request, "menu.html", menu_items)


@login_required(login_url="login")
def add_to_cart(request, menu_item_id):
    # Retrieve the menu item
    menu_item = get_object_or_404(MenuItem, id=menu_item_id)
    
    # Retrieve or create an order for the user
    if 'order_id' in request.session:
        order = get_object_or_404(Order, id=request.session['order_id'])
    else:
        order = Order(user=request.user, created_at=timezone.now(), total_amount=menu_item.price, is_completed=False)
        order.save()
        request.session['order_id'] = order.id
    
    # Create or update the order item
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        menu_item=menu_item,
        defaults={'quantity': 1, 'subtotal': menu_item.price}
    )
    
    if not created:
        # If the order item already exists, update the quantity and subtotal
        order_item.quantity += 1
        order_item.subtotal = order_item.quantity * menu_item.price
        order_item.save()
    
    # Update the total amount of the order
    order.total_amount = sum(item.subtotal for item in order.order_items.all())
    order.save()
    
    return redirect('home')

@login_required(login_url="login")
def cart_page(request):
     # Retrieve all orders for the current user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Pass the orders to the template
    return render(request, 'cart.html', {'orders': orders})

def pay_online(request, order_id):
    # Retrieve the order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    request.session['order_id'] = order.id

    # Check if the order is already completed
    if order.is_completed:
        messages.info(request, 'This order has already been completed.')
        del request.session['order_id']
        return redirect('home')  # Return to home

    if request.method == 'POST':
        payment_successful = True

        if payment_successful:
            # Mark the order as completed
            order.is_completed = True
            del request.session['order_id']
            order.save()

            messages.success(request, 'Payment was successful!')
            return redirect('cart')  # Return to cart
        else:
            messages.error(request, 'Payment failed. Please try again.')

    # Render payment page with order details
    return render(request, 'payment.html', {'order': order})


def pay_card(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    request.session['order_id'] = order.id

    if order.is_completed:
        messages.info(request, 'This order has already been completed.')
        del request.session['order_id']
        return redirect('home')  # Return to home

    if request.method == 'POST':
        card_no = request.POST['card_no']
        cvv = request.POST['cvv'] 
        mm = request.POST['MM']
        yy = request.POST['YY']
        pay_done = True
        c = Cards(card_no = card_no, cvv = cvv, mm = mm, yy = yy, pay_done = pay_done)
        c.save()
        if pay_done:
            # Mark the order as completed
            order.is_completed = True
            del request.session['order_id']
            order.save()

            messages.success(request, 'Payment was successful!')
            return redirect('cart')  # Replace with the actual order detail view
        else:
            messages.error(request, 'Payment failed. Please try again.')

    # Render payment page with order details
    return render(request, 'payment_card.html', {'order': order})

@login_required(login_url="login")
def order_page(request):
    
    # Get all the orders which are completed
    orders = Order.objects.filter(user=request.user).filter(is_completed=True).order_by("-created_at")

    #Render the order Page
    return render(request, 'order.html', {'orders':orders})

def repeat_order(request, order_id):
    # Fetch the existing order
    original_order = get_object_or_404(Order, id=order_id, user=request.user, is_completed=True)

    # Create a new order
    new_order = Order.objects.create(
        user=request.user,
        total_amount=original_order.total_amount,
        is_completed=False
    )

    # Copy the order items
    order_items = OrderItem.objects.filter(order=original_order)
    for item in order_items:
        OrderItem.objects.create(
            order=new_order,
            menu_item=item.menu_item,
            quantity=item.quantity,
            subtotal=item.subtotal
        )

    request.session['order_id'] = new_order.id

    # Redirect to cart
    return redirect('cart')

@login_required(login_url="login")
def book_table(request):
    guest_name = request.POST['name']
    guest_email = request.POST['email']
    guest_phone = request.POST['phone']
    guest_count = request.POST['number_guests']
    guest_time = request.POST['time']
    guest_message = request.POST['message']
    reservation_time = request.POST['date']

    input_format = "%d.%m.%Y"
    output_format = "%Y-%m-%d"
    
    # Parse the input date string
    date_obj = datetime.strptime(reservation_time, input_format)
    
    # Format the date object to the desired output format
    reservation_time=date_obj.strftime(output_format)
            
    # Check if any table is available
    tables = Table.objects.all()
    for table in tables:
        if table.available:
            table.user = request.user
            table.seats = guest_count
            table.available = False
            table.save()
            res = Reservation(table = table , user = request.user, guest_name = guest_name, guest_email = guest_email, guest_phone = guest_phone, guest_count = guest_count, guest_time = guest_time, guest_message = guest_message, reservation_time = reservation_time)
            
            subject = "Table Reservation at Digital Canteen."

            msg = "Your Table for "+str(guest_count)+" people has been successfully booked for date:"+str(reservation_time)+" for "+str(guest_time)+". \n Scan the QR Code below Or visit this link to see your Reservations \n\n http://127.0.0.1:8000/check_reservations"

            #Generating QR Code
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data("http://127.0.0.1:8000/check_reservations")
            qr.make(fit=True)
            
            img = qr.make_image(fill='black', back_color='white')
            img_byte_array = BytesIO()
            img.save(img_byte_array, format='PNG')
            img_byte_array.seek(0)

            qrcode_data = img_byte_array

            # Prepare email
            email = EmailMessage(subject=subject, body=msg, from_email=settings.EMAIL_HOST_USER, to=[guest_email,],)
    
            # Attach QR code
            email.attach('qrcode.png', qrcode_data.getvalue(), 'image/png')
            
            # Send email
            email.send()

            # send_mail(subject, msg, settings.EMAIL_HOST_USER, [guest_email,])
            
            res.save()
            messages.success(request, "Table Booked successfully!")
            return redirect('home')
        

    messages.error(request, "All Tables are Fully Booked at the moment. Please Try Again Later")
    return redirect('home')


#Checking all your Reservations
@login_required(login_url="login")
def check_reservations_page(request):
    res = Reservation.objects.filter(user = request.user)
    return render(request, "check_reservations.html", {"reservations":res})

@login_required(login_url="login")
def cancel_reservation(request, res_id):
    # Retrieve the reservation, or return a 404 error if it does not exist
    reservation = get_object_or_404(Reservation, pk=res_id)

    # Check if the logged-in user is the owner of the reservation
    if reservation.user != request.user:
        messages.error(request, "You do not have permission to cancel this reservation.")
        return redirect('home')  # Redirect to a home

    # Delete the reservation and free the table
    table = reservation.table

    table.user = User.objects.get(username = "canteen")
    table.seats = 0
    table.available = True
    table.save()

    reservation.delete()
    messages.success(request, "Reservation canceled successfully!")

    return redirect('home')  # Redirect to home






def sweets_example(request):
    sweets = MenuItem.objects.filter(category="Sweets")
    return render(request, "sweets_example.html", {"sweets":sweets})