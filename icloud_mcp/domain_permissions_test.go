package mcptools

import (
    "context"
    "encoding/json"
    "fmt"
    "slices"
    "testing"

    "github.com/mark3labs/mcp-go/mcp"
    "github.com/mark3labs/mcp-go/server"

    "github.com/ThomasCrouzet/icloud-mcp/internal/icloud"
    "github.com/ThomasCrouzet/icloud-mcp/internal/security"
)

func TestHomeAssistantIndependentDomainPermissions(t *testing.T) {
    for mask := 0; mask < 16; mask++ {
        calendarRead := mask&1 != 0
        calendarWrite := mask&2 != 0
        contactsRead := mask&4 != 0
        contactsWrite := mask&8 != 0
        t.Run(fmt.Sprintf("permissions_%04b", mask), func(t *testing.T) {
            plan := NewCapabilityPlan(false, contactsRead || contactsWrite, false, false, false).
                WithDomainAccess(calendarRead, calendarWrite, contactsRead, contactsWrite)
            svc := &icloud.MockService{}
            s := server.NewMCPServer("test-granular-rights", "1.0", server.WithToolCapabilities(false))
            deps := Deps{
                Service: svc,
                ContactsService: &fakeContactsService{},
                Audit: security.NewAuditLogger(&discardWriter{}),
                Redactor: security.NewRedactor("unused-secret"),
            }
            RegisterUnified(s, deps, plan)
            got := listToolNames(t, s)
            for _, tool := range []string{"list_calendars", "search_events", "get_event", "find_free_slots", "validate_event"} {
                if slices.Contains(got, tool) != calendarRead {
                    t.Errorf("%s exposed=%t want=%t", tool, slices.Contains(got, tool), calendarRead)
                }
            }
            for _, tool := range []string{"create_event", "update_event", "delete_event"} {
                if slices.Contains(got, tool) != calendarWrite {
                    t.Errorf("%s exposed=%t want=%t", tool, slices.Contains(got, tool), calendarWrite)
                }
            }
            for _, tool := range []string{"list_address_books", "search_contacts", "get_contact"} {
                if slices.Contains(got, tool) != contactsRead {
                    t.Errorf("%s exposed=%t want=%t", tool, slices.Contains(got, tool), contactsRead)
                }
            }
            for _, tool := range []string{"create_contact", "update_contact", "delete_contact"} {
                if slices.Contains(got, tool) != contactsWrite {
                    t.Errorf("%s exposed=%t want=%t", tool, slices.Contains(got, tool), contactsWrite)
                }
            }
            for _, tool := range []string{"calendar_capabilities", "icloud_capabilities"} {
                if !slices.Contains(got, tool) {
                    t.Errorf("missing local capability tool %s", tool)
                }
            }
            if len(got) != plan.ToolCount() {
                t.Errorf("got %d tools, plan reports %d", len(got), plan.ToolCount())
            }
            result, err := icloudCapabilitiesHandler(deps, plan)(context.Background(), mcp.CallToolRequest{})
            if err != nil || result.IsError {
                t.Fatalf("capabilities failed: %v %#v", err, result)
            }
            var response icloudCapabilitiesResponse
            if err := json.Unmarshal([]byte(resultText(t, result)), &response); err != nil {
                t.Fatal(err)
            }
            groups := response.CapabilityGroups
            if groups.CalendarRead != calendarRead || groups.CalendarWrite != calendarWrite ||
                groups.ContactsRead != contactsRead || groups.ContactsWrite != contactsWrite {
                t.Errorf("capabilities mismatch: %+v", groups)
            }
            if response.Domains.Calendar != (calendarRead || calendarWrite) ||
                response.Domains.Contacts != (contactsRead || contactsWrite) {
                t.Errorf("domain enabled flags mismatch: %+v", response.Domains)
            }
        })
    }
}

func TestHomeAssistantGlobalReadOnlyCannotBeBypassed(t *testing.T) {
    p := NewCapabilityPlan(true, true, false, false, false).WithDomainAccess(true, true, true, true)
    if p.CalendarWritesEnabled() || p.ContactsWritesEnabled() {
        t.Fatal("global read-only must suppress all mutations")
    }
}
