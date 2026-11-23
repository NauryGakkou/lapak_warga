from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.utils import timezone
from .forms import RegisterForm, ProductForm, ArticleForm, CheckoutForm
from .models import Product, Order, Cart, CartItem, OrderItem, Article, Category


# ─────────────────────────── AUTH ────────────────────────────

def home(request):
    products = Product.objects.filter(is_active=True).select_related("seller", "category")[:8]
    articles = Article.objects.filter(is_published=True)[:3]
    return render(request, "marketplace/home.html", {"products": products, "articles": articles})


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        Cart.objects.get_or_create(user=user)
        messages.success(request, "Akun berhasil dibuat. Selamat datang di Lapak Warga!")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


# ─────────────────────────── DASHBOARD ────────────────────────────

@login_required
def dashboard(request):
    if request.user.is_superuser:
        context = {
            "total_users": User.objects.count(),
            "total_products": Product.objects.count(),
            "total_orders": Order.objects.count(),
            "total_articles": Article.objects.count(),
            "recent_products": Product.objects.select_related("seller", "category")[:5],
            "recent_orders": Order.objects.select_related("user").order_by("-created_at")[:5],
        }
        return render(request, "marketplace/dashboard_admin.html", context)

    orders = Order.objects.filter(user=request.user)[:5]
    my_products = Product.objects.filter(seller=request.user)
    context = {
        "orders": orders,
        "product_count": my_products.count(),
        "order_count": Order.objects.filter(user=request.user).count(),
        "recent_products": my_products[:4],
    }
    return render(request, "marketplace/dashboard.html", context)


# ─────────────────────────── PRODUCTS ────────────────────────────

def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("seller", "category")
    categories = Category.objects.all()
    cat_slug = request.GET.get("kategori")
    if cat_slug:
        products = products.filter(category__slug=cat_slug)
    return render(request, "marketplace/product_list.html", {
        "products": products,
        "categories": categories,
        "active_category": cat_slug,
    })


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("seller", "category"),
        slug=slug,
        is_active=True
    )
    return render(request, "marketplace/product_detail.html", {"product": product})


# ─────────────────────── ADMIN PRODUCT CRUD ────────────────────────

def _require_admin(request):
    """Return True if user is superuser, else redirect."""
    return request.user.is_authenticated and request.user.is_superuser


@login_required
def admin_product_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Akses ditolak.")
        return redirect("dashboard")
    products = Product.objects.select_related("seller", "category").order_by("-created_at")
    return render(request, "marketplace/admin/product_list.html", {"products": products})


@login_required
def admin_product_add(request):
    if not request.user.is_superuser:
        messages.error(request, "Akses ditolak.")
        return redirect("dashboard")
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.seller = request.user
        product.save()
        messages.success(request, f"Produk '{product.name}' berhasil ditambahkan.")
        return redirect("admin_product_list")
    return render(request, "marketplace/admin/product_form.html", {"form": form, "action": "Tambah"})


