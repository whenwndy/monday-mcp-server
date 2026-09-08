import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from fastmcp import FastMCP
from pydantic import Field

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "monday.json"
_db: dict = json.loads(_DATA_PATH.read_text())


def _match(record: dict, field: str, value: str) -> bool:
    """Case-insensitive substring match on a field."""
    return value.lower() in str(record.get(field, "")).lower()


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="monday-mock",
    version="1.0.0",
    instructions=(
        "Mock Monday.com work OS for Beast Industries. Query and manage boards, groups, "
        "items, updates, docs, forms, and dashboards across Engineering, Operations, Sales, "
        "and Corporate workspaces. Use search_items to find work items across boards."
    ),
)

# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------

@mcp.tool()
def get_workspaces(
    id: Optional[str] = Field(default=None, description="Filter by workspace ID, e.g. ws-001"),
    name: Optional[str] = Field(default=None, description="Filter by workspace name (partial match)"),
) -> list[dict]:
    """List Monday.com workspaces. Optionally filter by ID or name."""
    results = _db["workspaces"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    return results


# ---------------------------------------------------------------------------
# Boards
# ---------------------------------------------------------------------------

@mcp.tool()
def get_boards(
    id: Optional[str] = Field(default=None, description="Filter by board ID, e.g. brd-001"),
    name: Optional[str] = Field(default=None, description="Filter by board name (partial match)"),
    workspace_id: Optional[str] = Field(default=None, description="Filter by workspace ID"),
    state: Optional[str] = Field(default=None, description="Filter by state: active | archived"),
    tag: Optional[str] = Field(default=None, description="Filter by tag (checks tags array, partial match)"),
) -> list[dict]:
    """List Monday.com boards. Optionally filter by ID, name, workspace, state, or tag."""
    results = _db["boards"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if workspace_id:
        results = [r for r in results if r["workspace_id"].lower() == workspace_id.lower()]
    if state:
        results = [r for r in results if _match(r, "state", state)]
    if tag:
        results = [r for r in results if any(tag.lower() in t.lower() for t in r.get("tags", []))]
    return results


# ---------------------------------------------------------------------------
# Groups
# ---------------------------------------------------------------------------

@mcp.tool()
def get_groups(
    board_id: Optional[str] = Field(default=None, description="Filter by board ID"),
    board_name: Optional[str] = Field(default=None, description="Filter by board name (partial match)"),
    archived: Optional[bool] = Field(default=None, description="Filter by archived status; omit to return all"),
) -> list[dict]:
    """List groups within Monday.com boards. Filter by board ID, board name, or archived status."""
    results = _db["groups"]
    if board_id:
        results = [r for r in results if r["board_id"].lower() == board_id.lower()]
    if board_name:
        results = [r for r in results if _match(r, "board_name", board_name)]
    if archived is not None:
        results = [r for r in results if r.get("archived") == archived]
    return results


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

@mcp.tool()
def get_items(
    id: Optional[str] = Field(default=None, description="Filter by item ID, e.g. itm-1001"),
    name: Optional[str] = Field(default=None, description="Filter by item name (partial match)"),
    board_id: Optional[str] = Field(default=None, description="Filter by board ID"),
    board_name: Optional[str] = Field(default=None, description="Filter by board name (partial match)"),
    group_id: Optional[str] = Field(default=None, description="Filter by group ID"),
    assignee: Optional[str] = Field(default=None, description="Filter by assignee name (partial match)"),
    status: Optional[str] = Field(default=None, description="Filter by column_values.status (partial match)"),
    tag: Optional[str] = Field(default=None, description="Filter by tag (checks tags array, partial match)"),
    search: Optional[str] = Field(default=None, description="Partial match on item name"),
) -> list[dict]:
    """List Monday.com items. Filter by ID, name, board, group, assignee, status, or tag."""
    results = _db["items"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if board_id:
        results = [r for r in results if r["board_id"].lower() == board_id.lower()]
    if board_name:
        results = [r for r in results if _match(r, "board_name", board_name)]
    if group_id:
        results = [r for r in results if r["group_id"].lower() == group_id.lower()]
    if assignee:
        results = [
            r for r in results
            if any(assignee.lower() in a.lower() for a in r.get("assignee_names", []))
        ]
    if status:
        results = [
            r for r in results
            if status.lower() in str(r.get("column_values", {}).get("status", "")).lower()
        ]
    if tag:
        results = [r for r in results if any(tag.lower() in t.lower() for t in r.get("tags", []))]
    if search:
        results = [r for r in results if _match(r, "name", search)]
    return results


# ---------------------------------------------------------------------------
# Updates
# ---------------------------------------------------------------------------

@mcp.tool()
def get_updates(
    item_id: Optional[str] = Field(default=None, description="Filter by item ID"),
    board_id: Optional[str] = Field(default=None, description="Filter by board ID"),
    creator_name: Optional[str] = Field(default=None, description="Filter by creator name (partial match)"),
) -> list[dict]:
    """List updates (comments) on Monday.com items. Filter by item, board, or creator."""
    results = _db["updates"]
    if item_id:
        results = [r for r in results if r["item_id"].lower() == item_id.lower()]
    if board_id:
        results = [r for r in results if r["board_id"].lower() == board_id.lower()]
    if creator_name:
        results = [r for r in results if _match(r, "creator_name", creator_name)]
    return results


# ---------------------------------------------------------------------------
# Docs
# ---------------------------------------------------------------------------

@mcp.tool()
def get_docs(
    id: Optional[str] = Field(default=None, description="Filter by doc ID, e.g. doc-001"),
    name: Optional[str] = Field(default=None, description="Filter by doc name (partial match)"),
    workspace_id: Optional[str] = Field(default=None, description="Filter by workspace ID"),
    tag: Optional[str] = Field(default=None, description="Filter by tag (checks tags array, partial match)"),
) -> list[dict]:
    """List Monday.com docs. Filter by ID, name, workspace, or tag."""
    results = _db["docs"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if workspace_id:
        results = [r for r in results if r["workspace_id"].lower() == workspace_id.lower()]
    if tag:
        results = [r for r in results if any(tag.lower() in t.lower() for t in r.get("tags", []))]
    return results


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------

@mcp.tool()
def get_forms(
    id: Optional[str] = Field(default=None, description="Filter by form ID, e.g. frm-001"),
    name: Optional[str] = Field(default=None, description="Filter by form name (partial match)"),
    board_id: Optional[str] = Field(default=None, description="Filter by associated board ID"),
    is_active: Optional[bool] = Field(default=None, description="Filter by active status; omit to return all"),
) -> list[dict]:
    """List Monday.com forms. Filter by ID, name, board, or active status."""
    results = _db["forms"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if board_id:
        results = [r for r in results if r["board_id"].lower() == board_id.lower()]
    if is_active is not None:
        results = [r for r in results if r.get("is_active") == is_active]
    return results


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------

@mcp.tool()
def get_dashboards(
    id: Optional[str] = Field(default=None, description="Filter by dashboard ID, e.g. dsh-001"),
    name: Optional[str] = Field(default=None, description="Filter by dashboard name (partial match)"),
    workspace_id: Optional[str] = Field(default=None, description="Filter by workspace ID"),
) -> list[dict]:
    """List Monday.com dashboards. Filter by ID, name, or workspace."""
    results = _db["dashboards"]
    if id:
        results = [r for r in results if r["id"].lower() == id.lower()]
    if name:
        results = [r for r in results if _match(r, "name", name)]
    if workspace_id:
        results = [r for r in results if r["workspace_id"].lower() == workspace_id.lower()]
    return results


# ---------------------------------------------------------------------------
# Search Items
# ---------------------------------------------------------------------------

@mcp.tool()
def search_items(
    query: str = Field(description="Search query — partial match on item name and notes"),
    board_id: Optional[str] = Field(default=None, description="Restrict search to a specific board ID"),
) -> list[dict]:
    """Search Monday.com items by partial match on name or notes. Optionally scope to a single board."""
    q = query.lower()
    results = _db["items"]
    if board_id:
        results = [r for r in results if r["board_id"].lower() == board_id.lower()]
    results = [
        r for r in results
        if q in r["name"].lower()
        or q in str(r.get("column_values", {}).get("notes", "")).lower()
    ]
    return results


# ---------------------------------------------------------------------------
# Create Item
# ---------------------------------------------------------------------------

@mcp.tool()
def create_item(
    board_id: str = Field(description="Board ID to create the item on, e.g. brd-001"),
    group_id: str = Field(description="Group ID within the board, e.g. grp-001-1"),
    name: str = Field(description="Item name / title"),
    assignee_names_csv: Optional[str] = Field(default=None, description="Comma-separated assignee names, e.g. 'Derek Holt,Priya Nair'"),
    status: Optional[str] = Field(default=None, description="Status label, e.g. 'In Progress'"),
    priority: Optional[str] = Field(default=None, description="Priority label, e.g. 'High'"),
    due_date: Optional[str] = Field(default=None, description="Due date in YYYY-MM-DD format"),
    notes: Optional[str] = Field(default=None, description="Notes / description for the item"),
) -> dict:
    """Create a new item on a Monday.com board. Returns the created item."""
    # Resolve board and group names for denormalization
    board_name = next((b["name"] for b in _db["boards"] if b["id"] == board_id), board_id)
    group_name = next((g["title"] for g in _db["groups"] if g["id"] == group_id), group_id)

    assignees = (
        [a.strip() for a in assignee_names_csv.split(",") if a.strip()]
        if assignee_names_csv
        else []
    )

    new_item = {
        "id": f"itm-{uuid.uuid4().hex[:6]}",
        "name": name,
        "board_id": board_id,
        "board_name": board_name,
        "group_id": group_id,
        "group_name": group_name,
        "state": "active",
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "creator_id": "usr-system",
        "creator_name": "System",
        "assignee_names": assignees,
        "column_values": {
            "status": status or "",
            "priority": priority or "",
            "due_date": due_date or "",
            "progress_pct": 0,
            "notes": notes or "",
        },
        "tags": [],
    }
    _db["items"].append(new_item)
    return new_item


# ---------------------------------------------------------------------------
# Update Item
# ---------------------------------------------------------------------------

@mcp.tool()
def update_item(
    id: str = Field(description="Item ID to update, e.g. itm-1001"),
    name: Optional[str] = Field(default=None, description="New item name / title"),
    status: Optional[str] = Field(default=None, description="New status label"),
    priority: Optional[str] = Field(default=None, description="New priority label"),
    due_date: Optional[str] = Field(default=None, description="New due date in YYYY-MM-DD format"),
    progress_pct: Optional[int] = Field(default=None, description="Progress percentage 0-100"),
    notes: Optional[str] = Field(default=None, description="New notes / description"),
) -> dict:
    """Update column values on an existing Monday.com item. Returns the updated item."""
    item = next((r for r in _db["items"] if r["id"].lower() == id.lower()), None)
    if item is None:
        return {"error": f"Item '{id}' not found."}

    if name is not None:
        item["name"] = name
    cv = item.setdefault("column_values", {})
    if status is not None:
        cv["status"] = status
    if priority is not None:
        cv["priority"] = priority
    if due_date is not None:
        cv["due_date"] = due_date
    if progress_pct is not None:
        cv["progress_pct"] = progress_pct
    if notes is not None:
        cv["notes"] = notes
    item["updated_at"] = _now_iso()
    return item


# ---------------------------------------------------------------------------
# Create Update (Comment)
# ---------------------------------------------------------------------------

@mcp.tool()
def create_update(
    item_id: str = Field(description="Item ID to comment on, e.g. itm-1001"),
    body: str = Field(description="Comment body text"),
) -> dict:
    """Add a comment/update to a Monday.com item. Returns the created update."""
    item = next((r for r in _db["items"] if r["id"].lower() == item_id.lower()), None)
    if item is None:
        return {"error": f"Item '{item_id}' not found."}

    new_update = {
        "id": f"upd-{uuid.uuid4().hex[:6]}",
        "item_id": item_id,
        "item_name": item["name"],
        "board_id": item["board_id"],
        "body": body,
        "created_at": _now_iso(),
        "creator_id": "usr-system",
        "creator_name": "System",
        "likes_count": 0,
        "replies": [],
    }
    _db["updates"].append(new_update)
    return new_update


# ---------------------------------------------------------------------------
# Move Item to Group
# ---------------------------------------------------------------------------

@mcp.tool()
def move_item_to_group(
    item_id: str = Field(description="Item ID to move, e.g. itm-1001"),
    target_group_id: str = Field(description="Target group ID, e.g. grp-001-3"),
) -> dict:
    """Move a Monday.com item to a different group. Updates group_id and group_name. Returns the updated item."""
    item = next((r for r in _db["items"] if r["id"].lower() == item_id.lower()), None)
    if item is None:
        return {"error": f"Item '{item_id}' not found."}

    group = next((g for g in _db["groups"] if g["id"].lower() == target_group_id.lower()), None)
    if group is None:
        return {"error": f"Group '{target_group_id}' not found."}

    item["group_id"] = group["id"]
    item["group_name"] = group["title"]
    item["updated_at"] = _now_iso()
    return item


# ---------------------------------------------------------------------------
# Archive Item
# ---------------------------------------------------------------------------

@mcp.tool()
def archive_item(
    item_id: str = Field(description="Item ID to archive, e.g. itm-1001"),
) -> dict:
    """Archive a Monday.com item by setting its state to 'archived'. Returns the updated item."""
    item = next((r for r in _db["items"] if r["id"].lower() == item_id.lower()), None)
    if item is None:
        return {"error": f"Item '{item_id}' not found."}

    item["state"] = "archived"
    item["updated_at"] = _now_iso()
    return item


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
