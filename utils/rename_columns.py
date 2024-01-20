rename_sec_columns = {
    'Symbol': 'symbol',   # The one to four or five character identifier for each NASDAQ-listed security.
    'ACT Symbol': 'symbol',   # Identifier for each security used in ACT and CTCI connectivity protocol. Typical identifiers have 1-5 character root symbol and then 1-3 characters for suffixes. Allow up to 14 characters.
    'Security Name': 'security_name',   # Company issuing the security.
    'Market Category': 'market_category',   # The category assigned to the issue by NASDAQ based on Listing Requirements.
    'Exchange': 'exchange',   # The listing stock exchange or market of a security.
    'Test Issue': 'test_issue',   # Indicates whether or not the security is a test security. Values: Y = yes, it is a test issue. N = no, it is not a test issue
    'CQS Symbol': 'cqs_symbol',   # Identifier of the security used to disseminate data via the SIAC Consolidated Quotation System (CQS) and Consolidated Tape System (CTS) data feeds. 
    'Financial Status': 'financial_status',   # Indicates when an issuer has failed to submit its regulatory filings on a timely basis, has failed to meet NASDAQ's continuing listing standards, and/or has filed for bankruptcy.
    'Round Lot': 'round_lot',   # The number of shares that make up a round lot for the given security.
    'Round Lot Size': 'round_lot_size',   # Idem.
    'NASDAQ Symbol': 'nasdaq_symbol',   # Identifier of the security used to in various NASDAQ connectivity protocols and NASDAQ market data feeds.
    'ETF': 'is_etf',   # Identifies whether the security is an exchange traded fund (ETF).
    'NextShares': 'nextshares', # N/A
}

rename_yf_columns = {
    "Open": "open",
    "High": "high",
    "Close": "close",
    "Low": "low",
    "Adj Close": "adj_close",
    "Volume": "volume",
}