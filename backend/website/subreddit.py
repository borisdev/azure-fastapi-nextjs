import json
from enum import StrEnum
from pathlib import Path
from typing import Any, List, Optional

import instructor
import praw
from loguru import logger
from openai import AzureOpenAI, OpenAI
from pydantic import BaseModel, Field
from rich import print
from website.chain import Chain

platform = "mac"
app_name = "nobsmed-anecdotal-experiences"
app_version = "0.1.0"
reddit_username = "Vast-Box-3388"
user_agent = f"{platform}:{app_name}:{app_version} (by /u/{reddit_username})"

reddit_app_client_id = "nUpb-ybo9WyrP2t_xL6BOg"
reddit_app_client_secret = "Lkk8CAJzj16HXTd7PBGbuU-huo7GaA"

reddit_client = praw.Reddit(
    client_id=reddit_app_client_id,
    client_secret=reddit_app_client_secret,
    password="",  # password is not needed for read-only access
    user_agent=user_agent,
    username="Vast-Box-3388",
)

reddit_client.read_only = True


# REPO_DIR = Path(__file__).parents[3]
# REDDIT_DIR = Path(REPO_DIR) / "data" / "subreddits"


# if flair_text tag contains any of these tokens, then the submission is relevant
whitelist_tokens = [
    "medical",
    "treatment",
    "medication",
    "triggers",
    "surgery",
    "success",
    "supplement",
    "therapy",
    "prescription",
    "infertility",
    "hypothyroidism",
    "hashimoto",
    "sleep",
    "side effects",
    "Meds",
    "Subtype",
    "Success",
    "tests",
    "food",
    "skin",
    "GERD",
]


class Comment(BaseModel):
    """

    - author Provides an instance of Redditor.
    - body The body of the comment, as Markdown.
    - body_html The body of the comment, as HTML.
    - created_utc Time the comment was created, represented in Unix Time.
    - distinguished Whether or not the comment is distinguished.
    - edited Whether or not the comment has been edited.
    - id The ID of the comment.
    - is_submitter Whether or not the comment author is also the author of the submission.
    - link_id The submission ID that the comment belongs to.
    - parent_id The ID of the parent comment (prefixed with t1_). If it is a
      top-level comment, this returns the submission ID instead (prefixed with
                                                                 t3_).
    - permalink A permalink for the comment. Comment objects from the inbox have a context attribute instead.
    - replies Provides an instance of CommentForest.
    - saved Whether or not the comment is saved.
    - score The number of upvotes for the comment.
    - stickied Whether or not the comment is stickied.
    - submission Provides an instance of Submission. The submission that the comment belongs to.
    - subreddit Provides an instance of Subreddit. The subreddit that the comment belongs to.
    - subreddit_id The subreddit ID that the comment belongs to.
    """

    author: Optional[str] = None
    body: Optional[str] = None
    body_html: Optional[str] = None
    created_utc: Optional[int] = None
    distinguished: Optional[str] = None
    edited: Optional[int] = None
    id: Optional[str] = None
    is_submitter: Optional[bool] = None
    link_id: Optional[str] = None
    parent_id: Optional[str] = None
    permalink: Optional[str] = None
    # replies: Optional[Any] = None
    saved: Optional[bool] = None
    score: Optional[int] = None
    stickied: Optional[bool] = None
    # CONTEXT
    previous_comment_text: Optional[str] = None
    submission_title: Optional[str] = None
    submission_selftext: Optional[str] = None
    enrichment: Optional[Any] = None
    submission_question: Optional[str] = None
    relevant: Optional[bool] = None  # post-download enrichment

    @classmethod
    def from_praw(cls, comment):
        try:
            author_name = comment.author.name
        except AttributeError:
            raise ValueError("Author name is not available")
        return cls(
            author=author_name,
            body=comment.body,
            body_html=comment.body_html,
            created_utc=comment.created_utc,
            distinguished=comment.distinguished,
            edited=comment.edited,
            id=comment.id,
            is_submitter=comment.is_submitter,
            link_id=comment.link_id,
            parent_id=comment.parent_id,
            permalink=comment.permalink,
            # replies=comment.replies,
            saved=comment.saved,
            score=comment.score,
            stickied=comment.stickied,
        )


class PredictThreadRelevanceInputSchema(BaseModel):
    title: str
    selftext: str


