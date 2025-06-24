# http://www.amazon.com/dp/ASIN/ref=nosim?tag=YOURASSOCIATEID
# # https://www.amazon.com/Baby-411-Clear-Answers-Advice/dp/1889392596?&linkCode=ll1&tag=nobsmed07-20&linkId=bb69dd47e174c52d7c8ecffbd7c545a0&language=en_US&ref_=as_li_ss_tl
# MY ASSOCIATE ID: nobsmed07-20
from pydantic import BaseModel


class HealthHackProduct(BaseModel):
    personal_context: str
    health_hack: str
    health_disorder: str
    intended_outcomes: str
    experienced_outcomes: str
    mechanism: str
    dosage: str
    product_title: str
    product_url: str


class InfantProduct(BaseModel):
    product_url: str | None = None
    name: str | None = None
    title: str | None = None  # For books
    age_range: str | None = None
    material: str | None = None
    comfort_support: str | None = None
    cleaning: str | None = None
    cleaning_effectiveness: str | None = None  # For bottle cleaners
    storage: str | None = None
    safety: str | None = None
    price_range: str
    reference_url: str | None = None
    amazon_url: str | None = None
    biggest_negative: str
    biggest_positive: str

    # Additional fields for different product types
    fragrance: str | None = None  # For detergents
    ease_of_use: str | None = None  # For bottle products
    author: str | None = None  # For books
    content_quality: str | None = None  # For books
    ease_of_understanding: str | None = None  # For books
    evidence_based: str | None = None  # For books
    sanitization: str | None = None  # For sanitizers
    drying_effectiveness: str | None = None  # For dryers
    comfort: str | None = None  # For high chairs
    adjustability: str | None = None  # For high chairs
    material_safety: str | None = None  # For playmats
    portability: str | None = None  # For playmats
    ease_of_install: str | None = None  # For car seats
    weight: str | None = None  # For car seats
    materials: str | None = None  # For bassinets (alternative to material)
    purpose: str | None = None  # For healing products
    effectiveness: str | None = None  # For healing products

    @property
    def display_name(self) -> str:
        """Return the appropriate name/title for display"""
        return self.name or self.title or "Unknown Product"


data = []
data.append(
    HealthHackProduct(
        product_url="https://amzn.to/4ehqesv",
        product_title="J Mac Botanicals, Organic Red Raspberry Leaf, Herbal Tea (16 Ounce Bag 200+ Cups) Cut & Sifted Dried Leaf",
        personal_context="Third-trimester pregnancy",
        health_hack="Raspberry leaf tea",
        health_disorder="Long labor",
        intended_outcomes="Shorter labor, easier delivery",
        experienced_outcomes="Second stage of labor was 9.6 minutes shorter on average, reduced need for forceps by 11.1%",
        mechanism="Raspberry leaf tea is believed to tone the uterine muscles, potentially leading to more effective contractions during labor.",
        dosage="2.4 grams per day (2-4 cups of tea, depending on strength)",
    )
)
data.append(
    HealthHackProduct(
        product_url="https://amzn.to/409hMGb",
        product_title="Terrasoul Superfoods Organic Medjool Dates, 2 Lbs - Soft Chewy Texture | Sweet Caramel Flavor | Farm Fresh",
        personal_context="Third-trimester pregnancy",
        health_hack="Date Fruit",
        health_disorder="Long labor",
        intended_outcomes="Shorter labor, easier delivery",
        experienced_outcomes="First stage cervical dilation was 3.5 cm vs. 2 cm in the non-date group; spontaneous labor in 96% of date consumers vs. 79% in non-date group, duration of first stage was 8.5 hours vs. 15 hours, 25% more intact membranes",
        mechanism="chemical binding that effects oxytocin receptors, leading to more effective contractions",
        dosage="4 dates per day (about 70 grams)",
    )
)

infant_bath_tubs = [
    {
        "product_url": "https://amzn.to/4npcr7B",
        "name": "Skip Hop Moby Smart Sling 3‑Stage",
        "age_range": "0–6 mo (up to 20 lb)",
        "material": "BPA- & PVC-free; PP & polyester sling",
        "comfort_support": "Adjustable mesh sling for newborns and infants",
        "cleaning": "Machine-washable sling; easy to rinse tub",
        "storage": "Bulky but sling hangs to dry",
        "safety": "Non-slip interior; sling anchors can be hard to remove",
        "price_range": "$40",
        "reference_url": "https://www.babylist.com/gp/skip-hop-skip-hop-moby-3-stage-bath-gift-set/28493/1308811",
        "amazon_url": "https://www.amazon.com/Skip-Hop-Moby-Smart-Sling/dp/B07FK7BG98/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Bulky and requires ample bathroom space; sling anchors can be difficult to remove.",
        "biggest_positive": "Versatile 3-stage design that grows with baby; adjustable sling offers excellent newborn support.",
    },
    {
        # https://amzn.to/3FVGZgm
        "product_url": "https://amzn.to/3FVGZgm",
        "name": "Angelcare Soft‑Touch Bath Support",
        "age_range": "0–6 mo (up to 20 lb)",
        "material": "Mesh with TPE/PP plastic; BPA-, PVC-, latex-, phthalate-free",
        "comfort_support": "Ergonomic cradle for upright newborn support",
        "cleaning": "Fast-drying mesh; hang to dry",
        "storage": "Lightweight and compact; hangs for storage",
        "safety": "Non-slip design; mold-resistant",
        "price_range": "$25–35",
        "reference_url": "https://www.motherandbaby.com/reviews/bathtime-products/angelcare-soft-touch-baby-bath-support/",
        "amazon_url": "https://www.amazon.com/Angelcare-Baby-Bath-Support-Grey/dp/B01M6YVW7B/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Needs to be used inside a larger tub or sink; not a standalone tub.",
        "biggest_positive": "Lightweight, hygienic design that dries quickly to prevent mold; very easy to store.",
    },
    {
        # https://amzn.to/4lkvBcL
        "product_url": "https://amzn.to/4lkvBcL",
        "name": "Baby Delight Cushy Nest Cloud",
        "age_range": "0–6 mo (up to ~20 lb)",
        "material": "GOTS organic cotton on rust-free frame",
        "comfort_support": "Soft, snug cushion for cozy fit",
        "cleaning": "Removable, machine-washable pad",
        "storage": "Folds flat, compact for storage",
        "safety": "Secure fit; monitor to avoid sliding",
        "price_range": "$40–50",
        "reference_url": "https://www.babydelight.com/products/cushy-nest-cloud-premium-infant-bather-grey-white",
        "amazon_url": "https://www.amazon.com/Baby-Delight-Premium-Organic-Comfortable/dp/B0CSMDJ636/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Cushion takes time to dry; not a standalone tub and requires a larger tub or sink.",
        "biggest_positive": "Organic cotton cushion offers superior softness and comfort for newborns.",
    },
    {
        # https://amzn.to/45FNNJu
        "product_url": "https://amzn.to/45FNNJu",
        "name": "Puj Flyte Compact Infant Bath",
        "age_range": "0–2 mo (~13 lb), some up to ~7 mo",
        "material": "Closed-cell foam; BPA- & PVC-free, mold-resistant",
        "comfort_support": "Cradle-style sink support",
        "cleaning": "Wipes clean; fast-drying foam",
        "storage": "Ultra-compact; great for travel",
        "safety": "Watch weight/length limits; fits sinks only",
        "price_range": "$35",
        "reference_url": "https://www.pnmag.com/pregnancy/pregnancy-gear/gear-reviews/puj-flyte/",
        "amazon_url": "https://www.amazon.com/Puj-Flyte-Compact-Infant-Bathtub/dp/B008PZ9VXY/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Very limited use time—outgrown quickly, typically by 2–3 months.",
        "biggest_positive": "Ultra-compact and travel-friendly design; perfect for small spaces and sink use.",
    },
]

