# Amazon product data for infant care and pregnancy
# MY ASSOCIATE ID: nobsmed07-20
from pydantic import BaseModel


class AmazonProduct(BaseModel):
    title: str
    url: str
    category: str
    cons: str
    pros: str
    price_range: str


# Converted Products using AmazonProduct class
infant_bath_tubs = [
    AmazonProduct(
        title="Skip Hop Moby Smart Sling 3-Stage Baby Bath Tub",
        url="https://www.amazon.com/Skip-Hop-Moby-Smart-Sling/dp/B01AFQI3J8/ref=nosim?tag=nobsmed07-20",
        category="Infant Bath Tubs",
        price_range="$40",
        cons="Bulky and requires ample bathroom space; sling anchors can be difficult to remove.",
        pros="Versatile 3-stage design that grows with baby; adjustable sling offers excellent newborn support.",
    ),
    AmazonProduct(
        title="Angelcare Baby Bath Support (Gray)",
        url="https://www.amazon.com/Angelcare-Baby-Bath-Support-Grey/dp/B01M6YVW7B/ref=nosim?tag=nobsmed07-20",
        category="Infant Bath Tubs",
        price_range="$25–35",
        cons="Needs to be used inside a larger tub or sink; not a standalone tub.",
        pros="Lightweight, hygienic design that dries quickly to prevent mold; very easy to store.",
    ),
    AmazonProduct(
        title="Baby Delight Cushy Nest Cloud Premium Infant Bather",
        url="https://www.amazon.com/Baby-Delight-Premium-Organic-Comfortable/dp/B0CSMDJ636/ref=nosim?tag=nobsmed07-20",
        category="Infant Bath Tubs",
        price_range="$40–50",
        cons="Cushion takes time to dry; not a standalone tub and requires a larger tub or sink.",
        pros="Organic cotton cushion offers superior softness and comfort for newborns.",
    ),
    AmazonProduct(
        title="Puj Flyte Compact Infant Bathtub",
        url="https://www.amazon.com/Puj-Flyte-Compact-Infant-Bathtub/dp/B008PZ9VXY/ref=nosim?tag=nobsmed07-20",
        category="Infant Bath Tubs",
        price_range="$35",
        cons="Very limited use time—outgrown quickly, typically by 2–3 months.",
        pros="Ultra-compact and travel-friendly design; perfect for small spaces and sink use.",
    ),
]

infant_laundry_detergents = [
    AmazonProduct(
        title="Dreft Stage 1: Newborn Liquid Laundry Detergent",
        url="https://www.amazon.com/Dreft-Stage-Newborn-Liquid-Detergent/dp/B004HXI3Y0/ref=nosim?tag=nobsmed07-20",
        category="Baby Laundry Detergents",
        price_range="$12–15 for 28 oz",
        cons="Some parents report residue build-up if overdosed or not rinsed well",
        pros="Trusted brand with long-standing pediatrician recommendations and gentle cleaning",
    ),
    AmazonProduct(
        title="Babyganics 3X Baby Laundry Detergent Concentrated",
        url="https://www.amazon.com/Babyganics-Laundry-Detergent-Concentrated-Fragrance/dp/B07BHVK34S/ref=nosim?tag=nobsmed07-20",
        category="Baby Laundry Detergents",
        price_range="$15–18 for 50 oz",
        cons="Higher price point compared to other baby detergents",
        pros="Excellent stain removal with natural ingredients, suitable for sensitive skin",
    ),
    AmazonProduct(
        title="Seventh Generation Laundry Detergent Free & Clear",
        url="https://www.amazon.com/Seventh-Generation-Laundry-Detergent-Fragrance/dp/B07P86GPKD/ref=nosim?tag=nobsmed07-20",
        category="Baby Laundry Detergents",
        price_range="$12–14 for 50 oz",
        cons="Some users note less effectiveness on very tough stains",
        pros="Highly eco-friendly and non-toxic formula, great for sensitive baby skin",
    ),
    AmazonProduct(
        title="Molly's Suds Laundry Powder Fragrance Free",
        url="https://www.amazon.com/Mollys-Suds-Laundry-Powder-Fragrance/dp/B00MDWI8RM/ref=nosim?tag=nobsmed07-20",
        category="Baby Laundry Detergents",
        price_range="$16–20 for 25 oz",
        cons="Powder form may not dissolve well in cold water",
        pros="Very natural and safe; excellent for eczema-prone skin",
    ),
]

