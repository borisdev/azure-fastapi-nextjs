## UI depends on .....

```
poetry run python -m website.pydantic_ai_examples.pydantic_model
```

Biomarkers

3,000 to 50,000 studies

LLM GAME PLAN ??

1. Just use opensearch to find experience with related words - or neural search actions outcomes takeway?
   or tell LLM just to return True or False for each experience and Question relevance
2. GAME PLAN

Biohack cards

UI

-   IMAGES ??
-   STREAM TEXT
-   Cols, arrows, buttons, badges
-   Mix all card types BUT allow filtering like Conner. OR just rank order??

CONTEXT

-   mini title - teaser
-   action
-   impact
-   mechanism
-   relevant studies
-   relevant experiences
-   indirect effects
-   link to full Biohack w all relevant studies and experiences
-   PRE-RUN BIOHACK SUMMARIES

```python

## 1st CREATE EXPERIENCES FOR ALL subreddits???
## 2nd get the docs for each biohack subclass
## 3rd for each biohack subclass cluster the docs
## 4th HYDATE EXPERIENCES WITH BERTopic_simple topics
## 5th show a taxonmoy in UI  ....device...d.topics...supplements..s.topics etc

subtypes = ["Diet", "Devices", "Medications", "Supplements"]
docs = defaultdict(list)
for subtype in subtypes:
    for topic in topics:
        for experience in experiences:
            if experience["biohack_subtype"]:
                docs[experience["biohack_subtype"]].append(experience)

## Then use BERTopic_simple to cluster the doc
lookup_doc2topic
use lookup_doc2topic populate `experience.topic` for each experience
```

## UI

Question: "Blueprint diet"

Diet

    t1 Blueprint diet
    t2 Ketogenic diet and Blueprint diet\

Supplement

    Blueprint diet and supplements
    Supplements and Blueprint diet

Exercise

    BlueGherkinGherkinprint diet and exercise
    Exercise and Blueprint diet

# Topics

-   Pregnancy
-   Sleep

# Topics Alternatives

-   Diet
-   Devices
-   Medications
-   Supplements

# We are giving users either a new weapon or a new medicine.

-   MUST DOCUMENT THIS PROJECT OR ELSE I WILL FORGET WHERE I LEFT OFF
-   open ai large handled is best because it handles "eyemask" best BUT still groups it with "weighted blanket"
-   use o1 to pick out hard negatives and score total performance - then fine-tune

```plaintext
user question ⇨ increase causal scope ➡ query (OpenSearch) ➡ LLM re-ranking + summary  ⇨ user answer
                                          ↕
                      studies ➡ opensearch index
                                    ↗
                                experiences
                               ↗         ↕     ⇨ website SEO content
                    reddit posts ➡     FAQs

```

TODOs

Backlog:

-   [ ] MVP Tests: Sleep, CSVD, Pregnancy, Prediabetes, Thyroid, PCOS, Transplant
-   [ ] Cache questions in OpenSearch

    """
    https://opensearch.org/docs/latest/search-plugins/knn/knn-index/#hnsw-memory-estimation
    HNSW memory estimation
    The memory required for HNSW is estimated to be 1.1 _ (4 _ dimension + 8 \* M) bytes/vector.

    Doc example with 1 million vectors of dimension 256 and M=16:

        >>> (1.1 * (4 * 256 + 8 * 16) * 1000000) / 10**9
        1.2672 GB

    My index has 100K experiences of dimension 384 and M=16

        >>> (1.1 * (4 * 384 + 8 * 16) * 100000) / 10**9

    My OLD cloud system had .5 GB for Opensearch so .25 GB for embeddings
    Compute says at .18 GB for embeddings, it was running out of memory

    4 GB systm RAM --> 2 GB for Opensearch --> 1 GB for embeddings (HEAP SIZE for HNSW graph)
    Available memory = (RAM - Elasticsearch Max Heap Size) \* Circuit Breaker Limit (i.e. 0.5 for 50%)
    To estimate the amount of memory your graphs will take up, we use the following formula:

    Total graph memory = 1.1 * (8*M + 4*dimension) * number of vectors (including replicas)
    For efficient queries:

    Total graph memory < Available memory
    """

    """
    PART 2: Score Biohacks, Answer the User's Question,

    -   try X, before Y because .....
    -   warnings about side effects
    -   warning about personal context
    -   what other mainstream sites say: google AI says, what AskAI says, what webMD days
    -   what main stream sites are missing:.........

    Biohack Score!!! First quadrants. Then score wihin quadarants.
    AFTER CLUSSTERING SPEED Up - GIVE YOU A DIRECT ANSWR WITH RESULTS
    test natural search "AND OR NOT"
    phrase extract broken
    mechanisms - snomed physiolocical term
    sparse embed !

    Evaluation to see if dense embeddings increase recall?

    -   Fart
    -   REM sleep
    -   Nausea and Bloating with pr-natal vitamins or pregnancy vitamins

    ## Agent tasks

    -   evaluate biohack recall dynamically ..."found 10 biohacks not in X, Y,
        Z", search for biohacks not show up in google ai, google search site:
        reddit.com, Ask AI
    -   user search history
    -   get studies dynamically after getting biohacks, then ask user to if he wants to go deeper
    -   opensarch aggregations of experiences and studies....then ask user if he wants to go deeper

    # parse sentence

    # generate synonyms for each part

    # maybe use OpenAI

Pre-compute clusters

    - action to biohack
    - maybe cluster by disorder also

Heirarchical clustering

    # since I have the heirarchical topics, I can lower the min_topic_size to 2
    # then use a threshold to filter out the smaller clusters in the frontend
    # remember the structure is a binary tree, every parent has 2 children

USE O1

-   handle randoms with o1
-   fine-tune again: use o1 to pick out hard negatives and score total performance

Pool all types of actions for next training?

Why?

-   Speed: once we have biohack name each experience belongs to, then don't need LLM experience clustering
-   SEO: make biohack static pages

Models

-   all-MiniLM-L6-v2 - fast and easy
-   all-MiniLM-L6-v2-mmr - fine-tuned, just for action, biohack subtype
-   text-embedding-3-large - BEST

Evaluation report
Report on baseline model

---

131 Topic when using biohack_subtype field
biohack_subtype is much better than actions
CPAP should be clustered more
Why CPAP in -1 cluster?
Random -1 should be broken down into clusters??? # n 129 when using reduced outliers from 432 to 50 in -1 outliers

    HAVE LLM PICKOUT ERRORS IN EACH CLUSTER
    mmr fine-tuned Errors
    ------------------------
    "Using a Bluetooth eyemask for sleep" is in CPAP Therapy Cluster

    open large has this weird cluster:
    ------------------------
    136: [
        'Using a weighted eye-mask for sleep and headache relief',
        'Using a Bluetooth sleep mask',
        'Using a sleep mask',
        'Using a weighted blanket for sleep',
        'Using a Bluetooth eyemask for sleep',
        'Using a 20lbs weighted blanket',
        'Using a weighted sleep mask to block out light and provide a cooling effect during sleep.',
        'Using a 10lb Luxe Weighted Blanket from Italic to help with anxiety at night.'
    ],

"""
