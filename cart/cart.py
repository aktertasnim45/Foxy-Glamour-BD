from decimal import Decimal
from django.conf import settings
from store.models import Product, Size

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False, size=None):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        # Create a unique key for the cart item based on product and size
        if size:
            cart_item_key = f"{product_id}_{size}"
        else:
            cart_item_key = product_id

        if cart_item_key not in self.cart:
            self.cart[cart_item_key] = {
                'quantity': 0, 
                'price': str(product.price),
                'product_id': product_id,
                'size': size
            }
        
        if override_quantity:
            self.cart[cart_item_key]['quantity'] = quantity
        else:
            self.cart[cart_item_key]['quantity'] += quantity
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, product, size=None):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if size:
            cart_item_key = f"{product_id}_{size}"
        else:
            cart_item_key = product_id

        if cart_item_key in self.cart:
            del self.cart[cart_item_key]
            self.save()

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        # Collect all product IDs from the cart items
        product_ids = set()
        for item in self.cart.values():
            # Handle legacy cart items where product_id might not be stored explicitly
            if 'product_id' in item:
                product_ids.add(item['product_id'])
            else:
                # Fallback implementation if logic changes on live cart
                # Ideally, we should migrate, but for now we might skip or try to parse keys
                pass 

        # If we have legacy keys that are just product_ids (integers in string form)
        # We can add those too if not covered above
        for key in self.cart.keys():
            if '_' not in key:
                product_ids.add(key)

        # Collect all unique size codes from cart items
        size_codes = set()
        for item in self.cart.values():
            s = item.get('size')
            if s and s != "Adjustable":
                size_codes.add(s)
        
        # Fetch Size objects
        size_map = {}
        if size_codes:
            sizes = Size.objects.filter(code__in=size_codes)
            for size in sizes:
                size_map[size.code] = size.name

        products = Product.objects.filter(id__in=product_ids)
        
        # Create a dictionary for faster lookup
        product_dict = {str(p.id): p for p in products}

        cart = self.cart.copy()

        for key, item in cart.items():
            item = item.copy() # Fix: Copy item to avoid modifying the session directly with non-serializable objects
            # Determine product_id for this item
            p_id = item.get('product_id')
            if not p_id:
                # Fallback for legacy items where key IS the product_id
                if '_' not in key:
                    p_id = key
            
            if p_id and p_id in product_dict:
                item['product'] = product_dict[p_id]
                item['net_price'] = Decimal(item['price'])
                item['total_price'] = item['net_price'] * item['quantity']

                # Resolve Size Name
                item_size = item.get('size')
                if item_size == "Adjustable":
                    item['size_name'] = "Adjustable" # Or "Free Size" if preferred
                elif item_size in size_map:
                    item['size_name'] = size_map[item_size]
                else:
                    item['size_name'] = item_size # Fallback to code/value if not found

                yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()