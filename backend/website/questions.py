# Health hack questions and answers for pregnancy and infant care
# MY ASSOCIATE ID: nobsmed07-20
from pydantic import BaseModel


class AmazonProduct(BaseModel):
    url: str
    title: str


class HealthHack(BaseModel):
    personal_context: str
    health_hack: str
    health_disorder: str
    intended_outcomes: str
    experienced_outcomes: str
    mechanism: str
    dosage: str
    products: list[AmazonProduct] = []


class Question(BaseModel):
    question: str
    health_hacks: list[HealthHack]


# Build health hacks data
health_hacks = []
health_hacks.append(
    HealthHack(
        personal_context="Third-trimester pregnancy",
        health_hack="Raspberry leaf tea",
        health_disorder="Long labor",
        intended_outcomes="Shorter labor, easier delivery",
        experienced_outcomes="Second stage of labor was 9.6 minutes shorter on average, reduced need for forceps by 11.1%",
        mechanism="Raspberry leaf tea is believed to tone the uterine muscles, potentially leading to more effective contractions during labor.",
        dosage="2.4 grams per day (2-4 cups of tea, depending on strength)",
        products=[
            AmazonProduct(
                url="https://www.amazon.com/MAC-BOTANICALS-Organic-Raspberry-Leaves/dp/B0BG3JT4F9/ref=nosim?tag=nobsmed07-20",
                title="J MAC BOTANICALS, Organic Red Raspberry Leaf, Herbal Tea (16 Ounce Bag 200+ Cups) Cut & sifted Dried Leaf",
            )
        ],
    )
)
health_hacks.append(
    HealthHack(
        personal_context="Third-trimester pregnancy",
        health_hack="Date Fruit",
        health_disorder="Long labor",
        intended_outcomes="Shorter labor, easier delivery",
        experienced_outcomes="First stage cervical dilation was 3.5 cm vs. 2 cm in the non-date group; spontaneous labor in 96% of date consumers vs. 79% in non-date group, duration of first stage was 8.5 hours vs. 15 hours, 25% more intact membranes",
        mechanism="chemical binding that effects oxytocin receptors, leading to more effective contractions",
        dosage="4 dates per day (about 70 grams)",
        products=[
            AmazonProduct(
                url="https://www.amazon.com/Terrasoul-Superfoods-Organic-Medjool-Pounds/dp/B01MREWFHO/ref=nosim?tag=nobsmed07-20",
                title="Terrasoul Superfoods Organic Medjool Dates, 2 Lbs - Soft Chewy Texture | Sweet Caramel Flavor | Farm Fresh",
            )
        ],
    )
)

# Build questions list
question = Question(
    question="In my third trimester of pregnancy, what health hacks can help me have a shorter and easier labor?",
    health_hacks=health_hacks,
)
questions = []
questions.append(question)
