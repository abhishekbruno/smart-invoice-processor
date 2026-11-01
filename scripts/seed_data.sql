-- Smart Invoice Processor Demo Seed Data
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (1, 'ACME-88401', 'Acme Office Supplies', '2024-05-10', '2024-06-09', 'Global Enterprises Corp.', 2200.0, 176.0, 2376.0, 'USD', 'PAID', 'data/processed/Acme_Office_Supplies_ACME_88401.pdf', '6a9b30a9e49a2628cd6932efdfc9f4507c7730662410975eba2540b70c9df181', 'Acme Office Supplies
INVOICE
Invoice #: ACME-88401
1200 Industrial Parkway, Chicago, IL 60607
Invoice Date: 2024-05-10
Due Date: 2024-06-09
Status: PAID
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Ergonomic Mesh Office Chair
4
$250.00
$1,000.00
Ultra-Wide 34 inch IPS Monitor
2
$450.00
$900.00
Mechanical Wireless Keyboards
4
$75.00
$300.00
Subtotal:
$2,200.00
Tax Amount:
$176.00
Total (USD):
$2,376.00
Thank you for your business. For billing inquiries, contact accounting@acmeofficesupplies.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:28', '2026-11-01 14:04:28', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (2, 'INV-AWS-2024-8192', 'Amazon Web Services', '2024-01-15', '2024-02-14', 'Global Enterprises Corp.', 735.0, 58.8, 793.8, 'USD', 'PAID', 'data/processed/AWS_INV_2024_8192.pdf', 'e65e542098bd1dcee4d3cb12d7cef1669ea77814ac4ad763379e584451e03b9a', 'Amazon Web
Services, Inc.
INVOICE
Invoice #: INV-AWS-2024-8192
410 Terry Avenue North, Seattle, WA 98109-5210
Invoice Date: 2024-01-15
Due Date: 2024-02-14
Status: PAID
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Amazon Elastic Compute Cloud (EC2) c5.xlarge
3
$145.00
$435.00
Amazon Simple Storage Service (S3) Standard
1
$50.00
$50.00
AWS Relational Database Service (RDS) Postgres
1
$215.00
$215.00
AWS CloudWatch Logs and Metrics
1
$35.00
$35.00
Subtotal:
$735.00
Tax Amount:
$58.80
Total (USD):
$793.80
Thank you for your business. For billing inquiries, contact accounting@amazonwebservicesinc..com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:28', '2026-11-01 14:04:28', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (3, 'CS-SEC-7701', 'CyberShield Security', '2024-07-15', '2024-08-14', 'Global Enterprises Europe', 5150.0, 1081.5, 6231.5, 'EUR', 'PAID', 'data/processed/CyberShield_Security_CS_7701.pdf', 'a66438589ed1c9ecff9aa896e000e62e3af4454667f52b01a9239e212b678f2f', 'CyberShield Security
INVOICE
Invoice #: CS-SEC-7701
Rue du Commerce 45, 1000 Brussels, Belgium
Invoice Date: 2024-07-15
Due Date: 2024-08-14
Status: PAID
BILL TO:
Global Enterprises Europe
Keizersgracht 421, 1016 EK Amsterdam, Netherlands
Description
Qty
Unit Price
Amount
Quarterly Cloud Security Posture Assessment
1
€1,800.00
€1,800.00
External Network Penetration Testing
1
€2,400.00
€2,400.00
SOC2 Compliance Remediation Review
1
€950.00
€950.00
Subtotal:
€5,150.00
Tax Amount:
€1,081.50
Total (EUR):
€6,231.50
Thank you for your business. For billing inquiries, contact accounting@cybershieldsecurity.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:28', '2026-11-01 14:04:28', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (4, 'DSA-IN-3329', 'DataStream Analytics', '2024-09-12', '2024-10-12', 'Global Enterprises India Pvt Ltd', NULL, NULL, NULL, 'INR', 'PAID', 'data/processed/DataStream_Analytics_DSA_3329.pdf', 'c7216b7c9431da1ea5ff83142d4505fe1e67c6a99fa73ac14472201663391123', 'DataStream Analytics
INVOICE
Invoice #: DSA-IN-3329
Plot 12, HITEC City, Hyderabad, Telangana 500081, India
Invoice Date: 2024-09-12
Due Date: 2024-10-12
Status: PAID
BILL TO:
Global Enterprises India Pvt Ltd
Cyber City, Gurugram, Haryana 122002, India
Description
Qty
Unit Price
Amount
Real-time Kafka Event Streaming Setup
1
I80,000.00
I80,000.00
Apache Spark Data Aggregation Pipeline
1
I65,000.00
I65,000.00
Data Engineering Team Knowledge Transfer
10
I3,000.00
I30,000.00
Subtotal:
I175,000.00
Tax Amount:
I31,500.00
Total (INR):
I206,500.00
Thank you for your business. For billing inquiries, contact accounting@datastreamanalytics.com.', '{"invoice_number": 0.95, "vendor_name": 0.5, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85}', '["Total amount was not detected in document.", "Flagged for review: Missing or zero total amount."]', 'suspected_duplicate', '2026-11-01 14:04:29', '2026-11-01 14:04:29', 1, 16, 'Superseded by complete extraction in Invoice #16');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (5, 'DCG-2024-055', 'DevConsulting Group', '2024-06-25', '2024-07-10', 'Global Enterprises India Pvt Ltd', NULL, NULL, NULL, 'INR', 'DUE UPON RECEIPT', 'data/processed/DevConsulting_Group_DCG_055.pdf', 'f94369791349c52179f7d377e9098386cf1a2d4ae8af5e1a631d799239599130', 'DevConsulting Group
INVOICE
Invoice #: DCG-2024-055
Level 6, Tech Park, Whitefield, Bengaluru, Karnataka
560066, India
Invoice Date: 2024-06-25
Due Date: 2024-07-10
Status: DUE UPON RECEIPT
BILL TO:
Global Enterprises India Pvt Ltd
Cyber City, Gurugram, Haryana 122002, India
Description
Qty
Unit Price
Amount
Python & Cloud Backend Architecture Consulting
40
I2,500.00
I100,000.00
Database Migration & Performance Tuning
15
I3,000.00
I45,000.00
Subtotal:
I145,000.00
Tax Amount:
I26,100.00
Total (INR):
I171,100.00
Thank you for your business. For billing inquiries, contact accounting@devconsultinggroup.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85}', '["Total amount was not detected in document.", "Flagged for review: Missing or zero total amount."]', 'suspected_duplicate', '2026-11-01 14:04:29', '2026-11-01 14:04:29', 1, 17, 'Superseded by complete extraction in Invoice #17');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (6, 'DO-INV-11029', 'DigitalOcean', '2024-04-18', '2024-05-02', 'Global Enterprises Corp.', 120.0, 9.6, 129.6, 'USD', 'OVERDUE', 'data/processed/DigitalOcean_DO_11029.pdf', '085d9c4a21b9a02ee2a92c66749f2fe113ab34c9542f53f06dfb333d2ff59659', 'DigitalOcean, LLC
INVOICE
Invoice #: DO-INV-11029
101 Avenue of the Americas, 10th Floor, New York, NY
10013
Invoice Date: 2024-04-18
Due Date: 2024-05-02
Status: OVERDUE
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Basic Droplet 4GB Memory 2 vCPUs
2
$24.00
$48.00
Managed PostgreSQL Cluster DBaaS
1
$60.00
$60.00
Spaces Object Storage 250GB
1
$12.00
$12.00
Subtotal:
$120.00
Tax Amount:
$9.60
Total (USD):
$129.60
Thank you for your business. For billing inquiries, contact accounting@digitaloceanllc.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:29', '2026-11-01 14:04:29', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (7, 'FN-UK-90231', 'FastNet Internet Services', '2024-06-01', '2024-06-30', 'Global Enterprises UK', 780.0, 156.0, 936.0, 'GBP', 'PAID', 'data/processed/FastNet_Internet_FN_90231.pdf', 'a87b025a912b58771f975fdfee250060eaaf9aeaf78df7899503da9b39b90135', 'FastNet Internet
Services
INVOICE
Invoice #: FN-UK-90231
88 King William Street, London, EC4N 7TW, United
Kingdom
Invoice Date: 2024-06-01
Due Date: 2024-06-30
Status: PAID
BILL TO:
Global Enterprises UK
100 Bishopsgate, London, EC2N 4AG, United Kingdom
Description
Qty
Unit Price
Amount
Dedicated Leased Line 1Gbps Fiber Internet
1
£650.00
£650.00
Static IPv4 Subnet Allocation /28
1
£45.00
£45.00
Managed Cisco Edge Router Service
1
£85.00
£85.00
Subtotal:
£780.00
Tax Amount:
£156.00
Total (GBP):
£936.00
Thank you for your business. For billing inquiries, contact accounting@fastnetinternetservices.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:29', '2026-11-01 14:04:29', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (8, 'GCP-INV-2024-4410', 'Google Cloud', '2024-03-05', '2024-04-04', 'Global Enterprises Corp.', 610.0, 48.8, 658.8, 'USD', 'PENDING', 'data/processed/Google_Cloud_GCP_4410.pdf', '5b2f0d862915655263971503ddff4373d3520ff579ca4a4b87d0c2984ee6c743', 'Google Cloud Platform
INVOICE
Invoice #: GCP-INV-2024-4410
1600 Amphitheatre Parkway, Mountain View, CA 94043
Invoice Date: 2024-03-05
Due Date: 2024-04-04
Status: PENDING
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
BigQuery Active Analysis and Storage
1
$320.00
$320.00
Cloud Run Serverless Compute Units
4
$45.00
$180.00
Google Cloud Armor Network Protection
1
$110.00
$110.00
Subtotal:
$610.00
Tax Amount:
$48.80
Total (USD):
$658.80
Thank you for your business. For billing inquiries, contact accounting@googlecloudplatform.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:29', '2026-11-01 14:04:29', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (9, 'MSFT-INV-99214', 'Microsoft', '2024-02-10', '2024-03-12', 'Global Enterprises Corp.', 860.0, 68.8, 928.8, 'USD', 'PAID', 'data/processed/Microsoft_Azure_MSFT_99214.pdf', 'f36ba043a2c0d387b114b32798f726e0742eb1cb5c3894249afa66667783d69b', 'Microsoft Corporation
INVOICE
Invoice #: MSFT-INV-99214
One Microsoft Way, Redmond, WA 98052
Invoice Date: 2024-02-10
Due Date: 2024-03-12
Status: PAID
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Azure Virtual Machines D4s_v5 Instance
2
$180.00
$360.00
Microsoft 365 E5 Enterprise License
10
$38.00
$380.00
Azure Cosmos DB Reserved Throughput
1
$120.00
$120.00
Subtotal:
$860.00
Tax Amount:
$68.80
Total (USD):
$928.80
Thank you for your business. For billing inquiries, contact accounting@microsoftcorporation.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:29', '2026-11-01 14:04:29', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (10, 'SLK-EUR-5012', 'Slack', '2024-04-01', '2024-05-01', 'Global Enterprises Europe', 425.0, 89.25, 514.25, 'EUR', 'PAID', 'data/processed/Slack_Technologies_SLK_5012.pdf', '4bf4925a03c84b581e0671f37f6315338667540139e20f6be9539fe2a208a28e', 'Slack Technologies
Limited
INVOICE
Invoice #: SLK-EUR-5012
4th Floor, One Park Place, Upper Hatch Street, Dublin 2,
Ireland
Invoice Date: 2024-04-01
Due Date: 2024-05-01
Status: PAID
BILL TO:
Global Enterprises Europe
Keizersgracht 421, 1016 EK Amsterdam, Netherlands
Description
Qty
Unit Price
Amount
Slack Enterprise Grid User Seats
25
€15.00
€375.00
Slack Connect Multi-Organization Channels
1
€50.00
€50.00
Subtotal:
€425.00
Tax Amount:
€89.25
Total (EUR):
€514.25
Thank you for your business. For billing inquiries, contact accounting@slacktechnologieslimited.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:29', '2026-11-01 14:04:29', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (11, 'TSI-2024-108', 'TechSolutions, LLC', '2024-08-05', '2024-09-04', 'Global Enterprises Corp.', 1600.0, 128.0, 1728.0, 'USD', 'PENDING', 'data/processed/TechSolutions_TSI_108.pdf', '60d8193fecf5cedc8a39cef5bd56bab151e86dbc4c1b587eecf334fc73f04f2d', 'TechSolutions, LLC
INVOICE
Invoice #: TSI-2024-108
500 Technology Way, Austin, TX 78701
Invoice Date: 2024-08-05
Due Date: 2024-09-04
Status: PENDING
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Custom CRM API Integration Pipeline
1
$1,250.00
$1,250.00
Automated Webhook Monitoring Service
1
$350.00
$350.00
Subtotal:
$1,600.00
Tax Amount:
$128.00
Total (USD):
$1,728.00
Thank you for your business. For billing inquiries, contact accounting@techsolutionsllc.com.', '{"invoice_number": 0.95, "vendor_name": 0.75, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:29', '2026-11-01 14:04:29', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (12, 'TW-881290', 'Twilio', '2024-03-20', '2024-04-19', 'Global Enterprises Corp.', 237.5, 19.0, 256.5, 'USD', 'PAID', 'data/processed/Twilio_TW_881290.pdf', '54e111c99ca1adf2c50b17f164869d288b7fc71fb8fee556acf07ec9a5454250', 'Twilio Inc.
INVOICE
Invoice #: TW-881290
101 Spear Street, 1st Floor, San Francisco, CA 94105
Invoice Date: 2024-03-20
Due Date: 2024-04-19
Status: PAID
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Programmable SMS Message Traffic
25000
$0.01
$187.50
Voice SIP Trunking Outbound Minutes
2000
$0.01
$30.00
Dedicated Local Phone Numbers
2
$10.00
$20.00
Subtotal:
$237.50
Tax Amount:
$19.00
Total (USD):
$256.50
Thank you for your business. For billing inquiries, contact accounting@twilioinc..com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:04:29', '2026-11-01 14:04:29', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (13, 'ACME-88401', 'Acme Office Supplies', '2024-05-10', '2024-06-09', 'Global Enterprises Corp.', 2200.0, 176.0, 2376.0, 'USD', 'PAID', 'data/processed/Acme_Office_Supplies_ACME_88401.pdf', '5289e16674ecaca73425f575c93ff25f47353d4808b01253b3e2ac2a1ba0e1ba', 'Acme Office Supplies
INVOICE
Invoice #: ACME-88401
1200 Industrial Parkway, Chicago, IL 60607
Invoice Date: 2024-05-10
Due Date: 2024-06-09
Status: PAID
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Ergonomic Mesh Office Chair
4
$250.00
$1,000.00
Ultra-Wide 34 inch IPS Monitor
2
$450.00
$900.00
Mechanical Wireless Keyboards
4
$75.00
$300.00
Subtotal:
$2,200.00
Tax Amount:
$176.00
Total (USD):
$2,376.00
Thank you for your business. For billing inquiries, contact accounting@acmeofficesupplies.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 1, 'Exact logical duplicate of Invoice #1 (ACME-88401) from Acme Office Supplies');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (14, 'INV-AWS-2024-8192', 'Amazon Web Services', '2024-01-15', '2024-02-14', 'Global Enterprises Corp.', 735.0, 58.8, 793.8, 'USD', 'PAID', 'data/processed/AWS_INV_2024_8192.pdf', '7684178bfb068f5ab111f10105e7a83a2cf8fa4ad49ae8fc92998d82535fa836', 'Amazon Web
Services, Inc.
INVOICE
Invoice #: INV-AWS-2024-8192
410 Terry Avenue North, Seattle, WA 98109-5210
Invoice Date: 2024-01-15
Due Date: 2024-02-14
Status: PAID
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Amazon Elastic Compute Cloud (EC2) c5.xlarge
3
$145.00
$435.00
Amazon Simple Storage Service (S3) Standard
1
$50.00
$50.00
AWS Relational Database Service (RDS) Postgres
1
$215.00
$215.00
AWS CloudWatch Logs and Metrics
1
$35.00
$35.00
Subtotal:
$735.00
Tax Amount:
$58.80
Total (USD):
$793.80
Thank you for your business. For billing inquiries, contact accounting@amazonwebservicesinc..com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 2, 'Exact logical duplicate of Invoice #2 (INV-AWS-2024-8192) from Amazon Web Services');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (15, 'CS-SEC-7701', 'CyberShield Security', '2024-07-15', '2024-08-14', 'Global Enterprises Europe', 5150.0, 1081.5, 6231.5, 'EUR', 'PAID', 'data/processed/CyberShield_Security_CS_7701.pdf', '79092b06037fa9186fb859777699eb7d1bac7b7854fe8f1a830d8323b9cd20a7', 'CyberShield Security
INVOICE
Invoice #: CS-SEC-7701
Rue du Commerce 45, 1000 Brussels, Belgium
Invoice Date: 2024-07-15
Due Date: 2024-08-14
Status: PAID
BILL TO:
Global Enterprises Europe
Keizersgracht 421, 1016 EK Amsterdam, Netherlands
Description
Qty
Unit Price
Amount
Quarterly Cloud Security Posture Assessment
1
€1,800.00
€1,800.00
External Network Penetration Testing
1
€2,400.00
€2,400.00
SOC2 Compliance Remediation Review
1
€950.00
€950.00
Subtotal:
€5,150.00
Tax Amount:
€1,081.50
Total (EUR):
€6,231.50
Thank you for your business. For billing inquiries, contact accounting@cybershieldsecurity.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 3, 'Exact logical duplicate of Invoice #3 (CS-SEC-7701) from CyberShield Security');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (16, 'DSA-IN-3329', 'DataStream Analytics', '2024-09-12', '2024-10-12', 'Global Enterprises India Pvt Ltd', 175000.0, 31500.0, 206500.0, 'INR', 'PAID', 'data/processed/DataStream_Analytics_DSA_3329.pdf', '23c1cccf369d22bf4589ed542ba7461c978357c8d7be785cd7e038047cf4b915', 'DataStream Analytics
INVOICE
Invoice #: DSA-IN-3329
Plot 12, HITEC City, Hyderabad, Telangana 500081, India
Invoice Date: 2024-09-12
Due Date: 2024-10-12
Status: PAID
BILL TO:
Global Enterprises India Pvt Ltd
Cyber City, Gurugram, Haryana 122002, India
Description
Qty
Unit Price
Amount
Real-time Kafka Event Streaming Setup
1
INR 80,000.00
INR 80,000.00
Apache Spark Data Aggregation Pipeline
1
INR 65,000.00
INR 65,000.00
Data Engineering Team Knowledge Transfer
10
INR 3,000.00
INR 30,000.00
Subtotal:
INR 175,000.00
Tax Amount:
INR 31,500.00
Total (INR):
INR 206,500.00
Thank you for your business. For billing inquiries, contact accounting@datastreamanalytics.com.', '{"invoice_number": 0.95, "vendor_name": 0.5, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'verified', '2026-11-01 14:05:14', '2026-11-01 15:22:36', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (17, 'DCG-2024-055', 'DevConsulting Group', '2024-06-25', '2024-07-10', 'Global Enterprises India Pvt Ltd', 145000.0, 26100.0, 171100.0, 'INR', 'DUE UPON RECEIPT', 'data/processed/DevConsulting_Group_DCG_055.pdf', '007845aa17b1aefa050e651fba8bc9dca8481adeadcb94ffdb8ddfba08fbe1a9', 'DevConsulting Group
INVOICE
Invoice #: DCG-2024-055
Level 6, Tech Park, Whitefield, Bengaluru, Karnataka
560066, India
Invoice Date: 2024-06-25
Due Date: 2024-07-10
Status: DUE UPON RECEIPT
BILL TO:
Global Enterprises India Pvt Ltd
Cyber City, Gurugram, Haryana 122002, India
Description
Qty
Unit Price
Amount
Python & Cloud Backend Architecture Consulting
40
INR 2,500.00
INR 100,000.00
Database Migration & Performance Tuning
15
INR 3,000.00
INR 45,000.00
Subtotal:
INR 145,000.00
Tax Amount:
INR 26,100.00
Total (INR):
INR 171,100.00
Thank you for your business. For billing inquiries, contact accounting@devconsultinggroup.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'processed', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 0, NULL, NULL);
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (18, 'DO-INV-11029', 'DigitalOcean', '2024-04-18', '2024-05-02', 'Global Enterprises Corp.', 120.0, 9.6, 129.6, 'USD', 'OVERDUE', 'data/processed/DigitalOcean_DO_11029.pdf', '7c5650838965308f725eb8b1595e9f0240911f5a16c50b249ee57e7eed918d50', 'DigitalOcean, LLC
INVOICE
Invoice #: DO-INV-11029
101 Avenue of the Americas, 10th Floor, New York, NY
10013
Invoice Date: 2024-04-18
Due Date: 2024-05-02
Status: OVERDUE
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Basic Droplet 4GB Memory 2 vCPUs
2
$24.00
$48.00
Managed PostgreSQL Cluster DBaaS
1
$60.00
$60.00
Spaces Object Storage 250GB
1
$12.00
$12.00
Subtotal:
$120.00
Tax Amount:
$9.60
Total (USD):
$129.60
Thank you for your business. For billing inquiries, contact accounting@digitaloceanllc.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 6, 'Exact logical duplicate of Invoice #6 (DO-INV-11029) from DigitalOcean');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (19, 'FN-UK-90231', 'FastNet Internet Services', '2024-06-01', '2024-06-30', 'Global Enterprises UK', 780.0, 156.0, 936.0, 'GBP', 'PAID', 'data/processed/FastNet_Internet_FN_90231.pdf', 'a575204b2a2f414013155f17df185991936f00a5da6c1589d303bf5c9a2e69cc', 'FastNet Internet
Services
INVOICE
Invoice #: FN-UK-90231
88 King William Street, London, EC4N 7TW, United
Kingdom
Invoice Date: 2024-06-01
Due Date: 2024-06-30
Status: PAID
BILL TO:
Global Enterprises UK
100 Bishopsgate, London, EC2N 4AG, United Kingdom
Description
Qty
Unit Price
Amount
Dedicated Leased Line 1Gbps Fiber Internet
1
£650.00
£650.00
Static IPv4 Subnet Allocation /28
1
£45.00
£45.00
Managed Cisco Edge Router Service
1
£85.00
£85.00
Subtotal:
£780.00
Tax Amount:
£156.00
Total (GBP):
£936.00
Thank you for your business. For billing inquiries, contact accounting@fastnetinternetservices.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 7, 'Exact logical duplicate of Invoice #7 (FN-UK-90231) from FastNet Internet Services');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (20, 'GCP-INV-2024-4410', 'Google Cloud', '2024-03-05', '2024-04-04', 'Global Enterprises Corp.', 610.0, 48.8, 658.8, 'USD', 'PENDING', 'data/processed/Google_Cloud_GCP_4410.pdf', '113e6dd6711d73ef7d122f6c15c74f24b4c14ba89f716bff64d542daa2b665cf', 'Google Cloud Platform
INVOICE
Invoice #: GCP-INV-2024-4410
1600 Amphitheatre Parkway, Mountain View, CA 94043
Invoice Date: 2024-03-05
Due Date: 2024-04-04
Status: PENDING
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
BigQuery Active Analysis and Storage
1
$320.00
$320.00
Cloud Run Serverless Compute Units
4
$45.00
$180.00
Google Cloud Armor Network Protection
1
$110.00
$110.00
Subtotal:
$610.00
Tax Amount:
$48.80
Total (USD):
$658.80
Thank you for your business. For billing inquiries, contact accounting@googlecloudplatform.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 8, 'Exact logical duplicate of Invoice #8 (GCP-INV-2024-4410) from Google Cloud');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (21, 'MSFT-INV-99214', 'Microsoft', '2024-02-10', '2024-03-12', 'Global Enterprises Corp.', 860.0, 68.8, 928.8, 'USD', 'PAID', 'data/processed/Microsoft_Azure_MSFT_99214.pdf', 'd4885c2db548e3652541a531be56111532c8796bff5e72d28f8da4b9c9aea6c6', 'Microsoft Corporation
INVOICE
Invoice #: MSFT-INV-99214
One Microsoft Way, Redmond, WA 98052
Invoice Date: 2024-02-10
Due Date: 2024-03-12
Status: PAID
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Azure Virtual Machines D4s_v5 Instance
2
$180.00
$360.00
Microsoft 365 E5 Enterprise License
10
$38.00
$380.00
Azure Cosmos DB Reserved Throughput
1
$120.00
$120.00
Subtotal:
$860.00
Tax Amount:
$68.80
Total (USD):
$928.80
Thank you for your business. For billing inquiries, contact accounting@microsoftcorporation.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 9, 'Exact logical duplicate of Invoice #9 (MSFT-INV-99214) from Microsoft');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (22, 'SLK-EUR-5012', 'Slack', '2024-04-01', '2024-05-01', 'Global Enterprises Europe', 425.0, 89.25, 514.25, 'EUR', 'PAID', 'data/processed/Slack_Technologies_SLK_5012.pdf', '52a761f9c4de2b3f48c5898170e5a491131b4c1c1bd6b8b60cca9b70e0dafb53', 'Slack Technologies
Limited
INVOICE
Invoice #: SLK-EUR-5012
4th Floor, One Park Place, Upper Hatch Street, Dublin 2,
Ireland
Invoice Date: 2024-04-01
Due Date: 2024-05-01
Status: PAID
BILL TO:
Global Enterprises Europe
Keizersgracht 421, 1016 EK Amsterdam, Netherlands
Description
Qty
Unit Price
Amount
Slack Enterprise Grid User Seats
25
€15.00
€375.00
Slack Connect Multi-Organization Channels
1
€50.00
€50.00
Subtotal:
€425.00
Tax Amount:
€89.25
Total (EUR):
€514.25
Thank you for your business. For billing inquiries, contact accounting@slacktechnologieslimited.com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 10, 'Exact logical duplicate of Invoice #10 (SLK-EUR-5012) from Slack');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (23, 'TSI-2024-108', 'TechSolutions, LLC', '2024-08-05', '2024-09-04', 'Global Enterprises Corp.', 1600.0, 128.0, 1728.0, 'USD', 'PENDING', 'data/processed/TechSolutions_TSI_108.pdf', 'e364a7cc9079de1a74afff93be0525cd4613d68d17eb43d53177485ea13d1554', 'TechSolutions, LLC
INVOICE
Invoice #: TSI-2024-108
500 Technology Way, Austin, TX 78701
Invoice Date: 2024-08-05
Due Date: 2024-09-04
Status: PENDING
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Custom CRM API Integration Pipeline
1
$1,250.00
$1,250.00
Automated Webhook Monitoring Service
1
$350.00
$350.00
Subtotal:
$1,600.00
Tax Amount:
$128.00
Total (USD):
$1,728.00
Thank you for your business. For billing inquiries, contact accounting@techsolutionsllc.com.', '{"invoice_number": 0.95, "vendor_name": 0.75, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 11, 'Exact logical duplicate of Invoice #11 (TSI-2024-108) from TechSolutions, LLC');
INSERT OR REPLACE INTO "invoices" ("id", "invoice_number", "vendor_name", "invoice_date", "due_date", "customer_name", "subtotal", "tax_amount", "total_amount", "currency", "payment_status", "source_file_path", "file_hash", "raw_text", "confidence_scores", "extraction_notes", "status", "created_at", "updated_at", "is_duplicate", "duplicate_of_id", "duplicate_reason") VALUES (24, 'TW-881290', 'Twilio', '2024-03-20', '2024-04-19', 'Global Enterprises Corp.', 237.5, 19.0, 256.5, 'USD', 'PAID', 'data/processed/Twilio_TW_881290.pdf', 'f4410e0b0291242c7cbc24a3e6ad0255be01396b0393c3d09b64aa61119b3c27', 'Twilio Inc.
INVOICE
Invoice #: TW-881290
101 Spear Street, 1st Floor, San Francisco, CA 94105
Invoice Date: 2024-03-20
Due Date: 2024-04-19
Status: PAID
BILL TO:
Global Enterprises Corp.
742 Evergreen Terrace, Springfield, OR 97477
Description
Qty
Unit Price
Amount
Programmable SMS Message Traffic
25000
$0.01
$187.50
Voice SIP Trunking Outbound Minutes
2000
$0.01
$30.00
Dedicated Local Phone Numbers
2
$10.00
$20.00
Subtotal:
$237.50
Tax Amount:
$19.00
Total (USD):
$256.50
Thank you for your business. For billing inquiries, contact accounting@twilioinc..com.', '{"invoice_number": 0.95, "vendor_name": 0.95, "invoice_date": 0.95, "due_date": 0.95, "customer_name": 0.85, "total_amount": 1.0, "subtotal": 0.98, "tax_amount": 0.98}', '[]', 'suspected_duplicate', '2026-11-01 14:05:14', '2026-11-01 14:05:14', 1, 12, 'Exact logical duplicate of Invoice #12 (TW-881290) from Twilio');
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (1, 1, 'Ergonomic Mesh Office Chair', 4.0, 250.0, 1000.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (2, 1, 'Ultra-Wide 34 inch IPS Monitor', 2.0, 450.0, 900.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (3, 1, 'Mechanical Wireless Keyboards', 4.0, 75.0, 300.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (4, 2, 'Amazon Elastic Compute Cloud (EC2) c5.xlarge', 3.0, 145.0, 435.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (5, 2, 'Amazon Simple Storage Service (S3) Standard', 1.0, 50.0, 50.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (6, 2, 'AWS Relational Database Service (RDS) Postgres', 1.0, 215.0, 215.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (7, 2, 'AWS CloudWatch Logs and Metrics', 1.0, 35.0, 35.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (8, 3, 'Quarterly Cloud Security Posture Assessment', 1.0, 1800.0, 1800.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (9, 3, 'External Network Penetration Testing', 1.0, 2400.0, 2400.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (10, 3, 'SOC2 Compliance Remediation Review', 1.0, 950.0, 950.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (11, 6, 'Basic Droplet 4GB Memory 2 vCPUs', 2.0, 24.0, 48.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (12, 6, 'Managed PostgreSQL Cluster DBaaS', 1.0, 60.0, 60.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (13, 6, 'Spaces Object Storage 250GB', 1.0, 12.0, 12.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (14, 7, 'Dedicated Leased Line 1Gbps Fiber Internet', 1.0, 650.0, 650.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (15, 7, 'Static IPv4 Subnet Allocation /28', 1.0, 45.0, 45.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (16, 7, 'Managed Cisco Edge Router Service', 1.0, 85.0, 85.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (17, 8, 'BigQuery Active Analysis and Storage', 1.0, 320.0, 320.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (18, 8, 'Cloud Run Serverless Compute Units', 4.0, 45.0, 180.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (19, 8, 'Google Cloud Armor Network Protection', 1.0, 110.0, 110.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (20, 9, 'Azure Virtual Machines D4s_v5 Instance', 2.0, 180.0, 360.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (21, 9, 'Microsoft 365 E5 Enterprise License', 10.0, 38.0, 380.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (22, 9, 'Azure Cosmos DB Reserved Throughput', 1.0, 120.0, 120.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (23, 10, 'Slack Enterprise Grid User Seats', 25.0, 15.0, 375.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (24, 10, 'Slack Connect Multi-Organization Channels', 1.0, 50.0, 50.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (25, 11, 'Custom CRM API Integration Pipeline', 1.0, 1250.0, 1250.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (26, 11, 'Automated Webhook Monitoring Service', 1.0, 350.0, 350.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (27, 12, 'Programmable SMS Message Traffic', 25000.0, 0.01, 187.5);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (28, 12, 'Voice SIP Trunking Outbound Minutes', 2000.0, 0.01, 30.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (29, 12, 'Dedicated Local Phone Numbers', 2.0, 10.0, 20.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (30, 13, 'Ergonomic Mesh Office Chair', 4.0, 250.0, 1000.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (31, 13, 'Ultra-Wide 34 inch IPS Monitor', 2.0, 450.0, 900.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (32, 13, 'Mechanical Wireless Keyboards', 4.0, 75.0, 300.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (33, 14, 'Amazon Elastic Compute Cloud (EC2) c5.xlarge', 3.0, 145.0, 435.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (34, 14, 'Amazon Simple Storage Service (S3) Standard', 1.0, 50.0, 50.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (35, 14, 'AWS Relational Database Service (RDS) Postgres', 1.0, 215.0, 215.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (36, 14, 'AWS CloudWatch Logs and Metrics', 1.0, 35.0, 35.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (37, 15, 'Quarterly Cloud Security Posture Assessment', 1.0, 1800.0, 1800.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (38, 15, 'External Network Penetration Testing', 1.0, 2400.0, 2400.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (39, 15, 'SOC2 Compliance Remediation Review', 1.0, 950.0, 950.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (40, 18, 'Basic Droplet 4GB Memory 2 vCPUs', 2.0, 24.0, 48.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (41, 18, 'Managed PostgreSQL Cluster DBaaS', 1.0, 60.0, 60.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (42, 18, 'Spaces Object Storage 250GB', 1.0, 12.0, 12.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (43, 19, 'Dedicated Leased Line 1Gbps Fiber Internet', 1.0, 650.0, 650.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (44, 19, 'Static IPv4 Subnet Allocation /28', 1.0, 45.0, 45.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (45, 19, 'Managed Cisco Edge Router Service', 1.0, 85.0, 85.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (46, 20, 'BigQuery Active Analysis and Storage', 1.0, 320.0, 320.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (47, 20, 'Cloud Run Serverless Compute Units', 4.0, 45.0, 180.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (48, 20, 'Google Cloud Armor Network Protection', 1.0, 110.0, 110.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (49, 21, 'Azure Virtual Machines D4s_v5 Instance', 2.0, 180.0, 360.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (50, 21, 'Microsoft 365 E5 Enterprise License', 10.0, 38.0, 380.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (51, 21, 'Azure Cosmos DB Reserved Throughput', 1.0, 120.0, 120.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (52, 22, 'Slack Enterprise Grid User Seats', 25.0, 15.0, 375.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (53, 22, 'Slack Connect Multi-Organization Channels', 1.0, 50.0, 50.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (54, 23, 'Custom CRM API Integration Pipeline', 1.0, 1250.0, 1250.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (55, 23, 'Automated Webhook Monitoring Service', 1.0, 350.0, 350.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (56, 24, 'Programmable SMS Message Traffic', 25000.0, 0.01, 187.5);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (57, 24, 'Voice SIP Trunking Outbound Minutes', 2000.0, 0.01, 30.0);
INSERT OR REPLACE INTO "invoice_items" ("id", "invoice_id", "description", "quantity", "unit_price", "amount") VALUES (58, 24, 'Dedicated Local Phone Numbers', 2.0, 10.0, 20.0);
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (1, '6a9b30a9e49a2628cd6932efdfc9f4507c7730662410975eba2540b70c9df181', 'Acme_Office_Supplies_ACME_88401.pdf', 2975, 'application/pdf', '2026-11-01 14:04:28', '2026-11-01 14:04:28');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (2, 'e65e542098bd1dcee4d3cb12d7cef1669ea77814ac4ad763379e584451e03b9a', 'AWS_INV_2024_8192.pdf', 3082, 'application/pdf', '2026-11-01 14:04:28', '2026-11-01 14:04:28');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (3, 'a66438589ed1c9ecff9aa896e000e62e3af4454667f52b01a9239e212b678f2f', 'CyberShield_Security_CS_7701.pdf', 3007, 'application/pdf', '2026-11-01 14:04:28', '2026-11-01 14:04:28');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (4, 'c7216b7c9431da1ea5ff83142d4505fe1e67c6a99fa73ac14472201663391123', 'DataStream_Analytics_DSA_3329.pdf', 3154, 'application/pdf', '2026-11-01 14:04:29', '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (5, 'f94369791349c52179f7d377e9098386cf1a2d4ae8af5e1a631d799239599130', 'DevConsulting_Group_DCG_055.pdf', 3145, 'application/pdf', '2026-11-01 14:04:29', '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (6, '085d9c4a21b9a02ee2a92c66749f2fe113ab34c9542f53f06dfb333d2ff59659', 'DigitalOcean_DO_11029.pdf', 3007, 'application/pdf', '2026-11-01 14:04:29', '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (7, 'a87b025a912b58771f975fdfee250060eaaf9aeaf78df7899503da9b39b90135', 'FastNet_Internet_FN_90231.pdf', 2992, 'application/pdf', '2026-11-01 14:04:29', '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (8, '5b2f0d862915655263971503ddff4373d3520ff579ca4a4b87d0c2984ee6c743', 'Google_Cloud_GCP_4410.pdf', 2994, 'application/pdf', '2026-11-01 14:04:29', '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (9, 'f36ba043a2c0d387b114b32798f726e0742eb1cb5c3894249afa66667783d69b', 'Microsoft_Azure_MSFT_99214.pdf', 2971, 'application/pdf', '2026-11-01 14:04:29', '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (10, '4bf4925a03c84b581e0671f37f6315338667540139e20f6be9539fe2a208a28e', 'Slack_Technologies_SLK_5012.pdf', 2969, 'application/pdf', '2026-11-01 14:04:29', '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (11, '60d8193fecf5cedc8a39cef5bd56bab151e86dbc4c1b587eecf334fc73f04f2d', 'TechSolutions_TSI_108.pdf', 2917, 'application/pdf', '2026-11-01 14:04:29', '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (12, '54e111c99ca1adf2c50b17f164869d288b7fc71fb8fee556acf07ec9a5454250', 'Twilio_TW_881290.pdf', 2990, 'application/pdf', '2026-11-01 14:04:29', '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (13, '5289e16674ecaca73425f575c93ff25f47353d4808b01253b3e2ac2a1ba0e1ba', 'Acme_Office_Supplies_ACME_88401.pdf', 2975, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (14, '7684178bfb068f5ab111f10105e7a83a2cf8fa4ad49ae8fc92998d82535fa836', 'AWS_INV_2024_8192.pdf', 3082, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (15, '79092b06037fa9186fb859777699eb7d1bac7b7854fe8f1a830d8323b9cd20a7', 'CyberShield_Security_CS_7701.pdf', 3007, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (16, '23c1cccf369d22bf4589ed542ba7461c978357c8d7be785cd7e038047cf4b915', 'DataStream_Analytics_DSA_3329.pdf', 3015, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (17, '007845aa17b1aefa050e651fba8bc9dca8481adeadcb94ffdb8ddfba08fbe1a9', 'DevConsulting_Group_DCG_055.pdf', 3007, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (18, '7c5650838965308f725eb8b1595e9f0240911f5a16c50b249ee57e7eed918d50', 'DigitalOcean_DO_11029.pdf', 3007, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (19, 'a575204b2a2f414013155f17df185991936f00a5da6c1589d303bf5c9a2e69cc', 'FastNet_Internet_FN_90231.pdf', 2992, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (20, '113e6dd6711d73ef7d122f6c15c74f24b4c14ba89f716bff64d542daa2b665cf', 'Google_Cloud_GCP_4410.pdf', 2994, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (21, 'd4885c2db548e3652541a531be56111532c8796bff5e72d28f8da4b9c9aea6c6', 'Microsoft_Azure_MSFT_99214.pdf', 2971, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (22, '52a761f9c4de2b3f48c5898170e5a491131b4c1c1bd6b8b60cca9b70e0dafb53', 'Slack_Technologies_SLK_5012.pdf', 2969, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (23, 'e364a7cc9079de1a74afff93be0525cd4613d68d17eb43d53177485ea13d1554', 'TechSolutions_TSI_108.pdf', 2917, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "file_metadata" ("id", "file_hash", "file_name", "file_size", "mime_type", "first_seen_at", "last_processed_at") VALUES (24, 'f4410e0b0291242c7cbc24a3e6ad0255be01396b0393c3d09b64aa61119b3c27', 'Twilio_TW_881290.pdf', 2990, 'application/pdf', '2026-11-01 14:05:14', '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (1, 'Acme_Office_Supplies_ACME_88401.pdf', 'data/processed/Acme_Office_Supplies_ACME_88401.pdf', '6a9b30a9e49a2628cd6932efdfc9f4507c7730662410975eba2540b70c9df181', 2975, 'success', NULL, 0.9390139579772949, '2026-11-01 14:04:28');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (2, 'AWS_INV_2024_8192.pdf', 'data/processed/AWS_INV_2024_8192.pdf', 'e65e542098bd1dcee4d3cb12d7cef1669ea77814ac4ad763379e584451e03b9a', 3082, 'success', NULL, 0.012752532958984375, '2026-11-01 14:04:28');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (3, 'CyberShield_Security_CS_7701.pdf', 'data/processed/CyberShield_Security_CS_7701.pdf', 'a66438589ed1c9ecff9aa896e000e62e3af4454667f52b01a9239e212b678f2f', 3007, 'success', NULL, 0.013129949569702148, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (4, 'DataStream_Analytics_DSA_3329.pdf', 'data/processed/DataStream_Analytics_DSA_3329.pdf', 'c7216b7c9431da1ea5ff83142d4505fe1e67c6a99fa73ac14472201663391123', 3154, 'needs_review', 'Total amount was not detected in document.; Flagged for review: Missing or zero total amount.', 0.013197660446166992, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (5, 'DevConsulting_Group_DCG_055.pdf', 'data/processed/DevConsulting_Group_DCG_055.pdf', 'f94369791349c52179f7d377e9098386cf1a2d4ae8af5e1a631d799239599130', 3145, 'needs_review', 'Total amount was not detected in document.; Flagged for review: Missing or zero total amount.', 0.01221919059753418, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (6, 'DigitalOcean_DO_11029.pdf', 'data/processed/DigitalOcean_DO_11029.pdf', '085d9c4a21b9a02ee2a92c66749f2fe113ab34c9542f53f06dfb333d2ff59659', 3007, 'success', NULL, 0.011035442352294922, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (7, 'FastNet_Internet_FN_90231.pdf', 'data/processed/FastNet_Internet_FN_90231.pdf', 'a87b025a912b58771f975fdfee250060eaaf9aeaf78df7899503da9b39b90135', 2992, 'success', NULL, 0.011074066162109375, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (8, 'Google_Cloud_GCP_4410.pdf', 'data/processed/Google_Cloud_GCP_4410.pdf', '5b2f0d862915655263971503ddff4373d3520ff579ca4a4b87d0c2984ee6c743', 2994, 'success', NULL, 0.011014461517333984, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (9, 'Microsoft_Azure_MSFT_99214.pdf', 'data/processed/Microsoft_Azure_MSFT_99214.pdf', 'f36ba043a2c0d387b114b32798f726e0742eb1cb5c3894249afa66667783d69b', 2971, 'success', NULL, 0.010677576065063477, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (10, 'Slack_Technologies_SLK_5012.pdf', 'data/processed/Slack_Technologies_SLK_5012.pdf', '4bf4925a03c84b581e0671f37f6315338667540139e20f6be9539fe2a208a28e', 2969, 'success', NULL, 0.011121511459350586, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (11, 'TechSolutions_TSI_108.pdf', 'data/processed/TechSolutions_TSI_108.pdf', '60d8193fecf5cedc8a39cef5bd56bab151e86dbc4c1b587eecf334fc73f04f2d', 2917, 'success', NULL, 0.011295080184936523, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (12, 'Twilio_TW_881290.pdf', 'data/processed/Twilio_TW_881290.pdf', '54e111c99ca1adf2c50b17f164869d288b7fc71fb8fee556acf07ec9a5454250', 2990, 'success', NULL, 0.010102510452270508, '2026-11-01 14:04:29');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (13, 'Acme_Office_Supplies_ACME_88401.pdf', 'data/processed/Acme_Office_Supplies_ACME_88401.pdf', '5289e16674ecaca73425f575c93ff25f47353d4808b01253b3e2ac2a1ba0e1ba', 2975, 'success', NULL, 0.9950575828552246, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (14, 'AWS_INV_2024_8192.pdf', 'data/processed/AWS_INV_2024_8192.pdf', '7684178bfb068f5ab111f10105e7a83a2cf8fa4ad49ae8fc92998d82535fa836', 3082, 'success', NULL, 0.01007080078125, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (15, 'CyberShield_Security_CS_7701.pdf', 'data/processed/CyberShield_Security_CS_7701.pdf', '79092b06037fa9186fb859777699eb7d1bac7b7854fe8f1a830d8323b9cd20a7', 3007, 'success', NULL, 0.01041412353515625, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (16, 'DataStream_Analytics_DSA_3329.pdf', 'data/processed/DataStream_Analytics_DSA_3329.pdf', '23c1cccf369d22bf4589ed542ba7461c978357c8d7be785cd7e038047cf4b915', 3015, 'success', NULL, 0.010111570358276367, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (17, 'DevConsulting_Group_DCG_055.pdf', 'data/processed/DevConsulting_Group_DCG_055.pdf', '007845aa17b1aefa050e651fba8bc9dca8481adeadcb94ffdb8ddfba08fbe1a9', 3007, 'success', NULL, 0.010665178298950195, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (18, 'DigitalOcean_DO_11029.pdf', 'data/processed/DigitalOcean_DO_11029.pdf', '7c5650838965308f725eb8b1595e9f0240911f5a16c50b249ee57e7eed918d50', 3007, 'success', NULL, 0.009203910827636719, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (19, 'FastNet_Internet_FN_90231.pdf', 'data/processed/FastNet_Internet_FN_90231.pdf', 'a575204b2a2f414013155f17df185991936f00a5da6c1589d303bf5c9a2e69cc', 2992, 'success', NULL, 0.008656501770019531, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (20, 'Google_Cloud_GCP_4410.pdf', 'data/processed/Google_Cloud_GCP_4410.pdf', '113e6dd6711d73ef7d122f6c15c74f24b4c14ba89f716bff64d542daa2b665cf', 2994, 'success', NULL, 0.009326696395874023, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (21, 'Microsoft_Azure_MSFT_99214.pdf', 'data/processed/Microsoft_Azure_MSFT_99214.pdf', 'd4885c2db548e3652541a531be56111532c8796bff5e72d28f8da4b9c9aea6c6', 2971, 'success', NULL, 0.008986949920654297, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (22, 'Slack_Technologies_SLK_5012.pdf', 'data/processed/Slack_Technologies_SLK_5012.pdf', '52a761f9c4de2b3f48c5898170e5a491131b4c1c1bd6b8b60cca9b70e0dafb53', 2969, 'success', NULL, 0.010051250457763672, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (23, 'TechSolutions_TSI_108.pdf', 'data/processed/TechSolutions_TSI_108.pdf', 'e364a7cc9079de1a74afff93be0525cd4613d68d17eb43d53177485ea13d1554', 2917, 'success', NULL, 0.009705066680908203, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (24, 'Twilio_TW_881290.pdf', 'data/processed/Twilio_TW_881290.pdf', 'f4410e0b0291242c7cbc24a3e6ad0255be01396b0393c3d09b64aa61119b3c27', 2990, 'success', NULL, 0.012721538543701172, '2026-11-01 14:05:14');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (25, 'Acme_Office_Supplies_ACME_88401.pdf', 'data/samples/Acme_Office_Supplies_ACME_88401.pdf', '5289e16674ecaca73425f575c93ff25f47353d4808b01253b3e2ac2a1ba0e1ba', 2975, 'duplicate', 'File hash already exists in database.', 0.0020046234130859375, '2026-11-01 14:05:25');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (26, 'AWS_INV_2024_8192.pdf', 'data/samples/AWS_INV_2024_8192.pdf', '7684178bfb068f5ab111f10105e7a83a2cf8fa4ad49ae8fc92998d82535fa836', 3082, 'duplicate', 'File hash already exists in database.', 0.003008127212524414, '2026-11-01 14:05:25');
INSERT OR REPLACE INTO "processing_records" ("id", "file_name", "file_path", "file_hash", "file_size", "status", "error_message", "duration_sec", "processed_at") VALUES (27, 'CyberShield_Security_CS_7701.pdf', 'data/samples/CyberShield_Security_CS_7701.pdf', '79092b06037fa9186fb859777699eb7d1bac7b7854fe8f1a830d8323b9cd20a7', 3007, 'duplicate', 'File hash already exists in database.', 0.0020012855529785156, '2026-11-01 14:05:25');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (1, 'USD', 'INR', '2024-01-15', '2024-01-15', 82.87, '82.87', 'European Central Bank via Frankfurter API (2024-01-15)', '2026-11-01 15:51:21');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (2, 'USD', 'INR', '2024-08-05', '2024-08-05', 84.15, '84.15', 'European Central Bank via Frankfurter API (2024-08-05)', '2026-11-01 15:51:55');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (3, 'EUR', 'INR', '2024-07-15', '2024-07-15', 91.168, '91.168', 'European Central Bank via Frankfurter API (2024-07-15)', '2026-11-01 15:51:55');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (4, 'GBP', 'INR', '2024-06-01', '2024-05-31', 106.05, '106.05', 'European Central Bank via Frankfurter API (2024-05-31)', '2026-11-01 15:51:56');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (5, 'USD', 'INR', '2024-05-10', '2024-05-10', 83.51, '83.51', 'European Central Bank via Frankfurter API (2024-05-10)', '2026-11-01 15:51:56');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (6, 'USD', 'INR', '2024-04-18', '2024-04-18', 83.52, '83.52', 'European Central Bank via Frankfurter API (2024-04-18)', '2026-11-01 15:51:56');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (7, 'EUR', 'INR', '2024-04-01', '2024-03-28', 90.1365, '90.1365', 'European Central Bank via Frankfurter API (2024-03-28)', '2026-11-01 15:51:56');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (8, 'USD', 'INR', '2024-03-20', '2024-03-20', 83.22, '83.22', 'European Central Bank via Frankfurter API (2024-03-20)', '2026-11-01 15:51:56');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (9, 'USD', 'INR', '2024-03-05', '2024-03-05', 82.91, '82.91', 'European Central Bank via Frankfurter API (2024-03-05)', '2026-11-01 15:51:56');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (10, 'USD', 'INR', '2024-02-10', '2024-02-09', 83.03, '83.03', 'European Central Bank via Frankfurter API (2024-02-09)', '2026-11-01 15:51:56');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (11, 'USD', 'INR', 'latest', '2026-10-30', 94.95, '94.95', 'European Central Bank via Frankfurter API (2026-10-30)', '2026-11-01 15:59:19');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (12, 'USD', 'EUR', 'latest', '2026-10-30', 0.89509, '0.89509', 'European Central Bank via Frankfurter API (2026-10-30)', '2026-11-01 16:32:10');
INSERT OR REPLACE INTO "exchange_rate_cache" ("id", "from_currency", "to_currency", "rate_date", "effective_date", "rate", "rate_decimal", "source", "fetched_at") VALUES (13, 'USD', 'GBP', 'latest', '2026-10-30', 0.74633, '0.74633', 'European Central Bank via Frankfurter API (2026-10-30)', '2026-11-01 16:32:11');
INSERT OR REPLACE INTO "user_settings" ("key", "value", "updated_at") VALUES ('preferred_display_currency', 'INR', '2026-11-01 20:52:36');
COMMIT;
PRAGMA foreign_keys = ON;
