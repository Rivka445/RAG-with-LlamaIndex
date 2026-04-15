from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ItemSource(BaseModel):
    tool: str = Field(description="הכלי שבו נכתב המסמך (למשל cursor, claude)")
    file: str = Field(description="נתיב הקובץ")
    anchor: Optional[str] = Field(None, description="כותרת/עוגן קרוב למידע (למשל '## Setup')")
    line_range: Optional[List[int]] = Field(None, description="טווח שורות [התחלה, סיום]")


class Decision(BaseModel):
    id: str = Field(description="מזהה ייחודי (למשל dec-001)")
    title: str = Field(description="כותרת תמציתית של ההחלטה")
    summary: str = Field(description="פירוט ההחלטה והסיבה")
    tags: List[str] = Field(default=[], description="תגיות (למשל: db, auth, frontend)")
    source: ItemSource
    observed_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class Rule(BaseModel):
    id: str = Field(description="מזהה ייחודי (למשל rule-001)")
    rule: str = Field(description="תיאור הכלל או ההנחיה")
    scope: str = Field(description="תחום היישום (למשל: ui, testing, security)")
    notes: Optional[str] = Field(None, description="הערות או חריגים")
    source: ItemSource
    observed_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class WarningItem(BaseModel):
    id: str = Field(description="מזהה ייחודי (למשל warn-001)")
    area: str = Field(description="הרכיב או האזור שבו יש להיזהר")
    message: str = Field(description="תוכן האזהרה")
    severity: str = Field(description="רמת חומרה: high, medium, low")
    source: ItemSource
    observed_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ProjectItems(BaseModel):
    decisions: List[Decision] = Field(default_factory=list)
    rules: List[Rule] = Field(default_factory=list)
    warnings: List[WarningItem] = Field(default_factory=list)


class FileInfo(BaseModel):
    path: str
    last_modified: str
    hash: str


class SourceMetadata(BaseModel):
    tool: str
    root_path: str
    files: List[FileInfo] = Field(default_factory=list)


class ExtractedProjectData(BaseModel):
    schema_version: str = "1.1"
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    sources: List[SourceMetadata] = Field(default_factory=list)
    items: ProjectItems = Field(default_factory=lambda: ProjectItems())
