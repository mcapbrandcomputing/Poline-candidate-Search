<!-- Neshama template: edit with project specifics. -->
# Copyright & Security Markings

Edit this file to define copyright, security classification, and ownership markings.
These markings will be automatically included in generated files.

## Using Variables

You can use variables that will be replaced with values from `markings_metadata.yml` (or `.json`).

**Available Variables:**
- `{ORGANIZATION}` or `{ORG}` - Organization name
- `{COPYRIGHT_YEARS}` or `{YEARS}` - Copyright year range (e.g., 2024-2026)
- `{VERSION}` or `{VER}` - Version number
- `{LICENSE}` - License text
- `{CONTRIBUTORS}` - Formatted contributors list
- `{CONTRIBUTORS_DETAILED}` - Detailed contributors with roles/contributions
- `{DISTRIBUTION_STATEMENT}` or `{DISTRIBUTION}` - Distribution statement
- `{CLASSIFICATION}` or `{CLASS}` - Security classification
- `{CURRENT_YEAR}` - Current year
- `{CUSTOM_*}` - Custom fields from metadata

**Quick Start:**
1. Run `neshama markings metadata --init` to create metadata file
2. Run `neshama markings set organization "Your Company"` to set organization
3. Run `neshama markings add-contributor "Your Name"` to add contributors

---

## Example with Variables

Copyright (c) {COPYRIGHT_YEARS} {ORGANIZATION}
{LICENSE}

Contributors:
{CONTRIBUTORS_DETAILED}

Version: {VERSION}

---

## Example without Variables (Static)

Copyright (c) [YEAR] [ORGANIZATION NAME]
All rights reserved.

PROPRIETARY AND CONFIDENTIAL

This material contains proprietary information of [ORGANIZATION NAME].
Disclosure, reproduction, or use without express written authorization is prohibited.

Distribution: [DISTRIBUTION STATEMENT]
Security Classification: [CLASSIFICATION LEVEL]

For official use only.

---

**Note:** Edit this file to use either variables (dynamic) or static text. Remove the examples above before deployment.
