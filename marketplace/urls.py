from django.urls import path
from . import views

urlpatterns = [
    # Produk publik
    path("produk/", views.product_list, name="product_list"),
    path("produk/<slug:slug>/", views.product_detail, name="product_detail"),

    # Artikel publik
    path("artikel/", views.article_list, name="article_list"),
    path("artikel/<slug:slug>/", views.article_detail, name="article_detail"),

    # Keranjang
    path("keranjang/", views.cart_detail, name="cart_detail"),
    path("keranjang/tambah/<int:product_id>/", views.cart_add, name="cart_add"),
    path("keranjang/update/<int:item_id>/", views.cart_update, name="cart_update"),
    path("keranjang/hapus/<int:item_id>/", views.cart_remove, name="cart_remove"),

    # Checkout & Pembayaran
    path("beli-sekarang/<int:product_id>/", views.buy_now, name="buy_now"),
    path("checkout/", views.checkout, name="checkout"),
    path("pesanan/<int:pk>/bayar/", views.order_payment, name="order_payment"),
    path("pesanan/<int:pk>/proses-bayar/", views.order_process_payment, name="order_process_payment"),
    path("pesanan/<int:pk>/ubah-metode/", views.order_change_payment, name="order_change_payment"),
    path("checkout/selesai/<int:pk>/", views.checkout_done, name="checkout_done"),

    # Admin - Produk
    path("dashboard/produk/", views.admin_product_list, name="admin_product_list"),
    path("dashboard/produk/tambah/", views.admin_product_add, name="admin_product_add"),
    path("dashboard/produk/<int:pk>/edit/", views.admin_product_edit, name="admin_product_edit"),
    path("dashboard/produk/<int:pk>/hapus/", views.admin_product_delete, name="admin_product_delete"),

    # Admin - Artikel
    path("dashboard/artikel/", views.admin_article_list, name="admin_article_list"),
    path("dashboard/artikel/tambah/", views.admin_article_add, name="admin_article_add"),
    path("dashboard/artikel/<int:pk>/edit/", views.admin_article_edit, name="admin_article_edit"),
    path("dashboard/artikel/<int:pk>/hapus/", views.admin_article_delete, name="admin_article_delete"),

    # Halaman statis
    path("kebijakan-privasi/", views.privacy_policy, name="privacy_policy"),
    path("syarat-ketentuan/", views.terms_of_service, name="terms_of_service"),
    path("tentang-kami/", views.about, name="about"),
    path("hubungi-kami/", views.contact, name="contact"),
]
