# Changelog

## 0.1.1

- Keep Contacts search usable when individual iCloud vCards are malformed or unsupported.
- Search skips only per-card protocol/decode failures; transport, containment, ETag and payload-limit failures remain strict.
- Search results report `partialFailure`, `invalidCardsSkipped`, and up to 20 safe invalid-contact references containing the address-book ID, final resource name and sanitized reason.
- Exact contact reads remain strict so a malformed target contact is never silently treated as valid.
- Added upstream Contacts package tests during the image build.

## 0.1.0

- Initial Home Assistant App wrapper.
- Pinned ThomasCrouzet/icloud-mcp v0.4.1 commit.
- Authenticated Streamable HTTP bridge with supergateway 4.1.0.
- Calendar enabled; Contacts and Mail independently configurable.
- Safe read-only default and no host port mapping.
