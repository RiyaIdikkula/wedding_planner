from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
import uuid
from .models import Dessert, DessertImage, Package
from django.core.files.storage import default_storage
from django.conf import settings
from .models import User, Package, Photographer, PhotographerImage, Stylist, StylistImage, Religion, PasswordReset
from .models import MainCourse, MainCourseImage
from .models import Starter, StarterImage,Event,EventImage
from .models import Dress, DressImage, Package
from django.http import JsonResponse,HttpResponseBadRequest
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from .models import BookedItem
import json

# Home page
def index(request):
    return render(request, 'index.html')

# User registration
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        # Validate input
        if not email or not password or not username:
            messages.error(request, 'Please fill out all required fields.', extra_tags='red-error')
        elif User.objects.filter(email=email).exists():
            messages.error(request, f'The email {email} is already registered.', extra_tags='red-error')
        elif User.objects.filter(phone=phone).exists():
            messages.error(request, 'Phone number already exists', extra_tags='red-error')
        else:
            # Create new user
            User.objects.create(
                username=username,
                email=email,
                phone=phone,
                password=make_password(password)  # Hash the password
            )
            messages.success(request, 'Registration successful.')
            return redirect('login')  # Redirect to the login page

    return render(request, 'register.html')

# Login view
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('admin_dashboard' if user.is_superuser else 'index')
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'login.html')

# Profile view
@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        if username:
            user.username = username
        if email:
            user.email = email
        if phone:
            user.phone = phone
        if password:
            user.set_password(password)  # Use set_password instead of make_password

        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile_view')
    
    context = {
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
    }
    return render(request, 'profile.html', context)

# Admin Dashboard view
@login_required
def admin_dashboard_view(request):
    context = {
        'name': request.user.username,
        'email': request.user.email,
        'total_users': User.objects.count(),
        'total_packages': Package.objects.count(),
        'total_photographers': Photographer.objects.count(),
        'total_stylists': Stylist.objects.count(),
        'total_events': Event.objects.count(),
        'total_starter': Starter.objects.count(),
        'total_deserts': Dessert.objects.count(),
        'total_main':MainCourse.objects.count(),
        # 'total_religion': Religion.objects.count(),
        'customers': User.objects.filter(is_superuser=False),
        'packages': Package.objects.all(),
    }
    return render(request, 'admin/admin_dashboard.html', context)

# Logout view
def logout_view(request):
    logout(request)
    return redirect('index')

# View customers
@login_required
def view_customers(request):
    customers = User.objects.filter(is_superuser=False)
    return render(request, 'admin/view_customer.html', {'customers': customers})

# View packages
@login_required
def view_packages(request):
    packages = Package.objects.all()
    return render(request, 'admin/view_packages.html', {'packages': packages})

