"""Fixed tool set and task set for the #226 docstring-format experiment.

18 tools in 6 families of 3 look-alikes. Every tool has the SAME information in
every docstring format: one summary line, one description per parameter, one
returns line. Formats differ only in markup (see gen_arms.py).

Each tool has two tasks:
  "summary" task: answerable from the summary line alone.
  "param"   task: names no domain word; only a parameter description
                  (an ID format, unit, scope) tells the right tool apart.
Written before any model call; not edited after results were seen.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Param:
    name: str
    type: str  # python annotation source
    desc: str
    default: str | None = None  # python source of default, None = required


@dataclass(frozen=True)
class ToolSpec:
    name: str
    summary: str
    params: tuple[Param, ...]
    returns_type: str
    returns: str


@dataclass(frozen=True)
class Task:
    id: str
    gold: str
    kind: str  # "summary" | "param"
    request: str


P = Param
TOOLS: tuple[ToolSpec, ...] = (
    # A. catalog lookups: the code format is the discriminator
    ToolSpec("lookup_book", "Look up a book in the library catalog.",
             (P("code", "str", "ISBN-13 of the book, thirteen digits such as 9780306406157."),),
             "dict", "The catalog record."),
    ToolSpec("lookup_product", "Look up an item in the store inventory.",
             (P("code", "str", "Store SKU in the form AB-1234."),),
             "dict", "The inventory record."),
    ToolSpec("lookup_paper", "Look up a published research paper.",
             (P("code", "str", "DOI of the paper, starting with '10.', such as 10.1038/nphys1170."),),
             "dict", "The paper's metadata."),
    # B. host metrics: the option is the discriminator
    ToolSpec("cpu_stats", "Report processor load for a server.",
             (P("host", "str", "Hostname of the server."),
              P("window_minutes", "int", "Averaging window in minutes: 1, 5 or 15.", "5")),
             "float", "Load average over the window."),
    ToolSpec("memory_stats", "Report RAM consumption for a server.",
             (P("host", "str", "Hostname of the server."),
              P("include_swap", "bool", "Also report swap / page-file usage.", "False")),
             "dict", "Used and free memory in MiB."),
    ToolSpec("disk_stats", "Report storage use for a server.",
             (P("host", "str", "Hostname of the server."),
              P("mount", "str", "Mount point or drive to inspect, such as /var or C:.", "'/'")),
             "dict", "Used and free bytes on the mount."),
    # C. messaging: the recipient format is the discriminator
    ToolSpec("send_email", "Deliver a written message to a person.",
             (P("recipient", "str", "Email address such as name@example.com."),
              P("text", "str", "Message body.")),
             "str", "Delivery id."),
    ToolSpec("send_sms", "Deliver a short text message to a person's phone.",
             (P("recipient", "str", "Phone number in E.164 form such as +14155550123."),
              P("text", "str", "Message body, at most 160 characters.")),
             "str", "Delivery id."),
    ToolSpec("post_message", "Post a message to a team chat space.",
             (P("recipient", "str", "Channel name beginning with '#', such as #ops."),
              P("text", "str", "Message body.")),
             "str", "Message permalink."),
    # D. files: the destination parameter is the discriminator
    ToolSpec("upload_file", "Copy a local file to cloud object storage.",
             (P("path", "str", "Local path of the file."),
              P("bucket", "str", "Name of the S3 bucket to copy into.")),
             "str", "Object URL."),
    ToolSpec("attach_file", "Attach a file to a support ticket.",
             (P("path", "str", "Local path of the file."),
              P("ticket_id", "str", "Ticket key such as SUP-1042.")),
             "str", "Attachment id."),
    ToolSpec("share_file", "Create a shareable download link for a file.",
             (P("path", "str", "Local path of the file."),
              P("expires_hours", "int", "Hours until the link stops working.", "24")),
             "str", "The link."),
    # E. time: the scheduling semantics are the discriminator
    ToolSpec("create_event", "Add an entry to the shared calendar.",
             (P("title", "str", "Event title shown to attendees."),
              P("start", "str", "ISO-8601 start time."),
              P("attendees", "list[str]", "Email addresses to invite.", "[]")),
             "str", "Event id."),
    ToolSpec("set_reminder", "Schedule a personal notification.",
             (P("text", "str", "What to remind about."),
              P("at", "str", "ISO-8601 time at which the notification fires.")),
             "str", "Reminder id."),
    ToolSpec("block_focus_time", "Reserve uninterrupted time on your own schedule.",
             (P("start", "str", "ISO-8601 start time."),
              P("duration_minutes", "int", "Length of the block in minutes."),
              P("mute_notifications", "bool", "Silence all notifications during the block.", "True")),
             "str", "Block id."),
    # F. conversions: the code/unit vocabulary is the discriminator
    ToolSpec("convert_currency", "Convert an amount between currencies.",
             (P("amount", "float", "Amount to convert."),
              P("source", "str", "ISO 4217 code of the source, such as EUR."),
              P("target", "str", "ISO 4217 code of the target, such as JPY.")),
             "float", "Converted amount."),
    ToolSpec("convert_units", "Convert a measurement between units.",
             (P("amount", "float", "Value to convert."),
              P("source", "str", "Unit symbol of the source, such as km, lb or degF."),
              P("target", "str", "Unit symbol of the target.")),
             "float", "Converted value."),
    ToolSpec("convert_timezone", "Convert a clock time between time zones.",
             (P("amount", "str", "Clock time to convert, such as 14:30."),
              P("source", "str", "IANA zone name of the source, such as Europe/Paris."),
              P("target", "str", "IANA zone name of the target.")),
             "str", "Converted clock time."),
)

TASKS: tuple[Task, ...] = (
    Task("A1s", "lookup_book", "summary", "Does the library catalog have the book with code 9780441172719?"),
    Task("A1p", "lookup_book", "param", "Pull up the record for 9781492056355."),
    Task("A2s", "lookup_product", "summary", "Check the store inventory record for item code KX-5521."),
    Task("A2p", "lookup_product", "param", "Pull up the record for QR-0087."),
    Task("A3s", "lookup_paper", "summary", "Find the metadata of the research paper with code 10.1145/3292500.3330701."),
    Task("A3p", "lookup_paper", "param", "Pull up the record for 10.1126/science.169.3946.635."),
    Task("B1s", "cpu_stats", "summary", "How busy is the processor on db-2 right now?"),
    Task("B1p", "cpu_stats", "param", "Give me the 15-minute average for db-2."),
    Task("B2s", "memory_stats", "summary", "How much RAM is web-1 using?"),
    Task("B2p", "memory_stats", "param", "Is web-1 leaning on its page file?"),
    Task("B3s", "disk_stats", "summary", "How much storage is left on build-7?"),
    Task("B3p", "disk_stats", "param", "Check C: on build-7."),
    Task("C1s", "send_email", "summary", "Write to dana@example.com that the build is green."),
    Task("C1p", "send_email", "param", "Tell ops-lead@acme.io the deploy finished."),
    Task("C2s", "send_sms", "summary", "Text my sister's phone that I'm running late; her number is +447700900123."),
    Task("C2p", "send_sms", "param", "Tell +14155550199 the car is outside."),
    Task("C3s", "post_message", "summary", "Post in the team chat space #release that we ship at 5pm."),
    Task("C3p", "post_message", "param", "Tell #oncall the pager is back up."),
    Task("D1s", "upload_file", "summary", "Copy backup.tar to cloud object storage in prod-archive."),
    Task("D1p", "upload_file", "param", "Put backup.tar into the S3 bucket prod-archive."),
    Task("D2s", "attach_file", "summary", "Attach crash.log to the support ticket SUP-3381."),
    Task("D2p", "attach_file", "param", "Put crash.log on SUP-3381."),
    Task("D3s", "share_file", "summary", "Make a download link for slides.pdf that I can send around."),
    Task("D3p", "share_file", "param", "Make slides.pdf reachable for the next 48 hours."),
    Task("E1s", "create_event", "summary", "Put 'Quarterly review' on the shared calendar for 2026-11-20T10:00 and invite ana@example.com."),
    Task("E1p", "create_event", "param", "Get ana@example.com and raj@example.com together at 2026-11-20T10:00 for 'Quarterly review'."),
    Task("E2s", "set_reminder", "summary", "Send me a notification at 2026-11-07T08:00 to renew my passport."),
    Task("E2p", "set_reminder", "param", "At 2026-11-07T08:00, ping me about the passport renewal."),
    Task("E3s", "block_focus_time", "summary", "Reserve 90 uninterrupted minutes on my schedule from 2026-11-07T14:00."),
    Task("E3p", "block_focus_time", "param", "Silence everything for 90 minutes starting 2026-11-07T14:00."),
    Task("F1s", "convert_currency", "summary", "Convert 250 euros to Japanese yen."),
    Task("F1p", "convert_currency", "param", "What is 250 CHF in SEK?"),
    Task("F2s", "convert_units", "summary", "Convert a 42 km measurement to miles."),
    Task("F2p", "convert_units", "param", "What is 98.6 degF in degC?"),
    Task("F3s", "convert_timezone", "summary", "Convert 14:30 from the Paris time zone to the Tokyo one."),
    Task("F3p", "convert_timezone", "param", "What is 14:30 Europe/Paris in America/Chicago?"),
)

assert len(TOOLS) == 18 and len({t.name for t in TOOLS}) == 18
assert len(TASKS) == 36 and all(any(t.name == k.gold for t in TOOLS) for k in TASKS)