infant_laundry_detergents = [
    {
        # https://amzn.to/40kdY4E
        "product_url": "https://amzn.to/40kdY4E",
        "name": "Dreft Stage 1: Newborn Liquid Laundry Detergent",
        "safety": "Hypoallergenic, pediatrician-recommended, dye- and phosphate-free",
        "fragrance": "Mild scent, designed specifically for newborns",
        "cleaning": "Effective on baby stains; gentle formula",
        "ease_of_use": "Liquid form, easy to measure and use",
        "price_range": "$12–15 for 28 oz",
        "reference_url": "https://www.babylist.com/hello-baby/best-baby-laundry-detergent",
        "amazon_url": "https://www.amazon.com/Dreft-Stage-Newborn-Liquid-Detergent/dp/B004HXI3Y0/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Some parents report residue build-up if overdosed or not rinsed well",
        "biggest_positive": "Trusted brand with long-standing pediatrician recommendations and gentle cleaning",
    },
    {
        # Babyganics 3X Baby Laundry Detergent
        # https://amzn.to/44lhkWw
        "product_url": "https://amzn.to/44lhkWw",
        "name": "Babyganics 3X Baby Laundry Detergent",
        "safety": "Plant-based, hypoallergenic, free of sulfates, dyes, and phthalates",
        "fragrance": "Fragrance-free and dye-free version available",
        "cleaning": "Strong cleaning power on tough stains while gentle on fabrics",
        "ease_of_use": "Concentrated liquid, less product per load",
        "price_range": "$15–18 for 50 oz",
        "reference_url": "https://www.consumerreports.org/laundry-detergents/best-laundry-detergents-for-baby-clothes/",
        "amazon_url": "https://www.amazon.com/Babyganics-Laundry-Detergent-Concentrated-Fragrance/dp/B07BHVK34S/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Higher price point compared to other baby detergents",
        "biggest_positive": "Excellent stain removal with natural ingredients, suitable for sensitive skin",
    },
    {
        # https://amzn.to/4ei9KQZ
        "product_url": "https://amzn.to/4ei9KQZ",
        "name": "Seventh Generation Free & Clear Baby Laundry Detergent",
        "safety": "EPA Safer Choice certified, free of dyes and fragrances",
        "fragrance": "Unscented",
        "cleaning": "Good stain removal, eco-friendly and biodegradable",
        "ease_of_use": "Liquid form, compatible with all machines including HE",
        "price_range": "$12–14 for 50 oz",
        "reference_url": "https://www.writecutter.com/best-baby-laundry-detergent/",
        "amazon_url": "https://www.amazon.com/Seventh-Generation-Laundry-Detergent-Fragrance/dp/B07P86GPKD/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Some users note less effectiveness on very tough stains",
        "biggest_positive": "Highly eco-friendly and non-toxic formula, great for sensitive baby skin",
    },
    {
        # Molly’s Suds Laundry Powder
        # https://amzn.to/46birdL
        "product_url": "https://amzn.to/46birdL",
        "name": "Molly’s Suds Laundry Powder",
        "safety": "100% plant-based, non-toxic, fragrance-free, safe for sensitive skin",
        "fragrance": "Fragrance-free",
        "cleaning": "Powerful stain-fighting even without harsh chemicals",
        "ease_of_use": "Powder form, easy to store and measure",
        "price_range": "$16–20 for 25 oz",
        "reference_url": "https://www.babylist.com/hello-baby/best-baby-laundry-detergent",
        "amazon_url": "https://www.amazon.com/Mollys-Suds-Laundry-Powder-Fragrance/dp/B00MDWI8RM/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Powder form may not dissolve well in cold water",
        "biggest_positive": "Very natural and safe; excellent for eczema-prone skin",
    },
]

infant_care_books = [
    {
        # https://amzn.to/45Dn4gD
        "product_url": "https://amzn.to/45Dn4gD",
        "title": "What to Expect the First Year",
        "author": "Heidi Murkoff",
        "content_quality": "Comprehensive, covers all aspects of infant care month-by-month",
        "ease_of_understanding": "Written in accessible, parent-friendly language",
        "evidence_based": "Mostly evidence-informed with practical tips",
        "price_range": "$15–20 paperback",
        "reference_url": "https://www.babylist.com/hello-baby/best-baby-books",
        "amazon_url": "https://www.amazon.com/What-Expect-First-Heidi-Murkoff/dp/0761187480/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Some readers find it overly detailed and lengthy",
        "biggest_positive": "Great for new parents wanting a detailed month-to-month guide",
    },
    {
        # https://amzn.to/469uIzk
        "product_url": "https://amzn.to/469uIzk",
        "title": "Caring for Your Baby and Young Child, 7th Edition",
        "author": "American Academy of Pediatrics",
        "content_quality": "Highly authoritative, medically reviewed, covers health and safety extensively",
        "ease_of_understanding": "Clear but more technical language, reference style",
        "evidence_based": "Strongly evidence-based, updated regularly with latest guidelines",
        "price_range": "$20–30 paperback",
        "reference_url": "https://www.healthychildren.org/English/ages-stages/baby/Pages/default.aspx",
        "amazon_url": "https://www.amazon.com/Caring-Your-Baby-Young-Child/dp/1610022870/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Some parents find it less approachable and more like a medical manual",
        "biggest_positive": "Trusted source for accurate and current infant health guidance",
    },
    {
        # https://amzn.to/45zctTO
        "product_url": "https://amzn.to/45zctTO",
        "title": "The Happiest Baby on the Block",
        "author": "Harvey Karp, M.D.",
        "content_quality": "Focuses on soothing techniques to reduce crying and improve sleep",
        "ease_of_understanding": "Engaging and easy to read with practical advice",
        "evidence_based": "Backed by research on infant calming reflexes",
        "price_range": "$12–18 paperback",
        "reference_url": "https://www.babylist.com/hello-baby/best-baby-sleep-books",
        "amazon_url": "https://www.amazon.com/Happiest-Baby-Block-Third-Soothing/dp/055338146X/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Narrow focus on soothing; less on other care aspects",
        "biggest_positive": "Highly effective, widely praised for improving infant sleep and reducing fussiness",
    },
    {
        # https://amzn.to/4k7vlNq
        "product_url": "https://amzn.to/4k7vlNq",
        "title": "Baby 411: Clear Answers & Smart Advice For Your Baby's First Year",
        "author": "Ari Brown, M.D., and Denise Fields",
        "content_quality": "Practical, question-and-answer format covering broad topics",
        "ease_of_understanding": "Very accessible with concise explanations",
        "evidence_based": "Well-researched and medically reviewed",
        "price_range": "$15–20 paperback",
        "reference_url": "https://www.whattoexpect.com/baby/baby-books/",
        "amazon_url": "https://www.amazon.com/Baby-411-Clear-Answers-Smart/dp/0761182902/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Format may feel fragmented for some readers",
        "biggest_positive": "Great quick-reference guide that’s easy to navigate",
    },
]