infant_care_books = [
    AmazonProduct(
        title="What to Expect the First Year by Heidi Murkoff",
        url="https://www.amazon.com/What-Expect-First-Heidi-Murkoff/dp/0761187480/ref=nosim?tag=nobsmed07-20",
        category="Baby Care Books",
        price_range="$15–20 paperback",
        cons="Some readers find it overly detailed and lengthy",
        pros="Great for new parents wanting a detailed month-to-month guide",
    ),
    AmazonProduct(
        title="Caring for Your Baby and Young Child by American Academy of Pediatrics",
        url="https://www.amazon.com/Caring-Your-Baby-Young-Child/dp/0593598199/ref=nosim?tag=nobsmed07-20",
        category="Baby Care Books",
        price_range="$20–30 paperback",
        cons="Some parents find it less approachable and more like a medical manual",
        pros="Trusted source for accurate and current infant health guidance",
    ),
    AmazonProduct(
        title="The Happiest Baby on the Block by Harvey Karp, M.D.",
        url="https://www.amazon.com/Happiest-Block-Revised-Updated-Second/dp/0553393235/ref=nosim?tag=nobsmed07-20",
        category="Baby Care Books",
        price_range="$12–18 paperback",
        cons="Narrow focus on soothing; less on other care aspects",
        pros="Highly effective, widely praised for improving infant sleep and reducing fussiness",
    ),
    AmazonProduct(
        title="Baby 411: Clear Answers & Smart Advice by Ari Brown, M.D.",
        url="https://amzn.to/4l0S7rf",
        category="Baby Care Books",
        price_range="$15–20 paperback",
        cons="Format may feel fragmented for some readers",
        pros="Great quick-reference guide that's easy to navigate",
    ),
]

bottle_cleaners = [
    AmazonProduct(
        title="Dr. Brown's Baby Bottle Brush",
        url="https://www.amazon.com/Dr-Browns-Bottle-Brush/dp/B00124N9HY/ref=nosim?tag=nobsmed07-20",
        category="Bottle Cleaners",
        price_range="$6–8",
        cons="Some users report bristles wearing out over time",
        pros="Effective and affordable; trusted brand with great cleaning reach",
    ),
    AmazonProduct(
        title="Munchkin Bristle Bottle Brush",
        url="https://www.amazon.com/Munchkin-Bristle-Bottle-Brush/dp/B00I2SK0OS/ref=nosim?tag=nobsmed07-20",
        category="Bottle Cleaners",
        price_range="$7–10",
        cons="Handle can be slippery when wet",
        pros="Good cleaning power with ergonomic design",
    ),
    AmazonProduct(
        title="OXO Tot Bottle Brush with Nipple Cleaner",
        url="https://www.amazon.com/OXO-Tot-Bottle-Brush-Nipple/dp/B00HY46DXQ/ref=nosim?tag=nobsmed07-20",
        category="Bottle Cleaners",
        price_range="$12–15",
        cons="Pricier than basic brushes",
        pros="High-quality, versatile brush with excellent cleaning reach",
    ),
    AmazonProduct(
        title="The First Years Quick Clean Bottle Brush",
        url="https://www.amazon.com/First-Years-Quick-Clean-Bottle/dp/B007TV5E0K/ref=nosim?tag=nobsmed07-20",
        category="Bottle Cleaners",
        price_range="$6–9",
        cons="Brush head may wear out faster",
        pros="Affordable and effective for everyday use",
    ),
]

