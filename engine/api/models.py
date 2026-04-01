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


class VolumeCreate(BaseModel):
    title: str
    type: str = "unknown"
    year: Optional[int] = None
    authors: List[str] = []
    format: str = "plain text"
    url: str = ""
    text: str


class VolumeDelete(BaseModel):
    volume_id: str


class InsertMarkerRequest(BaseModel):
    before_paragraph_id: str
    level: str = "scene"
    heading: Optional[str] = None


class VolumeReorder(BaseModel):
    order: List[str]  # volume IDs in desired display order


class VolumeUpdate(BaseModel):
    volume_id: str
    year: Optional[int] = None          # None = leave unchanged
    authors: Optional[List[str]] = None  # None = leave unchanged; [] = clear
    text: Optional[str] = None          # if provided, replaces source and resets curation