bottle_cleaners = [
    {
        "product_url": "https://www.amazon.com/Dr-Browns-Bottle-Brush/dp/B00124N9HY/ref=nosim?tag=nobsmed07-20",
        "name": "Dr. Brown’s Baby Bottle Brush",
        "cleaning_effectiveness": "Soft, dense bristles clean bottles thoroughly including hard-to-reach areas",
        "safety": "BPA-free materials, gentle on baby bottles",
        "ease_of_use": "Ergonomic handle, includes nipple cleaner tip",
        "price_range": "$6–8",
        "reference_url": "https://www.babylist.com/hello-baby/best-bottle-brush",
        "amazon_url": "https://www.amazon.com/Dr-Browns-Bottle-Brush/dp/B00124N9HY/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Some users report bristles wearing out over time",
        "biggest_positive": "Effective and affordable; trusted brand with great cleaning reach",
    },
    {
        "product_url": "https://www.amazon.com/Munchkin-Bristle-Bottle-Brush/dp/B00I2SK0OS/ref=nosim?tag=nobsmed07-20",
        "name": "Munchkin Bristle Bottle Brush",
        "cleaning_effectiveness": "Firm bristles for deep cleaning, angled for easy access",
        "safety": "BPA-free materials, non-toxic",
        "ease_of_use": "Comfort grip handle, includes nipple brush",
        "price_range": "$7–10",
        "reference_url": "https://www.whattoexpect.com/baby-products/munchkin-bottle-brush-review/",
        "amazon_url": "https://www.amazon.com/Munchkin-Bristle-Bottle-Brush/dp/B00I2SK0OS/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Handle can be slippery when wet",
        "biggest_positive": "Good cleaning power with ergonomic design",
    },
    {
        "product_url": "https://www.amazon.com/OXO-Tot-Bottle-Brush-Nipple/dp/B00HY46DXQ/ref=nosim?tag=nobsmed07-20",
        "name": "OXO Tot Bottle Brush with Nipple Cleaner",
        "cleaning_effectiveness": "Soft bristles with flexible head for thorough cleaning",
        "safety": "BPA-free, phthalate-free",
        "ease_of_use": "Comfortable non-slip handle, includes silicone nipple cleaner",
        "price_range": "$12–15",
        "reference_url": "https://www.consumerreports.org/baby-products/bottle-brushes/",
        "amazon_url": "https://www.amazon.com/OXO-Tot-Bottle-Brush-Nipple/dp/B00HY46DXQ/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Pricier than basic brushes",
        "biggest_positive": "High-quality, versatile brush with excellent cleaning reach",
    },
    {
        "product_url": "https://www.amazon.com/First-Years-Quick-Clean-Bottle/dp/B007TV5E0K/ref=nosim?tag=nobsmed07-20",
        "name": "The First Years Quick Clean Bottle Brush",
        "cleaning_effectiveness": "Soft bristles with integrated nipple cleaner; cleans quickly",
        "safety": "BPA-free materials",
        "ease_of_use": "Compact, easy to store, ergonomic handle",
        "price_range": "$6–9",
        "reference_url": "https://www.babygearlab.com/reviews/feeding/bottle-brush",
        "amazon_url": "https://www.amazon.com/First-Years-Quick-Clean-Bottle/dp/B007TV5E0K/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Brush head may wear out faster",
        "biggest_positive": "Affordable and effective for everyday use",
    },
]

bottle_sanitizers = [
    {
        "product_url": "https://www.amazon.com/Baby-Brezza-One-Step-Sterilizer/dp/B071R1NQ23/ref=nosim?tag=nobsmed07-20",
        "name": "Baby Brezza One Step Sterilizer and Dryer",
        "sanitization": "Steam sterilization kills 99.9% of bacteria, combined drying reduces moisture",
        "safety": "BPA-free materials, automatic shut-off for safety",
        "ease_of_use": "One-step operation, large capacity (up to 6 bottles)",
        "price_range": "$120–140",
        "reference_url": "https://www.babylist.com/hello-baby/best-bottle-sterilizer",
        "amazon_url": "https://www.amazon.com/Baby-Brezza-One-Step-Sterilizer/dp/B071R1NQ23/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Relatively expensive; large footprint on countertop",
        "biggest_positive": "Convenient sterilization and drying in one appliance; saves time",
    },
    {
        "product_url": "https://www.amazon.com/Philips-Avent-Microwave-Sterilizer-SCF284/dp/B00D49F2Q0/ref=nosim?tag=nobsmed07-20",
        "name": "Philips Avent Microwave Steam Sterilizer",
        "sanitization": "Effective steam sterilization in minutes using microwave",
        "safety": "BPA-free materials; microwave safe",
        "ease_of_use": "Quick cycle (~2 minutes), portable and compact",
        "price_range": "$30–50",
        "reference_url": "https://www.consumerreports.org/bottle-sterilizers/philips-avent-microwave-steam-sterilizer-review/",
        "amazon_url": "https://www.amazon.com/Philips-Avent-Microwave-Sterilizer-SCF284/dp/B00D49F2Q0/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Requires microwave; limited capacity (4 bottles)",
        "biggest_positive": "Fast and convenient; great for travel or small kitchens",
    },
    {
        "product_url": "https://www.amazon.com/Munchkin-Steam-Guard-Electric-Sterilizer/dp/B00S0HQ7WO/ref=nosim?tag=nobsmed07-20",
        "name": "Munchkin Steam Guard Electric Sterilizer",
        "sanitization": "Steam sterilization with safety guard; kills 99.9% germs",
        "safety": "BPA-free; automatic shutoff and safety guard",
        "ease_of_use": "Electric plug-in, cycles in about 6 minutes, holds up to 6 bottles",
        "price_range": "$50–70",
        "reference_url": "https://www.whattoexpect.com/baby-products/munchkin-steam-sterilizer-review/",
        "amazon_url": "https://www.amazon.com/Munchkin-Steam-Guard-Electric-Sterilizer/dp/B00S0HQ7WO/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Takes up countertop space; requires outlet",
        "biggest_positive": "Affordable electric sterilizer with safety features and good capacity",
    },
    {
        "product_url": "https://www.amazon.com/Wabi-Baby-Electric-Sterilizer/dp/B07NYRFM4G/ref=nosim?tag=nobsmed07-20",
        "name": "Wabi Baby Electric Steam Sterilizer",
        "sanitization": "Steam sterilization with drying function; compact design",
        "safety": "BPA-free, automatic shutoff, quiet operation",
        "ease_of_use": "One-button start; holds up to 6 bottles",
        "price_range": "$110–130",
        "reference_url": "https://www.babygearlab.com/reviews/feeding/bottle-sterilizer",
        "amazon_url": "https://www.amazon.com/Wabi-Baby-Electric-Sterilizer/dp/B07NYRFM4G/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Higher price point; drying cycle adds to total time",
        "biggest_positive": "Quiet, efficient sterilizing and drying with sleek design",
    },
]

