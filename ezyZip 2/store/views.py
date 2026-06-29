import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.conf import settings

from .models import Store, Product, Order, Message, Category
from .forms import RegisterForm, ProductForm, OrderStatusForm, MessageForm, StoreForm


# ──────────────────────────────────────────
#  Auth & Onboarding
# ──────────────────────────────────────────

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to EcoStore! Your store '{user.store.name}' is ready.")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'store/register.html', {'form': form})


def _get_user_store(user):
    """Return the store for the logged-in user, or None."""
    try:
        return user.store
    except Store.DoesNotExist:
        return None


# ──────────────────────────────────────────
#  Dashboard
# ──────────────────────────────────────────

@login_required
def dashboard(request):
    store = _get_user_store(request.user)
    if not store:
        return redirect('register')

    # Aggregate stats
    total_revenue = store.orders.filter(
        status__in=['delivered', 'shipped', 'processing']
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')

    total_orders = store.orders.count()
    total_products = store.products.count()
    low_stock = store.products.filter(stock__lt=10).count()

    # Recent orders
    recent_orders = store.orders.order_by('-created_at')[:5]

    # Monthly revenue for Chart.js (last 6 months)
    from datetime import timedelta
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_data = (
        store.orders
        .filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(revenue=Sum('total'), count=Count('id'))
        .order_by('month')
    )

    chart_labels = [d['month'].strftime('%b %Y') for d in monthly_data]
    chart_revenue = [float(d['revenue']) for d in monthly_data]
    chart_orders = [d['count'] for d in monthly_data]

    # Category breakdown
    category_data = (
        store.products
        .values('category')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    cat_labels = [d['category'].title() for d in category_data]
    cat_counts = [d['count'] for d in category_data]

    # Unread messages count
    unread_count = Message.objects.filter(receiver_store=store, is_read=False).count()

    context = {
        'active': 'dashboard',
        'store': store,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_products': total_products,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
        'chart_labels': json.dumps(chart_labels),
        'chart_revenue': json.dumps(chart_revenue),
        'chart_orders': json.dumps(chart_orders),
        'cat_labels': json.dumps(cat_labels),
        'cat_counts': json.dumps(cat_counts),
        'unread_count': unread_count,
    }
    return render(request, 'store/dashboard.html', context)


# ──────────────────────────────────────────
#  Products (CRUD)
# ──────────────────────────────────────────

@login_required
def products(request):
    store = _get_user_store(request.user)
    if not store:
        return redirect('register')

    qs = store.products.all()
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(sku__icontains=search))
    if category:
        qs = qs.filter(category=category)

    unread_count = Message.objects.filter(receiver_store=store, is_read=False).count()
    context = {
        'active': 'products',
        'store': store,
        'products': qs.order_by('-created_at'),
        'categories': Category.choices,
        'search': search,
        'selected_category': category,
        'unread_count': unread_count,
    }
    return render(request, 'store/products.html', context)


@login_required
def product_create(request):
    store = _get_user_store(request.user)
    if not store:
        return redirect('register')
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            messages.success(request, f"Product '{product.name}' created successfully.")
            return redirect('products')
    else:
        form = ProductForm()
    return render(request, 'store/product_form.html', {
        'active': 'products', 'store': store, 'form': form, 'action': 'Create'
    })


@login_required
def product_edit(request, pk):
    store = _get_user_store(request.user)
    product = get_object_or_404(Product, pk=pk, store=store)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product '{product.name}' updated.")
            return redirect('products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/product_form.html', {
        'active': 'products', 'store': store, 'form': form, 'action': 'Edit', 'product': product
    })


@login_required
def product_delete(request, pk):
    store = _get_user_store(request.user)
    product = get_object_or_404(Product, pk=pk, store=store)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f"Product '{name}' deleted.")
    return redirect('products')


# ──────────────────────────────────────────
#  Orders
# ──────────────────────────────────────────

