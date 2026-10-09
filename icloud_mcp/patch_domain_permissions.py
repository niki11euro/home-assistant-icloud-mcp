#!/usr/bin/env python3
"""Apply a pinned, fail-closed patch for independent Calendar/Contacts MCP permissions.

The upstream iCloud MCP revision is pinned in Dockerfile. Deliberately fail
builds when upstream Go sources change instead of guessing at security gates.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def swap(path, old, new):
    target = root / path
    data = target.read_text(encoding="utf-8")
    count = data.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one upstream anchor, found {count}")
    target.write_text(data.replace(old, new, 1), encoding="utf-8")

reg = "internal/mcptools/register.go"
swap(reg,
    "readOnly        bool\n\tcontactsEnabled bool",
    "readOnly        bool\n\tcalendarRead    bool\n\tcalendarWrite   bool\n\tcontactsRead   bool\n\tcontactsWrite  bool\n\tcontactsEnabled bool")
swap(reg,
    "readOnly:        readOnly,\n\t\tcontactsEnabled: contactsEnabled,",
    "readOnly:        readOnly,\n\t\tcalendarRead:    true,\n\t\tcalendarWrite:   !readOnly,\n\t\tcontactsRead:   contactsEnabled,\n\t\tcontactsWrite:  contactsEnabled && !readOnly,\n\t\tcontactsEnabled: contactsEnabled,")
swap(reg,
    "// ReadOnly reports whether the global mutation kill switch is active.",
    """// WithDomainAccess narrows the Calendar/Contacts MCP tool surfaces independently.
// The upstream global read-only flag remains an emergency mutation kill switch.
func (p CapabilityPlan) WithDomainAccess(calendarRead, calendarWrite, contactsRead, contactsWrite bool) CapabilityPlan {
    p.calendarRead = calendarRead
    p.calendarWrite = calendarWrite && !p.readOnly
    p.contactsRead = contactsRead
    p.contactsWrite = contactsWrite && !p.readOnly
    p.contactsEnabled = contactsRead || contactsWrite
    return p
}

func (p CapabilityPlan) CalendarReadsEnabled() bool { return p.calendarRead }
func (p CapabilityPlan) ContactsReadsEnabled() bool { return p.contactsRead }

// ReadOnly reports whether the global mutation kill switch is active.""")
swap(reg, "func (p CapabilityPlan) ReadOnly() bool { return p.readOnly }",
    """func (p CapabilityPlan) ReadOnly() bool {
    return !(p.CalendarWritesEnabled() || p.ContactsWritesEnabled() || p.MailMutationsEnabled() || p.MailSendEnabled())
}""")
swap(reg, "func (p CapabilityPlan) CalendarWritesEnabled() bool { return !p.readOnly }",
    "func (p CapabilityPlan) CalendarWritesEnabled() bool { return p.calendarWrite }")
swap(reg,
    """func (p CapabilityPlan) ContactsWritesEnabled() bool {
\treturn p.contactsEnabled && !p.readOnly
}""",
    """func (p CapabilityPlan) ContactsWritesEnabled() bool {
    return p.contactsWrite
}""")
swap(reg,
    """names := calendarReadToolNames()
\tif p.CalendarWritesEnabled() {
\t\tnames = append(names, calendarWriteToolNames()...)
\t}
\tif p.contactsEnabled {
\t\tnames = append(names, contactsReadToolNames()...)
\t\tif p.ContactsWritesEnabled() {
\t\t\tnames = append(names, contactsWriteToolNames()...)
\t\t}
\t}""",
    """names := []string{"calendar_capabilities"}
    if p.CalendarReadsEnabled() {
        names = calendarReadToolNames()
    }
    if p.CalendarWritesEnabled() {
        names = append(names, calendarWriteToolNames()...)
    }
    if p.ContactsReadsEnabled() {
        names = append(names, contactsReadToolNames()...)
    }
    if p.ContactsWritesEnabled() {
        names = append(names, contactsWriteToolNames()...)
    }""")
swap(reg, "ReadOnly      bool\n\tHealthEnabled bool",
    "ReadOnly      bool\n\tCalendarReadDisabled bool\n\tHealthEnabled bool")
swap(reg,
    """deps.ReadOnly = plan.ReadOnly()
\tregistered := registerCalendar(s, deps, plan.CalendarWritesEnabled())""",
    """deps.ReadOnly = !plan.CalendarWritesEnabled()
    deps.CalendarReadDisabled = !plan.CalendarReadsEnabled()
    registered := registerCalendarWithAccess(s, deps, plan.CalendarReadsEnabled(), plan.CalendarWritesEnabled())""")
swap(reg,
    """registered = append(registered, RegisterContacts(s, ContactsDeps{
\t\t\tService: deps.ContactsService, Audit: deps.Audit, Redactor: deps.Redactor,
\t\t}, plan.ContactsWritesEnabled())...)""",
    """registered = append(registered, RegisterContactsWithAccess(s, ContactsDeps{
            Service: deps.ContactsService, Audit: deps.Audit, Redactor: deps.Redactor,
        }, plan.ContactsReadsEnabled(), plan.ContactsWritesEnabled())...)""")

register_path = root / reg
register_code = register_path.read_text(encoding="utf-8")
idx = register_code.find("func registerCalendar(s *server.MCPServer, deps Deps, allowWrites bool) []string {")
if idx < 0 or not register_code[idx:].rstrip().endswith('return append(names, calendarWriteToolNames()...)\n}'):
    raise RuntimeError("register.go: unexpected calendar registration function")
