# DataTables API Parameter Format Documentation

## Overview

The `API_PAYLOAD` in `config/constants.py` contains all 60 parameters required for DataTables server-side processing (legacy format version 1.9). This document explains the complete parameter structure for the Telangana eTender portal API endpoint.

## Parameter Structure

### Total: 60 Parameters
- **Base parameters**: 10
- **Column-specific parameters**: 50 (5 parameters × 10 columns)

## Base Parameters (10)

| Parameter | Value | Description |
|-----------|-------|-------------|
| `sEcho` | "1" | Drawing counter - ensures AJAX responses match requests |
| `iColumns` | "10" | Number of columns in the table |
| `sColumns` | "department,notice_number,..." | Comma-separated list of column names |
| `iDisplayStart` | "0" | Record index to start displaying from |
| `iDisplayLength` | "10" | Number of records to display per page |
| `sSearch` | "" | Global search value |
| `bRegex` | "false" | Whether global search is regex |
| `iSortCol_0` | "0" | Column index to sort by |
| `sSortDir_0` | "asc" | Sort direction (asc/desc) |
| `iSortingCols` | "1" | Number of columns being sorted |

## Column-Specific Parameters (50)

For each of the 10 columns (indexed 0-9), there are 5 parameters:

| Parameter Pattern | Example | Description |
|------------------|---------|-------------|
| `mDataProp_N` | `mDataProp_0`: "0" | Column identifier/index |
| `sSearch_N` | `sSearch_0`: "" | Search value for this column |
| `bRegex_N` | `bRegex_0`: "false" | Whether column search is regex |
| `bSearchable_N` | `bSearchable_0`: "true" | Whether this column is searchable |
| `bSortable_N` | `bSortable_0`: "true" | Whether this column is sortable |

## Column Mapping

| Index | Column Name | Sortable | Description |
|-------|-------------|----------|-------------|
| 0 | department | Yes | Department/Organization name |
| 1 | notice_number | Yes | Tender notice number |
| 2 | category | Yes | Tender category |
| 3 | work_name | Yes | Work/project name |
| 4 | tender_value | Yes | Estimated tender value |
| 5 | published_date | Yes | Date tender was published |
| 6 | bid_start_date | Yes | Bid submission start date |
| 7 | bid_close_date | Yes | Bid submission close date |
| 8 | tender_id | **No** | Unique tender identifier |
| 9 | actions | **No** | Action buttons (View Details, etc.) |

## Key Implementation Details

### 1. sColumns Must Have Actual Names

The `sColumns` parameter must contain the actual column names separated by commas, not just empty commas.

**WRONG:** 
```python
"sColumns": ",,,,,,,,"
```

**CORRECT:**
```python
"sColumns": "department,notice_number,category,work_name,tender_value,published_date,bid_start_date,bid_close_date,tender_id,actions"
```

This was the primary fix in Issue #1 - the original implementation had empty commas which caused the API to not properly recognize column names.

### 2. Non-Sortable Columns

Columns 8 and 9 are marked as non-sortable (`bSortable_8: "false"`, `bSortable_9: "false"`):
- **Column 8 (tender_id)**: Unique identifier - no meaningful sort order
- **Column 9 (actions)**: UI elements (buttons/links) - not data that should be sorted

All other columns (0-7) are sortable.

### 3. All Columns Are Searchable

All 10 columns have `bSearchable_N: "true"` to enable server-side filtering on any column.

### 4. Default Configuration

- **Pagination**: Starts at record 0, displays 10 records per page
- **Sorting**: Default sort by column 0 (department) in ascending order
- **Search**: No default search value (empty strings)
- **Regex**: All regex flags set to false by default

## Usage Example

```python
from config.constants import API_PAYLOAD

# Use the complete parameter set in API request
response = session.post(
    API_ENDPOINT,
    data=API_PAYLOAD,
    headers=API_HEADERS
)

# Parse JSON response
data = response.json()
tenders = data.get('aaData', [])
```

## Modifying Parameters

To customize the API request:

```python
from config.constants import API_PAYLOAD

# Create a copy to modify
params = API_PAYLOAD.copy()

# Change pagination
params['iDisplayStart'] = '20'  # Skip first 20 records
params['iDisplayLength'] = '50'  # Show 50 records per page

# Add search filter
params['sSearch'] = 'infrastructure'  # Global search

# Change sorting
params['iSortCol_0'] = '5'  # Sort by published_date
params['sSortDir_0'] = 'desc'  # Descending order

# Filter specific column
params['sSearch_3'] = 'road construction'  # Search in work_name column
```

## Testing

Comprehensive parameter validation tests are available in `tests/unit/test_constants.py`:

```bash
# Run all parameter tests
pytest tests/unit/test_constants.py -v

# Run specific test
pytest tests/unit/test_constants.py::TestAPIPayload::test_scolumns_has_proper_names -v
```

### Test Coverage

The test suite includes 16 tests covering:
- ✅ All base parameters present
- ✅ Correct column count (10)
- ✅ sColumns has proper names (not empty)
- ✅ All column-specific parameters present
- ✅ mDataProp values match indices
- ✅ Non-sortable columns configuration
- ✅ All columns searchable
- ✅ Default search values empty
- ✅ Regex flags false by default
- ✅ Total parameter count (60)
- ✅ Default sorting configuration
- ✅ Default pagination
- ✅ sColumns matches TENDER_FIELDS
- ✅ All columns mapped in TENDER_FIELDS
- ✅ Indices are sequential (0-9)
- ✅ No duplicate indices

## Troubleshooting

### API Returns Empty Data

If the API returns `{"aaData": [], "iTotalRecords": 0}`:
- ✅ Check that `sColumns` has actual column names, not empty commas
- ✅ Verify all 60 parameters are present
- ✅ Ensure session cookie is established first
- ✅ Check that headers include `X-Requested-With: XMLHttpRequest`

### API Returns 403 Forbidden

- ✅ Establish session by visiting main page first
- ✅ Use complete headers from `config.constants.API_HEADERS`
- ✅ Verify running from allowed geography (India/Mumbai region)

## References

- **DataTables Legacy Documentation**: https://legacy.datatables.net/usage/server-side
- **Server-side Processing**: https://datatables.net/manual/server-side
- **Issue #1**: Fix API Scraper Session Management
- **Related Files**:
  - `config/constants.py`: Parameter definitions
  - `src/scrapers/api_scraper.py`: API scraper implementation
  - `tests/unit/test_constants.py`: Parameter validation tests

## Version History

- **v1.0** (2025-10-29): Initial implementation with 60 parameters, empty sColumns
- **v1.1** (2025-10-29): Fixed sColumns to include actual column names ✅