bottle_dryers = [
    {
        "product_url": "https://www.amazon.com/Baby-Brezza-One-Step-Sterilizer/dp/B071R1NQ23/ref=nosim?tag=nobsmed07-20",
        "name": "Baby Brezza One Step Sterilizer and Dryer",
        "drying_effectiveness": "Built-in fan drying after steam sterilization; reduces moisture effectively",
        "safety": "BPA-free materials, automatic shut-off",
        "ease_of_use": "One-step sterilize and dry; large capacity (up to 6 bottles)",
        "price_range": "$120–140",
        "reference_url": "https://www.babylist.com/hello-baby/best-bottle-sterilizer",
        "amazon_url": "https://www.amazon.com/Baby-Brezza-One-Step-Sterilizer/dp/B071R1NQ23/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Higher price point and larger footprint",
        "biggest_positive": "Convenient all-in-one sterilizer and dryer; saves counter space and time",
    },
    {
        "product_url": "https://www.amazon.com/Tommee-Tippee-Electric-Bottle-Accessory/dp/B00B7UI9KK/ref=nosim?tag=nobsmed07-20",
        "name": "Tommee Tippee Electric Bottle and Accessory Dryer",
        "drying_effectiveness": "Uses heated air to dry bottles and accessories quickly",
        "safety": "BPA-free; cool-touch exterior",
        "ease_of_use": "Simple push-button operation; compact design",
        "price_range": "$70–90",
        "reference_url": "https://www.whattoexpect.com/baby-products/tommee-tippee-bottle-dryer-review/",
        "amazon_url": "https://www.amazon.com/Tommee-Tippee-Electric-Bottle-Accessory/dp/B00B7UI9KK/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Can be noisy during drying cycle",
        "biggest_positive": "Efficient drying, fits various bottle types and accessories",
    },
    {
        "product_url": "https://www.amazon.com/Dr-Browns-Bottle-Warmer-Dryer/dp/B07Q7ZTW6M/ref=nosim?tag=nobsmed07-20",
        "name": "Dr. Brown’s Bottle Warmer and Dryer",
        "drying_effectiveness": "Gentle warm air drying combined with warming feature",
        "safety": "BPA-free; automatic shut-off",
        "ease_of_use": "Dual function for warming and drying; easy controls",
        "price_range": "$70–90",
        "reference_url": "https://www.babygearlab.com/reviews/feeding/bottle-dryer",
        "amazon_url": "https://www.amazon.com/Dr-Browns-Bottle-Warmer-Dryer/dp/B07Q7ZTW6M/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Limited drying capacity compared to standalone dryers",
        "biggest_positive": "Convenient 2-in-1 device; saves space and time",
    },
    {
        "product_url": "https://www.amazon.com/Munchkin-Warm-Glow-Bottle-Warmer/dp/B07RZ95N3Q/ref=nosim?tag=nobsmed07-20",
        "name": "Munchkin Warm Glow Bottle Warmer and Dryer",
        "drying_effectiveness": "Uses warm air to dry and warm bottles with gentle temperature control",
        "safety": "BPA-free materials; auto shut-off",
        "ease_of_use": "Simple interface, indicator lights",
        "price_range": "$60–80",
        "reference_url": "https://www.whattoexpect.com/baby-products/munchkin-bottle-warming-drying-review/",
        "amazon_url": "https://www.amazon.com/Munchkin-Warm-Glow-Bottle-Warmer/dp/B07RZ95N3Q/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Drying can take longer compared to dedicated dryers",
        "biggest_positive": "Affordable 2-in-1 warming and drying solution",
    },
]

infant_high_chairs = [
    {
        "product_url": "https://amzn.to/44hNBh5",
        "name": "Graco Blossom 6-in-1 Convertible High Chair",
        "safety": "Meets ASTM standards, 5-point harness",
        "comfort": "Padded seat with adjustable recline",
        "cleaning": "Removable, machine-washable seat pad; dishwasher-safe trays",
        "adjustability": "6 modes from infant to toddler and booster",
        "price_range": "$150–200",
        "reference_url": "https://www.babylist.com/hello-baby/best-high-chair",
        "amazon_url": "https://www.amazon.com/Graco-Blossom-Convertible-High-Chair/dp/B00I8JZ1H4/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Large footprint; bulky when fully assembled",
        "biggest_positive": "Grows with child, versatile and durable",
    },
    {
        # Joovy Nook High Chair
        # https://amzn.to/4npgRvd
        "product_url": "https://amzn.to/4npgRvd",
        "name": "Joovy Nook High Chair",
        "safety": "5-point harness, meets safety standards",
        "comfort": "Padded seat, reclines slightly",
        "cleaning": "Removable seat pad; dishwasher-safe trays",
        "adjustability": "Compact fold; fits in tight spaces",
        "price_range": "$130–150",
        "reference_url": "https://www.whattoexpect.com/baby-products/joovy-nook-high-chair-review/",
        "amazon_url": "https://www.amazon.com/Joovy-Nook-High-Chair/dp/B00FQ0G8I0/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Tray can be hard to remove with one hand",
        "biggest_positive": "Compact fold and sleek design ideal for small spaces",
    },
    {
        # https://amzn.to/3ZKr2QS
        "product_url": "https://amzn.to/3ZKr2QS",
        "name": "Inglesina Fast Table Chair",
        "safety": "Meets safety standards, secure clamp for table attachment",
        "comfort": "Padded fabric seat with backrest",
        "cleaning": "Removable washable cover",
        "adjustability": "Attaches directly to table; portable",
        "price_range": "$100–120",
        "reference_url": "https://www.babygearlab.com/reviews/feeding/high-chairs/inglesina-fast",
        "amazon_url": "https://www.amazon.com/Inglesina-Fast-Table-Chair/dp/B00O7SS3AA/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Not suitable for very heavy babies; limited to table use",
        "biggest_positive": "Portable and space-saving; great for travel or small kitchens",
    },
    {
        # https://amzn.to/43YvmON
        "product_url": "https://amzn.to/43YvmON",
        "name": "Fisher-Price SpaceSaver High Chair",
        "safety": "3-point harness; stable design",
        "comfort": "Padded seat insert, removable",
        "cleaning": "Removable, machine-washable pad; dishwasher-safe tray",
        "adjustability": "Attaches to most chairs; folds flat",
        "price_range": "$50–70",
        "reference_url": "https://www.babylist.com/hello-baby/best-space-saver-high-chair",
        "amazon_url": "https://www.amazon.com/Fisher-Price-SpaceSaver-High-Chair/dp/B00FK1K1UU/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Less secure than standalone high chairs; limited weight capacity",
        "biggest_positive": "Affordable, easy to use, great for smaller spaces",
    },
]

