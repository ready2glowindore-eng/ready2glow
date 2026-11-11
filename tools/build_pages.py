#!/usr/bin/env python3
"""
Build Ready2Glow's SEO service pages from index.html.

index.html is the single source of truth: header, footer, booking modal and
service cards (names, prices, durations, images) are copied from it, so the
service pages always match the home page.

Usage (from the project root):   python3 tools/build_pages.py

Re-run it whenever you change services or prices in index.html.
"""
import html
import json
import os
import re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ready2glow.in/"
TODAY = date.today().isoformat()
E = html.escape

# --------------------------------------------------------------------------
# Page content (edit text here)
# --------------------------------------------------------------------------
PAGES = [
    {
        "cat": "facials",
        "slug": "facial-cleanup-at-home-indore",
        "name": "Facial & Cleanup",
        "title": "Facial & Cleanup at Home in Indore | Ready2Glow",
        "description": "Book a facial or cleanup at home in Indore – fruit facial, gold facial, D-tan and deep-cleansing cleanup by trained beauticians. Book on WhatsApp in a minute.",
        "h1": "Facial & Cleanup at Home in Indore",
        "intro": "Get fresh, glowing skin without leaving your home. Our beauticians bring a complete facial kit to your doorstep anywhere in Indore – from a quick deep-cleansing cleanup to a luxurious gold facial before a function.",
        "guide_title": "Which facial is right for you?",
        "guide": [
            ("Cleanup", "Best as a monthly routine. Removes dirt, oil and dead skin with cleansing, scrub, steam and a mask – ideal for busy schedules."),
            ("Fruit Facial", "Gentle and refreshing, suitable for most skin types. Great when your skin looks dull or tired."),
            ("Gold Facial", "A popular choice 2–3 days before weddings, parties and festivals for a radiant, glowing finish."),
            ("D-Tan Pack", "Helps reduce sun tan on the face and neck – a good add-on after summer or travel."),
        ],
        "steps": ["Skin check and cleansing", "Scrub and steam to open pores", "Massage with facial cream", "Face pack or mask", "Toner and moisturiser to finish"],
        "aftercare": ["Avoid direct sun and heavy makeup for 24 hours.", "Don't use scrubs or face wash with strong actives for 2 days.", "Drink plenty of water and keep your skin moisturised.", "Book your facial 2–3 days before an event, not on the same day."],
        "faqs": [
            ("How often should I get a facial or cleanup?", "A cleanup every 3–4 weeks is ideal for most people. A facial such as fruit or gold facial can be done once a month or before special occasions."),
            ("Is a home facial suitable for sensitive skin?", "Yes. Tell us about sensitivity, allergies or acne in the booking form's additional instructions and our beautician will choose suitable products and skip harsh steps."),
            ("What do I need to arrange at home?", "Just a bed or reclining chair, a pillow and access to water. Our beautician brings the products, towels and disposable items."),
            ("How long does a facial at home take?", "A cleanup takes about 45 minutes and a facial between 60 and 75 minutes, depending on the service you choose."),
        ],
    },
    {
        "cat": "waxing",
        "slug": "waxing-at-home-indore",
        "name": "Waxing",
        "title": "Waxing at Home in Indore – Arms, Legs & Body | Ready2Glow",
        "description": "Hygienic waxing at home in Indore: full arms, full legs, underarms and full body waxing by trained beauticians. Single-use strips and spatulas. Book on WhatsApp.",
        "h1": "Waxing at Home in Indore",
        "intro": "Smooth, long-lasting results in the privacy of your home. Ready2Glow beauticians carry everything needed for clean, comfortable waxing – so you can skip the parlour queue and book a slot that suits you.",
        "guide_title": "Waxing services we offer",
        "guide": [
            ("Full Arms Waxing", "Complete arms from wrist to shoulder for smooth, hair-free skin."),
            ("Full Legs Waxing", "Full legs from ankle to thigh – ideal before holidays and functions."),
            ("Underarms Waxing", "Quick and hygienic, takes about 10 minutes."),
            ("Full Body Waxing", "Head-to-toe waxing in a single appointment for completely smooth skin."),
        ],
        "steps": ["Skin cleansed and prepped with powder", "Wax applied in the direction of hair growth", "Strip removed quickly against hair growth", "Soothing post-wax lotion applied"],
        "aftercare": ["Avoid hot showers, saunas and swimming for 24 hours.", "Skip deodorant and perfume on freshly waxed skin for a few hours.", "Wear loose clothing to reduce friction.", "Exfoliate gently after 2–3 days to prevent ingrown hair."],
        "faqs": [
            ("How long should hair be before waxing?", "About 4–6 mm (roughly 2–3 weeks of growth after shaving) gives the best results."),
            ("Is home waxing hygienic?", "Yes. Our beauticians use fresh strips and spatulas for every customer and never double-dip used spatulas into the wax."),
            ("Does waxing hurt?", "There is brief discomfort, which reduces with regular waxing. Let us know if you have sensitive skin so we can take extra care."),
            ("How long do waxing results last?", "Usually 3–4 weeks, depending on your hair growth."),
        ],
    },
    {
        "cat": "threading",
        "slug": "threading-at-home-indore",
        "name": "Threading",
        "title": "Eyebrow & Face Threading at Home in Indore | Ready2Glow",
        "description": "Eyebrow threading, upper lip and full face threading at home in Indore by experienced beauticians. Neat, precise shaping at your doorstep. Book on WhatsApp.",
        "h1": "Eyebrow & Face Threading at Home in Indore",
        "intro": "Perfectly shaped brows and smooth facial skin without a trip to the parlour. Our beauticians shape your eyebrows to suit your face and remove facial hair quickly and neatly using clean cotton thread.",
        "guide_title": "Threading services",
        "guide": [
            ("Eyebrow Threading", "Clean, defined brows shaped to suit your face – takes about 10 minutes."),
            ("Upper Lip Threading", "Quick and precise upper lip hair removal in about 5 minutes."),
            ("Full Face Threading", "Forehead, upper lip, chin and sides of the face for a smooth, even finish."),
        ],
        "steps": ["Discuss the brow shape you want", "Skin cleaned and lightly powdered", "Hair removed with fresh cotton thread", "Soothing toner or aloe gel applied"],
        "aftercare": ["Avoid makeup on the threaded area for a few hours.", "Skip facials, scrubs and direct sun for 24 hours.", "Apply aloe vera gel if you notice slight redness."],
        "faqs": [
            ("How often should I get my eyebrows threaded?", "Every 2–3 weeks keeps your brows in shape, depending on how fast your hair grows."),
            ("Can I book threading together with other services?", "Yes. Threading is a popular add-on with a cleanup, facial or waxing in the same home appointment."),
            ("Is a new thread used for every customer?", "Yes, a fresh cotton thread is used for every customer."),
        ],
    },
    {
        "cat": "mani-pedi",
        "slug": "manicure-pedicure-at-home-indore",
        "name": "Manicure & Pedicure",
        "title": "Manicure & Pedicure at Home in Indore | Ready2Glow",
        "description": "Relaxing manicure, pedicure and spa pedicure at home in Indore. Nail shaping, cuticle care, scrub, massage and polish by trained beauticians. Book on WhatsApp.",
        "h1": "Manicure & Pedicure at Home in Indore",
        "intro": "Pamper your hands and feet at home. Our manicure and pedicure services include soaking, scrubbing, cuticle care, a relaxing massage and nail polish – all done with sanitised tools at your doorstep in Indore.",
        "guide_title": "Choose your hand & foot care",
        "guide": [
            ("Manicure", "Nail shaping, cuticle care, hand scrub, massage and polish for neat, soft hands."),
            ("Pedicure", "Foot soak, scrub, callus care, massage and polish – great for tired feet."),
            ("Spa Pedicure", "An indulgent pedicure with a mask and longer massage for extra relaxation."),
        ],
        "steps": ["Old polish removed and nails shaped", "Soak in warm water", "Cuticle care and scrub", "Relaxing massage", "Nail polish of your choice"],
        "aftercare": ["Let polish dry fully – avoid water for 30 minutes.", "Moisturise hands and feet daily.", "Wear gloves while washing dishes to protect your nails."],
        "faqs": [
            ("What do I need to arrange for a pedicure at home?", "A chair to sit on and access to warm water. Our beautician brings the tub, tools, products and towels."),
            ("Are the tools sanitised?", "Yes. Metal tools are sanitised before every appointment and disposable items such as files are fresh for each customer."),
            ("How long does a manicure and pedicure take?", "A manicure takes about 40 minutes and a pedicure about 50 minutes. A spa pedicure takes around an hour."),
        ],
    },
    {
        "cat": "hair",
        "slug": "hair-spa-at-home-indore",
        "name": "Hair Care",
        "title": "Hair Spa & Hair Care at Home in Indore | Ready2Glow",
        "description": "Book a hair spa, relaxing head massage or hair cut at home in Indore. Nourishing hair treatments by trained professionals at your doorstep. Book on WhatsApp.",
        "h1": "Hair Spa & Hair Care at Home in Indore",
        "intro": "Soft, shiny, healthy hair without stepping out. Ready2Glow brings deep-conditioning hair spas, stress-relieving head massages and stylish hair cuts to your home anywhere in Indore.",
        "guide_title": "Hair services",
        "guide": [
            ("Hair Spa", "Deep-conditioning treatment with massage and steam for dry, frizzy or damaged hair."),
            ("Head Massage", "Relaxing oil massage that relieves stress and nourishes the scalp."),
            ("Hair Cut", "A trendy cut or simple trim, styled the way you like."),
        ],
        "steps": ["Hair and scalp check", "Shampoo and conditioning", "Hair spa cream and massage", "Steam to help absorption", "Rinse and finish"],
        "aftercare": ["Avoid heat styling for 24 hours after a hair spa.", "Use a mild, sulphate-free shampoo.", "Book a hair spa every 3–4 weeks for best results."],
        "faqs": [
            ("How often should I get a hair spa?", "Once every 3–4 weeks is ideal for most hair types, or more often if your hair is very dry or damaged."),
            ("Do I need to wash my hair before the appointment?", "No. For a hair spa our beautician handles the wash. For a hair cut, clean, dry hair is preferred."),
            ("Can I combine a head massage with other services?", "Yes, a head massage pairs well with a facial or hair spa in the same appointment."),
        ],
    },
    {
        "cat": "makeup",
        "slug": "makeup-artist-at-home-indore",
        "name": "Makeup & Styling",
        "title": "Makeup Artist at Home in Indore | Ready2Glow",
        "description": "Book a makeup artist at home in Indore for party makeup and saree draping. Flawless looks for weddings, functions and festivals at your doorstep. Book on WhatsApp.",
        "h1": "Makeup Artist at Home in Indore",
        "intro": "Look your best for weddings, parties, festivals and functions – without rushing to a salon. Our makeup artists come to your home with professional products and finish with neat saree draping if you need it.",
        "guide_title": "Makeup & styling services",
        "guide": [
            ("Party Makeup", "A complete, long-lasting look for parties, receptions and festivals, matched to your outfit."),
            ("Saree Draping", "Neat, secure draping in your preferred style so you can move comfortably all day."),
        ],
        "steps": ["Discuss your outfit and the look you want", "Skin prep and base", "Eyes, contour and lips", "Setting for long wear", "Saree draping (if booked)"],
        "aftercare": ["Remove makeup gently with a cleanser or micellar water before sleeping.", "Moisturise well after removing makeup.", "For an event, book 2–3 days ahead so we can confirm your preferred time."],
        "faqs": [
            ("How early should I book a makeup artist?", "For weddings and festival dates, book 3–7 days in advance. For other days, 1–2 days' notice is usually enough."),
            ("Do you use my makeup or yours?", "Our artist brings professional products. If you have allergies or prefer your own products, mention it in the booking form."),
            ("Can you do makeup for more than one person?", "Yes. Add the services for each person to your booking and mention the number of people in the additional instructions."),
        ],
    },
]

