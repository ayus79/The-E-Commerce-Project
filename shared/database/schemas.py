from core.constants import CoreCollections


# ---------- Customers ----------

# CREATE_CUSTOMERS_TABLE = f"""
# CREATE TABLE IF NOT EXISTS customers (
#     id BIGSERIAL PRIMARY KEY,
#     email VARCHAR(255) UNIQUE NOT NULL,
#     hashed_password TEXT NOT NULL,
#     full_name VARCHAR(255) NOT NULL,
#     phone_number VARCHAR(20),
#     is_active BOOLEAN NOT NULL DEFAULT TRUE,
#     is_verified BOOLEAN NOT NULL DEFAULT FALSE,
#     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
#     updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
# );
# """

# ---------- Products ----------

CREATE_PRODUCTS_TABLE = f"""
CREATE TABLE IF NOT EXISTS {CoreCollections.PRODUCTS} (
    id BIGSERIAL PRIMARY KEY,
    sku VARCHAR(64) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0),
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    attributes JSONB,                             -- flexible per-category fields
    is_published BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

# CREATE_PRODUCT_VARIANTS_TABLE = """
# CREATE TABLE IF NOT EXISTS product_variants (
#     id BIGSERIAL PRIMARY KEY,
#     product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
#     sku VARCHAR(64) UNIQUE NOT NULL,
#     variant_attributes JSONB NOT NULL,   -- e.g. {"size": "M", "color": "Red"}
#     price_override NUMERIC(12, 2),        -- NULL = use parent product's price
#     is_active BOOLEAN NOT NULL DEFAULT TRUE,
#     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
# );
# """

# ---------- Orders ----------

CREATE_ORDERS_TABLE = f"""
CREATE TABLE IF NOT EXISTS {CoreCollections.ORDERS} (
    id BIGSERIAL PRIMARY KEY,
    order_number VARCHAR(32) UNIQUE NOT NULL,      -- human-facing ref, e.g. ORD-20260929-0001
    customer_id BIGINT NOT NULL REFERENCES customers(id),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- pending | paid | shipped | delivered | cancelled | refunded
    subtotal NUMERIC(12, 2) NOT NULL,
    tax_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    shipping_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    discount_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

CREATE_ORDER_ITEMS_TABLE = f"""
CREATE TABLE IF NOT EXISTS {CoreCollections.ORDER_ITEMS} (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products(id),
    product_name VARCHAR(255) NOT NULL,             -- snapshot at time of purchase
    unit_price NUMERIC(12, 2) NOT NULL,              -- snapshot at time of purchase
    quantity INT NOT NULL CHECK (quantity > 0),
    line_total NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""
