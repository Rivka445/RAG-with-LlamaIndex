"""
extract.py - Structured Data Extraction using LlamaIndex
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from llama_index.core import SimpleDirectoryReader
from llama_index.core.prompts import PromptTemplate
from llama_index.llms.openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
from models import (
    Decision, Rule, WarningItem,
    ExtractedProjectData, SourceMetadata, FileInfo,
)


class ExtractedDecisions(BaseModel):
    decisions: List[Decision] = Field(default_factory=list)

class ExtractedRules(BaseModel):
    rules: List[Rule] = Field(default_factory=list)

class ExtractedWarnings(BaseModel):
    warnings: List[WarningItem] = Field(default_factory=list)


def _file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return f"sha256:{h.hexdigest()}"


def _file_last_modified(path: str) -> str:
    ts = os.path.getmtime(path)
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _renumber(items: list, prefix: str, start: int) -> int:
    for item in items:
        item.id = f"{prefix}-{start:03d}"
        start += 1
    return start


def run_extraction(base_data_dir: str | None = None, output_file: str | None = None):
    if base_data_dir is None:
        base_data_dir = str(Path(__file__).resolve().parent.parent / "data")
    if output_file is None:
        output_file = str(Path(__file__).resolve().parent / "structured_project_data.json")

    llm = OpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

    print(f"Scanning: {base_data_dir}")
    documents = SimpleDirectoryReader(input_dir=base_data_dir, recursive=True).load_data()

    result = ExtractedProjectData()
    dec_counter, rule_counter, warn_counter = 1, 1, 1
    sources_map: dict[str, SourceMetadata] = {}
    now = datetime.now(tz=timezone.utc).isoformat()

    for doc in documents:
        file_path = doc.metadata.get("file_path", "unknown")
        tool = os.path.basename(os.path.dirname(file_path))
        print(f"  [{tool}] {os.path.basename(file_path)}")

        if tool not in sources_map:
            sources_map[tool] = SourceMetadata(tool=tool, root_path=os.path.dirname(file_path))
        sources_map[tool].files.append(FileInfo(
            path=file_path,
            last_modified=_file_last_modified(file_path),
            hash=_file_hash(file_path),
        ))

        ctx = f"tool={tool}, file={file_path}, now={now}"

        # --- Decisions ---
        try:
            extracted = llm.structured_predict(
                ExtractedDecisions,
                PromptTemplate(
                    "Extract all technical decisions from the text below.\n"
                    "Context: {ctx}\n"
                    "For each decision set: id=dec-NNN, title, summary, tags, "
                    "source.tool={tool}, source.file={file}, source.anchor=nearest heading, "
                    "source.line_range=null, observed_at={now}\n\n"
                    "Text:\n{text}"
                ),
                ctx=ctx, tool=tool, file=file_path, now=now, text=doc.text,
            )
            dec_counter = _renumber(extracted.decisions, "dec", dec_counter)
            result.items.decisions.extend(extracted.decisions)
            print(f"    decisions: {len(extracted.decisions)}")
        except Exception as e:
            print(f"    decisions ERR: {e}")

        # --- Rules ---
        try:
            extracted_r = llm.structured_predict(
                ExtractedRules,
                PromptTemplate(
                    "Extract all rules and guidelines from the text below.\n"
                    "Context: {ctx}\n"
                    "For each rule set: id=rule-NNN, rule (description), scope (ui/testing/security/db/api), "
                    "notes, source.tool={tool}, source.file={file}, source.anchor=nearest heading, "
                    "source.line_range=null, observed_at={now}\n\n"
                    "Text:\n{text}"
                ),
                ctx=ctx, tool=tool, file=file_path, now=now, text=doc.text,
            )
            rule_counter = _renumber(extracted_r.rules, "rule", rule_counter)
            result.items.rules.extend(extracted_r.rules)
            print(f"    rules: {len(extracted_r.rules)}")
        except Exception as e:
            print(f"    rules ERR: {e}")

        # --- Warnings ---
        try:
            extracted_w = llm.structured_predict(
                ExtractedWarnings,
                PromptTemplate(
                    "Extract all warnings, sensitivities and 'do not touch' notes from the text below.\n"
                    "Context: {ctx}\n"
                    "For each warning set: id=warn-NNN, area, message, severity (high/medium/low), "
                    "source.tool={tool}, source.file={file}, source.anchor=nearest heading, "
                    "source.line_range=null, observed_at={now}\n\n"
                    "Text:\n{text}"
                ),
                ctx=ctx, tool=tool, file=file_path, now=now, text=doc.text,
            )
            warn_counter = _renumber(extracted_w.warnings, "warn", warn_counter)
            result.items.warnings.extend(extracted_w.warnings)
            print(f"    warnings: {len(extracted_w.warnings)}")
        except Exception as e:
            print(f"    warnings ERR: {e}")

    result.sources = list(sources_map.values())

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.model_dump_json(indent=2))

    print(f"\nDone: {len(result.items.decisions)} decisions, "
          f"{len(result.items.rules)} rules, {len(result.items.warnings)} warnings")
    print(f"Saved: {output_file}")


if __name__ == "__main__":
    arg_dir = sys.argv[1] if len(sys.argv) > 1 else None
    run_extraction(arg_dir)