AREAS = {
    "Central Indore": ["Palasia", "Old Palasia", "New Palasia", "Rajwada", "Sapna Sangeeta", "Tilak Nagar", "Manorama Ganj"],
    "East Indore": ["Vijay Nagar", "Scheme No. 54", "Scheme No. 78", "Nipania", "Khajrana", "Mahalaxmi Nagar", "Bicholi Mardana", "Saket Nagar", "LIG Colony", "MR 10"],
    "West Indore": ["Sudama Nagar", "Annapurna", "Rajendra Nagar", "Bengali Square"],
    "South Indore & AB Road": ["Bhawarkuan", "AB Road", "Rau", "Silicon City"],
}

# Info pages: body is trusted HTML written here. {services_links} is filled in automatically.
INFO_PAGES = [
    {
        "slug": "beauty-packages-indore",
        "name": "Packages & Offers",
        "title": "Beauty Packages at Home in Indore | Ready2Glow",
        "description": "Save with Ready2Glow beauty packages at home in Indore – Glow Essentials, Party Ready, Monthly Pamper and Pre-Bridal Glow. Combine services and book on WhatsApp.",
        "h1": "Beauty Packages & Offers at Home in Indore",
        "intro": "Combine your favourite services into one home appointment and save. Every package is done by a trained Ready2Glow beautician at your doorstep in Indore.",
        "schema_type": "WebPage",
        "cards": "packages",
        "body": """
        <h2 class="h-sm">Why book a package?</h2>
        <ul class="tick-list">
          <li><strong>Better value</strong> – packages cost less than booking each service separately.</li>
          <li><strong>One visit</strong> – everything is done in a single home appointment.</li>
          <li><strong>Made for occasions</strong> – party, pre-bridal and monthly grooming packages cover what you need.</li>
        </ul>
        <h2 class="h-sm">Which package should I choose?</h2>
        <ul class="tick-list">
          <li><strong>Glow Essentials</strong> – a quick monthly refresh: cleanup, threading and arms waxing.</li>
          <li><strong>Party Ready</strong> – gold facial, party makeup and saree draping for functions and festivals.</li>
          <li><strong>Monthly Pamper</strong> – facial, legs waxing, manicure and pedicure for complete self-care.</li>
          <li><strong>Pre-Bridal Glow</strong> – a complete pre-wedding routine; book it 2–3 days before the big day.</li>
        </ul>
        <p>You can also add individual services to any package – see all {services_links}.</p>
""",
    },
    {
        "slug": "areas-we-serve-indore",
        "name": "Areas We Serve",
        "title": "Areas We Serve in Indore | Ready2Glow Home Beauty",
        "description": "Ready2Glow provides beauty parlour services at home across Indore – Vijay Nagar, Palasia, Bhawarkuan, Nipania, Rau, Annapurna, Sudama Nagar and more.",
        "h1": "Home Beauty Services Across Indore",
        "intro": "Looking for a beautician at home near you? Ready2Glow beauticians visit homes across Indore. Here are the localities we regularly serve.",
        "schema_type": "WebPage",
        "body": "{areas_html}" + """
        <h2 class="h-sm">Don’t see your area?</h2>
        <p>We are growing across Indore. Add your locality in the booking form and our team will tell you on WhatsApp if a beautician is available for your area and time slot.</p>
        <h2 class="h-sm">Services available at home</h2>
        <p>All of our {services_links} are available across these areas.</p>
""",
    },
    {
        "slug": "about-us",
        "name": "About Us",
        "title": "About Ready2Glow – Home Beauty Service in Indore",
        "description": "Ready2Glow is a home beauty service in Indore offering salon-quality facials, waxing, threading, mani-pedi, hair care and makeup at your doorstep.",
        "h1": "About Ready2Glow",
        "intro": "Ready2Glow brings salon-quality beauty services to homes across Indore – so you can look and feel your best without travelling or waiting at a parlour.",
        "schema_type": "AboutPage",
        "body": """
        <h2 class="h-sm">What we do</h2>
        <p>We offer {services_links} at home. You choose the services you want, pick a date and time, and a trained beautician arrives at your door with everything needed for the appointment.</p>
        <h2 class="h-sm">Our promise</h2>
        <ul class="tick-list">
          <li><strong>Hygiene first</strong> – sanitised tools and single-use items such as wax strips, spatulas and threads for every customer.</li>
          <li><strong>Trained, verified beauticians</strong> – our beauticians are ID-verified and experienced in skin, hair and makeup services.</li>
          <li><strong>Clear pricing</strong> – prices are listed on our website, and your estimated total is shown before you book.</li>
          <li><strong>Your time, your place</strong> – appointments from 8 AM to 8 PM, all seven days.</li>
        </ul>
        <h2 class="h-sm">How booking works</h2>
        <ol class="step-list">
          <li>Add the services you want to your booking.</li>
          <li>Enter your name, phone, area and preferred slot.</li>
          <li>WhatsApp opens with your booking request – just press Send.</li>
          <li>Our team replies to confirm your beautician and time.</li>
        </ol>
""",
    },
    {
        "slug": "contact-us",
        "name": "Contact Us",
        "title": "Contact Ready2Glow – Book Home Beauty Services in Indore",
        "description": "Contact Ready2Glow on WhatsApp or call +91 88203 69048 to book home beauty services in Indore. Open 8 AM – 8 PM, all days.",
        "h1": "Contact Ready2Glow",
        "intro": "Questions or bookings – we’re happy to help. The fastest way to reach us is WhatsApp.",
        "schema_type": "ContactPage",
        "body": """
        <div class="contact-cards">
          <a class="contact-card" href="https://wa.me/918820369048" target="_blank" rel="noopener"><span class="contact-ico" aria-hidden="true">💬</span><strong>WhatsApp</strong><span>+91 88203 69048</span></a>
          <a class="contact-card" href="tel:+918820369048"><span class="contact-ico" aria-hidden="true">📞</span><strong>Call</strong><span>+91 88203 69048</span></a>
          <a class="contact-card" href="https://www.instagram.com/ready2gloww/" target="_blank" rel="noopener"><span class="contact-ico" aria-hidden="true">📸</span><strong>Instagram</strong><span>@ready2gloww</span></a>
        </div>
        <h2 class="h-sm">Timings</h2>
        <p>8:00 AM – 8:00 PM, Monday to Sunday.</p>
        <h2 class="h-sm">Service area</h2>
        <p>We provide home beauty services across Indore, Madhya Pradesh. <a href="../areas-we-serve-indore/">See the areas we serve</a>.</p>
        <h2 class="h-sm">Book an appointment</h2>
        <p>Choose from our {services_links}, then tap <strong>Book Now</strong> to send your booking request on WhatsApp.</p>
        <p><button type="button" class="btn-wa js-open-booking">Book Now on WhatsApp</button></p>
""",
    },
    {
        "slug": "privacy-policy",
        "name": "Privacy Policy",
        "title": "Privacy Policy | Ready2Glow",
        "description": "How Ready2Glow handles the information you share when booking home beauty services in Indore.",
        "h1": "Privacy Policy",
        "intro": "This page explains what information we use when you book with Ready2Glow and how we handle it.",
        "schema_type": "WebPage",
        "body": """
        <p><em>Last updated: {today_long}</em></p>
        <h2 class="h-sm">Information you share</h2>
        <p>When you book, the booking form asks for your name, mobile number, area in Indore, preferred date and time, and any instructions you choose to add. This information is <strong>not sent to or stored on our website’s servers</strong>. It is placed into a WhatsApp message on your own device, and it is only shared with us if you choose to press Send in WhatsApp.</p>
        <h2 class="h-sm">How we use it</h2>
        <p>We use the details in your WhatsApp message only to confirm and provide your appointment, contact you about it, and reply to your questions. We do not sell or rent your information.</p>
        <h2 class="h-sm">WhatsApp</h2>
        <p>Messages you send us are delivered through WhatsApp, which is operated by WhatsApp LLC under its own privacy policy and terms.</p>
        <h2 class="h-sm">Information stored in your browser</h2>
        <p>To keep your selected services while you browse, the website stores the list of selected services in your browser’s local storage. It does not include your name or phone number, and you can clear it at any time by removing the services or clearing your browser data.</p>
        <h2 class="h-sm">Third-party services</h2>
        <p>The website loads fonts from Google Fonts, which may receive your IP address as part of delivering the font files. The site is hosted on GitHub Pages.</p>
        <h2 class="h-sm">Contact</h2>
        <p>For questions about this policy or to ask us to delete your booking messages, contact us on WhatsApp at +91 88203 69048.</p>
""",
    },
]