# Add package
@login_required
def add_package(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')

        # Check if a package with the same name already exists
        if Package.objects.filter(name=name).exists():
            messages.error(request, 'A package with this name already exists.', extra_tags='red-error')
            return redirect('add_package')  # Redirect to the add package page
        else:
            # Create the new package if it doesn't already exist
            Package.objects.create(name=name, price=price)
            
            return redirect('view_packages')

    return render(request, 'admin/add_packages.html')

# Edit package
@login_required
def edit_package(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    if request.method == 'POST':
        package.price = request.POST.get('price')
        package.save()
        messages.success(request, 'Package updated successfully.')
        return redirect('view_packages')
    return render(request, 'admin/edit_packages.html', {'package': package})

# Delete package
@login_required
def delete_package(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    if request.method == 'POST':
        package.delete()
        messages.success(request, 'Package deleted successfully.')
        return redirect('view_packages')
    return render(request, 'admin/delete_packages.html', {'package': package})

# Add photographer
@login_required
def add_photographer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        package_id = request.POST.get('package_id')
        contact_number = request.POST.get('contact_number')
        description = request.POST.get('description')
        images = request.FILES.getlist('images')
        package = Package.objects.get(pk=package_id)
        
        # Create the Photographer instance
        photographer = Photographer.objects.create(
            name=name, 
            package=package,
            contact_number=contact_number, 
            description=description
        )
        # Add the images to the photographer
        for image in images:
                PhotographerImage.objects.create(photographer=photographer, image=image)

        return redirect('photographer_list')  # redirect to the desired page after creation
    packages = Package.objects.all()  # Fetch all packages
    return render(request, 'admin/add_photographer.html', {'packages': packages})

# Photographer list
@login_required
def photographer_list(request):
    photographers = Photographer.objects.all()
    return render(request, 'admin/photographer_list.html', {'photographers': photographers})

# Edit photographer
@login_required
def edit_photographer(request, photographer_id):
    photographer = get_object_or_404(Photographer, pk=photographer_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        package_id = request.POST.get('package_id')
        contact_number = request.POST.get('contact_number')
        description = request.POST.get('description')
        images = request.FILES.getlist('images')
        package = Package.objects.get(pk=package_id)
        photographer.save()
        for image in images:
            PhotographerImage.objects.create(photographer=photographer, image=image)
        delete_images = request.POST.getlist('delete_images')
        PhotographerImage.objects.filter(id__in=delete_images).delete()
        
        return redirect('photographer_list')
 
    packages = Package.objects.all()  # Fetch all packages

    return render(request, 'admin/edit_photographer.html', {'photographer': photographer, 'packages': packages})

# Delete photographer
@login_required
def delete_photographer(request, photographer_id):
    photographer = get_object_or_404(Photographer, pk=photographer_id)
    if request.method == 'POST':
        photographer.delete()
        messages.success(request, 'Photographer deleted successfully.')
        return redirect('photographer_list')
    return render(request, 'admin/delete_photographer.html', {'photographer': photographer})

# Add stylist
@login_required
def add_stylist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        package_id = request.POST.get('package')
        description = request.POST.get('description')
        images = request.FILES.getlist('images')

        # Fetch the package object
        try:
            package = Package.objects.get(pk=package_id)
        except ObjectDoesNotExist:
            messages.error(request, 'Selected package does not exist.', extra_tags='red-error')
            return redirect('add_stylist')

        # Check if stylist with the same name already exists
        if Stylist.objects.filter(name=name).exists():
            messages.error(request, 'A stylist with this name already exists.', extra_tags='red-error')
            return redirect('add_stylist')

        try:
            # Create a new stylist and associate it with the package
            stylist = Stylist.objects.create(
                name=name,
                description=description,
                package=package  # Use the package object directly
            )

            # Save each image associated with the stylist
            for image in images:
                StylistImage.objects.create(stylist=stylist, image=image)
            
            messages.success(request, 'Stylist added successfully.')
            return redirect('stylist_list')

        except IntegrityError:
            messages.error(request, 'There was an error saving the stylist. Please try again.', extra_tags='red-error')
            return redirect('add_stylist')

    packages = Package.objects.all()  # Fetch all packages for the dropdown
    return render(request, 'admin/add_stylist.html', {'packages': packages})

# Stylist list
@login_required
def stylist_list(request):
    stylists = Stylist.objects.all()
    return render(request, 'admin/stylist_list.html', {'stylists': stylists})

# Edit stylist
@login_required
def edit_stylist(request, stylist_id):
    stylist = get_object_or_404(Stylist, pk=stylist_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        package_id = request.POST.get('package_id')
        images = request.FILES.getlist('images')
        delete_images = request.POST.getlist('delete_images')

        if package_id:  # Ensure package_id is provided
            package = get_object_or_404(Package, pk=package_id)
            stylist.package = package

        stylist.name = name
        stylist.description = description
        stylist.save()

        # Handle image uploads
        for image in images:
            StylistImage.objects.create(stylist=stylist, image=image)

        # Handle image deletions
        StylistImage.objects.filter(id__in=delete_images).delete()

        return redirect('stylist_list')

    packages = Package.objects.all()  # Fetch all packages
    return render(request, 'admin/edit_stylist.html', {'stylist': stylist, 'packages': packages})

# Delete stylist
@login_required
def delete_stylist(request, stylist_id):
    stylist = get_object_or_404(Stylist, pk=stylist_id)
    if request.method == 'POST':
        stylist.delete()
        messages.success(request, 'Stylist deleted successfully.')
        return redirect('stylist_list')
    return render(request, 'admin/delete_stylist.html', {'stylist': stylist})

# View religions
@login_required

def view_religions(request):
    religions = Religion.objects.all()
    return render(request, 'admin/view_religions.html', {'religions': religions})

# Add religion
@login_required
def add_religion(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        Religion.objects.create(name=name)
        return redirect('view_religions')
    return render(request, 'admin/add_religion.html')

# Edit religion
@login_required
def edit_religion(request, id):
    religions = get_object_or_404(Religion, pk=id)
    if request.method == 'POST':
        religions.name = request.POST.get('name')
        religions.save()
        return redirect('view_religions')
    return render(request, 'admin/edit_religion.html', {'religions': religions})

# Delete religion
@login_required
def delete_religion(request, id):
    religions = get_object_or_404(Religion, pk=id)
    if request.method == 'POST':
        religions.delete()
        return redirect('view_religions')
    return render(request, 'admin/delete_religion.html', {'religions': religions})

# Forgot password
# Password reset form
def password_reset_form(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            token = uuid.uuid4()
            PasswordReset.objects.create(user=user, token=token)
            reset_link = request.build_absolute_uri(f'/reset/{token}/')
            email_subject = 'Password Reset Request'
            email_body = f'Click the link to reset your password: {reset_link}'
            email_message = EmailMultiAlternatives(email_subject, email_body, settings.DEFAULT_FROM_EMAIL, [email])
            email_message.send()
            messages.success(request, 'Password reset email sent.')
        else:
            messages.error(request, 'Email not found.')
    return render(request, 'password_reset_form.html')

# Password reset confirm
def password_reset_confirm(request, token):
    password_reset = PasswordReset.objects.filter(token=token).first()
    if not password_reset:
        messages.error(request, 'Invalid or expired token.')
        return redirect('password_reset_form')

    if request.method == 'POST':
        password = request.POST.get('password')
        user = password_reset.user
        user.password = make_password(password)
        user.save()
        password_reset.delete()
        messages.success(request, 'Password reset successful.')
        return redirect('login')

    return render(request, 'password_reset_confirm.html')

# Handle 404 errors
def handler404(request, exception):
    return render(request, '404.html', status=404)

def customer_photographer_list(request):
    photographers = Photographer.objects.prefetch_related('images').all()
    return render(request, 'customer_photographer_list.html', {'photographers': photographers})

def add_event(request):
    if request.method == 'POST':
        
        package_id = request.POST.get('package_id')
        
        event_type_name = request.POST.get('event_type_name')
        event_description = request.POST.get('event_description')
        
        package = Package.objects.get(pk=package_id)
    
        # if Event.objects.filter(event_type_name=event_type_name).exists():
        #     messages.error(request, 'This Event with this name already exists.', extra_tags='red-error')
        #     return redirect('add_event')
        # else:
        event = Event.objects.create(
            
            package=package,
            
            event_type_name=event_type_name,
            event_description=event_description
            )

        images = request.FILES.getlist('images')
        for image in images:
                EventImage.objects.create(event=event, image=image)

        messages.success(request, 'Event added successfully.')
        return redirect('event_list')

    
    packages = Package.objects.all()
    
    return render(request, 'admin/add_event.html', { 'packages': packages})

def event_list(request):
    events = Event.objects.all()
    return render(request, 'admin/event_list.html', {'events': events})

def edit_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if request.method == 'POST':
        event.occasion_id = request.POST.get('occasion_id')
        event.package_id = request.POST.get('package_id')
        event.id = request.POST.get('id')
        
        event.event_description = request.POST.get('event_description')
        event.save()

        images = request.FILES.getlist('images')
        
        for image in images:
                EventImage.objects.create(event=event, image=image)
        delete_images = request.POST.getlist('delete_images')
        EventImage.objects.filter(id__in=delete_images).delete()
        
        return redirect('event_list')

    
    packages = Package.objects.all()
   
    return render(request, 'admin/edit_event.html', {'event': event, 'packages': packages})

def delete_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    event.delete()
    messages.success(request, 'Event deleted successfully.')
    return redirect('event_list')

# views.py
def add_main_course(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        main_course_type = request.POST.get('main_course_type')
        images = request.FILES.getlist('images')
        package = Package.objects.get(pk=package_id)

        if MainCourse.objects.filter(name=name).exists():
            messages.error(request, 'This Main Course with this name already exists.', extra_tags='red-error')
            return redirect('add_main_course')
        else:
            main_course = MainCourse.objects.create(
            package=package,
            name=name,
            description=description,
            type=main_course_type
            )
        
            for image in images:
                MainCourseImage.objects.create(main_course=main_course, image=image)

            return redirect('view_main_courses')

    packages = Package.objects.all()
    return render(request, 'admin/add_main_course.html', {'packages': packages})

def view_main_courses(request):
    main_courses = MainCourse.objects.all()
    return render(request, 'admin/view_main_courses.html', {'main_courses': main_courses})

def edit_main_course(request, pk):
    main_course = get_object_or_404(MainCourse, pk=pk)
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
       
        description = request.POST.get('description')
        type = request.POST.get('type')
        new_images = request.FILES.getlist('images')
        delete_images = request.POST.getlist('delete_images')

        package = get_object_or_404(Package, pk=package_id)
        main_course.package = package
        
        main_course.description = description
        main_course.type = type

        # Handle new images
        for image in new_images:
            MainCourseImage.objects.create(main_course=main_course, image=image)

        # Handle deletions
        for image_id in delete_images:
            image = get_object_or_404(MainCourseImage, pk=image_id)
            image.delete()

        main_course.save()
        
        return redirect('view_main_courses')
    else:
        packages = Package.objects.all()
        return render(request, 'admin/edit_main_course.html', {'main_course': main_course, 'packages': packages})

def delete_main_course(request, pk):
    main_course = get_object_or_404(MainCourse, pk=pk)
    if request.method == 'POST':
        # Delete the main course
        main_course.delete()
        return redirect('view_main_courses')
    return render(request, 'admin/delete_main_course.html', {'main_course': main_course})

def add_dessert(request):
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        images = request.FILES.getlist('images')

        package = get_object_or_404(Package, pk=package_id)
        if Dessert.objects.filter(name=name).exists():
            messages.error(request, 'This Dessert with this name already exists.', extra_tags='red-error')
            return redirect('add_dessert')
        else:
            dessert = Dessert.objects.create(
            package=package,
            name=name,
            description=description
            )

            for image in images:
                dessert_image = DessertImage.objects.create(image=image)
                dessert.images.add(dessert_image)

            dessert.save()
            return redirect('view_desserts')

    packages = Package.objects.all()
    return render(request, 'admin/add_desert.html', {'packages': packages})

def view_desserts(request):
    desserts = Dessert.objects.all()
    return render(request, 'admin/view_deserts.html', {'desserts': desserts})

def edit_dessert(request, pk):
    dessert = get_object_or_404(Dessert, pk=pk)
    if request.method == 'POST':
        package_id = request.POST.get('package_id')
        name = request.POST.get('name')
        description = request.POST.get('description')
        images = request.FILES.getlist('images')
        delete_images = request.POST.getlist('delete_images')

        package = get_object_or_404(Package, pk=package_id)
        dessert.package = package
        dessert.name = name
        dessert.description = description

        # Update images
        if images:
            for image in images:
                dessert_image = DessertImage.objects.create(image=image)
                dessert.images.add(dessert_image)

        # Delete selected images
        if delete_images:
            for image_id in delete_images:
                dessert_image = get_object_or_404(DessertImage, id=image_id)
                if default_storage.exists(dessert_image.image.name):
                    default_storage.delete(dessert_image.image.name)
                dessert_image.delete()

        dessert.save()
        return redirect('view_desserts')

    packages = Package.objects.all()
    return render(request, 'admin/edit_desert.html', {'dessert': dessert, 'packages': packages})

def delete_dessert(request, pk):
    dessert = get_object_or_404(Dessert, pk=pk)
    if request.method == 'POST':
        for dessert_image in dessert.images.all():
            
            if default_storage.exists(dessert_image.image.name):
                default_storage.delete(dessert_image.image.name)
            dessert_image.delete()
        dessert.delete()
        return redirect('view_desserts')
    return render(request, 'admin/delete_desert.html', {'dessert': dessert})

@login_required
def add_starter(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        starter_type = request.POST.get('starter_type')
        package_id = request.POST.get('package_id')  # Get package_id from POST data
        
        package_id = get_object_or_404(Package, pk=package_id)
        
        images = request.FILES.getlist('images')
        
        # if Starter.objects.filter(name=name).exists():
        #     messages.error(request, 'This Starter with this name already exists.', extra_tags='red-error')
            
        #     return redirect('add_starter')
        # else:
            
            
            # Create Starter object
        starter = Starter.objects.create(
                name=name,
                package_id=package_id,  # Correct field name here
                description=description,
                starter_type=starter_type
            )
            
        print(f"Starter created: {starter}")

            # Handle image uploads
        for image in images:
                StarterImage.objects.create(starter=starter, image=image)
                print(f"Image uploaded for starter {starter.name}")

            # Success message
        return redirect('starter_list')
    
    # Handle GET request
    packages = Package.objects.all()
    
    return render(request, 'admin/add_starter.html', {'packages': packages})
def view_starters(request):
    starters = Starter.objects.all()  # Change variable name to starters
    return render(request, 'admin/view_starters.html', {'starters': starters})

@login_required
def edit_starter(request, starter_id):
    starter = get_object_or_404(Starter, starter_id=starter_id)
    packages = Package.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        starter_type = request.POST.get('starter_type')
        package_id = request.POST.get('package_id')

        starter.name = name
        starter.description = description
        starter.starter_type = starter_type
        starter.package_id = Package.objects.get(package_id=package_id)
        starter.save()

        # Handle image deletions
        delete_images = request.POST.getlist('delete_images')
        StarterImage.objects.filter(id__in=delete_images).delete()

        # Handle new image uploads
        new_images = request.FILES.getlist('images')
        for image in new_images:
            StarterImage.objects.create(starter=starter, image=image)

        messages.success(request, 'Starter updated successfully!')
        return redirect('starter_list')

    context = {
        'starter': starter,
        'packages': packages,
    }
    return render(request, 'admin/edit_starter.html', context) 


@login_required
def delete_starter(request, starter_id):
    starter = get_object_or_404(Starter, pk=starter_id)
    
    if request.method == 'POST':
        starter.delete()
        messages.success(request, 'Starter deleted successfully.')
        return redirect('starter_list')
    
    return render(request, 'admin/delete_starter.html', {'starter': starter})

def package_view(request):
    packages = Package.objects.all()
    context = {
        'packages': packages
    }
    return render(request, 'package_view.html', context)

def package_details(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    photographers = Photographer.objects.filter(package_id=package_id)
    context = {
        'package': package,
        'photographers': photographers,
    }
    return render(request, 'package_detail.html', context)

def stylist_package(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    stylists = Stylist.objects.filter(package=package).prefetch_related('images')
    context = {
        'package': package,
        'stylists': stylists,
    }
    return render(request, 'stylist_package.html', context)

def stylist_customer(request, stylist_id):
    stylist = get_object_or_404(Stylist, stylist_id=stylist_id)
    images = stylist.images.all()
    context = {
        'stylist': stylist,
        'images': images,
    }
    return render(request, 'event_customer.html', context)

def cater_list(request):
    packages = Package.objects.exclude(package_id=1)
    
    context = {
        'packages': packages
    }
    return render(request, 'caters_package.html', context)

def caters_customer(request, package_id):
    package = get_object_or_404(Package, package_id=package_id)
    starters = Starter.objects.filter(package_id=package.package_id)
    main_courses = MainCourse.objects.filter(package_id=package.package_id)
    desserts = Dessert.objects.filter(package_id=package.package_id)

    # Debug print statements
    print(f"Package ID: {package.package_id}")
    for starter in starters:
        print(f"Starter ID: {starter.starter_id}, Name: {starter.name}")

    context = {
        'package': package,
        'starters': starters,
        'main_courses': main_courses,
        'desserts': desserts,
    }
    return render(request, 'caters_customers.html', context)

def starter_details(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    starters = Starter.objects.filter(package_id=package)
    context = {
        'package': package,
        'starters': starters,
    }
    return render(request, 'starter_detail.html', context)

def starter_detail(request, item_id):
    starter = get_object_or_404(Starter, starter_id=item_id)
    images = starter.images.all()
    context = {
        'starter': starter,
        'images': images,
    }
    return render(request, 'starter_item_detail.html', context)

def main_course_details(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    main_courses = MainCourse.objects.filter(package=package).prefetch_related('images')
    context = {
        'package': package,
        'main_courses': main_courses,
    }
    return render(request, 'main_course_detail.html', context)

def main_course_detail(request, item_id):
    main_course = get_object_or_404(MainCourse, main_course_id=item_id)
    images = main_course.images.all()
    context = {
        'main_course': main_course,
        'images': images,
    }
    return render(request, 'main_course_item_detail.html', context)

def dessert_details(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    desserts = Dessert.objects.filter(package=package).prefetch_related('images')
    context = {
        'package': package,
        'desserts': desserts,
    }
    return render(request, 'dessert_detail.html', context)

def dessert_detail(request, item_id):
    dessert = get_object_or_404(Dessert, dessert_id=item_id)
    images = dessert.images.all()
    context = {
        'dessert': dessert,
        'images': images,
    }
    return render(request, 'dessert_details.html', context)


def cart_view(request):
    cart = request.session.get('cart', {})
    stylists = Stylist.objects.filter(stylist_id__in=cart.get('stylist', []))
    photographers = Photographer.objects.filter(photographer_id__in=cart.get('photographer', []))
    packages = Package.objects.filter(package_id__in=cart.get('package', []))
    
    context = {
        'stylists': stylists,
        'photographers': photographers,
        'packages': packages,
    }
    
    return render(request, 'cart.html', context)

def photographer_detail(request, photographer_id):
    photographer = get_object_or_404(Photographer, photographer_id=photographer_id)
    context = {
        'photographer': photographer,
    }
    return render(request, 'photographer_individual_detail.html', context)

def event_package(request, package_id):
    package = get_object_or_404(Package, package_id=package_id)
    events = Event.objects.filter(package=package)
    context = {
        'package': package,
        'events': events,
    }
    return render(request, 'event_package.html', context)

def event_customer(request, item_id):
    event = get_object_or_404(Event, event_id=item_id)
    images = event.images.all()
    context = {
        'event': event,
        'images': images,
    }
    return render(request, 'event_customer.html', context)

def booking_view(request):
    booking_item_ids = request.session.get('booking_items', [])
    booking_items = BookedItem.objects.filter(id__in=booking_item_ids)
    return render(request, 'booking.html', {'booking_items': booking_items})

@require_POST
@csrf_protect
def add_to_booking(request):
    data = json.loads(request.body)
    
    # Create a new BookedItem
    booked_item = BookedItem.objects.create(
        user=request.user,
        name=data['name'],
        item_type=data['type'],
        package_name=data['package'],
        image_url=data.get('image_url', '')
    )
    
    # Add the booked item to the session
    if 'booking_items' not in request.session:
        request.session['booking_items'] = []
    request.session['booking_items'].append(booked_item.id)
    request.session.modified = True
    
    return JsonResponse({'status': 'success', 'item_id': booked_item.id})

def checkout_view(request):
    # Implement your checkout logic here
    return render(request, 'checkout.html')
from django.shortcuts import render, redirect
from .models import Package, WeddingInfo  # Assuming you have these models

def checkout_view(request):
    packages = Package.objects.all()  # Fetching all the packages to display in the form
    
    if request.method == "POST":
        customer_name = request.POST.get('customerName')
        bride_name = request.POST.get('brideName')
        groom_name = request.POST.get('groomName')
        guest_count = request.POST.get('guestCount')
        wedding_dates = request.POST.get('weddingDates')
        address = request.POST.get('address')
        package_id = request.POST.get('package_id')

        # Check for date conflicts
        if WeddingInfo.has_date_conflict(wedding_dates):
            messages.error(request, "One or more of the selected dates are already booked. Please choose different dates.")
            return render(request, 'wedding_info_form.html', {'packages': packages})

        # Assuming you have a model WeddingInfo to save this information
        wedding_info = WeddingInfo(
            customer_name=customer_name,
            bride_name=bride_name,
            groom_name=groom_name,
            guest_count=guest_count,
            wedding_dates=wedding_dates,
            address=address,
            package_id=package_id,
        )
        wedding_info.save()

        return redirect('success')  # Redirect to a success page after submission

    return render(request, 'checkout.html', {'packages': packages})

def success_view(request):
    return render(request, 'success.html')


def photographer_details(request, package_id):
    package = get_object_or_404(Package, pk=package_id)
    photographers = Photographer.objects.filter(package=package).prefetch_related('images')
    
    context = {
        'package': package,
        'photographers': photographers,
    }
    return render(request, 'photographer_detail.html', context)

def photographer_detail(request, photographer_id):
    photographer = get_object_or_404(Photographer, photographer_id=photographer_id)
    images = photographer.images.all()
    context = {
        'photographer': photographer,
        'images': images,
    }
    return render(request, 'photographer_details.html', context)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import  Package, WeddingInfo

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Package, WeddingInfo
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
def checkout_view(request):
    user = request.user
    package_id = request.GET.get('package_id')
    selected_package = None

    if package_id:
        selected_package = get_object_or_404(Package, pk=package_id)

    if request.method == 'POST':
        customer_name = request.POST.get('customerName')
        bride_name = request.POST.get('brideName')
        groom_name = request.POST.get('groomName')
        guest_count = request.POST.get('guestCount')
        wedding_dates = request.POST.get('weddingDates')
        address = request.POST.get('address')
        package_id = request.POST.get('package_id')
        

        try:
            
            package = Package.objects.get(pk=package_id)
            wedding_info = WeddingInfo.objects.create(
                user=request.user,
                customer_name=customer_name,
                bride_name=bride_name,
                groom_name=groom_name,
                guest_count=guest_count,
                wedding_dates=wedding_dates,
                venue_address=address,
                package=package
            )
            messages.success(request, "Wedding information saved successfully!")
            return redirect('checkout_success')
        except Exception as e:
            messages.error(request, f"Error saving wedding information: {str(e)}")

    packages = Package.objects.all()
    context = {
         'user': user,
        'packages': packages,
        'selected_package': selected_package,
    }
    return render(request, 'checkout.html', context)


def checkout_success(request):
    return render(request, 'checkout_success.html')

from django.db import IntegrityError

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Dress, DressImage, Package

@login_required
def upload_dress(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        package_id = request.POST.get('package')
        
        # Validate fields
        if not all([name, description, package_id]):
            print("One or more fields are missing.")
            return redirect('add_dress')
        
        # Check if package_id exists
        try:
            package = Package.objects.get(pk=package_id)
        except Package.DoesNotExist:
            print("Package not found.")
            return redirect('add_dress')

        # Create Dress object
        dress = Dress.objects.create(
            name=name,
            description=description,
            package=package
        )
        print(f"Dress created: {dress}")

        # Handle image upload
        images = request.FILES.getlist('images')
        if images:  # Check if images were uploaded
            for image in images:
                DressImage.objects.create(dress=dress, image=image)
                print(f"Image uploaded: {image}")

        return redirect('view_dresses')

    packages = Package.objects.all()
    return render(request, 'admin/upload_dress.html', {'packages': packages})

def dress_list(request):
    dresses = Dress.objects.prefetch_related('images').all()  # Prefetch related images to reduce queries
    return render(request, 'admin/dress_list.html', {'dresses': dresses})


from django.shortcuts import render
from .models import Dress

def dress_view(request):
    dresses = Dress.objects.prefetch_related('images').all()  # Fetch all dresses with their related images
    return render(request, 'dress_view.html', {'dresses': dresses})

# def dress_view(request):
#     images = DressImage.objects.filter(dress=dress)  # Adjust as needed
#     return render(request, 'dress_view.html', {'images': images})



def try_on(request, dress_id):
    dress = get_object_or_404(Dress, id=dress_id)
    dress_image = dress.images.first().image.url if dress.images.exists() else None
    print(f'Dress Image URL: {dress_image}')  # Check the output in your server console
    return render(request, 'try_on.html', {'dressImage': dress_image})


def face_detection_view(request):
    return render(request, 'try_on_result.html')