infant_nursing_pillows = [
    {
        "product_url": "https://www.amazon.com/Boppy-Original-Nursing-Pillow-Positioner/dp/B001GX7F70/ref=nosim?tag=nobsmed07-20",
        "name": "Boppy Original Nursing Pillow and Positioner",
        "comfort_support": "C-shaped pillow provides good arm and back support",
        "cleaning": "Machine washable cover; removable and easy to clean",
        "safety": "Firm support with soft cushioning",
        "price_range": "$30–40",
        "reference_url": "https://www.babylist.com/hello-baby/best-nursing-pillow",
        "amazon_url": "https://www.amazon.com/Boppy-Original-Nursing-Pillow-Positioner/dp/B001GX7F70/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "May be bulky for some users; not adjustable",
        "biggest_positive": "Versatile, widely used, and easy to clean",
    },
    {
        "product_url": "https://www.amazon.com/My-Brest-Friend-Nursing-Pillow/dp/B00B20B3GG/ref=nosim?tag=nobsmed07-20",
        "name": "My Brest Friend Nursing Pillow",
        "comfort_support": "Wrap-around design offers firm, flat surface support with adjustable strap",
        "cleaning": "Machine washable cover; removable",
        "safety": "Provides stable, ergonomic feeding position",
        "price_range": "$40–50",
        "reference_url": "https://www.whattoexpect.com/baby-products/my-brest-friend-nursing-pillow-review/",
        "amazon_url": "https://www.amazon.com/My-Brest-Friend-Nursing-Pillow/dp/B00B20B3GG/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Less versatile for non-nursing uses",
        "biggest_positive": "Excellent support and positioning; highly rated by moms",
    },
    {
        "product_url": "https://www.amazon.com/Infantino-Elevate-Adjustable-Nursing-Pillow/dp/B00I3Q3QTS/ref=nosim?tag=nobsmed07-20",
        "name": "Infantino Elevate Adjustable Nursing Pillow",
        "comfort_support": "Adjustable height for customizable support",
        "cleaning": "Machine washable cover; removable",
        "safety": "Firm and supportive, good for multiple feeding positions",
        "price_range": "$25–30",
        "reference_url": "https://www.babygearlab.com/reviews/feeding/nursing-pillows/infantino-elevate",
        "amazon_url": "https://www.amazon.com/Infantino-Elevate-Adjustable-Nursing-Pillow/dp/B00I3Q3QTS/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Adjustable feature can be cumbersome to use",
        "biggest_positive": "Affordable and customizable height support",
    },
    {
        "product_url": "https://www.amazon.com/Leachco-Cuddle-U-Original-Nursing-Pillow/dp/B0006VXCY6/ref=nosim?tag=nobsmed07-20",
        "name": "Leachco Cuddle-U Original Nursing Pillow",
        "comfort_support": "Firm with plush cover; U-shaped for versatile use",
        "cleaning": "Machine washable cover; removable",
        "safety": "Good support for both mom and baby",
        "price_range": "$40–50",
        "reference_url": "https://www.babylist.com/hello-baby/best-nursing-pillow",
        "amazon_url": "https://www.amazon.com/Leachco-Cuddle-U-Original-Nursing-Pillow/dp/B0006VXCY6/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Bulky design can be less portable",
        "biggest_positive": "Versatile use beyond nursing; supportive and comfortable",
    },
]

non_toxic_playmats = [
    {
        "product_url": "https://www.amazon.com/Skip-Hop-Playspot-Soft-Foam/dp/B077PLVLCX/ref=nosim?tag=nobsmed07-20",
        "name": "Skip Hop Playspot Foam Floor Tiles",
        "material_safety": "Phthalate-free, BPA-free EVA foam",
        "comfort": "Soft foam padding; cushioned for infant play",
        "cleaning": "Wipe clean with mild soap and water",
        "portability": "Modular tiles can be assembled/disassembled for storage",
        "price_range": "$70–90 for set",
        "reference_url": "https://www.babylist.com/hello-baby/best-baby-playmats",
        "amazon_url": "https://www.amazon.com/Skip-Hop-Playspot-Soft-Foam/dp/B077PLVLCX/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Foam can trap dirt and dust; slight odor at first",
        "biggest_positive": "Easy to customize size and shape; safe foam material",
    },
    {
        "product_url": "https://www.amazon.com/Lollacup-Organic-Cotton-Playmat/dp/B07THY88SV/ref=nosim?tag=nobsmed07-20",
        "name": "Lollacup Organic Cotton Playmat",
        "material_safety": "GOTS certified organic cotton and natural filling",
        "comfort": "Soft, breathable surface with gentle cushioning",
        "cleaning": "Machine washable cover; spot clean filler",
        "portability": "Lightweight and foldable for storage",
        "price_range": "$130–150",
        "reference_url": "https://www.wholesomebaby.com/blog/best-organic-baby-playmats",
        "amazon_url": "https://www.amazon.com/Lollacup-Organic-Cotton-Playmat/dp/B07THY88SV/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Pricey compared to foam mats; less water-resistant",
        "biggest_positive": "Highly natural materials; excellent breathability and softness",
    },
    {
        "product_url": "https://www.amazon.com/Silikids-Silicone-Play-Mat/dp/B08FMPD8PK/ref=nosim?tag=nobsmed07-20",
        "name": "Silikids Silicone Playmat",
        "material_safety": "100% food-grade, BPA- and phthalate-free silicone",
        "comfort": "Soft but firm surface; waterproof and easy to clean",
        "cleaning": "Dishwasher safe; quick wipe down",
        "portability": "Rolls or folds compactly",
        "price_range": "$80–110",
        "reference_url": "https://www.whattoexpect.com/baby-products/best-baby-playmat/",
        "amazon_url": "https://www.amazon.com/Silikids-Silicone-Play-Mat/dp/B08FMPD8PK/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Less cushioned than foam or fabric mats",
        "biggest_positive": "Durable, hygienic, and super easy to clean",
    },
    {
        "product_url": "https://www.amazon.com/Baby-Care-Play-Mat-Eccomum/dp/B07Y93DXHZ/ref=nosim?tag=nobsmed07-20",
        "name": "Baby Care Play Mat by Eccomum",
        "material_safety": "Non-toxic, BPA-, phthalate-, lead-free, certified safe foam",
        "comfort": "Thick foam padding with soft surface",
        "cleaning": "Wipe clean; waterproof surface",
        "portability": "Folds for easy storage and transport",
        "price_range": "$60–80",
        "reference_url": "https://www.babygearlab.com/reviews/playmats/baby-care-play-mat",
        "amazon_url": "https://www.amazon.com/Baby-Care-Play-Mat-Eccomum/dp/B07Y93DXHZ/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Edges can curl slightly after extended use",
        "biggest_positive": "Good thickness and cushioning at a reasonable price",
    },
]

