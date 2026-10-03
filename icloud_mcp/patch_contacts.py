#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

def replace_once(relative, old, new):
    path = root / relative
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{relative}: expected exactly one match, found {count}")
    path.write_text(text.replace(old, new, 1))

replace_once(
    "internal/contacts/service.go",
    '''// SearchResult reports summaries and whether either result or scan bounds
// prevented a complete response.
type SearchResult struct {
	Contacts         []ContactSummary `json:"contacts"`
	Truncated        bool             `json:"truncated,omitempty"`
	ScanLimitReached bool             `json:"scanLimitReached,omitempty"`
}
''',
    '''// InvalidContactReference identifies one contact resource that could not be
// decoded during a bounded search. Resource is only the final escaped path
// segment, never the full CardDAV URL or raw vCard.
type InvalidContactReference struct {
	AddressBook string `json:"addressBook"`
	Resource    string `json:"resource,omitempty"`
	Reason      string `json:"reason"`
}

// SearchResult reports summaries and whether either result or scan bounds
// prevented a complete response. Malformed individual vCards are skipped so
// that one broken contact does not make the whole address book unreadable.
type SearchResult struct {
	Contacts            []ContactSummary         `json:"contacts"`
	Truncated           bool                     `json:"truncated,omitempty"`
	ScanLimitReached    bool                     `json:"scanLimitReached,omitempty"`
	PartialFailure      bool                     `json:"partialFailure,omitempty"`
	InvalidCardsSkipped int                      `json:"invalidCardsSkipped,omitempty"`
	InvalidContacts     []InvalidContactReference `json:"invalidContacts,omitempty"`
}
'''
)

replace_once(
    "internal/contacts/operations.go",
    '''type addressObject struct {
	url     *url.URL
	card    vcard.Card
	raw     *rawCard
	version string
	etag    string
}
''',
    '''type addressObject struct {
	url     *url.URL
	card    vcard.Card
	raw     *rawCard
	version string
	etag    string
}

const maxInvalidContactReferences = 20

type reportStats struct {
	rowsSeen        int
	invalidCards    int
	invalidContacts []InvalidContactReference
}
'''
)

replace_once(
    "internal/contacts/operations.go",
    '''func xmlEscape(value string) string {
	var builder strings.Builder
	_ = xml.EscapeText(&builder, []byte(value))
	return builder.String()
}

func (c *Client) report(ctx context.Context, book bookRecord, body string, rowLimit int, byteCap int64) ([]addressObject, bool, int64, error) {
''',
    '''func xmlEscape(value string) string {
	var builder strings.Builder
	_ = xml.EscapeText(&builder, []byte(value))
	return builder.String()
}

func contactResourceName(target *url.URL) string {
	if target == nil {
		return ""
	}
	value := strings.TrimSuffix(target.EscapedPath(), "/")
	if slash := strings.LastIndexByte(value, '/'); slash >= 0 {
		value = value[slash+1:]
	}
	return truncateUTF8(value, maxUIDBytes)
}

func (c *Client) report(ctx context.Context, book bookRecord, body string, rowLimit int, byteCap int64, tolerateInvalidCards bool, stats *reportStats) ([]addressObject, bool, int64, error) {
'''
)

replace_once(
    "internal/contacts/operations.go",
    '''		if !urlWithin(resourceURL, book.url, false) {
			return nil, false, int64(len(response.Body)), newError(CodeProtocolError, 0, "Contacts REPORT returned a resource outside its address book")
		}
		card, version, decodeErr := decodeCard([]byte(prop.AddressData.Value))
		if decodeErr != nil {
			return nil, false, int64(len(response.Body)), decodeErr
		}
''',
    '''		if !urlWithin(resourceURL, book.url, false) {
			return nil, false, int64(len(response.Body)), newError(CodeProtocolError, 0, "Contacts REPORT returned a resource outside its address book")
		}
		if stats != nil {
			stats.rowsSeen++
		}
		card, version, decodeErr := decodeCard([]byte(prop.AddressData.Value))
		if decodeErr != nil {
			if tolerateInvalidCards {
				typed := AsError(decodeErr)
				if typed != nil && typed.Code == CodeProtocolError {
					if stats != nil {
						stats.invalidCards++
						if len(stats.invalidContacts) < maxInvalidContactReferences {
							reason := typed.Message
							if reason == "" {
								reason = "invalid vCard"
							}
							stats.invalidContacts = append(stats.invalidContacts, InvalidContactReference{
								AddressBook: book.public.Identifier,
								Resource:    contactResourceName(resourceURL),
								Reason:      reason,
							})
						}
					}
					continue
				}
			}
			return nil, false, int64(len(response.Body)), decodeErr
		}
'''
)

replace_once(
    "internal/contacts/operations.go",
    '''	var matches []ContactSummary
	scanLimit := false
''',
    '''	var matches []ContactSummary
	var invalidContacts []InvalidContactReference
	invalidCardsSkipped := 0
	scanLimit := false
'''
)