bottle_sanitizers = [
    AmazonProduct(
        title="Baby Brezza One Step Sterilizer and Dryer",
        url="https://www.amazon.com/Baby-Brezza-One-Step-Sterilizer/dp/B071R1NQ23/ref=nosim?tag=nobsmed07-20",
        category="Bottle Sanitizers",
        price_range="$120–140",
        cons="Relatively expensive; large footprint on countertop",
        pros="Convenient sterilization and drying in one appliance; saves time",
    ),
    AmazonProduct(
        title="Philips Avent Microwave Steam Sterilizer",
        url="https://www.amazon.com/Philips-Avent-Microwave-Sterilizer-SCF284/dp/B00D49F2Q0/ref=nosim?tag=nobsmed07-20",
        category="Bottle Sanitizers",
        price_range="$30–50",
        cons="Requires microwave; limited capacity (4 bottles)",
        pros="Fast and convenient; great for travel or small kitchens",
    ),
    AmazonProduct(
        title="Munchkin Steam Guard Electric Sterilizer",
        url="https://www.amazon.com/Munchkin-Steam-Guard-Electric-Sterilizer/dp/B00S0HQ7WO/ref=nosim?tag=nobsmed07-20",
        category="Bottle Sanitizers",
        price_range="$50–70",
        cons="Takes up countertop space; requires outlet",
        pros="Affordable electric sterilizer with safety features and good capacity",
    ),
    AmazonProduct(
        title="Wabi Baby Electric Steam Sterilizer",
        url="https://www.amazon.com/Wabi-Baby-Electric-Sterilizer/dp/B07NYRFM4G/ref=nosim?tag=nobsmed07-20",
        category="Bottle Sanitizers",
        price_range="$110–130",
        cons="Higher price point; drying cycle adds to total time",
        pros="Quiet, efficient sterilizing and drying with sleek design",
    ),
]

bottle_dryers = [
    AmazonProduct(
        title="Baby Brezza One Step Sterilizer and Dryer",
        url="https://www.amazon.com/Baby-Brezza-One-Step-Sterilizer/dp/B071R1NQ23/ref=nosim?tag=nobsmed07-20",
        category="Bottle Dryers",
        price_range="$120–140",
        cons="Higher price point and larger footprint",
        pros="Convenient all-in-one sterilizer and dryer; saves counter space and time",
    ),
    AmazonProduct(
        title="Tommee Tippee Electric Bottle and Accessory Dryer",
        url="https://www.amazon.com/Tommee-Tippee-Electric-Bottle-Accessory/dp/B00B7UI9KK/ref=nosim?tag=nobsmed07-20",
        category="Bottle Dryers",
        price_range="$70–90",
        cons="Can be noisy during drying cycle",
        pros="Efficient drying, fits various bottle types and accessories",
    ),
    AmazonProduct(
        title="Dr. Brown's Bottle Warmer and Dryer",
        url="https://www.amazon.com/Dr-Browns-Bottle-Warmer-Dryer/dp/B07Q7ZTW6M/ref=nosim?tag=nobsmed07-20",
        category="Bottle Dryers",
        price_range="$70–90",
        cons="Limited drying capacity compared to standalone dryers",
        pros="Convenient 2-in-1 device; saves space and time",
    ),
    AmazonProduct(
        title="Munchkin Warm Glow Bottle Warmer and Dryer",
        url="https://www.amazon.com/Munchkin-Warm-Glow-Bottle-Warmer/dp/B07RZ95N3Q/ref=nosim?tag=nobsmed07-20",
        category="Bottle Dryers",
        price_range="$60–80",
        cons="Drying can take longer compared to dedicated dryers",
        pros="Affordable 2-in-1 warming and drying solution",
    ),
]

infant_high_chairs = [
    AmazonProduct(
        title="Graco Blossom 6-in-1 Convertible High Chair",
        url="https://www.amazon.com/dp/B08C6ZD793/ref=nosim?tag=nobsmed07-20",
        category="Baby High Chairs",
        price_range="$150–200",
        cons="Large footprint; bulky when fully assembled",
        pros="Grows with child, versatile and durable",
    ),
    AmazonProduct(
        title="Joovy Nook High Chair",
        url="https://www.amazon.com/Joovy-Nook-High-Chair/dp/B00FQ0G8I0/ref=nosim?tag=nobsmed07-20",
        category="Baby High Chairs",
        price_range="$130–150",
        cons="Tray can be hard to remove with one hand",
        pros="Compact fold and sleek design ideal for small spaces",
    ),
    AmazonProduct(
        title="Inglesina Fast Table Chair",
        url="https://www.amazon.com/dp/B00IOGIM9S/ref=nosim?tag=nobsmed07-20",
        category="Baby High Chairs",
        price_range="$100–120",
        cons="Not suitable for very heavy babies; limited to table use",
        pros="Portable and space-saving; great for travel or small kitchens",
    ),
    AmazonProduct(
        title="Fisher-Price Space Saver High Chair",
        url="https://www.amazon.com/dp/B08KFQK84Q/ref=nosim?tag=nobsmed07-20",
        category="Baby High Chairs",
        price_range="$50–70",
        cons="Less secure than standalone high chairs; limited weight capacity",
        pros="Affordable, easy to use, great for smaller spaces",
    ),
]