register_code = register_code[:idx] + """func registerCalendar(s *server.MCPServer, deps Deps, allowWrites bool) []string {
    return registerCalendarWithAccess(s, deps, true, allowWrites)
}

// registerCalendarWithAccess registers only the permitted remote Calendar tools.
// Local metadata remains visible even when calendar data reads are disabled.
func registerCalendarWithAccess(s *server.MCPServer, deps Deps, allowReads, allowWrites bool) []string {
    names := []string{"calendar_capabilities"}
    if allowReads {
        s.AddTool(newListCalendarsTool(), listCalendarsHandler(deps))
        s.AddTool(newSearchEventsTool(deps.DefaultLocation), searchEventsHandler(deps))
        s.AddTool(newGetEventTool(), getEventHandler(deps))
        s.AddTool(newFindFreeSlotsTool(deps.DefaultLocation), findFreeSlotsHandler(deps))
        s.AddTool(newValidateEventTool(deps.DefaultLocation), validateEventHandler(deps))
        names = calendarReadToolNames()
    }
    s.AddTool(newCalendarCapabilitiesTool(), calendarCapabilitiesHandler(deps))
    if allowWrites {
        s.AddTool(newCreateEventTool(deps.DefaultLocation), createEventHandler(deps))
        s.AddTool(newUpdateEventTool(deps.DefaultLocation), updateEventHandler(deps))
        s.AddTool(newDeleteEventTool(deps.DefaultLocation), deleteEventHandler(deps))
        names = append(names, calendarWriteToolNames()...)
    }
    return names
}
"""
register_path.write_text(register_code, encoding="utf-8")

contacts_file = root / "internal/mcptools/contacts_register.go"
existing = contacts_file.read_text(encoding="utf-8")
if "func RegisterContacts(s *server.MCPServer, deps ContactsDeps, allowWrites bool) []string {" not in existing:
    raise RuntimeError("contacts_register.go: upstream anchor is missing")
contacts_file.write_text("""package mcptools

import "github.com/mark3labs/mcp-go/server"

// RegisterContacts preserves the upstream all-reads/optional-writes API.
func RegisterContacts(s *server.MCPServer, deps ContactsDeps, allowWrites bool) []string {
    return RegisterContactsWithAccess(s, deps, true, allowWrites)
}

// RegisterContactsWithAccess keeps read and mutation tool registration independent.
func RegisterContactsWithAccess(s *server.MCPServer, deps ContactsDeps, allowReads, allowWrites bool) []string {
    if deps.Redactor == nil {
        panic("mcptools: Contacts tools require a non-nil redactor")
    }
    names := []string{}
    if allowReads {
        s.AddTool(newListAddressBooksTool(), listAddressBooksHandler(deps))
        s.AddTool(newSearchContactsTool(), searchContactsHandler(deps))
        s.AddTool(newGetContactTool(), getContactHandler(deps))
        names = append(names, contactsReadToolNames()...)
    }
    if allowWrites {
        s.AddTool(newCreateContactTool(), createContactHandler(deps))
        s.AddTool(newUpdateContactTool(), updateContactHandler(deps))
        s.AddTool(newDeleteContactTool(), deleteContactHandler(deps))
        names = append(names, contactsWriteToolNames()...)
    }
    return names
}
""", encoding="utf-8")

swap("internal/mcptools/calendar_capabilities.go",
    "tools := calendarReadToolNames()\n\t\tif !deps.ReadOnly {",
    """tools := []string{"calendar_capabilities"}
        if !deps.CalendarReadDisabled {
            tools = calendarReadToolNames()
        }
        if !deps.ReadOnly {""")
swap("internal/mcptools/icloud_capabilities.go",
    "Calendar: true,",
    "Calendar: plan.CalendarReadsEnabled() || plan.CalendarWritesEnabled(),")
swap("internal/mcptools/icloud_capabilities.go",
    "CalendarRead:  true,",
    "CalendarRead:  plan.CalendarReadsEnabled(),")
swap("internal/mcptools/icloud_capabilities.go",
    "ContactsRead:  plan.ContactsEnabled(),",
    "ContactsRead:  plan.ContactsReadsEnabled(),")

swap("cmd/icloud-mcp/main.go",
    """\tplan := mcptools.NewCapabilityPlan(
\t\tcfg.ReadOnly,
\t\tcfg.EnableContacts,
\t\tcfg.EnableMail,
\t\tcfg.EffectiveMailWrite(),
\t\tcfg.EffectiveMailSend(),
\t)""",
    """    plan := mcptools.NewCapabilityPlan(
        cfg.ReadOnly,
        cfg.EnableContacts,
        cfg.EnableMail,
        cfg.EffectiveMailWrite(),
        cfg.EffectiveMailSend(),
    ).WithDomainAccess(
        appDomainPermission("ICLOUD_MCP_CALENDAR_READ", true),
        appDomainPermission("ICLOUD_MCP_CALENDAR_WRITE", !cfg.ReadOnly),
        appDomainPermission("ICLOUD_MCP_CONTACTS_READ", cfg.EnableContacts),
        appDomainPermission("ICLOUD_MCP_CONTACTS_WRITE", cfg.EffectiveContactsWrite()),
    )""")

(root / "cmd/icloud-mcp/app_permissions.go").write_text("""package main

import "os"

// appDomainPermission reads a validated Home Assistant boolean.
// Missing variables preserve the original upstream behavior. Invalid
// present values fail closed; the HA wrapper rejects them before startup.
func appDomainPermission(name string, fallback bool) bool {
    value, present := os.LookupEnv(name)
    if !present {
        return fallback
    }
    return value == "true"
}
""", encoding="utf-8")
print("Applied iCloud domain permission patch (pinned upstream revision).")
