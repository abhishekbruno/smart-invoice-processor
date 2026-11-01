import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from typing import Dict, List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config.settings import settings


SAMPLE_INVOICES_DATA: List[Dict] = [
    {
        "filename": "AWS_INV_2024_8192.pdf",
        "vendor": "Amazon Web Services, Inc.",
        "vendor_address": "410 Terry Avenue North, Seattle, WA 98109-5210",
        "invoice_number": "INV-AWS-2024-8192",
        "invoice_date": "2024-01-15",
        "due_date": "2024-02-14",
        "customer": "Global Enterprises Corp.",
        "customer_address": "742 Evergreen Terrace, Springfield, OR 97477",
        "currency": "USD",
        "currency_sym": "$",
        "payment_status": "PAID",
        "items": [
            ("Amazon Elastic Compute Cloud (EC2) c5.xlarge", 3.0, 145.00, 435.00),
            ("Amazon Simple Storage Service (S3) Standard", 1.0, 50.00, 50.00),
            ("AWS Relational Database Service (RDS) Postgres", 1.0, 215.00, 215.00),
            ("AWS CloudWatch Logs and Metrics", 1.0, 35.00, 35.00),
        ],
        "subtotal": 735.00,
        "tax": 58.80,
        "total": 793.80,
    },
    {
        "filename": "Microsoft_Azure_MSFT_99214.pdf",
        "vendor": "Microsoft Corporation",
        "vendor_address": "One Microsoft Way, Redmond, WA 98052",
        "invoice_number": "MSFT-INV-99214",
        "invoice_date": "2024-02-10",
        "due_date": "2024-03-12",
        "customer": "Global Enterprises Corp.",
        "customer_address": "742 Evergreen Terrace, Springfield, OR 97477",
        "currency": "USD",
        "currency_sym": "$",
        "payment_status": "PAID",
        "items": [
            ("Azure Virtual Machines D4s_v5 Instance", 2.0, 180.00, 360.00),
            ("Microsoft 365 E5 Enterprise License", 10.0, 38.00, 380.00),
            ("Azure Cosmos DB Reserved Throughput", 1.0, 120.00, 120.00),
        ],
        "subtotal": 860.00,
        "tax": 68.80,
        "total": 928.80,
    },
    {
        "filename": "Google_Cloud_GCP_4410.pdf",
        "vendor": "Google Cloud Platform",
        "vendor_address": "1600 Amphitheatre Parkway, Mountain View, CA 94043",
        "invoice_number": "GCP-INV-2024-4410",
        "invoice_date": "2024-03-05",
        "due_date": "2024-04-04",
        "customer": "Global Enterprises Corp.",
        "customer_address": "742 Evergreen Terrace, Springfield, OR 97477",
        "currency": "USD",
        "currency_sym": "$",
        "payment_status": "PENDING",
        "items": [
            ("BigQuery Active Analysis and Storage", 1.0, 320.00, 320.00),
            ("Cloud Run Serverless Compute Units", 4.0, 45.00, 180.00),
            ("Google Cloud Armor Network Protection", 1.0, 110.00, 110.00),
        ],
        "subtotal": 610.00,
        "tax": 48.80,
        "total": 658.80,
    },
    {
        "filename": "Twilio_TW_881290.pdf",
        "vendor": "Twilio Inc.",
        "vendor_address": "101 Spear Street, 1st Floor, San Francisco, CA 94105",
        "invoice_number": "TW-881290",
        "invoice_date": "2024-03-20",
        "due_date": "2024-04-19",
        "customer": "Global Enterprises Corp.",
        "customer_address": "742 Evergreen Terrace, Springfield, OR 97477",
        "currency": "USD",
        "currency_sym": "$",
        "payment_status": "PAID",
        "items": [
            ("Programmable SMS Message Traffic", 25000.0, 0.0075, 187.50),
            ("Voice SIP Trunking Outbound Minutes", 2000.0, 0.015, 30.00),
            ("Dedicated Local Phone Numbers", 2.0, 10.00, 20.00),
        ],
        "subtotal": 237.50,
        "tax": 19.00,
        "total": 256.50,
    },
    {
        "filename": "Slack_Technologies_SLK_5012.pdf",
        "vendor": "Slack Technologies Limited",
        "vendor_address": "4th Floor, One Park Place, Upper Hatch Street, Dublin 2, Ireland",
        "invoice_number": "SLK-EUR-5012",
        "invoice_date": "2024-04-01",
        "due_date": "2024-05-01",
        "customer": "Global Enterprises Europe",
        "customer_address": "Keizersgracht 421, 1016 EK Amsterdam, Netherlands",
        "currency": "EUR",
        "currency_sym": "€",
        "payment_status": "PAID",
        "items": [
            ("Slack Enterprise Grid User Seats", 25.0, 15.00, 375.00),
            ("Slack Connect Multi-Organization Channels", 1.0, 50.00, 50.00),
        ],
        "subtotal": 425.00,
        "tax": 89.25,
        "total": 514.25,
    },
    {
        "filename": "DigitalOcean_DO_11029.pdf",
        "vendor": "DigitalOcean, LLC",
        "vendor_address": "101 Avenue of the Americas, 10th Floor, New York, NY 10013",
        "invoice_number": "DO-INV-11029",
        "invoice_date": "2024-04-18",
        "due_date": "2024-05-02",
        "customer": "Global Enterprises Corp.",
        "customer_address": "742 Evergreen Terrace, Springfield, OR 97477",
        "currency": "USD",
        "currency_sym": "$",
        "payment_status": "OVERDUE",
        "items": [
            ("Basic Droplet 4GB Memory 2 vCPUs", 2.0, 24.00, 48.00),
            ("Managed PostgreSQL Cluster DBaaS", 1.0, 60.00, 60.00),
            ("Spaces Object Storage 250GB", 1.0, 12.00, 12.00),
        ],
        "subtotal": 120.00,
        "tax": 9.60,
        "total": 129.60,
    },
    {
        "filename": "Acme_Office_Supplies_ACME_88401.pdf",
        "vendor": "Acme Office Supplies",
        "vendor_address": "1200 Industrial Parkway, Chicago, IL 60607",
        "invoice_number": "ACME-88401",
        "invoice_date": "2024-05-10",
        "due_date": "2024-06-09",
        "customer": "Global Enterprises Corp.",
        "customer_address": "742 Evergreen Terrace, Springfield, OR 97477",
        "currency": "USD",
        "currency_sym": "$",
        "payment_status": "PAID",
        "items": [
            ("Ergonomic Mesh Office Chair", 4.0, 250.00, 1000.00),
            ("Ultra-Wide 34 inch IPS Monitor", 2.0, 450.00, 900.00),
            ("Mechanical Wireless Keyboards", 4.0, 75.00, 300.00),
        ],
        "subtotal": 2200.00,
        "tax": 176.00,
        "total": 2376.00,
    },
    {
        "filename": "FastNet_Internet_FN_90231.pdf",
        "vendor": "FastNet Internet Services",
        "vendor_address": "88 King William Street, London, EC4N 7TW, United Kingdom",
        "invoice_number": "FN-UK-90231",
        "invoice_date": "2024-06-01",
        "due_date": "2024-06-30",
        "customer": "Global Enterprises UK",
        "customer_address": "100 Bishopsgate, London, EC2N 4AG, United Kingdom",
        "currency": "GBP",
        "currency_sym": "£",
        "payment_status": "PAID",
        "items": [
            ("Dedicated Leased Line 1Gbps Fiber Internet", 1.0, 650.00, 650.00),
            ("Static IPv4 Subnet Allocation /28", 1.0, 45.00, 45.00),
            ("Managed Cisco Edge Router Service", 1.0, 85.00, 85.00),
        ],
        "subtotal": 780.00,
        "tax": 156.00,
        "total": 936.00,
    },
    {
        "filename": "DevConsulting_Group_DCG_055.pdf",
        "vendor": "DevConsulting Group",
        "vendor_address": "Level 6, Tech Park, Whitefield, Bengaluru, Karnataka 560066, India",
        "invoice_number": "DCG-2024-055",
        "invoice_date": "2024-06-25",
        "due_date": "2024-07-10",
        "customer": "Global Enterprises India Pvt Ltd",
        "customer_address": "Cyber City, Gurugram, Haryana 122002, India",
        "currency": "INR",
        "currency_sym": "INR ",
        "payment_status": "DUE UPON RECEIPT",
        "items": [
            ("Python & Cloud Backend Architecture Consulting", 40.0, 2500.00, 100000.00),
            ("Database Migration & Performance Tuning", 15.0, 3000.00, 45000.00),
        ],
        "subtotal": 145000.00,
        "tax": 26100.00,
        "total": 171100.00,
    },
    {
        "filename": "CyberShield_Security_CS_7701.pdf",
        "vendor": "CyberShield Security",
        "vendor_address": "Rue du Commerce 45, 1000 Brussels, Belgium",
        "invoice_number": "CS-SEC-7701",
        "invoice_date": "2024-07-15",
        "due_date": "2024-08-14",
        "customer": "Global Enterprises Europe",
        "customer_address": "Keizersgracht 421, 1016 EK Amsterdam, Netherlands",
        "currency": "EUR",
        "currency_sym": "€",
        "payment_status": "PAID",
        "items": [
            ("Quarterly Cloud Security Posture Assessment", 1.0, 1800.00, 1800.00),
            ("External Network Penetration Testing", 1.0, 2400.00, 2400.00),
            ("SOC2 Compliance Remediation Review", 1.0, 950.00, 950.00),
        ],
        "subtotal": 5150.00,
        "tax": 1081.50,
        "total": 6231.50,
    },
    {
        "filename": "TechSolutions_TSI_108.pdf",
        "vendor": "TechSolutions, LLC",
        "vendor_address": "500 Technology Way, Austin, TX 78701",
        "invoice_number": "TSI-2024-108",
        "invoice_date": "2024-08-05",
        "due_date": "2024-09-04",
        "customer": "Global Enterprises Corp.",
        "customer_address": "742 Evergreen Terrace, Springfield, OR 97477",
        "currency": "USD",
        "currency_sym": "$",
        "payment_status": "PENDING",
        "items": [
            ("Custom CRM API Integration Pipeline", 1.0, 1250.00, 1250.00),
            ("Automated Webhook Monitoring Service", 1.0, 350.00, 350.00),
        ],
        "subtotal": 1600.00,
        "tax": 128.00,
        "total": 1728.00,
    },
    {
        "filename": "DataStream_Analytics_DSA_3329.pdf",
        "vendor": "DataStream Analytics",
        "vendor_address": "Plot 12, HITEC City, Hyderabad, Telangana 500081, India",
        "invoice_number": "DSA-IN-3329",
        "invoice_date": "2024-09-12",
        "due_date": "2024-10-12",
        "customer": "Global Enterprises India Pvt Ltd",
        "customer_address": "Cyber City, Gurugram, Haryana 122002, India",
        "currency": "INR",
        "currency_sym": "INR ",
        "payment_status": "PAID",
        "items": [
            ("Real-time Kafka Event Streaming Setup", 1.0, 80000.00, 80000.00),
            ("Apache Spark Data Aggregation Pipeline", 1.0, 65000.00, 65000.00),
            ("Data Engineering Team Knowledge Transfer", 10.0, 3000.00, 30000.00),
        ],
        "subtotal": 175000.00,
        "tax": 31500.00,
        "total": 206500.00,
    },
]