class PredictThreadRelevanceResponse(BaseModel):
    relevance: bool = Field(
        title="Anectodal Experiences Relevance",
        description="""
            True - Answer with true if comments in this subreddit group provide anectodal evidence on the effectives of different treatments or interventions on treating medical disorders.
            False - Answer false if this subreddit group will not provide anectodal evidence on the effectives of different treatments or interventions treating medical disorders.
            """,
    )


class PredictThreadRelevanceChain(Chain):

    input_schema = PredictThreadRelevanceInputSchema
    output_schema = PredictThreadRelevanceResponse

    @classmethod
    def make_input_text(cls, *, input: PredictThreadRelevanceInputSchema) -> str:
        input_text = f"""
        Title: {input.title}
        Selftext: {input.selftext}
        """
        return input_text


class Submission(BaseModel):
    author: Optional[str] = None
    author_flair_text: Optional[str] = None
    clicked: Optional[bool] = None
    comments: Optional[List[Comment]] = None
    created_utc: Optional[int] = None
    distinguished: Optional[str] = None
    edited: Optional[int] = None
    id: Optional[str] = None
    is_original_content: Optional[bool] = None
    is_self: Optional[bool] = None
    link_flair_template_id: Optional[str] = None
    link_flair_text: Optional[str] = None
    locked: Optional[bool] = None
    name: Optional[str] = None
    num_comments: Optional[int] = None
    over_18: Optional[bool] = None
    permalink: Optional[str] = None
    saved: Optional[bool] = None
    score: Optional[int] = None
    selftext: Optional[str] = None
    spoiler: Optional[bool] = None
    stickied: Optional[bool] = None
    title: Optional[str] = None
    upvote_ratio: Optional[float] = None
    url: Optional[str] = None
    total_awards_received: Optional[int] = None
    gilded: Optional[int] = None
    relevant: Optional[bool] = None  # post-download enrichment

    @property
    def tag_as_not_seeking_empathy(self) -> bool:
        if self.link_flair_text is None:
            return True
        else:
            if "empathy" in self.link_flair_text.lower():
                return False
            else:
                return True

    @property
    def tag_in_whitelist(self) -> bool:
        # if flair_text tag contains any of these tokens, then the submission is relevant
        whitelist_tokens = [
            "medical",
            "treatment",
            "medication",
            "triggers",
            "surgery",
            "success",
            "supplement",
            "therapy",
            "prescription",
            "infertility",
            "hypothyroidism",
            "hashimoto",
            "sleep",
            "side effects",
            "Meds",
            "Subtype",
            "Success",
            "tests",
            "food",
            "skin",
            "GERD",
        ]
        if self.link_flair_text is None:
            return True
        else:
            for token in whitelist_tokens:
                if token.lower() in self.link_flair_text.lower():
                    return True
        return False

    @classmethod
    def from_praw(cls, submission):

        relevant_submission = False
        link_flair_text = getattr(submission, "link_flair_text", None)
        if link_flair_text is None:
            result = PredictThreadRelevanceChain.predict(
                max_tokens=50,
                llm_name="gpt-4o-mini",
                input_object=PredictThreadRelevanceInputSchema(
                    title=submission.title, selftext=submission.selftext
                ),
            )
            if result.relevance:
                relevant_submission = True
            else:
                relevant_submission = False
        else:
            for token in whitelist_tokens:
                if token.lower() in submission.title.lower():
                    relevant_submission = True
                    break
        if not relevant_submission:
            # logger.warning(f"Skipping submission: {submission.title}")
            raise ValueError("Submission is not relevant")
        else:
            pass
            # logger.success("Relevant submission")
            # logger.success(submission.title)
            # logger.info(submission.selftext)

        comment_objs = []
        comments = submission.comments.list()
        if comments is not None and len(comments) > 0:
            for comment in comments:
                try:
                    comment_obj = Comment.from_praw(comment)
                    comment_objs.append(comment_obj)
                except ValueError as e:
                    logger.error("Error creating comment object, skipping comment")
                    logger.error(e)
                    continue
        try:
            author_name = submission.author.name
        except AttributeError:
            raise ValueError("Author name is not available")
        return cls(
            author=author_name,
            author_flair_text=submission.author_flair_text,
            clicked=submission.clicked,
            comments=comment_objs,
            created_utc=submission.created_utc,
            distinguished=submission.distinguished,
            edited=submission.edited,
            id=submission.id,
            is_original_content=submission.is_original_content,
            is_self=submission.is_self,
            link_flair_template_id=getattr(submission, "link_flair_template_id", None),
            link_flair_text=submission.link_flair_text,
            locked=submission.locked,
            name=submission.name,
            num_comments=submission.num_comments,
            over_18=submission.over_18,
            permalink=submission.permalink,
            # poll_data=submission.poll_data,
            saved=submission.saved,
            score=submission.score,
            selftext=submission.selftext,
            spoiler=submission.spoiler,
            stickied=submission.stickied,
            title=submission.title,
            upvote_ratio=submission.upvote_ratio,
            url=submission.url,
            total_awards_received=submission.total_awards_received,
            gilded=submission.gilded,
        )


