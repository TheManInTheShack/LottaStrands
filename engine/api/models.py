from pydantic import BaseModel
from typing import List, Optional


class MergeRequest(BaseModel):
    level: str          # "scene", "shot", "paragraph", etc.
    indices: List[int]  # indices of nodes to merge, in order
    heading: str        # heading for the merged node


class SplitRequest(BaseModel):
    level: str
    index: int          # index of the node to split
    at_child_index: int # first child index that goes into the second half
    heading_before: Optional[str] = None
    heading_after: Optional[str] = None


class RenameRequest(BaseModel):
    level: str
    index: int
    heading: str