infant_nursing_pillows = [
    AmazonProduct(
        title="Boppy Original Nursing Pillow and Positioner",
        url="https://www.amazon.com/Boppy-Original-Nursing-Pillow-Positioner/dp/B001GX7F70/ref=nosim?tag=nobsmed07-20",
        category="Baby Nursing Pillows",
        price_range="$30–40",
        cons="May be bulky for some users; not adjustable",
        pros="Versatile, widely used, and easy to clean",
    ),
    AmazonProduct(
        title="My Brest Friend Nursing Pillow",
        url="https://www.amazon.com/My-Brest-Friend-Nursing-Pillow/dp/B00B20B3GG/ref=nosim?tag=nobsmed07-20",
        category="Baby Nursing Pillows",
        price_range="$40–50",
        cons="Less versatile for non-nursing uses",
        pros="Excellent support and positioning; highly rated by moms",
    ),
    AmazonProduct(
        title="Infantino Elevate Adjustable Nursing Pillow",
        url="https://www.amazon.com/Infantino-Elevate-Adjustable-Nursing-Pillow/dp/B00I3Q3QTS/ref=nosim?tag=nobsmed07-20",
        category="Baby Nursing Pillows",
        price_range="$25–30",
        cons="Adjustable feature can be cumbersome to use",
        pros="Affordable and customizable height support",
    ),
    AmazonProduct(
        title="Leachco Cuddle-U Original Nursing Pillow",
        url="https://www.amazon.com/dp/B01M7POA7N/ref=nosim?tag=nobsmed07-20",
        category="Baby Nursing Pillows",
        price_range="$40–50",
        cons="Bulky design can be less portable",
        pros="Versatile use beyond nursing; supportive and comfortable",
    ),
]

non_toxic_playmats = [
    AmazonProduct(
        title="Skip Hop Playspot Foam Floor Tiles",
        url="https://www.amazon.com/Skip-Hop-Playspot-Soft-Foam/dp/B077PLVLCX/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Play Mats",
        price_range="$70–90 for set",
        cons="Foam can trap dirt and dust; slight odor at first",
        pros="Easy to customize size and shape; safe foam material",
    ),
    AmazonProduct(
        title="Lollacup Organic Cotton Playmat",
        url="https://www.amazon.com/Lollacup-Organic-Cotton-Playmat/dp/B07THY88SV/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Play Mats",
        price_range="$130–150",
        cons="Pricey compared to foam mats; less water-resistant",
        pros="Highly natural materials; excellent breathability and softness",
    ),
    AmazonProduct(
        title="Silikids Silicone Playmat",
        url="https://www.amazon.com/Silikids-Silicone-Play-Mat/dp/B08FMPD8PK/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Play Mats",
        price_range="$80–110",
        cons="Less cushioned than foam or fabric mats",
        pros="Durable, hygienic, and super easy to clean",
    ),
    AmazonProduct(
        title="Baby Care Play Mat by Eccomum",
        url="https://www.amazon.com/Baby-Care-Play-Mat-Eccomum/dp/B07Y93DXHZ/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Play Mats",
        price_range="$60–80",
        cons="Edges can curl slightly after extended use",
        pros="Good thickness and cushioning at a reasonable price",
    ),
]