class FetchedSubreddit(BaseModel):
    display_name: str
    title: str
    public_description: str
    subscribers: Optional[int] = None
    submissions: list[Submission]

    @classmethod
    def load_from_subreddit_name(cls, subreddit_name: str) -> "FetchedSubreddit":
        logger.warning(
            f"Deprecated for FetchedSubreddit ....Loading data from subreddit: {subreddit_name}"
        )
        print(f"Loading data from subreddit: {subreddit_name}")
        source_file_path = (
            Path(REDDIT_DIR) / f"subreddit_{subreddit_name}_submissions.json"
        )

        logger.debug(f"Loading data from {source_file_path}")
        with open(source_file_path, "r") as f:
            data = json.load(f)
        logger.success(f"Loaded data from {source_file_path}")

        return cls(**data)

    def get_submissions(
        self,
        whitelist_tag_filter: bool,
    ) -> List[Submission]:
        """Get valid submissions from the subreddit"""

        relevant_submissions = []
        all_submissions = [
            s
            for s in self.submissions
            if s.author != "AutoModerator"
            and s.tag_as_not_seeking_empathy
            and s.link_flair_text != "Mod Announcement"
        ]

        if whitelist_tag_filter:
            white_listed_submissions = [
                s for s in all_submissions if s.tag_in_whitelist
            ]
            relevant_submissions = white_listed_submissions
        else:
            relevant_submissions = all_submissions
        logger.warning(f"whitelist_tag_filter: {whitelist_tag_filter}")
        logger.info(f"Submissions: {len(relevant_submissions)}")

        for submission in relevant_submissions:
            comments = submission.comments
            if comments is not None:
                for comment in comments:
                    if comment.author == "AutoModerator" or comment.body is None:
                        del comment
        return relevant_submissions

    @classmethod
    def from_reddit_api(cls, *, subreddit_display_names: List[str]) -> None:
        error_messages = []
        comment_count = 0
        idxes = range(len(subreddit_display_names))

        for idx, subreddit_display_name in enumerate(subreddit_display_names):
            logger.info(
                f"{subreddit_display_name}: {idx} of {len(idxes)} subreddits, {comment_count} grand total comments"
            )
            data = {}
            subreddit_display_name = subreddit_display_name.replace("r/", "")
            subreddit_object = reddit_client.subreddit(subreddit_display_name)

            class SubredditMeta(BaseModel):
                title: str
                display_name: str
                name: str
                description: str
                public_description: str
                subscribers: int

            print(f"Subreddit: {subreddit_object}")
            data["title"] = subreddit_object.title
            data["display_name"] = subreddit_object.display_name
            data["name"] = subreddit_object.name
            data["description"] = subreddit_object.description
            data["public_description"] = subreddit_object.public_description
            data["subscribers"] = subreddit_object.subscribers
            # validate data
            SubredditMeta(**data)
            submission_objects = []
            submission_count = 0
            for submission in subreddit_object.hot(limit=None):
                try:
                    submission_object = Submission.from_praw(submission)
                    submission_count += 1
                    submission_objects.append(submission_object)
                    if submission_object.comments is not None:
                        comment_count += len(submission_object.comments)
                    else:
                        comment_count += 0
                except Exception as e:
                    # logger.error(
                    #     f"{subreddit_display_name}: Error getting submission: {e}"
                    # )
                    error_message = (
                        f"{subreddit_display_name}: Error getting submission: {e}"
                    )
                    error_messages.append(error_message)
                    continue
            data["submissions"] = submission_objects
            instance = cls(**data)
            sink_file = f"subreddit_{subreddit_display_name}_submissions.json"
            sink_file = REDDIT_DIR / sink_file
            logger.info(f"Writing to sink file: {sink_file}")
            with open(sink_file, "w") as f:
                f.write(instance.model_dump_json(indent=2))
            logger.success(
                f"Subreddit: {subreddit_display_name} has {len(submission_objects)} submissions written to {sink_file}, {comment_count} grand total comments"
            )
            print(f"Error messages: {error_messages}")
        print(f"Error messages: {error_messages}")


