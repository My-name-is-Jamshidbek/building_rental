from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from django.db.models import Sum
from django.core.paginator import Paginator
from django.utils import timezone
from .forms import ClientForm, ProductForm, TrashForm, UserUpdateForm, CustomUserCreationForm, ProductMoldForm
from .models import Trash, Product, ProductMold, ProductHistory, ProductMoldHistory, Client


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # or another desired landing page

    # Create the form with POST data if available, or None for GET
    form = AuthenticationForm(request=request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # Log in the user.
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully.")
            return redirect(request.GET.get('next') or 'home')
        else:
            messages.error(request, "Invalid username or password.")

    # Always return a response, whether GET or invalid POST.
    return render(request, 'login.html', {'form': form})



@login_required
@staff_member_required
def dashboard(request):
    # Overall metrics for Trash records
    total_trash = Trash.objects.count()
    total_completed = Trash.objects.filter(is_end=True).count()
    total_revenue = Trash.objects.aggregate(total=Sum('total'))['total'] or 0
    total_prepayment = Trash.objects.aggregate(total=Sum('prepayment'))['total'] or 0

    # Counts for other models
    client_count = Client.objects.count()
    product_count = Product.objects.count()
    productmold_count = ProductMold.objects.count()

    # Recent transactions and clients (adjust limits as necessary)
    recent_transactions = Trash.objects.order_by('-created_at')[:10]
    recent_clients = Client.objects.order_by('-id')[:5]

    # Generate daily revenue data (group by day)
    daily_data = Trash.objects.annotate(day=TruncDay('created_at')) \
                               .values('day') \
                               .annotate(total=Sum('total')) \
                               .order_by('day')
    chart_labels = [entry['day'].strftime("%Y-%m-%d") for entry in daily_data]
    daily_revenue_data = [entry['total'] for entry in daily_data]

    # Generate weekly revenue data (group by week)
    weekly_data = Trash.objects.annotate(week=TruncWeek('created_at')) \
                                .values('week') \
                                .annotate(total=Sum('total')) \
                                .order_by('week')
    weekly_revenue_data = [entry['total'] for entry in weekly_data]
    # Format weekly labels as "YYYY-WW"
    weekly_labels = [entry['week'].strftime("%Y-W%W") for entry in weekly_data]

    # Generate monthly revenue data (group by month)
    monthly_data = Trash.objects.annotate(month=TruncMonth('created_at')) \
                                 .values('month') \
                                 .annotate(total=Sum('total')) \
                                 .order_by('month')
    monthly_revenue_data = [entry['total'] for entry in monthly_data]
    monthly_labels = [entry['month'].strftime("%Y-%m") for entry in monthly_data]

    # Prepare context data for the dashboard template.
    # The daily data is used by default but weekly and monthly are also passed.
    context = {
        'total_trash': total_trash,
        'total_completed': total_completed,
        'total_revenue': total_revenue,
        'total_prepayment': total_prepayment,
        'client_count': client_count,
        'product_count': product_count,
        'productmold_count': productmold_count,
        'recent_transactions': recent_transactions,
        'recent_clients': recent_clients,
        'chart_labels': chart_labels,          # daily labels by default
        'daily_revenue_data': daily_revenue_data,
        'weekly_revenue_data': weekly_revenue_data,
        'weekly_labels': weekly_labels,
        'monthly_revenue_data': monthly_revenue_data,
        'monthly_labels': monthly_labels,
    }
    return render(request, 'admin/core/dashboard.html', context)

@login_required
@staff_member_required
def user_list(request):
    users = User.objects.all().order_by('id')
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Create a blank user creation form.
    create_form = CustomUserCreationForm()
    # Create an update form for each user on the current page.
    update_forms = {user.id: UserUpdateForm(instance=user) for user in page_obj}

    context = {
        'page_obj': page_obj,
        'create_form': create_form,
        'update_forms': update_forms,
    }
    return render(request, 'admin/core/user_list.html', context)


@login_required
@staff_member_required
def user_create(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully!')
        else:
            messages.error(request, 'Error creating user. Please correct the errors below.')
    return redirect('user_list')


@login_required
@staff_member_required
def user_update(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            user = form.save(commit=False)
            new_password = form.cleaned_data.get('password')
            # If a new password is provided, update it.
            if new_password:
                user.set_password(new_password)
            user.save()
            messages.success(request, 'User updated successfully!')
        else:
            messages.error(request, 'Error updating user. Please correct the errors below.')
    return redirect('user_list')


@login_required
@staff_member_required
def user_delete(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, 'User deleted successfully!')
    else:
        messages.error(request, 'Invalid request.')
    return redirect('user_list')


@login_required
def client_list(request):
    clients = Client.objects.all().order_by('id')
    paginator = Paginator(clients, 10)  # Display 10 clients per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Prepare a blank creation form.
    create_form = ClientForm()
    # Create an update form for each client in the current page.
    update_forms = {client.id: ClientForm(instance=client) for client in page_obj}

    return render(request, 'admin/core/client_list.html', {
        'page_obj': page_obj,
        'create_form': create_form,
        'update_forms': update_forms,
    })


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client created successfully!')
        else:
            messages.error(request, 'Error creating client. Please correct the errors below.')
    return redirect('client_list')


@login_required
def client_update(request, pk):
    client_obj = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Client updated successfully!')
        else:
            messages.error(request, 'Error updating client. Please correct the errors below.')
    return redirect('client_list')


@login_required
def client_delete(request, pk):
    client_obj = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client_obj.delete()
        messages.success(request, 'Client deleted successfully!')
    else:
        messages.error(request, 'Invalid request.')
    return redirect('client_list')


@login_required
def product_list(request):
    products = Product.objects.all().order_by('id')
    paginator = Paginator(products, 10)  # Display 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Create a blank form instance for product creation.
    create_form = ProductForm()
    # Create an update form for each product in the current page.
    update_forms = {product.id: ProductForm(instance=product) for product in page_obj}

    return render(request, 'admin/core/product_list.html', {
        'page_obj': page_obj,
        'create_form': create_form,
        'update_forms': update_forms,
    })


@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
        else:
            messages.error(request, 'Error creating product. Please correct the errors below.')
    return redirect('product_list')


@login_required
def product_update(request, pk):
    product_obj = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
        else:
            messages.error(request, 'Error updating product. Please correct the errors below.')
    return redirect('product_list')


@login_required
def product_delete(request, pk):
    product_obj = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product_obj.delete()
        messages.success(request, 'Product deleted successfully!')
    else:
        messages.error(request, 'Invalid request.')
    return redirect('product_list')


@login_required
def productmold_list(request):
    productmolds = ProductMold.objects.all().order_by('id')
    paginator = Paginator(productmolds, 10)  # Adjust to show 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Blank form for creation
    create_form = ProductMoldForm()
    # Prepare update forms for each record in current page
    update_forms = {pm.id: ProductMoldForm(instance=pm) for pm in page_obj}

    return render(request, 'admin/core/productmold_list.html', {
        'page_obj': page_obj,
        'create_form': create_form,
        'update_forms': update_forms,
    })


@login_required
def productmold_create(request):
    if request.method == 'POST':
        form = ProductMoldForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product Mold created successfully!')
        else:
            messages.error(request, 'Error creating Product Mold. Please correct the errors below.')
    return redirect('productmold_list')


@login_required
def productmold_update(request, pk):
    productmold_obj = get_object_or_404(ProductMold, pk=pk)
    if request.method == 'POST':
        form = ProductMoldForm(request.POST, instance=productmold_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product Mold updated successfully!')
        else:
            messages.error(request, 'Error updating Product Mold. Please correct the errors below.')
    return redirect('productmold_list')


@login_required
def productmold_delete(request, pk):
    productmold_obj = get_object_or_404(ProductMold, pk=pk)
    if request.method == 'POST':
        productmold_obj.delete()
        messages.success(request, 'Product Mold deleted successfully!')
    else:
        messages.error(request, 'Invalid request.')
    return redirect('productmold_list')


@login_required
def trash_list(request):
    trashes = Trash.objects.all().order_by('id')
    paginator = Paginator(trashes, 10)  # Show 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Instantiate a blank creation form.
    create_form = TrashForm()

    # Retrieve clients list for the client selection popup.
    clients = Client.objects.all().order_by('fullname')

    return render(request, 'admin/core/trash_list.html', {
        'page_obj': page_obj,
        'create_form': create_form,
        'clients': clients,
    })


@login_required
def trash_create(request):
    if request.method == 'POST':
        form = TrashForm(request.POST)
        if form.is_valid():
            trash = form.save(commit=False)
            # Automatically assign the current user.
            trash.user = request.user
            # total and is_end are not provided by the form.
            trash.total = 0
            trash.is_end = False
            trash.save()
            messages.success(request, 'Trash record created successfully!')
        else:
            messages.error(request, 'Error creating trash record. Please correct the errors below.')
    return redirect('trash_list')


@login_required
def trash_delete(request, pk):
    trash_obj = get_object_or_404(Trash, pk=pk)
    if request.method == 'POST':
        trash_obj.delete()
        messages.success(request, 'Trash record deleted successfully!')
    else:
        messages.error(request, 'Invalid request.')
    return redirect('trash_list')


@login_required
def trash_complete(request, pk):
    trash_obj = get_object_or_404(Trash, pk=pk)
    if request.method == 'POST':
        trash_obj.is_end = True
        trash_obj.save()
        messages.success(request, 'Trash record marked as complete.')
    else:
        messages.error(request, 'Invalid request.')
    return redirect('trash_list')


@login_required
def trash_detail(request, pk):
    """
    Displays a page for adding products and product molds dynamically to
    a particular Trash record. Each dynamic card allows the user to:
      - Select a product (displayed with full details)
      - Enter the desired quantity (not exceeding the product’s available count)
      - Optionally, select a product mold.
    """
    trash = get_object_or_404(Trash, pk=pk)
    products_list = Product.objects.all()
    productmolds_list = ProductMold.objects.all()

    if request.method == 'POST':
        # Retrieve lists from POST (note the names "product[]", "product_count[]" and "product_mold[]")
        product_ids = request.POST.getlist('product[]')
        product_count_list = request.POST.getlist('product_count[]')
        product_mold_ids = request.POST.getlist('product_mold[]')

        # Process each card (using zip over the three lists)
        for prod_id, count_str, mold_id in zip(product_ids, product_count_list, product_mold_ids):
            # Skip processing a card if both selections are empty.
            if not prod_id and not mold_id:
                continue

            # Process selected product and its count, if provided.
            if prod_id:
                try:
                    product = Product.objects.get(pk=prod_id)
                    try:
                        count = int(count_str)
                    except ValueError:
                        count = 1  # Default count if input is not a valid number

                    # Check if the entered count exceeds the product's available quantity.
                    if count > product.count:
                        messages.error(request, f"{product.name} maximum available quantity is {product.count}.")
                        continue

                    # Create a ProductHistory record.
                    ProductHistory.objects.create(
                        product=product,
                        trash=trash,
                        start_time=timezone.now(),
                        count=count  # Assumes ProductHistory has a 'count' field.
                    )
                except Product.DoesNotExist:
                    messages.error(request, f"Product with id {prod_id} not found.")

            # Process selected product mold (optional).
            if mold_id:
                try:
                    mold = ProductMold.objects.get(pk=mold_id)
                    # Create a ProductMoldHistory record.
                    ProductMoldHistory.objects.create(
                        product_mold=mold,
                        trash=trash,
                        start_time=timezone.now(),
                    )
                except ProductMold.DoesNotExist:
                    messages.error(request, f"Product Mold with id {mold_id} not found.")

        messages.success(request, "Items added successfully!")
        return redirect('trash_detail', pk=trash.pk)

    return render(request, 'admin/core/trash_detail.html', {
        'trash': trash,
        'products': products_list,
        'productmolds': productmolds_list,
    })



@login_required
def trash_items(request, pk):
    """
    Display a page to add new items (via dynamic cards) to a Trash record,
    and show the existing history items. In the history tables, if a record is complete,
    show its completed time and the computed total cost. (The cost calculation may be done
    when a record is completed in a separate view.)
    """
    trash = get_object_or_404(Trash, pk=pk)
    products_list = Product.objects.all()
    productmolds_list = ProductMold.objects.all()
    product_histories = ProductHistory.objects.filter(trash=trash)
    product_mold_histories = ProductMoldHistory.objects.filter(trash=trash)

    # old_items is used to preserve form input if errors occur
    old_items = None

    if request.method == 'POST':
        # Process new items additions from dynamic cards.
        item_values = request.POST.getlist('item[]')
        quantity_list = request.POST.getlist('quantity[]')
        old_items = [{'item': item_val, 'quantity': qty} for item_val, qty in zip(item_values, quantity_list)]
        error_detected = False

        for item_val, qty_str in zip(item_values, quantity_list):
            if not item_val:
                error_detected = True
                messages.error(request, "You must select an item for every card.")
                continue

            try:
                quantity = int(qty_str)
            except ValueError:
                error_detected = True
                messages.error(request, "Quantity must be a number.")
                continue

            # Process Product option
            if item_val.startswith("product_"):
                prod_id = item_val.split("_", 1)[1]
                try:
                    product = Product.objects.get(pk=prod_id)
                except Product.DoesNotExist:
                    error_detected = True
                    messages.error(request, f"Product with id {prod_id} not found.")
                    continue

                if quantity > product.count:
                    error_detected = True
                    messages.error(request, f"Maximum available quantity for {product.name} is {product.count}.")
                    continue

                # Create ProductHistory record (assumes history 'count' field exists)
                ProductHistory.objects.create(
                    product=product,
                    trash=trash,
                    count=quantity,
                    start_time=timezone.now()
                )

            # Process Product Mold option
            elif item_val.startswith("mold_"):
                mold_id = item_val.split("_", 1)[1]
                try:
                    mold = ProductMold.objects.get(pk=mold_id)
                except ProductMold.DoesNotExist:
                    error_detected = True
                    messages.error(request, f"Product Mold with id {mold_id} not found.")
                    continue

                if quantity > mold.count:
                    error_detected = True
                    messages.error(request, f"Maximum available quantity for mold {mold.length} is {mold.count}.")
                    continue

                ProductMoldHistory.objects.create(
                    product_mold=mold,
                    trash=trash,
                    count=quantity,
                    start_time=timezone.now()
                )
        if error_detected:
            # Re-render page preserving the old items input.
            return render(request, 'admin/core/trash_items.html', {
                'trash': trash,
                'products': products_list,
                'productmolds': productmolds_list,
                'product_histories': product_histories,
                'product_mold_histories': product_mold_histories,
                'old_items': old_items,
            })
        messages.success(request, "Items added successfully!")
        return redirect('trash_detail', pk=trash.pk)

    return render(request, 'admin/core/trash_items.html', {
        'trash': trash,
        'products': products_list,
        'productmolds': productmolds_list,
        'product_histories': product_histories,
        'product_mold_histories': product_mold_histories,
        'old_items': old_items,
    })


@login_required
def product_history_complete(request, pk):
    """
    Marks a ProductHistory record as complete by setting end_time.
    Then it calculates the cost by:
         (end_time - start_time in days) * product.price
    and adds that amount to the parent Trash's total.
    """
    history = get_object_or_404(ProductHistory, pk=pk)

    if request.method == "POST":
        if history.end_time is None:
            history.end_time = timezone.now()
            # Calculate duration in days as a float (total seconds / 86400)
            duration = (history.end_time - history.start_time).total_seconds() / 86400.0
            # Get the product's cost (assume product.price holds the per-day cost)
            cost = history.product.price
            total_cost = duration * cost
            history.save()

            # Update the parent Trash record's total cost
            trash = history.trash
            trash.total += total_cost
            trash.save()

            messages.success(request, f"Record completed. Total cost ${total_cost:.2f} added to the trash total.")
        else:
            messages.info(request, "This record has already been completed.")
        return redirect('trash_detail', pk=history.trash.pk)
    else:
        messages.error(request, "Invalid request method.")
        return redirect('trash_detail', pk=history.trash.pk)


@login_required
def productmold_history_complete(request, pk):
    history = get_object_or_404(ProductMoldHistory, pk=pk)

    if request.method == "POST":
        if history.end_time is None:
            history.end_time = timezone.now()
            duration = (history.end_time - history.start_time).total_seconds() / 86400.0
            cost = history.product_mold.price  # Assume product mold also has a price field
            total_cost = duration * cost
            history.save()

            trash = history.trash
            trash.total += total_cost
            trash.save()

            messages.success(request, f"Mold record completed. Total cost ${total_cost:.2f} added to trash total.")
        else:
            messages.info(request, "This mold record has already been completed.")
        return redirect('trash_detail', pk=history.trash.pk)
    else:
        messages.error(request, "Invalid request method.")
        return redirect('trash_detail', pk=history.trash.pk)

@login_required
def product_history_delete(request, pk):
    """
    Delete a ProductHistory record.
    If the record has been completed (end_time is set) and a total_cost exists,
    subtract that total_cost from the parent Trash record's total before deletion.
    Only accepts POST requests.
    """
    history = get_object_or_404(ProductHistory, pk=pk)
    trash = history.trash

    if request.method == "POST":
        # If the history record is complete and has a computed total_cost,
        # subtract it from the Trash total. Adjust if your model stores the computed value.
        if history.end_time and hasattr(history, 'total_cost'):
            trash.total -= history.total_cost
            trash.save()

        history.delete()
        messages.success(request, "Product history record deleted successfully.")
        return redirect('trash_detail', pk=trash.pk)
    else:
        messages.error(request, "Invalid request method.")
        return redirect('trash_detail', pk=trash.pk)


@login_required
def productmold_history_delete(request, pk):
    """
    Delete a ProductHistory record.
    If the record has been completed (end_time is set) and a total_cost exists,
    subtract that total_cost from the parent Trash record's total before deletion.
    Only accepts POST requests.
    """
    history = get_object_or_404(ProductMoldHistory, pk=pk)
    trash = history.trash

    if request.method == "POST":
        # If the history record is complete and has a computed total_cost,
        # subtract it from the Trash total. Adjust if your model stores the computed value.
        if history.end_time and hasattr(history, 'total_cost'):
            trash.total -= history.total_cost
            trash.save()

        history.delete()
        messages.success(request, "Product Mold history record deleted successfully.")
        return redirect('trash_detail', pk=trash.pk)
    else:
        messages.error(request, "Invalid request method.")
        return redirect('trash_detail', pk=trash.pk)


def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('dashboard')
        else:
            return redirect('client_list')
    else:
        return render(request, 'home.html')