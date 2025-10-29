"""
Constants and URL patterns for Tender Scraper Engine
"""

# URL Endpoints
TENDER_LIST_PAGE = "/TenderDetailsHome.html"
TENDER_LIST_API = "/TenderDetailsHomeJson.html"
TENDER_DETAIL_PAGE = "/ViewDetailTenderDetail.html"

# Table selectors
TABLE_ID = "pagetable13"
TABLE_ROW_SELECTOR = "tbody tr"

# Tender fields mapping (from API/table columns)
TENDER_FIELDS = {
    "department": 0,
    "notice_number": 1,
    "category": 2,
    "work_name": 3,
    "tender_value": 4,
    "published_date": 5,
    "bid_start_date": 6,
    "bid_close_date": 7,
    "tender_id": 8,
    "actions": 9,
}

# HTTP Headers for API scraping
# Complete headers captured from browser DevTools for AJAX requests
# These headers mimic a real browser to avoid 403 Forbidden errors
API_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "tender.telangana.gov.in",
    "Origin": "https://tender.telangana.gov.in",
    "Referer": "https://tender.telangana.gov.in/TenderDetailsHome.html",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"macOS"',
}

# HTTP Headers for document downloads
DOWNLOAD_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://tender.telangana.gov.in/",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# API Request payload (default parameters)
API_PAYLOAD = {
    "sEcho": "1",
    "iColumns": "10",
    "sColumns": ",,,,,,,,",
    "iDisplayStart": "0",
    "iDisplayLength": "10",
    "mDataProp_0": "0",
    "sSearch_0": "",
    "bRegex_0": "false",
    "bSearchable_0": "true",
    "bSortable_0": "true",
    "mDataProp_1": "1",
    "sSearch_1": "",
    "bRegex_1": "false",
    "bSearchable_1": "true",
    "bSortable_1": "true",
    "mDataProp_2": "2",
    "sSearch_2": "",
    "bRegex_2": "false",
    "bSearchable_2": "true",
    "bSortable_2": "true",
    "mDataProp_3": "3",
    "sSearch_3": "",
    "bRegex_3": "false",
    "bSearchable_3": "true",
    "bSortable_3": "true",
    "mDataProp_4": "4",
    "sSearch_4": "",
    "bRegex_4": "false",
    "bSearchable_4": "true",
    "bSortable_4": "true",
    "mDataProp_5": "5",
    "sSearch_5": "",
    "bRegex_5": "false",
    "bSearchable_5": "true",
    "bSortable_5": "true",
    "mDataProp_6": "6",
    "sSearch_6": "",
    "bRegex_6": "false",
    "bSearchable_6": "true",
    "bSortable_6": "true",
    "mDataProp_7": "7",
    "sSearch_7": "",
    "bRegex_7": "false",
    "bSearchable_7": "true",
    "bSortable_7": "true",
    "mDataProp_8": "8",
    "sSearch_8": "",
    "bRegex_8": "false",
    "bSearchable_8": "true",
    "bSortable_8": "false",
    "mDataProp_9": "9",
    "sSearch_9": "",
    "bRegex_9": "false",
    "bSearchable_9": "true",
    "bSortable_9": "false",
    "sSearch": "",
    "bRegex": "false",
    "iSortCol_0": "0",
    "sSortDir_0": "asc",
    "iSortingCols": "1",
}

# Regex patterns for document parsing
PATTERNS = {
    "emd": r"EMD[:\s]*(?:Rs\.?|INR)?[\s]*([0-9,]+(?:\.[0-9]{2})?)",
    "tender_fee": r"Tender[:\s]+Fee[:\s]*(?:Rs\.?|INR)?[\s]*([0-9,]+(?:\.[0-9]{2})?)",
    "estimated_cost": r"Estimated[:\s]+Cost[:\s]*(?:Rs\.?|INR)?[\s]*([0-9,]+(?:\.[0-9]{2})?)",
    "date": r"(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
}

# File type extensions
DOCUMENT_TYPES = {
    "pdf": [".pdf"],
    "excel": [".xls", ".xlsx"],
    "word": [".doc", ".docx"],
}

# Status codes
STATUS = {
    "pending": "PENDING",
    "in_progress": "IN_PROGRESS",
    "completed": "COMPLETED",
    "failed": "FAILED",
    "downloading": "DOWNLOADING",
    "downloaded": "DOWNLOADED",
    "parsing": "PARSING",
    "parsed": "PARSED",
}
