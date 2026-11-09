import sqlite3
import os
import sys

# Ensure UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "database", "jewellery_store.db")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Store Information / Inbound FAQs / Policies
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS store_info (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)

    # Daily Gold & Silver Rates (per gram in INR)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_rates (
        metal TEXT PRIMARY KEY,
        purity TEXT,
        rate_per_gram REAL,
        last_updated TEXT
    );
    """)

    # Jewellery Catalog
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        metal TEXT,
        purity TEXT,
        weight_grams REAL,
        making_charges_percent REAL,
        in_stock INTEGER,
        estimated_price REAL,
        description TEXT
    );
    """)

    # Inbound Call Logs Only
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inbound_call_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        caller_phone TEXT,
        language_detected TEXT,
        inquiry_type TEXT,
        caller_query TEXT,
        receptionist_reply TEXT,
        call_action TEXT DEFAULT 'CONTINUE', -- 'CONTINUE', 'HANGUP', 'TRANSFER_HUMAN'
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed Default Store Info for Shashvat Jewels Pvt Ltd
    default_info = [
        ("store_name", "Shashvat Jewels Pvt Ltd"),
        ("address", "Diamond Factory & Showroom Unit, B2B & Retail Hub"),
        ("landmark", "Diamond Industrial Park / MG Road"),
        ("timings", "Monday to Saturday 10:00 AM to 8:00 PM, Sunday closed"),
        ("whatsapp", "+91 98765 43210"),
        ("phone", "+91 98765 43210"),
        ("manager_phone", "+91 98765 00000"),
        ("specialty", "Certified Natural & CVD Lab-Grown Diamonds, Fine Gold & Bridal Jewellery, B2B Bulk Manufacturing & Export."),
        ("certifications", "100% IGI & GIA Certified Diamonds, BIS Hallmarked 916 Gold."),
        ("return_policy", "100% exchange on gold value at prevailing market rate. Full buyback guarantee on certified diamonds as per company policy."),
        ("custom_orders", "Custom CAD designs, loose CVD diamonds, and bridal orders fulfilled with 3D design preview in 7-10 days.")
    ]
    cursor.executemany("INSERT OR REPLACE INTO store_info (key, value) VALUES (?, ?);", default_info)

    # Seed Default Rates (per gram)
    default_rates = [
        ("gold_24k", "24 Karat (99.9% Pure)", 7850.0, "Today"),
        ("gold_22k", "22 Karat (91.6% Hallmark)", 7200.0, "Today"),
        ("gold_18k", "18 Karat (Diamond Jewellery)", 5890.0, "Today"),
        ("silver_999", "Fine Silver 999", 95.0, "Today")
    ]
    cursor.executemany("INSERT OR REPLACE INTO daily_rates (metal, purity, rate_per_gram, last_updated) VALUES (?, ?, ?, ?);", default_rates)

    # Re-seed inventory with Shashvat Jewels diamond & fine jewelry catalog
    cursor.execute("DELETE FROM products;")
    sample_products = [
        ("1.00 Carat Round Solitaire Diamond Ring (IGI Certified)", "ring", "CVD Diamond & 18K Gold", "18K", 3.8, 10.0, 1, 55000.0, "IGI certified VVS-EF clarity CVD diamond in 18K hallmarked gold."),
        ("2.00 Carat Cushion Cut Diamond Studded Ring", "ring", "Diamond & 18K White Gold", "18K", 4.5, 12.0, 1, 95000.0, "Luxury diamond cocktail ring with international authenticity certificate."),
        ("22K Gold Antique Bridal Peacock Necklace", "necklace", "Gold", "22K", 35.0, 11.0, 1, 285000.0, "Handcrafted temple jewellery bridal necklace with 916 BIS hallmark."),
        ("Tennis Bracelet with 5.00 Carat Lab-Grown Diamonds", "bracelet", "Diamond & 18K Gold", "18K", 14.5, 8.0, 1, 160000.0, "Continuous line of prong-set brilliant cut CVD diamonds in 18K white gold."),
        ("Classic 22K Men's Daily Wear Gold Chain", "chain", "Gold", "22K", 18.0, 8.0, 1, 142000.0, "Heavy-duty hallmarked 916 rope chain for men."),
        ("Certified Loose CVD Diamonds (B2B Bulk Lot)", "loose_diamond", "CVD Diamond", "VVS-EF", 10.0, 0.0, 1, 250000.0, "Calibrated melee and loose parcel diamonds with certificate."),
        ("Traditional 22K Gold Kadas / Bangles (Set of 2)", "bangles", "Gold", "22K", 38.0, 10.0, 1, 305000.0, "Screw-lock antique finish bridal kadas with hallmark stamp."),
        ("Floral Diamond Drop Earrings", "earrings", "Diamond & 18K Gold", "18K", 5.2, 12.0, 1, 68000.0, "Chandelier diamond earrings with IGI certificate.")
    ]
    cursor.executemany("""
    INSERT INTO products (name, category, metal, purity, weight_grams, making_charges_percent, in_stock, estimated_price, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, sample_products)

    conn.commit()
    conn.close()

def get_store_knowledge_summary():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT key, value FROM store_info;")
    info = {row["key"]: row["value"] for row in c.fetchall()}

    c.execute("SELECT metal, purity, rate_per_gram FROM daily_rates;")
    rates = {row["metal"]: f"₹{row['rate_per_gram']}/gm ({row['purity']})" for row in c.fetchall()}
    conn.close()

    summary = f"""Store Name: {info.get('store_name')}
Address & Landmark: {info.get('address')}, {info.get('landmark')}
Timings: {info.get('timings')}
Today's Rates: 24K Gold: {rates.get('gold_24k')}, 22K Gold: {rates.get('gold_22k')}, 18K Gold: {rates.get('gold_18k')}, Silver: {rates.get('silver_999')}
Hallmark & Certification: {info.get('hallmark')}
Exchange & Return Policy: {info.get('return_policy')}
Custom Orders: {info.get('custom_orders')}
Contact / WhatsApp: {info.get('whatsapp')}
Manager Phone for Transfer: {info.get('manager_phone')}
"""
    return summary

def search_products(query_term=""):
    conn = get_connection()
    c = conn.cursor()
    if not query_term:
        c.execute("SELECT name, category, metal, purity, weight_grams, estimated_price, in_stock FROM products LIMIT 10;")
    else:
        term = f"%{query_term.strip()}%"
        c.execute("""
        SELECT name, category, metal, purity, weight_grams, estimated_price, in_stock, description
        FROM products
        WHERE name LIKE ? OR category LIKE ? OR metal LIKE ? OR description LIKE ?
        LIMIT 6;
        """, (term, term, term, term))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def log_inbound_call(caller_phone, language, inquiry_type, caller_query, reply, action="CONTINUE"):
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("""
        INSERT INTO inbound_call_logs (caller_phone, language_detected, inquiry_type, caller_query, receptionist_reply, call_action)
        VALUES (?, ?, ?, ?, ?, ?);
        """, (caller_phone, language, inquiry_type, caller_query, reply, action))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging inbound call: {e}")

def get_recent_inbound_logs(limit=10):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    SELECT id, caller_phone, language_detected, inquiry_type, caller_query, receptionist_reply, call_action, timestamp
    FROM inbound_call_logs
    ORDER BY id DESC LIMIT ?;
    """, (limit,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()
    print("Inbound Jewellery DB Initialized successfully!")