baby_carrier_wraps = [
    {
        "product_url": "https://www.amazon.com/Moby-Wrap-Classic-Carrier/dp/B0017XOSKK/ref=nosim?tag=nobsmed07-20",
        "name": "Moby Wrap Classic",
        "safety": "Supports newborn to 35 lbs; certified safe fabric",
        "comfort": "Soft, stretchy cotton blend; distributes weight evenly",
        "ease_of_use": "Requires practice to wrap correctly; multiple tying styles",
        "material": "100% cotton",
        "price_range": "$45–55",
        "reference_url": "https://www.babylist.com/hello-baby/best-baby-carriers",
        "amazon_url": "https://www.amazon.com/Moby-Wrap-Classic-Carrier/dp/B0017XOSKK/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Steep learning curve for proper tying",
        "biggest_positive": "Versatile and very supportive for newborns",
    },
    {
        "product_url": "https://www.amazon.com/Boba-Baby-Carrier-Wrap/dp/B00MZ4AXN6/ref=nosim?tag=nobsmed07-20",
        "name": "Boba Wrap",
        "safety": "Supports newborn to 35 lbs; breathable and secure",
        "comfort": "Soft, stretchy cotton/spandex blend; snug fit",
        "ease_of_use": "Easier to tie than some other wraps; stretchy material",
        "material": "95% cotton, 5% spandex",
        "price_range": "$45–55",
        "reference_url": "https://www.whattoexpect.com/baby-products/boba-wrap-review/",
        "amazon_url": "https://www.amazon.com/Boba-Baby-Carrier-Wrap/dp/B00MZ4AXN6/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Can feel too snug or hot in warm climates",
        "biggest_positive": "Comfortable stretch with easier wrapping",
    },
    {
        "product_url": "https://www.amazon.com/Solly-Baby-Wrap/dp/B00H7D7G5Y/ref=nosim?tag=nobsmed07-20",
        "name": "Solly Baby Wrap",
        "safety": "Designed for newborns and infants up to 25 lbs; breathable fabric",
        "comfort": "Lightweight, soft, silky fabric; great for warmer weather",
        "ease_of_use": "Simple instructions; quick to learn wrapping",
        "material": "60% cotton, 40% polyester",
        "price_range": "$80–90",
        "reference_url": "https://www.babylist.com/hello-baby/best-baby-carriers",
        "amazon_url": "https://www.amazon.com/Solly-Baby-Wrap/dp/B00H7D7G5Y/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Higher price point; limited weight capacity",
        "biggest_positive": "Soft, lightweight fabric ideal for summer and sensitive skin",
    },
    {
        "product_url": "https://www.amazon.com/LILLEbaby-Baby-Wrap/dp/B07FKKKR6W/ref=nosim?tag=nobsmed07-20",
        "name": "LILLEbaby Baby Wrap",
        "safety": "Supports newborn to 25 lbs; strong and durable fabric",
        "comfort": "Breathable cotton blend with ergonomic design",
        "ease_of_use": "Moderate learning curve; clear instructions",
        "material": "100% cotton",
        "price_range": "$60–80",
        "reference_url": "https://www.whattoexpect.com/baby-products/lillebaby-wrap-review/",
        "amazon_url": "https://www.amazon.com/LILLEbaby-Baby-Wrap/dp/B07FKKKR6W/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Can be bulky to carry when not in use",
        "biggest_positive": "Durable and supportive with ergonomic comfort",
    },
]