ALL_SLUGS = [p["slug"] for p in PAGES] + [p["slug"] for p in INFO_PAGES]

# --------------------------------------------------------------------------
# Extract shared parts from index.html
# --------------------------------------------------------------------------
index = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

def between(start, end, text=index, include_end=True):
    i = text.index(start)
    j = text.index(end, i) + (len(end) if include_end else 0)
    return text[i:j]

header = between('  <header class="site-header">', "  </header>")
tail = between("  <!-- ============ FOOTER ============ -->", "</body>", include_end=False)
head_assets = between('  <link rel="icon" href="favicon.ico"', '  <link rel="stylesheet" href="css/style.css">')

# Service cards, by category, from the main services grid
grid = between('<div class="grid js-services-grid">', '<div class="center"><button type="button" class="btn-ghost js-view-all"')
cards = {}
for m in re.finditer(r'        <article class="svc[^"]*"[^>]*data-cat="([^"]+)">.*?</article>', grid, re.S):
    cards.setdefault(m.group(1), []).append(m.group(0).replace("svc is-extra", "svc"))
deals = between('<div class="grid grid-deals">', "</section>")
cards["packages"] = re.findall(r'        <article class="svc deal"[^>]*>.*?</article>', deals, re.S)
card_data = {}
for cat, items in cards.items():
    card_data[cat] = [{
        "name": html.unescape(re.search(r'data-name="([^"]+)"', c).group(1)),
        "price": int(re.search(r'data-price="(\d+)"', c).group(1)),
        "duration": (re.search(r'data-duration="([^"]+)"', c) or [None, ""])[1],
        "desc": html.unescape(re.search(r'<p class="svc-desc">(.*?)</p>', c).group(1)),
    } for c in items]

