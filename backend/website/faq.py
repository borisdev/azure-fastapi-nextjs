from typing import List, Optional, Union

from pydantic import BaseModel, Field

from website.deep_experiences import DeepExperience


class FAQ(BaseModel):

    question: str  # validate its uniqueness
    slug: str
    deep_experiences: Optional[List[DeepExperience]] = None

    # below automatically generated
    # rather than remembering to add code to changing instantiation logic
    # @cached_property  # just run once after deserialization
    # @computed_field  # based on other fields and included in serialization