post_delivery_healing_products = [
    {
        "product_url": "https://www.amazon.com/Earth-Mama-Organic-Perineal-Spray/dp/B001FX46XY/ref=nosim?tag=nobsmed07-20",
        "name": "Earth Mama Organic Perineal Spray",
        "purpose": "Soothes and heals perineal area after delivery",
        "effectiveness": "Reduces irritation, promotes healing with herbal ingredients",
        "safety": "Certified organic, safe for sensitive skin and breastfeeding moms",
        "ease_of_use": "Easy spray application, portable",
        "price_range": "$10–15",
        "reference_url": "https://www.whattoexpect.com/baby-products/earth-mama-perineal-spray-review/",
        "amazon_url": "https://www.amazon.com/Earth-Mama-Organic-Perineal-Spray/dp/B001FX46XY/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "May require frequent application",
        "biggest_positive": "Natural ingredients and gentle relief",
    },
    {
        "product_url": "https://www.amazon.com/Frida-Mom-Perineal-Cooling-Pads/dp/B01FZX3NCI/ref=nosim?tag=nobsmed07-20",
        "name": "Frida Mom Perineal Cooling Pads",
        "purpose": "Provides cooling relief for perineal swelling and discomfort",
        "effectiveness": "Immediate cooling effect; reduces pain and swelling",
        "safety": "Non-toxic, hypoallergenic, fragrance-free",
        "ease_of_use": "Disposable pads, easy to apply and discard",
        "price_range": "$15–20 for pack",
        "reference_url": "https://www.babylist.com/hello-baby/best-postpartum-products",
        "amazon_url": "https://www.amazon.com/Frida-Mom-Perineal-Cooling-Pads/dp/B01FZX3NCI/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Single-use; ongoing cost",
        "biggest_positive": "Convenient and fast-acting relief",
    },
    {
        "product_url": "https://www.amazon.com/Lanolin-Nipple-Cream-Lansinoh/dp/B000RQWFM6/ref=nosim?tag=nobsmed07-20",
        "name": "Lanolin Nipple Cream (Lansinoh)",
        "purpose": "Heals cracked, sore nipples during breastfeeding",
        "effectiveness": "Soothes and promotes healing; safe for baby",
        "safety": "All-natural lanolin; FDA-approved",
        "ease_of_use": "Apply directly to nipples; no need to remove before feeding",
        "price_range": "$8–15",
        "reference_url": "https://www.whattoexpect.com/baby-products/lansinoh-nipple-cream-review/",
        "amazon_url": "https://www.amazon.com/Lansinoh-HPA-Lanolin-Nipple-Cream/dp/B000RQWFM6/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Can be greasy if over-applied",
        "biggest_positive": "Trusted and effective for breastfeeding moms",
    },
    {
        "product_url": "https://www.amazon.com/TUCKS-Medicated-Cooling-Pads/dp/B0011U3P94/ref=nosim?tag=nobsmed07-20",
        "name": "Tucks Medicated Cooling Pads",
        "purpose": "Relieves hemorrhoid pain and irritation after delivery",
        "effectiveness": "Cooling effect soothes pain and itching",
        "safety": "Witch hazel based; safe for postpartum use",
        "ease_of_use": "Disposable pads; easy to use",
        "price_range": "$5–10",
        "reference_url": "https://www.babygearlab.com/reviews/health/tucks-cooling-pads",
        "amazon_url": "https://www.amazon.com/TUCKS-Medicated-Cooling-Pads/dp/B0011U3P94/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Single-use; may cause mild dryness",
        "biggest_positive": "Affordable and widely available relief",
    },
    {
        "product_url": "https://www.amazon.com/Frida-Mom-Upside-Down-Peri-Bottle/dp/B07RGQFLJB/ref=nosim?tag=nobsmed07-20",
        "name": "Frida Mom Upside Down Peri Bottle",
        "purpose": "Cleans perineal area without wiping after delivery",
        "effectiveness": "Soothes and gently cleans postpartum sensitive areas",
        "safety": "BPA-free; angled nozzle for ergonomic use",
        "ease_of_use": "Handheld squeeze bottle with angled neck",
        "price_range": "$15–20",
        "reference_url": "https://www.babylist.com/hello-baby/best-peri-bottle",
        "amazon_url": "https://www.amazon.com/Frida-Mom-Upside-Down-Peri-Bottle/dp/B07RGQFLJB/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Needs refilling often; only comes in one size",
        "biggest_positive": "Essential for gentle postpartum hygiene",
    },
    {
        "product_url": "https://www.amazon.com/Kindred-Bravely-Abdominal-Support-Postpartum/dp/B09M9SJSGB/ref=nosim?tag=nobsmed07-20",
        "name": "Kindred Bravely Abdominal Recovery Binder",
        "purpose": "Provides abdominal and lower back support post C-section or vaginal delivery",
        "effectiveness": "Reduces pain and improves posture during healing",
        "safety": "Latex-free, breathable materials",
        "ease_of_use": "Adjustable Velcro closure; machine washable",
        "price_range": "$45–65",
        "reference_url": "https://www.whattoexpect.com/baby-products/postpartum-belly-wraps/",
        "amazon_url": "https://www.amazon.com/Kindred-Bravely-Abdominal-Support-Postpartum/dp/B09M9SJSGB/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Can feel tight if worn too long",
        "biggest_positive": "Targeted core support for faster recovery",
    },
    {
        "product_url": "https://www.amazon.com/Lansinoh-Therapearl-Breast-Therapy-Pack/dp/B007VT2OQ4/ref=nosim?tag=nobsmed07-20",
        "name": "Lansinoh Hot and Cold Breast Therapy Pads",
        "purpose": "Relieves breast engorgement, plugged ducts, and pain",
        "effectiveness": "Microwavable or freezable for temperature therapy",
        "safety": "Non-toxic gel; safe to use while breastfeeding",
        "ease_of_use": "Reusable pads fit inside bra or pump flanges",
        "price_range": "$12–18",
        "reference_url": "https://www.babygearlab.com/reviews/health/lansinoh-therapy-pads",
        "amazon_url": "https://www.amazon.com/Lansinoh-Therapearl-Breast-Therapy-Pack/dp/B007VT2OQ4/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Pads can lose heat quickly",
        "biggest_positive": "Dual hot/cold therapy with reusable design",
    },
    {
        "product_url": "https://www.amazon.com/Dermoplast-Relieving-Spray-2-75-Ounce-Canisters/dp/B000GCQZX0/ref=nosim?tag=nobsmed07-20",
        "name": "Dermoplast Pain Relieving Spray",
        "purpose": "Numbs and soothes perineal or incision-area pain",
        "effectiveness": "Provides fast-acting topical pain relief",
        "safety": "Safe for external use; OB-recommended",
        "ease_of_use": "Spray application; travel-friendly",
        "price_range": "$7–10",
        "reference_url": "https://www.babylist.com/hello-baby/best-postpartum-pain-relief",
        "amazon_url": "https://www.amazon.com/Dermoplast-Relieving-Spray-2-75-Ounce-Canisters/dp/B000GCQZX0/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Not for internal use; short-acting",
        "biggest_positive": "Trusted hospital-grade pain relief",
    },
    {
        "product_url": "https://www.amazon.com/Sitz-Bath-Soak-Postpartum-Recovery/dp/B074W8HBMR/ref=nosim?tag=nobsmed07-20",
        "name": "Sitz Bath Soak by Thena Natural Wellness",
        "purpose": "Soothes hemorrhoids, tears, and swelling in perineal area",
        "effectiveness": "Reduces inflammation and promotes natural healing",
        "safety": "100% natural ingredients: Epsom salt, witch hazel, calendula",
        "ease_of_use": "Add to warm water; use in sitz bath or peri bottle",
        "price_range": "$15–20",
        "reference_url": "https://www.healthline.com/health/postpartum-sitz-bath-benefits",
        "amazon_url": "https://www.amazon.com/Sitz-Bath-Soak-Postpartum-Recovery/dp/B074W8HBMR/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Requires separate sitz tub or basin",
        "biggest_positive": "Natural herbal relief with proven benefits",
    },
]

