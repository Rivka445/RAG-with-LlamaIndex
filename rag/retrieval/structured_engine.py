import json
import logging
import re
from pathlib import Path
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.llms import LLM

# structured JSON is kept under the repository's extraction/ folder (root-level)
STRUCTURED_JSON_PATH = Path(__file__).resolve().parent.parent.parent / "extraction" / "structured_project_data.json"

SCHEMA_DESCRIPTION = """
הנתונים המובנים מכילים שלושה סוגי פריטים:
- decisions: החלטות טכניות (שדות: id, title, source.tool, source.file)
- rules: כללים והנחיות (שדות: id, title, source.tool, source.file)
- warnings: אזהרות (שדות: id, title, source.tool, source.file)

כל פריט שייך לכלי (tool): "cursor" או "claude".
"""


logger = logging.getLogger(__name__)


class StructuredQueryEngine(CustomQueryEngine):
    """מנוע שליפה מובנית: LLM בונה פילטר → שולף מ-JSON → LLM מכין תשובה."""
    llm: LLM
    structured_data: dict

    def custom_query(self, query_str: str):
        raise NotImplementedError("use acustom_query")

    async def _build_query_plan(self, query_str: str) -> dict:
        filter_prompt = f"""
אתה מערכת שליפת נתונים. בהתאם לסכמה הבאה:
{SCHEMA_DESCRIPTION}

המשתמש שאל: "{query_str}"

החזר JSON בלבד (ללא הסברים) עם השדות הבאים:
{
  "category": "decisions" | "rules" | "warnings" | "all",
  "tool_filter": "cursor" | "claude" | null,
  "operation": "count" | "list" | "search",
  "search_term": "<מילת חיפוש אם רלוונטי, אחרת null>"
}
"""
        response = await self.llm.acomplete(filter_prompt)
        raw = getattr(response, "text", str(response)).strip()
        logger.debug("_build_query_plan raw response: %s", raw)

        # Try to extract JSON from fenced code blocks first, then look for a JSON object
        def _extract_json(text: str) -> str:
            # fenced ```json ... ```
            m = re.search(r"```\s*json\s*(.*?)```", text, flags=re.S | re.I)
            if m:
                return m.group(1).strip()
            # fenced without json
            m = re.search(r"```(.*?)```", text, flags=re.S)
            if m:
                return m.group(1).strip()
            # try to find first {...} block
            m = re.search(r"\{[\s\S]*\}", text)
            if m:
                return m.group(0)
            return text

        candidate = _extract_json(raw)

        # Try standard json.loads, then a permissive fallback if available
        try:
            return json.loads(candidate.strip())
        except Exception as e:
            logger.debug("json.loads failed: %s", e)
            try:
                # try dirtyjson if installed (permissive)
                import dirtyjson as _dj  # type: ignore

                return _dj.loads(candidate)
            except Exception:
                # final fallback: raise with debug info
                logger.warning("Failed to parse query plan JSON. Raw response:\n%s", raw)
                raise

    def _filter_items(self, query_plan: dict) -> tuple[list, str]:
        items_db = self.structured_data.get("items", {})
        category = query_plan.get("category", "all")
        tool_filter = query_plan.get("tool_filter")
        operation = query_plan.get("operation", "list")
        search_term = query_plan.get("search_term")

        categories = ["decisions", "rules", "warnings"] if category == "all" else [category]
        results = []
        for cat in categories:
            items = items_db.get(cat, [])
            if tool_filter:
                items = [i for i in items if (i.get("source") or {}).get("tool") == tool_filter]
            if search_term:
                term = search_term.lower()
                items = [i for i in items if term in (i.get("title") or i.get("rule") or i.get("message") or "").lower()]
            results.extend({"category": cat, **item} for item in items)

        if operation == "count":
            return results, f"נמצאו {len(results)} פריטים."
        if not results:
            return results, "לא נמצאו פריטים התואמים את השאילתה."
        lines = [f"[{r['category']}][{r.get('id','?')}] {r.get('title') or r.get('rule') or r.get('message') or ''}" for r in results]
        return results, "\n".join(lines)

    async def acustom_query(self, query_str: str):
        parsed_ok = True
        try:
            query_plan = await self._build_query_plan(query_str)
        except Exception:
            parsed_ok = False
            logger.info("Could not parse query plan for query: %s", query_str)
            # fallback to a permissive plan (list all)
            query_plan = {"category": "all", "tool_filter": None, "operation": "list", "search_term": None}

        _, raw_data = self._filter_items(query_plan)

        answer_prompt = f"""
המשתמש שאל: "{query_str}"

תוצאות השליפה מהנתונים המובנים:
{raw_data}

ענה למשתמש בצורה ברורה ותמציתית בהתבסס על התוצאות בלבד.
"""
        if not parsed_ok:
            answer_prompt += "\n\nהערה: לא הצלחתי לפרסר את תוכנית השאילתה; השתמשתי בתוכנית ברירת מחדל כדי לשלוף תוצאות."

        final = await self.llm.acomplete(answer_prompt)
        return str(final.text)