def relink(block):
    """Make shared HTML work from a page one folder deep."""
    block = re.sub(r'(src|href)="(images/|css/|js/|favicon|apple-touch)', r'\1="../\2', block)
    block = block.replace('href="#top"', 'href="../"').replace('href="./"', 'href="../"').replace('href="./#', 'href="../#')
    block = re.sub(r'href="#(services|deals|popular|faq|contact|book|about)"', r'href="../#\1"', block)
    for slug in ALL_SLUGS:  # menu + footer page links
        block = block.replace(f'href="{slug}/"', f'href="../{slug}/"')
    return block

page_header = relink(header)
# The booking modal's "+ Add more services" link should stay on the current page
page_tail = relink(tail).replace('href="../#services" class="link-add js-add-more"', 'href="#services" class="link-add js-add-more"')
page_head_assets = relink(head_assets)

def rupee(n):
    return "₹" + f"{n:,}"

def ld(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2).replace("</", "<\\/")

# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------
def render(p):
    cat, url = p["cat"], SITE + p["slug"] + "/"
    items = card_data[cat]
    start = min(i["price"] for i in items)
    others = [o for o in PAGES if o is not p]

    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": p["h1"], "item": url}]}
    service = {"@context": "https://schema.org", "@type": "Service", "name": p["h1"], "serviceType": p["name"],
               "description": p["description"], "url": url,
               "provider": {"@type": "BeautySalon", "@id": SITE + "#business", "name": "Ready2Glow", "url": SITE, "telephone": "+91-8820369048"},
               "areaServed": {"@type": "City", "name": "Indore"},
               "hasOfferCatalog": {"@type": "OfferCatalog", "name": p["name"] + " services", "itemListElement": [
                   {"@type": "Offer", "price": str(i["price"]), "priceCurrency": "INR",
                    "itemOffered": {"@type": "Service", "name": i["name"], "description": i["desc"]}} for i in items]}}
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faqs"]]}

    rows = "\n".join(f'              <tr><td>{E(i["name"])}</td><td>{E(i["duration"] or "–")}</td><td class="num">{rupee(i["price"])}</td></tr>' for i in items)
    guide = "\n".join(f'            <li><strong>{E(t)}</strong> – {E(d)}</li>' for t, d in p["guide"])
    steps = "\n".join(f'            <li>{E(s)}</li>' for s in p["steps"])
    after = "\n".join(f'            <li>{E(s)}</li>' for s in p["aftercare"])
    faqs = "\n".join(f'''        <details class="faq-item">
          <summary>{E(q)}</summary>
          <p>{E(a)}</p>
        </details>''' for q, a in p["faqs"])
    other_links = "\n".join(f'          <li><a href="../{o["slug"]}/">{E(o["h1"].replace(" in Indore", ""))}</a></li>' for o in others)
    card_html = "\n".join(relink(c) for c in cards[cat])

    return f'''<!doctype html>
<html lang="en-IN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{E(p["title"])}</title>
  <meta name="description" content="{E(p["description"])}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#e6007e">
  <meta name="geo.region" content="IN-MP">
  <meta name="geo.placename" content="Indore">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Ready2Glow">
  <meta property="og:title" content="{E(p["title"])}">
  <meta property="og:description" content="{E(p["description"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}images/cat-{cat}.jpg">
  <meta property="og:locale" content="en_IN">
  <meta name="twitter:card" content="summary_large_image">
{page_head_assets}

  <script type="application/ld+json">
{ld(breadcrumb)}
  </script>
  <script type="application/ld+json">
{ld(service)}
  </script>
  <script type="application/ld+json">
{ld(faq)}
  </script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

{page_header}

  <main id="main">
    <section class="page-hero" aria-labelledby="page-title">
      <div class="container page-hero-inner">
        <div class="page-hero-copy">
          <nav class="breadcrumb" aria-label="Breadcrumb"><a href="../">Home</a> <span aria-hidden="true">›</span> <span aria-current="page">{E(p["name"])}</span></nav>
          <h1 id="page-title">{E(p["h1"])}</h1>
          <p class="page-hero-sub">{E(p["intro"])}</p>
          <p class="page-hero-from">Starting at <b>{rupee(start)}</b></p>
          <div class="page-hero-cta">
            <a class="btn-yellow" href="#services">Choose Services</a>
          </div>
        </div>
        <div class="page-hero-art"><img src="../images/cat-{cat}.jpg" alt="{E(p["h1"])} – Ready2Glow" width="300" height="420" fetchpriority="high"></div>
      </div>
    </section>

    <section class="section" id="services" aria-labelledby="svc-title">
      <div class="container">
        <header class="sec-head">
          <p class="sec-eyebrow">Book at Home</p>
          <h2 id="svc-title">{E(p["name"])} Services &amp; Prices</h2>
        </header>
        <div class="grid grid-page">
{card_html}
        </div>
      </div>
    </section>

    <section class="section band-soft" aria-labelledby="guide-title">
      <div class="container two-col">
        <div class="prose">
          <h2 id="guide-title" class="h-sm">{E(p["guide_title"])}</h2>
          <ul class="tick-list">
{guide}
          </ul>
          <h2 class="h-sm">Price List</h2>
          <table class="price-table">
            <thead><tr><th scope="col">Service</th><th scope="col">Duration</th><th scope="col" class="num">Price</th></tr></thead>
            <tbody>
{rows}
            </tbody>
          </table>
          <p class="fine-print left">Prices are estimates. The final price is confirmed on WhatsApp.</p>
        </div>
        <div class="prose">
          <h2 class="h-sm">How It Works at Home</h2>
          <ol class="step-list">
{steps}
          </ol>
          <h2 class="h-sm">Aftercare Tips</h2>
          <ul class="tick-list">
{after}
          </ul>
        </div>
      </div>
    </section>

    <section class="section" id="book" aria-labelledby="book-title">
      <div class="container book-wrap book-wrap-page">
        <div class="book-main">
          <h2 id="book-title">Book {E(p["name"])} at Home</h2>
          <p class="book-sub">Add services above, then send your booking request on WhatsApp. Our team confirms your beautician and time.</p>
          <div class="book-summary">
            <div class="js-summary-list" data-variant="panel"></div>
            <div class="summary-total">Estimated Total: <strong class="js-total">₹0</strong></div>
          </div>
          <button type="button" class="btn-wa js-open-booking">Book Now on WhatsApp</button>
        </div>
        <ul class="trust">
          <li><div><strong>Verified Beauticians</strong><span>Every Ready2Glow beautician is ID-verified and background-checked.</span></div><span class="trust-ico" aria-hidden="true">🛡️</span></li>
          <li><div><strong>Hygienic Kits</strong><span>Sanitised tools and single-use items at every appointment.</span></div><span class="trust-ico" aria-hidden="true">🧴</span></li>
          <li><div><strong>All Over Indore</strong><span>Vijay Nagar, Palasia, Bhawarkuan, Nipania, Rau and more.</span></div><span class="trust-ico" aria-hidden="true">📍</span></li>
        </ul>
      </div>
    </section>

    <section class="section band-soft" id="faq" aria-labelledby="faq-title">
      <div class="container two-col">
        <div>
          <h2 id="faq-title" class="h-sm">{E(p["name"])} at Home – FAQs</h2>
{faqs}
        </div>
        <div>
          <h2 class="h-sm">Other Services at Home</h2>
          <ul class="other-links">
{other_links}
          </ul>
          <p class="areas">Ready2Glow serves homes across Indore. <a href="../#faq">See all areas we serve</a>.</p>
        </div>
      </div>
    </section>
  </main>

{page_tail}</body>
</html>
'''

