# amazon_cgm_search = AmazonSearch(
#     search_term="continuous glucose monitor",
#     search_url="https://www.amazon.com/s?k=continuous+glucose+monitor&crid=NA3KJZEKET1Z&sprefix=Continuous+Gluci%2Caps%2C230&linkCode=ll2&tag=nobsmed-20&linkId=d07f81f39ce99933b9f143d92900f1ff&language=en_US&ref_=as_li_ss_tl",
# )
class AmazonSearch(BaseModel):
    search_term: str
    search_url: str


class AmazonListing(BaseModel):
    asin: str
    link: str
    price: float
    rating: float
    reviews: int
    url: str
    image: str
    description: str
