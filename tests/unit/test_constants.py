"""
Unit tests for config.constants module.

Tests API_PAYLOAD parameter format for DataTables server-side processing.
"""

import pytest
from config.constants import API_PAYLOAD, TENDER_FIELDS


class TestAPIPayload:
    """Test suite for API_PAYLOAD parameter validation."""
    
    def test_payload_has_all_base_parameters(self):
        """Verify all required base DataTables parameters are present."""
        required_base_params = [
            'sEcho',           # Drawing counter
            'iColumns',        # Number of columns
            'sColumns',        # Column names
            'iDisplayStart',   # Pagination start
            'iDisplayLength',  # Pagination length
            'sSearch',         # Global search value
            'bRegex',          # Global search regex flag
            'iSortCol_0',      # Sort column index
            'sSortDir_0',      # Sort direction
            'iSortingCols',    # Number of sorting columns
        ]
        
        for param in required_base_params:
            assert param in API_PAYLOAD, f"Missing required base parameter: {param}"
    
    def test_payload_has_correct_column_count(self):
        """Verify iColumns matches the expected number of columns."""
        assert API_PAYLOAD['iColumns'] == '10', "iColumns should be '10'"
    
    def test_scolumns_has_proper_names(self):
        """Verify sColumns contains actual column names, not empty values."""
        sColumns = API_PAYLOAD['sColumns']
        
        # Should not be just empty commas
        assert sColumns != ',,,,,,,,,', "sColumns should have actual column names"
        
        # Should contain expected column names
        expected_columns = [
            'department', 'notice_number', 'category', 'work_name',
            'tender_value', 'published_date', 'bid_start_date',
            'bid_close_date', 'tender_id', 'actions'
        ]
        
        column_names = sColumns.split(',')
        assert len(column_names) == 10, f"Expected 10 columns, got {len(column_names)}"
        assert column_names == expected_columns, f"Column names don't match expected order"
    
    def test_all_column_specific_parameters_present(self):
        """Verify all column-specific parameters exist for each column."""
        num_columns = int(API_PAYLOAD['iColumns'])
        
        for i in range(num_columns):
            # Each column should have these 5 parameters
            required_params = [
                f'mDataProp_{i}',
                f'sSearch_{i}',
                f'bRegex_{i}',
                f'bSearchable_{i}',
                f'bSortable_{i}',
            ]
            
            for param in required_params:
                assert param in API_PAYLOAD, f"Missing parameter: {param}"
    
    def test_mdataprop_values_match_indices(self):
        """Verify mDataProp values match their column indices."""
        num_columns = int(API_PAYLOAD['iColumns'])
        
        for i in range(num_columns):
            param_name = f'mDataProp_{i}'
            expected_value = str(i)
            actual_value = API_PAYLOAD[param_name]
            
            assert actual_value == expected_value, \
                f"{param_name} should be '{expected_value}', got '{actual_value}'"
    
    def test_non_sortable_columns(self):
        """Verify tender_id and actions columns are marked as non-sortable."""
        # Columns 8 (tender_id) and 9 (actions) should not be sortable
        assert API_PAYLOAD['bSortable_8'] == 'false', "Column 8 (tender_id) should not be sortable"
        assert API_PAYLOAD['bSortable_9'] == 'false', "Column 9 (actions) should not be sortable"
        
        # Other columns should be sortable
        for i in range(8):
            assert API_PAYLOAD[f'bSortable_{i}'] == 'true', \
                f"Column {i} should be sortable"
    
    def test_all_columns_searchable(self):
        """Verify all columns are marked as searchable."""
        num_columns = int(API_PAYLOAD['iColumns'])
        
        for i in range(num_columns):
            assert API_PAYLOAD[f'bSearchable_{i}'] == 'true', \
                f"Column {i} should be searchable"
    
    def test_default_search_values_empty(self):
        """Verify search fields are empty by default."""
        assert API_PAYLOAD['sSearch'] == '', "Global search should be empty by default"
        
        num_columns = int(API_PAYLOAD['iColumns'])
        for i in range(num_columns):
            assert API_PAYLOAD[f'sSearch_{i}'] == '', \
                f"Column {i} search should be empty by default"
    
    def test_regex_flags_false_by_default(self):
        """Verify regex flags are set to false by default."""
        assert API_PAYLOAD['bRegex'] == 'false', "Global regex should be false"
        
        num_columns = int(API_PAYLOAD['iColumns'])
        for i in range(num_columns):
            assert API_PAYLOAD[f'bRegex_{i}'] == 'false', \
                f"Column {i} regex should be false by default"
    
    def test_total_parameter_count(self):
        """Verify total parameter count is correct (60 for 10 columns)."""
        # 10 base parameters + (5 parameters × 10 columns) = 60 total
        expected_count = 10 + (5 * 10)
        actual_count = len(API_PAYLOAD)
        
        assert actual_count == expected_count, \
            f"Expected {expected_count} parameters, got {actual_count}"
    
    def test_default_sorting_configuration(self):
        """Verify default sorting is set to first column, ascending."""
        assert API_PAYLOAD['iSortCol_0'] == '0', "Should sort by first column by default"
        assert API_PAYLOAD['sSortDir_0'] == 'asc', "Should sort ascending by default"
        assert API_PAYLOAD['iSortingCols'] == '1', "Should have 1 sorting column by default"
    
    def test_default_pagination(self):
        """Verify default pagination settings."""
        assert API_PAYLOAD['iDisplayStart'] == '0', "Should start at first record"
        assert API_PAYLOAD['iDisplayLength'] == '10', "Should display 10 records by default"
    
    def test_scolumns_matches_tender_fields(self):
        """Verify sColumns order matches TENDER_FIELDS mapping."""
        column_names = API_PAYLOAD['sColumns'].split(',')
        
        # Build expected column names from TENDER_FIELDS
        num_columns = len(column_names)
        expected_names = [''] * num_columns
        for field, index in TENDER_FIELDS.items():
            if index < num_columns:
                expected_names[index] = field
        
        assert column_names == expected_names, \
            f"sColumns order doesn't match TENDER_FIELDS mapping"


class TestTenderFields:
    """Test suite for TENDER_FIELDS mapping."""
    
    def test_all_columns_mapped(self):
        """Verify all 10 columns have field mappings."""
        expected_fields = {
            'department', 'notice_number', 'category', 'work_name',
            'tender_value', 'published_date', 'bid_start_date',
            'bid_close_date', 'tender_id', 'actions'
        }
        
        assert set(TENDER_FIELDS.keys()) == expected_fields, \
            "TENDER_FIELDS should have all expected field names"
    
    def test_indices_are_sequential(self):
        """Verify column indices are 0-9 with no gaps."""
        indices = sorted(TENDER_FIELDS.values())
        expected_indices = list(range(10))
        
        assert indices == expected_indices, \
            f"Indices should be 0-9, got {indices}"
    
    def test_no_duplicate_indices(self):
        """Verify no two fields map to the same index."""
        indices = list(TENDER_FIELDS.values())
        assert len(indices) == len(set(indices)), \
            "Found duplicate indices in TENDER_FIELDS"