non_toxic_infant_car_seats = [
    {
        "product_url": "https://www.amazon.com/Stokke-Pipa-Nuna-Black-Seat/dp/B07KZLS66W/ref=nosim?tag=nobsmed07-20",
        "name": "Stokke PIPA by Nuna Infant Car Seat",
        "safety": "All models (post-2020) are flame retardant & PFAS-free, Greenguard Gold certified",
        "ease_of_install": "Rigid LATCH, color-coded indicators for correct leveling",
        "comfort": "Lightweight (8.5 lb); plush organic jersey inserts",
        "weight": "8.5 lb",
        "price_range": "$450",
        "reference_url": "https://www.thelaceylist.com/thelist/non-toxic-flame-retardant-free-car-seats",
        "amazon_url": "https://www.amazon.com/Stokke-Pipa-Nuna-Black-Seat/dp/B07KZLS66W/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "High price; limited stroller compatibility",
        "biggest_positive": "Outstanding safety in a super-light, non-toxic design",
    },
    {
        "product_url": "https://www.amazon.com/Chicco-ClearTex%C2%AE-Rear-Facing-Compatible-Strollers/dp/B08Q1LS11S/ref=nosim?tag=nobsmed07-20",
        "name": "Chicco KeyFit 35 ClearTex Infant Car Seat",
        "safety": "ClearTex fabric is flame retardant & PFAS-free; Greenguard Gold certified",
        "ease_of_install": "Easy LATCH install with leveling indicators",
        "comfort": "Plush newborn insert, fits up to 35 lb",
        "weight": "10 lb",
        "price_range": "$229",
        "reference_url": "https://www.leafscore.com/eco-friendly-kids-products/best-non-toxic-infant-car-seats/",
        "amazon_url": "https://www.amazon.com/Chicco-ClearTex%C2%AE-Rear-Facing-Compatible-Strollers/dp/B08Q1LS11S/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Anti‑rebound bar may reduce legroom in small cars",
        "biggest_positive": "Affordable, widely available, and easy to install",
    },
    {
        "product_url": "https://www.amazon.com/Clek-Adjustable-Lightweight-Positions-Retardant-Free/dp/B0CZPCX345/ref=nosim?tag=nobsmed07-20",
        "name": "Clek Liing Infant Car Seat (Mammoth/Railroad fabric)",
        "safety": "Flame retardant & PFAS-free Mammoth/Railroad fabric; narrow base",
        "ease_of_install": "Built-in rigid LATCH, compact & easy to fit 3-across",
        "comfort": "Good padding and head support; 9 lb weight",
        "weight": "9 lb",
        "price_range": "$299",
        "reference_url": "https://www.parentingmode.com/non-toxic-car-seats/",
        "amazon_url": "https://www.amazon.com/Clek-Adjustable-Lightweight-Positions-Retardant-Free/dp/B0CZPCX345/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Premium price; only certain fabrics are fully non-toxic",
        "biggest_positive": "Premium safety and narrow design for tight car bellies",
    },
    {
        "product_url": "https://www.amazon.com/Maxi-Cosi-Mico-Infant-Polished-Pebble/dp/B08ZGL173B/ref=nosim?tag=nobsmed07-20",
        "name": "Maxi-Cosi Mico 30 PureCosi Infant Car Seat",
        "safety": "PureCosi fabric is flame retardant & PFAS-free polyester",
        "ease_of_install": "One-click LATCH, adjustable base & canopy",
        "comfort": "Fits 4–30 lb, lightweight at ~8.5 lb, breathable fabric",
        "weight": "8.5 lb",
        "price_range": "$199",
        "reference_url": "https://www.crunchyandcurious.com/car-seats-without-flame-retardants/",
        "amazon_url": "https://www.amazon.com/Maxi-Cosi-Mico-Infant-Polished-Pebble/dp/B08ZGL173B/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "No load-leg base; lighter weight means less heft",
        "biggest_positive": "Affordable and non-toxic with strong safety features",
    },
]

non_toxic_bassinets = [
    {
        "product_url": "https://www.amazon.com/Sn%C3%BCz-SnuzPod-Bedside-Crib-Natural/dp/B08J9151BL/ref=nosim?tag=nobsmed07-20",
        "name": "SnuzPod4 Bedside Bassinet",
        "safety": "JPMA-certified; certified breathable mattress, adjustable height/incline",
        "materials": "Sustainably sourced wood; fabric free of flame retardants",
        "ease_of_use": "Rocks & floor mode; fits beside bed with adjustable height",
        "price_range": "$350–400",
        "reference_url": "https://www.wired.com/review/snuzpod4-bassinet",
        "amazon_url": "https://www.amazon.com/Sn%C3%BCz-SnuzPod-Bedside-Crib-Natural/dp/B08J9151BL/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Manual setup; no auto-soothing features",
        "biggest_positive": "Simple, stylish, sustainably built with non-toxic materials",
    },
    {
        "product_url": "https://www.amazon.com/Babybay-Original-Co-Sleeper-Natural-Untreated/dp/B007NZHXZK/ref=nosim?tag=nobsmed07-20",
        "name": "babybay Original Bedside Sleeper",
        "safety": "No plastics or harmful glues; complies with ASTM/CPSC/FSC standards",
        "materials": "100% natural beechwood, water-based finishes, low-VOC",
        "ease_of_use": "Attaches to bed frame; converts to freestanding",
        "price_range": "$245+",
        "reference_url": "https://sustainawill.com/best-non-toxic-and-organic-bassinets/",
        "amazon_url": "https://www.amazon.com/Babybay-Original-Co-Sleeper-Natural-Untreated/dp/B007NZHXZK/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Mattress not organic; may require buying separately",
        "biggest_positive": "Completely natural wood design, zero-VOC finishes",
    },
    {
        "product_url": "https://www.amazon.com/BabyBj%C3%B6rn-041121US-BABYBJORN-Cradle-White/dp/B008TML9AQ/ref=nosim?tag=nobsmed07-20",
        "name": "BABYBJÖRN Cradle",
        "safety": "OEKO‑TEX Standard 100 certified fabrics; breathable mesh sides",
        "materials": "Formal-dehyde–free wood/MDF; certified polyester fabrics",
        "ease_of_use": "Lightweight, portable, gentle rocking; machine‑washable cover",
        "price_range": "$199–230",
        "reference_url": "https://greatforkids.org/bassinet/best-non-toxic-bassinet/",
        "amazon_url": "https://www.amazon.com/BabyBj%C3%B6rn-041121US-BABYBJORN-Cradle-White/dp/B008TML9AQ/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "No bedside attach option; limited longevity (~6 mo)",
        "biggest_positive": "Highly breathable, compact, and non-toxic materials",
    },
    {
        "product_url": "https://www.amazon.com/BreathableBaby-Breathable-Mesh-Portable-Sleeper/dp/B08T7TNJWZ/ref=nosim?tag=nobsmed07-20",
        "name": "BreathableBaby Mesh Portable Sleeper",
        "safety": "Greenguard Gold certified; non-toxic paint, free of lead, phthalates, VOCs",
        "materials": "Sustainable New Zealand pine, mesh sides",
        "ease_of_use": "Folds compactly for portability; roomy interior",
        "price_range": "$249",
        "reference_url": "https://www.wonderbaby.org/articles/non-toxic-bassinet",
        "amazon_url": "https://www.amazon.com/BreathableBaby-Breathable-Mesh-Portable-Sleeper/dp/B08T7TNJWZ/ref=nosim?tag=nobsmed07-20",
        "biggest_negative": "Use limited to early months due to size",
        "biggest_positive": "Spacious, breathable, and environmentally conscious design",
    },
]
