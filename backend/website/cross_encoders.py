import math

from pydantic import BaseModel
from rich import print
from sentence_transformers.cross_encoder import CrossEncoder

# https://huggingface.co/docs/transformers/model_doc/auto#auto-classes
# https://www.sbert.net/examples/applications/cross-encoder/README.html
# https://www.sbert.net/docs/pretrained_cross-encoders.html
# "cross-encoder/ms-marco-TinyBERT-L-12-v2",
# "cross-encoder/ms-marco-MiniLM-L-12-v2"  # BEST
# "msmarco-distilbert-base-v4",  # best

# Relevance Threshold .20
ketamine_text = """

ketmine hurts social life.

Chronic migraine costs society a lot of money.

Real-world study of intranasal ketamine for use in patients with refractory chronic migraine.

Subanesthetic ketamine infusion has been used for managing refractory headache in inpatient or outpatient infusion settings. Intranasal (IN) ketamine may be an alternative option for outpatient care.

We performed a retrospective study at a single tertiary headache center to assess the clinical effectiveness and tolerability of IN ketamine in patients with refractory chronic migraine (rCM). Candidates who received IN ketamine between January 2019 and February 2020 were screened through an electronic medical record query. Manual chart reviews and structured phone interviews were conducted upon obtaining informed consent.

Among 242 subjects screened, 169 (age 44.3±13.8; female 79.9%) were interviewed. They reported 25.0±8.7 monthly headache days and tried 6.9±3.1 preventive medications. Overall, they used roughly 7.8±7.0 sprays (ie., 78 mg) per day and 11.6±8.9 days per month. Intranasal ketamine was reported as “very effective” in 49.1% and quality of life (QOL) was considered “much better” in 35.5%. However, 74.0% reported at least one adverse event (AE).

In this retrospective study, IN ketamine can serve as an acute treatment for rCM by reducing headache intensity and improving QOL with relatively tolerable AEs. Most patients found IN ketamine effective and continued to use it despite these AEs. The study is limited by its single-center design and selection/recall biases. Well-designed prospective placebo-controlled trials are necessary to demonstrate the efficacy and safety of IN ketamine in patients with migraine.
"""


def sigmoid(x):
    result = 1 / (1 + math.exp(-x))
    return result


def format_score(score):
    r = sigmoid(score)
    r = float(r)
    r = round(r, 2)
    return r


class Concepts(BaseModel):
    treatment: str
    mechanism: str
    why: str
    cause: str
    effect: str
    result: str


class CrossEncoderModel:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = CrossEncoder(self.model_name)

    def predict_new(self, question, biohacks):
        pairs = zip(biohacks, [question] * len(biohacks))
        pairs = list(pairs)
        scores = self.model.predict(pairs)
        scores = [format_score(score) for score in scores]
        results = zip(biohacks, scores)
        results = dict(results)
        return results

    def predict(self, passage, problem, treatment):
        concepts = Concepts(
            **dict(
                treatment=f"What are treatments for {problem}?",
                mechanism=f"What is the mechanism for {treatment} to treat {problem}?",
                why=f"What are the mechanisms, pathways, causes or reasons {treatment} reduces {problem}?",
                cause=f"What is the bio-chemical effects of {treatment} on the body?",
                effect=f"What is the effect of {treatment} intervention on the patients or subjects?",
                result=f"What was the evaluation, result or outcome of {treatment} on the patients or subjects?",
                side_effects=f"What are the adverse, side-effects of {treatment}?",
            )
        )
        concept_names = []
        pairs = []
        for concept, question in concepts.dict().items():
            pairs.append((question, passage))
            concept_names.append(concept)
        # from pprint import pprint

        # pprint(pairs)
        scores = self.model.predict(pairs)
        scores = [format_score(score) for score in scores]
        results = zip(concept_names, scores)
        results = dict(results)
        return results


if __name__ == "__main__":
    cross_encoder = CrossEncoderModel(
        model_name="cross-encoder/ms-marco-MiniLM-L-12-v2"
    )
    question = "Vegetarian diet and Pregnancy"
    biohacks = [
        "Omega-3 fatty acids for vegetarians",
        "Vitamin B12 for vegetarians",
        "Vitamin D for vegetarians",
        "Iron for pregnant vegetarians",
        "Farting while pregnant",
        "Diabetes and pregnancy",
        "Pregnancy and vegetarianism",
        "Pregnancy and diet",
        "Pregnancy and meat eating",
        "Vegetarianism and excercise",
        "Being Vegan and a healthy baby",
    ]
    results = cross_encoder.predict_new(question, biohacks)
    print(results)
    # problem = "migraine"
    # treatment = "ketamine"
    # sentences = ketamine_text.split("\n\n")
    # count = 1
    # for sentence in sentences:
    #     passage = sentence.strip()
    #     if passage != "":
    #         count += 1
    #         scores = cross_encoder.predict(passage, problem, treatment)
    #         print(f"{count}  {sentence}")
    #         print(scores)