@login_required
def orders(request):
    store = _get_user_store(request.user)
    if not store:
        return redirect('register')

    qs = store.orders.all()
    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    unread_count = Message.objects.filter(receiver_store=store, is_read=False).count()
    context = {
        'active': 'orders',
        'store': store,
        'orders': qs.order_by('-created_at'),
        'status_choices': Order.Status.choices,
        'status_filter': status_filter,
        'unread_count': unread_count,
    }
    return render(request, 'store/orders.html', context)


@login_required
def order_detail(request, pk):
    store = _get_user_store(request.user)
    order = get_object_or_404(Order, pk=pk, store=store)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Order status updated.")
            return redirect('orders')
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'store/order_detail.html', {
        'active': 'orders', 'store': store, 'order': order, 'form': form
    })


# ──────────────────────────────────────────
#  Marketplace
# ──────────────────────────────────────────

@login_required
def marketplace(request):
    store = _get_user_store(request.user)
    if not store:
        return redirect('register')

    qs = Product.objects.exclude(store=store).select_related('store')
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'newest')

    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(store__name__icontains=search))
    if category:
        qs = qs.filter(category=category)

    sort_map = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'name': 'name',
    }
    qs = qs.order_by(sort_map.get(sort, '-created_at'))

    unread_count = Message.objects.filter(receiver_store=store, is_read=False).count()
    context = {
        'active': 'marketplace',
        'store': store,
        'products': qs,
        'categories': Category.choices,
        'search': search,
        'selected_category': category,
        'sort': sort,
        'unread_count': unread_count,
    }
    return render(request, 'store/marketplace.html', context)


# ──────────────────────────────────────────
#  Messaging
# ──────────────────────────────────────────

@login_required
def inbox(request):
    store = _get_user_store(request.user)
    if not store:
        return redirect('register')

    # Get all stores we've had conversations with
    sent_to = Message.objects.filter(sender_store=store).values_list('receiver_store_id', flat=True)
    received_from = Message.objects.filter(receiver_store=store).values_list('sender_store_id', flat=True)
    partner_ids = set(list(sent_to) + list(received_from))
    partner_ids.discard(store.id)

    conversations = []
    for partner_id in partner_ids:
        partner = Store.objects.get(pk=partner_id)
        last_msg = Message.objects.filter(
            Q(sender_store=store, receiver_store=partner) |
            Q(sender_store=partner, receiver_store=store)
        ).last()
        unread = Message.objects.filter(
            sender_store=partner, receiver_store=store, is_read=False
        ).count()
        conversations.append({
            'partner': partner,
            'last_message': last_msg,
            'unread': unread,
        })

    conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else timezone.now(), reverse=True)
    unread_count = Message.objects.filter(receiver_store=store, is_read=False).count()

    context = {
        'active': 'messages',
        'store': store,
        'conversations': conversations,
        'unread_count': unread_count,
    }
    return render(request, 'store/inbox.html', context)


@login_required
def conversation(request, store_id):
    my_store = _get_user_store(request.user)
    if not my_store:
        return redirect('register')

    partner = get_object_or_404(Store, pk=store_id)
    if partner == my_store:
        return redirect('inbox')

    # Mark messages as read
    Message.objects.filter(
        sender_store=partner, receiver_store=my_store, is_read=False
    ).update(is_read=True)

    msgs = Message.objects.filter(
        Q(sender_store=my_store, receiver_store=partner) |
        Q(sender_store=partner, receiver_store=my_store)
    ).select_related('product').order_by('timestamp')

    form = MessageForm()
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender_store = my_store
            msg.receiver_store = partner
            product_id = request.POST.get('product_id')
            if product_id:
                try:
                    msg.product = Product.objects.get(pk=product_id)
                except Product.DoesNotExist:
                    pass
            msg.save()
            return redirect('conversation', store_id=store_id)

    unread_count = Message.objects.filter(receiver_store=my_store, is_read=False).count()
    context = {
        'active': 'messages',
        'store': my_store,
        'partner': partner,
        'messages_list': msgs,
        'form': form,
        'unread_count': unread_count,
    }
    return render(request, 'store/conversation.html', context)