baby_carrier_wraps = [
    AmazonProduct(
        title="Moby Wrap Classic",
        url="https://www.amazon.com/dp/B000OY539A/ref=nosim?tag=nobsmed07-20",
        category="Baby Carrier Wraps",
        price_range="$45–55",
        cons="Steep learning curve for proper tying",
        pros="Versatile and very supportive for newborns",
    ),
    AmazonProduct(
        title="Boba Baby Carrier Wrap",
        url="https://www.amazon.com/Boba-Baby-Carrier-Wrap/dp/B00MZ4AXN6/ref=nosim?tag=nobsmed07-20",
        category="Baby Carrier Wraps",
        price_range="$45–55",
        cons="Can feel too snug or hot in warm climates",
        pros="Comfortable stretch with easier wrapping",
    ),
    AmazonProduct(
        title="Solly Baby Wrap",
        url="https://www.amazon.com/Solly-Baby-Wrap/dp/B00H7D7G5Y/ref=nosim?tag=nobsmed07-20",
        category="Baby Carrier Wraps",
        price_range="$80–90",
        cons="Higher price point; limited weight capacity",
        pros="Soft, lightweight fabric ideal for summer and sensitive skin",
    ),
    AmazonProduct(
        title="LILLEbaby Baby Wrap",
        url="https://www.amazon.com/LILLEbaby-Baby-Wrap/dp/B07FKKKR6W/ref=nosim?tag=nobsmed07-20",
        category="Baby Carrier Wraps",
        price_range="$60–80",
        cons="Can be bulky to carry when not in use",
        pros="Durable and supportive with ergonomic comfort",
    ),
]

post_delivery_healing_products = [
    AmazonProduct(
        title="Earth Mama Organic Perineal Spray",
        url="https://www.amazon.com/dp/B0065ZTKWS/ref=nosim?tag=nobsmed07-20",
        category="Post Delivery Healing Products",
        price_range="$10–15",
        cons="May require frequent application",
        pros="Natural ingredients and gentle relief",
    ),
    AmazonProduct(
        title="Frida Mom Perineal Cooling Pads",
        url="https://www.amazon.com/Frida-Mom-Perineal-Cooling-Instant/dp/B07W7LTMR8/ref=nosim?tag=nobsmed07-20",
        category="Post Delivery Healing Products",
        price_range="$15–20 for pack",
        cons="Single-use; ongoing cost",
        pros="Convenient and fast-acting relief",
    ),
    AmazonProduct(
        title="Lanolin Nipple Cream (Lansinoh)",
        url="https://www.amazon.com/dp/B005MI648C/ref=nosim?tag=nobsmed07-20",
        category="Post Delivery Healing Products",
        price_range="$8–15",
        cons="Can be greasy if over-applied",
        pros="Trusted and effective for breastfeeding moms",
    ),
    AmazonProduct(
        title="Tucks Medicated Cooling Pads",
        url="https://www.amazon.com/dp/B06ZYLFV8L/ref=nosim?tag=nobsmed07-20",
        category="Post Delivery Healing Products",
        price_range="$5–10",
        cons="Single-use; may cause mild dryness",
        pros="Affordable and widely available relief",
    ),
    AmazonProduct(
        title="Frida Mom Upside Down Peri Bottle",
        url="https://www.amazon.com/Frida-Mom-Upside-Down-Bottle/dp/B07W6ZBLN7/ref=nosim?tag=nobsmed07-20",
        category="Post Delivery Healing Products",
        price_range="$15–20",
        cons="Needs refilling often; only comes in one size",
        pros="Essential for gentle postpartum hygiene",
    ),
    AmazonProduct(
        title="Kindred Bravely Abdominal Recovery Binder",
        url="https://www.amazon.com/Kindred-Bravely-Belly-Bandit-Postpartum/dp/B077SCFQW1/ref=nosim?tag=nobsmed07-20",
        category="Post Delivery Healing Products",
        price_range="$45–65",
        cons="Can feel tight if worn too long",
        pros="Targeted core support for faster recovery",
    ),
    AmazonProduct(
        title="Lansinoh Hot and Cold Breast Therapy Pads",
        url="https://www.amazon.com/Lansinoh-TheraPearl-Breast-Therapy-Reusable/dp/B002KGHUL4/ref=nosim?tag=nobsmed07-20",
        category="Post Delivery Healing Products",
        price_range="$12–18",
        cons="Pads can lose heat quickly",
        pros="Dual hot/cold therapy with reusable design",
    ),
    AmazonProduct(
        title="Dermoplast Pain Relieving Spray",
        url="https://www.amazon.com/dp/B073PBPC51/ref=nosim?tag=nobsmed07-20",
        category="Post Delivery Healing Products",
        price_range="$7–10",
        cons="Not for internal use; short-acting",
        pros="Trusted hospital-grade pain relief",
    ),
    AmazonProduct(
        title="Sitz Bath Soak by Thena Natural Wellness",
        url="https://www.amazon.com/Sitz-Bath-Soak-Postpartum-Recovery/dp/B08G4LQXL1/ref=nosim?tag=nobsmed07-20",
        category="Post Delivery Healing Products",
        price_range="$15–20",
        cons="Requires separate sitz tub or basin",
        pros="Natural herbal relief with proven benefits",
    ),
]