def generate_pdf(data: Dict, output_path: Path) -> Path:
    """Generates a professional invoice PDF file with ReportLab."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Heading1"],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#1E293B"),
        fontName="Helvetica-Bold",
    )
    subtitle_style = ParagraphStyle(
        "VendorSub",
        parent=styles["Normal"],
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#475569"),
    )
    header_right = ParagraphStyle(
        "HeaderRight",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        alignment=2,  # Right
        textColor=colors.HexColor("#334155"),
    )
    status_style = ParagraphStyle(
        "StatusBadge",
        parent=styles["Normal"],
        fontSize=12,
        leading=14,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0F766E") if data["payment_status"] == "PAID" else colors.HexColor("#B91C1C"),
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#1E293B"),
    )
    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0F172A"),
    )

    story = []

    # 1. Header Table (Vendor on Left, Invoice Details on Right)
    sym = data["currency_sym"]
    header_data = [
        [
            Paragraph(f"<b>{data['vendor']}</b>", title_style),
            Paragraph(f"<b>INVOICE</b><br/><b>Invoice #:</b> {data['invoice_number']}", header_right),
        ],
        [
            Paragraph(data["vendor_address"], subtitle_style),
            Paragraph(
                f"<b>Invoice Date:</b> {data['invoice_date']}<br/>"
                f"<b>Due Date:</b> {data['due_date']}<br/>"
                f"<b>Status:</b> {data['payment_status']}",
                header_right,
            ),
        ],
    ]

    header_table = Table(header_data, colWidths=[3.8 * inch, 3.4 * inch])
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(header_table)
    story.append(Spacer(1, 15))

    # 2. Bill To Section
    bill_to_data = [
        [
            Paragraph(
                f"<b>BILL TO:</b><br/>"
                f"<b>{data['customer']}</b><br/>"
                f"{data['customer_address']}",
                subtitle_style,
            )
        ]
    ]
    bill_table = Table(bill_to_data, colWidths=[7.2 * inch])
    bill_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.append(bill_table)
    story.append(Spacer(1, 20))

    # 3. Line Items Table
    items_header = [
        Paragraph("<b>Description</b>", table_cell_bold),
        Paragraph("<b>Qty</b>", table_cell_bold),
        Paragraph("<b>Unit Price</b>", table_cell_bold),
        Paragraph("<b>Amount</b>", table_cell_bold),
    ]

    table_rows = [items_header]
    for desc, qty, unit, amt in data["items"]:
        qty_str = f"{qty:.2f}" if isinstance(qty, float) and not qty.is_integer() else f"{int(qty)}"
        table_rows.append(
            [
                Paragraph(desc, table_cell),
                Paragraph(qty_str, table_cell),
                Paragraph(f"{sym}{unit:,.2f}", table_cell),
                Paragraph(f"{sym}{amt:,.2f}", table_cell),
            ]
        )

    # Summary rows (Subtotal, Tax, Total)
    table_rows.append(
        [
            "",
            "",
            Paragraph("<b>Subtotal:</b>", table_cell_bold),
            Paragraph(f"{sym}{data['subtotal']:,.2f}", table_cell_bold),
        ]
    )
    table_rows.append(
        [
            "",
            "",
            Paragraph("<b>Tax Amount:</b>", table_cell_bold),
            Paragraph(f"{sym}{data['tax']:,.2f}", table_cell_bold),
        ]
    )
    table_rows.append(
        [
            "",
            "",
            Paragraph(f"<b>Total ({data['currency']}):</b>", table_cell_bold),
            Paragraph(f"<b>{sym}{data['total']:,.2f}</b>", table_cell_bold),
        ]
    )

    col_widths = [3.8 * inch, 0.8 * inch, 1.3 * inch, 1.3 * inch]
    items_table = Table(table_rows, colWidths=col_widths)
    items_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0284C7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("GRID", (0, 0), (-1, len(data["items"])), 0.5, colors.HexColor("#CBD5E1")),
                ("LINEBELOW", (2, -3), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("BACKGROUND", (2, -1), (-1, -1), colors.HexColor("#F1F5F9")),
            ]
        )
    )
    story.append(items_table)
    story.append(Spacer(1, 25))

    # 4. Footer notes
    footer_text = Paragraph(
        f"<i>Thank you for your business. For billing inquiries, contact accounting@{data['vendor'].lower().replace(' ', '').replace(',', '')}.com.</i>",
        subtitle_style,
    )
    story.append(footer_text)

    doc.build(story)
    return output_path


def generate_all_samples(target_dir: Optional[Path] = None) -> List[Path]:
    """Generates all 12 sample invoice PDFs into target_dir or default samples directory."""
    dest_dir = target_dir or settings.SAMPLES_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    generated_files = []

    for invoice_data in SAMPLE_INVOICES_DATA:
        file_path = dest_dir / invoice_data["filename"]
        created_path = generate_pdf(invoice_data, file_path)
        generated_files.append(created_path)

    return generated_files


if __name__ == "__main__":
    files = generate_all_samples()
    print(f"Successfully generated {len(files)} sample invoice PDFs in '{settings.SAMPLES_DIR}'.")