@login_required
def contact_store(request, store_id):
    """Quick 'Contact Store' from marketplace — creates convo and redirects."""
    my_store = _get_user_store(request.user)
    if not my_store:
        return redirect('register')

    partner = get_object_or_404(Store, pk=store_id)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        product_id = request.POST.get('product_id')
        if content:
            msg = Message(sender_store=my_store, receiver_store=partner, content=content)
            if product_id:
                try:
                    msg.product = Product.objects.get(pk=product_id)
                except Product.DoesNotExist:
                    pass
            msg.save()
            messages.success(request, f"Message sent to {partner.name}!")
    return redirect('conversation', store_id=store_id)


# ──────────────────────────────────────────
#  AI Advisor
# ──────────────────────────────────────────

@login_required
def ai_advisor(request):
    store = _get_user_store(request.user)
    if not store:
        return redirect('register')

    market_products = Product.objects.exclude(store=store).select_related('store')[:50]
    my_products = store.products.all()

    unread_count = Message.objects.filter(receiver_store=store, is_read=False).count()
    context = {
        'active': 'ai',
        'store': store,
        'market_products': market_products,
        'my_products': my_products,
        'unread_count': unread_count,
    }
    return render(request, 'store/ai_advisor.html', context)


@login_required
@require_POST
def ai_chat(request):
    """AJAX endpoint: calls Gemini API with store context."""
    store = _get_user_store(request.user)
    if not store:
        return JsonResponse({'error': 'No store found.'}, status=400)

    try:
        body = json.loads(request.body)
        user_message = body.get('message', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Empty message.'}, status=400)

    # Build rich context for the AI
    my_products_data = list(store.products.values('name', 'price', 'stock', 'category'))
    market_products_data = list(
        Product.objects.exclude(store=store)
        .select_related('store')
        .values('name', 'price', 'stock', 'category', 'store__name')[:30]
    )
    revenue = store.orders.filter(
        status__in=['delivered', 'shipped', 'processing']
    ).aggregate(total=Sum('total'))['total'] or 0

    system_context = f"""You are an AI business advisor for EcoStore, an e-commerce marketplace platform.

Store Context:
- Store Name: {store.name}
- Description: {store.description or 'N/A'}
- My Products ({len(my_products_data)}): {json.dumps(my_products_data, default=str)}
- Total Revenue: ${revenue}
- Total Orders: {store.orders.count()}

Marketplace Overview ({len(market_products_data)} competitor products visible):
{json.dumps(market_products_data, default=str)}

Provide concise, actionable business advice. Use bullet points when listing items.
Focus on pricing strategy, inventory, market gaps, and growth opportunities.
Keep responses under 300 words unless the question is very detailed."""

    api_key = settings.GEMINI_API_KEY
    if api_key == 'YOUR_GEMINI_API_KEY_HERE':
        # Demo mode — return a mock response
        mock = f"""**AI Advisor (Demo Mode)**

Based on your store **{store.name}**, here are some insights:

• **Pricing**: Your products appear competitive in the marketplace.
• **Inventory**: Keep an eye on low-stock items to avoid losing sales.
• **Market Gap**: Consider expanding into underserved categories visible in the marketplace.
• **Growth**: Engaging with other stores via messaging can open B2B opportunities.

*Set your GEMINI_API_KEY environment variable to unlock full AI analysis.*"""
        return JsonResponse({'reply': mock})

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_context
        )
        response = model.generate_content(user_message)
        return JsonResponse({'reply': response.text})
    except ImportError:
        return JsonResponse({'reply': '⚠️ google-generativeai package not installed. Run: pip install google-generativeai'})
    except Exception as e:
        return JsonResponse({'reply': f'⚠️ Gemini API error: {str(e)}'})


# ──────────────────────────────────────────
#  Store Settings
# ──────────────────────────────────────────

@login_required
def store_settings(request):
    store = _get_user_store(request.user)
    if not store:
        return redirect('register')

    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            messages.success(request, "Store settings updated.")
            return redirect('store_settings')
    else:
        form = StoreForm(instance=store)

    unread_count = Message.objects.filter(receiver_store=store, is_read=False).count()
    return render(request, 'store/settings.html', {
        'active': 'settings', 'store': store, 'form': form, 'unread_count': unread_count
    })