replace_once(
    "internal/contacts/operations.go",
    '''		requestLimit := remainingCards + 1
		objects, overflow, used, err := c.report(ctx, book, searchQuery(opts, requestLimit), requestLimit, remainingBytes)
		if err != nil {
			return SearchResult{}, err
		}
		remainingBytes -= used
		complete := len(objects)
		if complete > remainingCards {
			complete = remainingCards
		}
		for _, object := range objects[:complete] {
			remainingCards--
			if contactMatches(object.card, opts) {
				matches = append(matches, cardSummary(object.card, book.public.Identifier, object.etag))
			}
		}
		if overflow || len(objects) > complete || remainingCards == 0 && index < len(books)-1 {
			scanLimit = true
			break
		}
''',
    '''		budget := remainingCards
		requestLimit := budget + 1
		stats := &reportStats{}
		objects, overflow, used, err := c.report(ctx, book, searchQuery(opts, requestLimit), requestLimit, remainingBytes, true, stats)
		if err != nil {
			return SearchResult{}, err
		}
		remainingBytes -= used
		invalidCardsSkipped += stats.invalidCards
		for _, invalid := range stats.invalidContacts {
			if len(invalidContacts) >= maxInvalidContactReferences {
				break
			}
			invalidContacts = append(invalidContacts, invalid)
		}
		validBudget := budget - stats.invalidCards
		if validBudget < 0 {
			validBudget = 0
		}
		complete := len(objects)
		if complete > validBudget {
			complete = validBudget
		}
		for _, object := range objects[:complete] {
			if contactMatches(object.card, opts) {
				matches = append(matches, cardSummary(object.card, book.public.Identifier, object.etag))
			}
		}
		rowsConsumed := stats.rowsSeen
		if rowsConsumed > budget {
			rowsConsumed = budget
		}
		remainingCards = budget - rowsConsumed
		if overflow || stats.rowsSeen > rowsConsumed || len(objects) > complete || remainingCards == 0 && index < len(books)-1 {
			scanLimit = true
			break
		}
'''
)

replace_once(
    "internal/contacts/operations.go",
    '''	result := SearchResult{ScanLimitReached: scanLimit, Truncated: len(matches) > opts.Limit}
''',
    '''	result := SearchResult{
		ScanLimitReached:    scanLimit,
		Truncated:           len(matches) > opts.Limit,
		PartialFailure:      invalidCardsSkipped > 0,
		InvalidCardsSkipped: invalidCardsSkipped,
		InvalidContacts:     invalidContacts,
	}
'''
)

replace_once(
    "internal/contacts/operations.go",
    '''	objects, overflow, _, err := c.report(ctx, book, uidQuery(uid), 3, maxReportBytes)
''',
    '''	objects, overflow, _, err := c.report(ctx, book, uidQuery(uid), 3, maxReportBytes, false, nil)
'''
)

marker = '\nfunc TestSearchQueryUsesEscapedServerSideFiltersAndBoundedFullData(t *testing.T) {'
test = r'''
func TestSearchSkipsInvalidVCardAndReportsReference(t *testing.T) {
	valid := v3Card("good", "Good Contact", "EMAIL:good@example.com")
	invalid := strings.Replace(v3Card("broken", "Broken Contact"), "N:Broken Contact;;;;\r\n", "", 1)
	cards := map[string]string{
		"/home/book/good.vcf":   valid,
		"/home/book/broken.vcf": invalid,
	}
	client := NewClient(discoveryDoer(multiCardResponseXML(cards)), "https://contacts.icloud.com/", allowContactsHost)
	book := discoveredBook(t, client)

	result, err := client.SearchContacts(context.Background(), SearchOptions{AddressBook: book.Identifier})
	if err != nil {
		t.Fatalf("SearchContacts() error = %v", err)
	}
	if len(result.Contacts) != 1 || result.Contacts[0].UID != "good" {
		t.Fatalf("contacts = %#v, want only valid contact", result.Contacts)
	}
	if !result.PartialFailure || result.InvalidCardsSkipped != 1 {
		t.Fatalf("partial/skipped = %v/%d, want true/1", result.PartialFailure, result.InvalidCardsSkipped)
	}
	if len(result.InvalidContacts) != 1 {
		t.Fatalf("invalid contacts = %#v, want one reference", result.InvalidContacts)
	}
	invalidRef := result.InvalidContacts[0]
	if invalidRef.AddressBook != book.Identifier || invalidRef.Resource != "broken.vcf" || invalidRef.Reason == "" {
		t.Fatalf("invalid contact reference = %#v", invalidRef)
	}
}

'''
path = root / "internal/contacts/contacts_test.go"
text = path.read_text()
if text.count(marker) != 1:
    raise SystemExit(f"contacts_test.go: expected one insertion marker, found {text.count(marker)}")
path.write_text(text.replace(marker, "\n" + test + marker.lstrip("\n"), 1))