non_toxic_infant_car_seats = [
    AmazonProduct(
        title="Stokke PIPA by Nuna Infant Car Seat",
        url="https://www.amazon.com/Stokke-Pipa-Nuna-Black-Seat/dp/B07KZLS66W/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Infant Car Seats",
        price_range="$450",
        cons="High price; limited stroller compatibility",
        pros="Outstanding safety in a super-light, non-toxic design",
    ),
    AmazonProduct(
        title="Chicco KeyFit 35 ClearTex Infant Car Seat",
        url="https://www.amazon.com/Chicco-ClearTex%C2%AE-Rear-Facing-Compatible-Strollers/dp/B08Q1LS11S/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Infant Car Seats",
        price_range="$229",
        cons="Anti‑rebound bar may reduce legroom in small cars",
        pros="Affordable, widely available, and easy to install",
    ),
    AmazonProduct(
        title="Clek Liing Infant Car Seat (Mammoth/Railroad fabric)",
        url="https://www.amazon.com/Clek-Adjustable-Lightweight-Positions-Retardant-Free/dp/B0CZPCX345/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Infant Car Seats",
        price_range="$299",
        cons="Premium price; only certain fabrics are fully non-toxic",
        pros="Premium safety and narrow design for tight car bellies",
    ),
    AmazonProduct(
        title="Maxi-Cosi Mico 30 PureCosi Infant Car Seat",
        url="https://www.amazon.com/Maxi-Cosi-Mico-Infant-Polished-Pebble/dp/B08ZGL173B/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Infant Car Seats",
        price_range="$199",
        cons="No load-leg base; lighter weight means less heft",
        pros="Affordable and non-toxic with strong safety features",
    ),
]

non_toxic_bassinets = [
    AmazonProduct(
        title="SnuzPod4 Bedside Bassinet",
        url="https://www.amazon.com/Sn%C3%BCz-SnuzPod-Bedside-Crib-Natural/dp/B08J9151BL/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Bassinets",
        price_range="$350–400",
        cons="Manual setup; no auto-soothing features",
        pros="Simple, stylish, sustainably built with non-toxic materials",
    ),
    AmazonProduct(
        title="babybay Original Bedside Sleeper",
        url="https://www.amazon.com/dp/B007NZHXZK/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Bassinets",
        price_range="$245+",
        cons="Mattress not organic; may require buying separately",
        pros="Completely natural wood design, zero-VOC finishes",
    ),
    AmazonProduct(
        title="BABYBJÖRN Cradle",
        url="https://www.amazon.com/dp/B008TML9AQ/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Bassinets",
        price_range="$199–230",
        cons="No bedside attach option; limited longevity (~6 mo)",
        pros="Highly breathable, compact, and non-toxic materials",
    ),
    AmazonProduct(
        title="BreathableBaby Mesh Portable Sleeper",
        url="https://www.amazon.com/BreathableBaby-Breathable-Mesh-Portable-Sleeper/dp/B08T7TNJWZ/ref=nosim?tag=nobsmed07-20",
        category="Non-Toxic Bassinets",
        price_range="$249",
        cons="Use limited to early months due to size",
        pros="Spacious, breathable, and environmentally conscious design",
    ),
]