@login_required
def admin_product_edit(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Akses ditolak.")
        return redirect("dashboard")
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Produk '{product.name}' berhasil diperbarui.")
        return redirect("admin_product_list")
    return render(request, "marketplace/admin/product_form.html", {
        "form": form, "product": product, "action": "Edit"
    })


@login_required
def admin_product_delete(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Akses ditolak.")
        return redirect("dashboard")
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        name = product.name
        product.delete()
        messages.success(request, f"Produk '{name}' berhasil dihapus.")
        return redirect("admin_product_list")
    return render(request, "marketplace/admin/product_confirm_delete.html", {"product": product})


# ─────────────────────── ARTIKEL ────────────────────────

def article_list(request):
    articles = Article.objects.filter(is_published=True).select_related("author")
    return render(request, "marketplace/article_list.html", {"articles": articles})


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, "marketplace/article_detail.html", {"article": article})


@login_required
def admin_article_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Akses ditolak.")
        return redirect("dashboard")
    articles = Article.objects.select_related("author").order_by("-created_at")
    return render(request, "marketplace/admin/article_list.html", {"articles": articles})


@login_required
def admin_article_add(request):
    if not request.user.is_superuser:
        messages.error(request, "Akses ditolak.")
        return redirect("dashboard")
    form = ArticleForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        article = form.save(commit=False)
        article.author = request.user
        article.save()
        messages.success(request, f"Artikel '{article.title}' berhasil disimpan.")
        return redirect("admin_article_list")
    return render(request, "marketplace/admin/article_form.html", {"form": form, "action": "Tambah"})


@login_required
def admin_article_edit(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Akses ditolak.")
        return redirect("dashboard")
    article = get_object_or_404(Article, pk=pk)
    form = ArticleForm(request.POST or None, request.FILES or None, instance=article)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Artikel '{article.title}' berhasil diperbarui.")
        return redirect("admin_article_list")
    return render(request, "marketplace/admin/article_form.html", {
        "form": form, "article": article, "action": "Edit"
    })


@login_required
def admin_article_delete(request, pk):
    if not request.user.is_superuser:
        messages.error(request, "Akses ditolak.")
        return redirect("dashboard")
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        title = article.title
        article.delete()
        messages.success(request, f"Artikel '{title}' berhasil dihapus.")
        return redirect("admin_article_list")
    return render(request, "marketplace/admin/article_confirm_delete.html", {"article": article})


# ─────────────────────── KERANJANG ────────────────────────

def _get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related("product")
    total = sum(item.subtotal for item in items)
    return render(request, "marketplace/cart.html", {"cart": cart, "items": items, "total": total})


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = _get_cart(request.user)
    qty = int(request.POST.get("quantity", 1))
    if qty < 1:
        qty = 1
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += qty
    else:
        item.quantity = qty
    if item.quantity > product.stock:
        item.quantity = product.stock
    item.save()
    messages.success(request, f"'{product.name}' ditambahkan ke keranjang.")
    return redirect(request.POST.get("next", "cart_detail"))


@login_required
def cart_update(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    qty = int(request.POST.get("quantity", 1))
    if qty < 1:
        item.delete()
        messages.info(request, "Produk dihapus dari keranjang.")
    else:
        if qty > item.product.stock:
            qty = item.product.stock
        item.quantity = qty
        item.save()
    return redirect("cart_detail")


@login_required
def cart_remove(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, "Produk dihapus dari keranjang.")
    return redirect("cart_detail")


# ─────────────────────── CHECKOUT & PEMBAYARAN ────────────────────────

@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if product.stock < 1:
        messages.error(request, f"Maaf, stok untuk '{product.name}' sudah habis.")
        return redirect("product_detail", slug=product.slug)

    try:
        qty = int(request.POST.get("quantity", request.GET.get("quantity", 1)))
    except (ValueError, TypeError):
        qty = 1

    if qty < 1:
        qty = 1
    elif qty > product.stock:
        qty = product.stock

    total = product.price * qty
    form = CheckoutForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        order = form.save(commit=False)
        order.user = request.user
        order.total = total
        order.save()

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            price=product.price,
            quantity=qty,
        )
        product.stock -= qty
        product.save()

        messages.success(request, f"Pesanan #{order.pk} berhasil dibuat! Silakan selesaikan pembayaran.")
        return redirect("order_payment", pk=order.pk)

    return render(request, "marketplace/direct_checkout.html", {
        "form": form,
        "product": product,
        "quantity": qty,
        "total": total,
    })


@login_required
def checkout(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related("product")
    if not items.exists():
        messages.warning(request, "Keranjang Anda kosong.")
        return redirect("cart_detail")
    total = sum(item.subtotal for item in items)
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        order = form.save(commit=False)
        order.user = request.user
        order.total = total
        order.save()
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )
            # kurangi stok
            item.product.stock -= item.quantity
            item.product.save()
        cart.items.all().delete()
        messages.success(request, f"Pesanan #{order.pk} berhasil dibuat! Silakan selesaikan pembayaran.")
        return redirect("order_payment", pk=order.pk)
    return render(request, "marketplace/checkout.html", {
        "form": form, "items": items, "total": total
    })


@login_required
def order_payment(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status == "paid":
        messages.info(request, "Pesanan ini sudah dibayar.")
        return redirect("checkout_done", pk=order.pk)

    # Generate virtual account dummy nomor
    va_numbers = {
        "bca_va": f"12608{request.user.id:04d}{order.id:04d}",
        "bri_va": f"80777{request.user.id:04d}{order.id:04d}",
        "mandiri_va": f"88708{request.user.id:04d}{order.id:04d}",
    }
    va_number = va_numbers.get(order.payment_method, "")

    items = order.items.select_related("product")
    return render(request, "marketplace/order_payment.html", {
        "order": order,
        "items": items,
        "va_number": va_number,
        "payment_choices": Order.PAYMENT_CHOICES,
    })


@login_required
def order_change_payment(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == "POST":
        new_method = request.POST.get("payment_method")
        valid_methods = [choice[0] for choice in Order.PAYMENT_CHOICES]
        if new_method in valid_methods:
            order.payment_method = new_method
            order.save()
            messages.success(request, f"Metode pembayaran diubah ke {order.get_payment_method_display()}.")
    return redirect("order_payment", pk=order.pk)


@login_required
def order_process_payment(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if request.method == "POST":
        if order.status != "paid":
            order.status = "paid"
            order.paid_at = timezone.now()
            order.save()
            messages.success(request, f"✅ Pembayaran pesanan #{order.pk} berhasil diverifikasi! Terima kasih.")
        return redirect("checkout_done", pk=order.pk)
    return redirect("order_payment", pk=order.pk)


@login_required
def checkout_done(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, "marketplace/checkout_done.html", {"order": order})


# ─────────────────────── STATIC PAGES ────────────────────────

def privacy_policy(request):
    return render(request, "marketplace/pages/privacy.html")


def terms_of_service(request):
    return render(request, "marketplace/pages/terms.html")


def about(request):
    return render(request, "marketplace/pages/about.html")


def contact(request):
    return render(request, "marketplace/pages/contact.html")