def services_links_html():
    links = [f'<a href="../{p["slug"]}/">{E(p["name"].lower())}</a>' for p in PAGES]
    return "services – " + ", ".join(links[:-1]) + " and " + links[-1]

def areas_html():
    out = []
    for region, names in AREAS.items():
        items = "".join(f"<li>{E(n)}</li>" for n in names)
        out.append(f'        <h2 class="h-sm">{E(region)}</h2>\n        <ul class="area-list">{items}</ul>')
    return "\n".join(out)

def render_info(p):
    url = SITE + p["slug"] + "/"
    today_long = date.today().strftime("%-d %B %Y")
    body = (p["body"].replace("{areas_html}", areas_html())
            .replace("{services_links}", services_links_html())
            .replace("{today_long}", today_long))
    breadcrumb = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE},
        {"@type": "ListItem", "position": 2, "name": p["name"], "item": url}]}
    page_ld = {"@context": "https://schema.org", "@type": p["schema_type"], "name": p["h1"], "url": url,
               "description": p["description"],
               "about": {"@type": "BeautySalon", "@id": SITE + "#business", "name": "Ready2Glow"}}
    if p["slug"] == "areas-we-serve-indore":
        page_ld["about"]["areaServed"] = [{"@type": "Place", "name": n + ", Indore"} for ns in AREAS.values() for n in ns]
    cards_block = ""
    if p.get("cards"):
        card_html = "\n".join(relink(c) for c in cards[p["cards"]])
        cards_block = f'''
    <section class="section" id="services" aria-label="{E(p["name"])}">
      <div class="container">
        <div class="grid grid-deals">
{card_html}
        </div>
      </div>
    </section>
'''
    robots = "noindex, follow" if p["slug"] == "privacy-policy" else "index, follow, max-image-preview:large"
    return f'''<!doctype html>
<html lang="en-IN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{E(p["title"])}</title>
  <meta name="description" content="{E(p["description"])}">
  <meta name="robots" content="{robots}">
  <link rel="canonical" href="{url}">
  <meta name="theme-color" content="#e6007e">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Ready2Glow">
  <meta property="og:title" content="{E(p["title"])}">
  <meta property="og:description" content="{E(p["description"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}images/og-image.jpg">
  <meta property="og:locale" content="en_IN">
  <meta name="twitter:card" content="summary_large_image">
{page_head_assets}

  <script type="application/ld+json">
{ld(breadcrumb)}
  </script>
  <script type="application/ld+json">
{ld(page_ld)}
  </script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>

{page_header}

  <main id="main">
    <section class="page-hero page-hero-slim" aria-labelledby="page-title">
      <div class="container">
        <nav class="breadcrumb" aria-label="Breadcrumb"><a href="../">Home</a> <span aria-hidden="true">›</span> <span aria-current="page">{E(p["name"])}</span></nav>
        <h1 id="page-title">{E(p["h1"])}</h1>
        <p class="page-hero-sub">{E(p["intro"])}</p>
      </div>
    </section>
{cards_block}
    <section class="section">
      <div class="container prose">
{body}
      </div>
    </section>
  </main>

{page_tail}</body>
</html>
'''