biohacker_subreddits = [
    # 13 best subreddits for biohackers https://daveasprey.com/best-biohacker-subreddits/
    ## didnt work "r/HumanPerformance",
    "r/Biohackers",
    "r/DecidingToBeBetter",
    "r/EatCheapAndHealthy",
    "r/Fitness",
    "r/GetMotivated",
    "r/HIIT",
    "r/Health",
    "r/Healthygamers",
    "r/IntermittentFasting",
    "r/Keto",
    "r/Longevity",
    "r/Meditation",
    "r/Nootropics",
    "r/Nutrition",
    "r/Psychology",
    "r/QuantifiedSelf",
    "r/Supplements",
    "r/Transhumanism",
]
sleep_subreddits = [
    "r/Dreams",
    "r/Sleep",
    "r/SleepHacks",
    "r/SleepApnea",
    "r/GetOutOfBed",
    "r/Insomnia",
]
fertility = {
    # r/IVF
    "Fertility": "Fertility",
    "FirstTimeTTC": "First Time Trying to Conceive",
    "Infertility": "Infertility",
    "InfertilityBabies": "Pregnancy after Infertility Struggle",
    "PCOS": "Polycystic Ovary Syndrome (PCOS)",
    "SecondaryInfertility": "Secondary Infertility",
    "TFABChartStalkers": "Trying to Conceive Data Analysis",
    "TTC30": "Trying to Conceive Over 30",
    "TTC40": "Trying to Conceive Over 40",
    "TTC_PCOS": "Trying to Conceive with PCOS",
    "TTChealthy": "Trying to Conceive & Health",
    "TryingForABaby": "Trying For A Baby",
    "secondaryinfertility": "Secondary Infertility",
    "stilltrying": "Trying to Conceive for a While",
    "tryingforanother": "Trying for Another Baby",
    "ttchealthy": "Trying to Conceive & Health",
    "whatworkedforme": "Trying to Conceive Success Stories",
}
pregnancy_subreddits = [
    "r/BabyBumps",
    "r/BB30",
    "r/Mommit",
    "r/CautiousBB",
    "r/fitpregnancy",
    "r/pregnant",
    "r/moderatelygranolamoms",
    "r/BabyBumpsandBeyondAu",
    "r/BabyBumpsCanada",
    "r/babyloss",
    "r/doulas",
    "r/ectopicpregnancy",
    "r/EctopicSupportGroup",
    "r/EmpoweredBirth",
    "r/FitPostpartumJourney",
    "r/homebirth",
    "r/Midwives",
    "r/Miscarriage",
    "r/NIPT",
    "r/PCOSandPregnant",
    "r/PlusSizePregnancy",
    "r/Postpartum_Depression",
    "r/PostpartumAnxiety",
    "r/postpartumprogress",
    "r/pregnancy_care",
    "r/PregnancyAfterTFMR",
    "r/pregnancyproblems",
    "r/PregnancyUK",
    "r/PregnantbyIVF",
    "r/Seahorse_Dads",
    "r/ShortCervixSupport",
    "r/tfmr_support",
    "r/Tokophobia",
]
new_biohacker_subreddits = [
    "r/Neuroscience",
    "r/BecomingTheIceman",
    "r/Biohacked",
    "r/Biohacking",
    "r/HubermanLab",
    "r/Meditation",
    "r/Peptides",
    "r/RationalPsychonaut",
    "r/biohackingscience",
    "r/getdisciplined",
    "r/intermittentfasting",
    "r/ketoscience",
    "r/longevity",
]


if __name__ == "__main__":
    # subreddit_display_names = sleep_subreddits + biohacker_subreddits
    subreddit_display_names = pregnancy_subreddits
    FetchedSubreddit.from_reddit_api(subreddit_display_names=subreddit_display_names)
    subreddit_display_names = new_biohacker_subreddits
    FetchedSubreddit.from_reddit_api(subreddit_display_names=subreddit_display_names)