def build_404():
    return f'''<!doctype html>
<html lang="en-IN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Page Not Found | Ready2Glow</title>
  <meta name="robots" content="noindex">
  <base href="/">
{head_assets}
</head>
<body>
{header}
  <main id="main" class="section">
    <div class="container prose center-text">
      <h1 class="h-sm">Sorry, this page doesn’t exist</h1>
      <p>The page you’re looking for may have moved. Explore our home beauty services in Indore instead:</p>
      <ul class="other-links">
{chr(10).join(f'        <li><a href="{p["slug"]}/">{E(p["h1"])}</a></li>' for p in PAGES)}
      </ul>
      <p><a class="btn-ghost" href="./">Go to Home</a></p>
    </div>
  </main>
{tail}</body>
</html>
'''

def build_sitemap():
    urls = ([(SITE, "1.0")] + [(SITE + p["slug"] + "/", "0.8") for p in PAGES]
            + [(SITE + p["slug"] + "/", "0.6") for p in INFO_PAGES if p["slug"] != "privacy-policy"])
    body = "\n".join(f'''  <url>
    <loc>{u}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>{pr}</priority>
  </url>''' for u, pr in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n'

if __name__ == "__main__":
    for p in PAGES:
        d = os.path.join(ROOT, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(render(p))
        print("built", p["slug"] + "/", f'({len(card_data[p["cat"]])} services)')
    for p in INFO_PAGES:
        d = os.path.join(ROOT, p["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(render_info(p))
        print("built", p["slug"] + "/")
    open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(build_404())
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(build_sitemap())
    print("built 404.html, sitemap.xml")
