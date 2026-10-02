"""Generate the fictional "Nimbus Works Pvt. Ltd." policy corpus. Owner: D.

    python scripts/make_sample_pdfs.py

Writes 7 PDFs to data/pdfs/ and an answer key to eval/corpus_facts.md.
The corpus is designed to exercise the pipeline (see PLAN.md section 12):
  - numbered headings and clauses (docs 01-04, 06, 07)
  - tables (01, 02, 03, 07) and bulleted/numbered lists with a lead-in ending in ":" (01, 03, 06)
  - one FLAT PDF with no headings at all (05) to test the fallback chunker
  - a notice that supersedes part of a policy (02 vs 01)
  - cross-document references (03 <-> 07, 04 -> 03 / 06)
  - exact identifiers and amounts (Form HR-204, EXP-17, RW-02, TRV-09, INR 1,200 ...), for BM25
  - running headers/footers and page numbers, to test noise removal
All content is invented. Only ASCII plus a few WinAnsi characters are used (no rupee sign).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import fitz  # PyMuPDF, used only to verify the output
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "data" / "pdfs"
FACTS_MD = ROOT / "eval" / "corpus_facts.md"

COMPANY = "Nimbus Works Pvt. Ltd."

# --- styles ------------------------------------------------------------------
BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=14.5, spaceAfter=7)
TITLE = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=22, leading=26, spaceAfter=6)
META = ParagraphStyle("meta", parent=BODY, fontSize=9, leading=12, textColor=colors.HexColor("#444444"),
                      spaceAfter=12)
H1 = ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=14.5, leading=18, spaceBefore=12, spaceAfter=6)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12.5, leading=16, spaceBefore=8, spaceAfter=4)
ITEM = ParagraphStyle("item", parent=BODY, leftIndent=16, bulletIndent=4, spaceAfter=3)
CELL = ParagraphStyle("cell", fontName="Helvetica", fontSize=10, leading=13)
CELLB = ParagraphStyle("cellb", fontName="Helvetica-Bold", fontSize=10, leading=13)


def table(rows: list[list[str]], widths: list[float]) -> Table:
    data = [[Paragraph(c, CELLB if i == 0 else CELL) for c in row] for i, row in enumerate(rows)]
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E6E6E6")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def build(filename: str, title: str, doc_id: str, blocks: list, running_title: str) -> None:
    """blocks: ('title'|'meta'|'h1'|'h2'|'p'|'bullets'|'steps'|'table', payload)."""
    story = []
    for kind, payload in blocks:
        if kind == "title":
            story.append(Paragraph(payload, TITLE))
        elif kind == "meta":
            story.append(Paragraph(payload, META))
        elif kind == "h1":
            story.append(Paragraph(payload, H1))
        elif kind == "h2":
            story.append(Paragraph(payload, H2))
        elif kind == "p":
            story.append(Paragraph(payload, BODY))
        elif kind == "bullets":
            story.extend(Paragraph(t, ITEM, bulletText="\u2022") for t in payload)
            story.append(Spacer(1, 4))
        elif kind == "steps":
            story.extend(Paragraph(t, ITEM, bulletText=f"{i}.") for i, t in enumerate(payload, 1))
            story.append(Spacer(1, 4))
        elif kind == "table":
            rows, widths = payload
            story.append(table(rows, widths))
            story.append(Spacer(1, 10))
        else:
            raise ValueError(kind)

    def decorate(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(20 * mm, A4[1] - 12 * mm, f"{COMPANY}  |  {doc_id}")
        canvas.drawRightString(A4[0] - 20 * mm, A4[1] - 12 * mm, "INTERNAL USE ONLY")
        canvas.drawString(20 * mm, 10 * mm, running_title)
        canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Page {doc.page}")
        canvas.restoreState()

    SimpleDocTemplate(
        str(PDF_DIR / filename), pagesize=A4, title=title, author=COMPANY,
        leftMargin=20 * mm, rightMargin=20 * mm, topMargin=24 * mm, bottomMargin=20 * mm,
    ).build(story, onFirstPage=decorate, onLaterPages=decorate)


# =============================================================================
# 01 Leave Policy
# =============================================================================
LEAVE = [
    ("title", "Leave Policy"),
    ("meta", "Document ID: POL-HR-001  |  Version 3.1  |  Effective from 1 April 2025  |  Owner: Human Resources"),
    ("h1", "1. Purpose and Scope"),
    ("p", "This policy explains the types of leave available to employees of Nimbus Works Pvt. Ltd. and how to "
          "apply for them. It applies to all full-time employees, including those serving probation, unless a "
          "section says otherwise. Contract staff and interns are governed by their individual agreements."),
    ("h1", "2. Leave Entitlements"),
    ("h2", "2.1 Annual Entitlement"),
    ("p", "Leave is credited on a calendar-year basis (1 January to 31 December). New joiners receive a pro-rated "
          "credit for the months remaining in the year of joining. The table below summarises the annual "
          "entitlement for each leave type."),
    ("table", ([["Leave type", "Entitlement", "Carry forward"],
                ["Casual Leave", "8 days per year", "Not allowed"],
                ["Sick Leave", "12 days per year", "Not allowed"],
                ["Earned Leave", "18 days per year", "Up to 10 days"],
                ["Maternity Leave", "26 weeks", "Not applicable"],
                ["Bereavement Leave", "5 days per event", "Not applicable"]], [55, 60, 55])),
    ("h2", "2.2 Casual Leave"),
    ("p", "Casual Leave is meant for short, personal or unplanned needs. A maximum of 3 consecutive days of Casual "
          "Leave may be taken at one time. Requests should be submitted in the HR portal at least 1 working day in "
          "advance, except in emergencies."),
    ("h2", "2.3 Sick Leave"),
    ("p", "Employees are entitled to 12 paid sick days per calendar year. If you are absent for more than 2 "
          "consecutive working days because of illness, you must submit a medical certificate within 3 working "
          "days of returning to work, using Form HR-204. Unused Sick Leave lapses on 31 December and cannot be "
          "encashed or carried forward."),
    ("h2", "2.4 Earned Leave"),
    ("p", "Earned Leave accrues at 1.5 days for every completed month of service, which gives 18 days per year. "
          "Up to 10 unused days can be carried forward to the next year; any balance above 10 days lapses. Earned "
          "Leave of more than 3 consecutive days must be requested at least 7 days in advance and approved by the "
          "reporting manager. Unused Earned Leave can be encashed only at the time of separation from the company."),
    ("h1", "3. Special Leave"),
    ("h2", "3.1 Maternity Leave"),
    ("p", "Female employees are entitled to 26 weeks of paid maternity leave for the first two children, provided "
          "they have completed at least 80 days of service in the 12 months before the expected delivery date. The "
          "request must be submitted to HR at least 8 weeks before the expected date of delivery. Additional leave "
          "beyond 26 weeks, if needed, is treated as unpaid leave and requires approval from the HR Head."),
    ("h2", "3.2 Bereavement Leave"),
    ("p", "Employees may take 5 paid days of Bereavement Leave on the death of a member of their immediate "
          "family. Immediate family means:"),
    ("bullets", ["Spouse or domestic partner", "Children and step-children", "Parents and step-parents",
                 "Siblings", "Parents-in-law"]),
    ("p", "Bereavement Leave is separate from, and does not reduce, the Casual Leave balance."),
    ("h1", "4. Applying for Leave"),
    ("h2", "4.1 How to Apply"),
    ("p", "Follow these steps to apply for any type of leave:"),
    ("steps", ["Log in to the HR portal and choose the leave type.",
               "Select the dates and enter a short reason.",
               "Submit the request to your reporting manager.",
               "Your manager approves or rejects the request within 2 working days."]),
    ("p", "Leave is considered approved only after the manager's approval appears in the HR portal. Verbal approval "
          "is not sufficient."),
    ("h2", "4.2 Unapproved Absence"),
    ("p", "Absence without approved leave for more than 3 consecutive working days is treated as unauthorised "
          "absence. Unauthorised absence results in loss of pay for those days and may lead to disciplinary action "
          "under the Code of Conduct."),
    ("h1", "5. Policy Review"),
    ("p", "HR reviews this policy once a year. Questions about leave can be sent to hr@nimbusworks.example."),
]

# =============================================================================
# 02 HR Notice (supersedes part of 01)
# =============================================================================
NOTICE = [
    ("title", "HR Notice: Revised Leave and Holiday Arrangements for 2026"),
    ("meta", "Notice ID: HR-NOT-2025-14  |  Issued: 15 December 2025  |  Effective from: 1 January 2026"),
    ("h1", "1. Summary of Changes"),
    ("p", "This notice announces two changes that take effect on 1 January 2026 and publishes the list of company "
          "holidays for 2026."),
    ("h1", "2. Casual Leave Increase"),
    ("p", "From 1 January 2026, the annual Casual Leave entitlement increases from 8 days to 10 days per calendar "
          "year. This notice supersedes the Casual Leave figure in Section 2.1 of the Leave Policy (POL-HR-001, "
          "version 3.1). All other rules for Casual Leave, including the limit of 3 consecutive days, remain "
          "unchanged."),
    ("h1", "3. Quarterly Wellness Day"),
    ("p", "The last working Friday of every quarter (March, June, September and December) is a company-wide "
          "Wellness Day. Offices are closed on Wellness Days and no leave needs to be applied. Teams that provide "
          "customer support will arrange rotating cover and give affected employees a replacement day within the "
          "same quarter."),
    ("h1", "4. Company Holidays 2026"),
    ("p", "The company observes 10 fixed paid holidays in 2026, listed below. Employees may also take 2 optional "
          "holidays per year from the regional festival list on the HR portal, with manager approval."),
    ("table", ([["Date", "Holiday"],
                ["26 Jan 2026", "Republic Day"], ["4 Mar 2026", "Holi"], ["21 Mar 2026", "Eid al-Fitr"],
                ["3 Apr 2026", "Good Friday"], ["1 May 2026", "May Day"], ["15 Aug 2026", "Independence Day"],
                ["2 Oct 2026", "Gandhi Jayanti"], ["20 Oct 2026", "Dussehra"], ["8 Nov 2026", "Diwali"],
                ["25 Dec 2026", "Christmas Day"]], [60, 80])),
    ("h1", "5. Questions"),
    ("p", "Send questions about this notice to hr@nimbusworks.example."),
]

# =============================================================================
# 03 Expense Reimbursement Policy
# =============================================================================
EXPENSE = [
    ("title", "Expense Reimbursement Policy"),
    ("meta", "Document ID: POL-FIN-002  |  Version 2.0  |  Effective from 1 July 2025  |  Owner: Finance"),
    ("h1", "1. Purpose"),
    ("p", "This policy sets out which business expenses employees can claim, the limits that apply, and how to "
          "submit a claim. It applies to all employees. Expenses that are incurred during overnight business travel "
          "are also covered by the Business Travel Policy."),
    ("h1", "2. Eligible Expenses"),
    ("h2", "2.1 Meals"),
    ("p", "Employees on business duty within their base city may claim meals up to the daily limit for their "
          "grade. The limit depends on grade, as shown below."),
    ("table", ([["Grade", "Daily meal limit"],
                ["L1 to L2", "INR 800"],
                ["L3 to L4", "INR 1,200"],
                ["L5 and above", "INR 2,000"]], [70, 70])),
    ("p", "Meals during overnight business travel are covered by the per diem in the Business Travel Policy "
          "(POL-FIN-005) and not by the limits above."),
    ("h2", "2.2 Local Transport"),
    ("p", "Taxi, cab and auto-rickshaw fares for business travel within a city are reimbursable with receipts. "
          "Employees are encouraged to use app-based cabs where available, since these provide a digital receipt "
          "automatically. Personal commuting between home and the office is not reimbursable."),
    ("h2", "2.3 Client Entertainment"),
    ("p", "Client meals and entertainment must be approved in advance by the Department Head. The claim must name "
          "the client company and list all attendees."),
    ("h1", "3. Non-Reimbursable Expenses"),
    ("p", "The following expenses are not reimbursable:"),
    ("bullets", ["Personal travel and personal commuting",
                 "Traffic fines, parking penalties and other fines",
                 "Alcohol, except at pre-approved client events",
                 "Expenses of family members or dependants",
                 "Gifts to colleagues"]),
    ("h1", "4. Submitting Claims"),
    ("h2", "4.1 Submission Deadline"),
    ("p", "Submit claims on Form EXP-17 through the Finance portal within 30 calendar days of the date of the "
          "expense. Claims submitted after 30 days need written approval from the Finance Controller. A receipt "
          "must be attached for every expense above INR 500."),
    ("h2", "4.2 Approval Limits"),
    ("p", "Claims are approved according to the total amount of the claim:"),
    ("table", ([["Claim amount", "Approver"],
                ["Up to INR 10,000", "Reporting manager"],
                ["INR 10,001 to INR 50,000", "Department Head"],
                ["Above INR 50,000", "Department Head and Finance Controller"]], [70, 90])),
    ("h2", "4.3 Payment"),
    ("p", "Approved claims are paid within 10 working days of final approval, directly to the employee's salary "
          "account."),
    ("h1", "5. Questions"),
    ("p", "Send questions about expenses to finance@nimbusworks.example."),
]

# =============================================================================
# 04 Remote and Hybrid Work Policy
# =============================================================================
REMOTE = [
    ("title", "Remote and Hybrid Work Policy"),
    ("meta", "Document ID: POL-HR-003  |  Version 1.4  |  Effective from 1 October 2025  |  Owner: Human Resources"),
    ("h1", "1. Overview"),
    ("p", "Nimbus Works follows a hybrid model that combines time in the office with time working remotely. This "
          "policy describes who is eligible, how many days must be spent in the office, and which allowances apply."),
    ("h1", "2. Eligibility"),
    ("p", "Employees who have completed their 6-month probation period are eligible for hybrid work. Roles "
          "designated as onsite-only, such as laboratory, facilities and reception roles, are not eligible."),
    ("h1", "3. Office Attendance"),
    ("h2", "3.1 In-Office Days"),
    ("p", "Hybrid employees must work from the office at least 3 days per week. Tuesday and Thursday are team "
          "anchor days on which every hybrid employee is expected to be in the office."),
    ("h2", "3.2 Core Hours"),
    ("p", "On remote days, employees must be available online between 11:00 and 16:00 IST. Outside these core "
          "hours, working times are flexible as agreed with the manager."),
    ("h1", "4. Equipment and Allowances"),
    ("h2", "4.1 Home Office Stipend"),
    ("p", "Eligible employees receive a one-time home office stipend of INR 15,000 for a desk, chair, monitor or "
          "similar equipment. The stipend can be claimed once, within 12 months of becoming eligible, using Form "
          "EXP-17 with receipts attached."),
    ("h2", "4.2 Internet Allowance"),
    ("p", "A monthly internet allowance of INR 1,000 is paid with the salary to eligible hybrid employees. No "
          "receipts are required."),
    ("h2", "4.3 Company Laptop"),
    ("p", "A company laptop is provided to all hybrid employees and must be used for all work. The laptop must be "
          "configured and used according to the Information Security Policy (POL-IT-004)."),
    ("h1", "5. Working from Another City"),
    ("p", "Employees may work remotely from a city other than their base location for up to 20 working days in a "
          "calendar year. Requests must be submitted on Form RW-02 at least 10 working days in advance and need "
          "manager approval. Working from another country is not permitted without written approval from both HR "
          "and Legal."),
    ("h1", "6. Changing Hybrid Arrangements"),
    ("p", "The company may change or withdraw hybrid arrangements with 30 days' notice if business needs or "
          "performance concerns require it."),
]

# =============================================================================
# 05 Code of Conduct: FLAT, no headings, no title, single body font
# =============================================================================
CONDUCT = [
    ("p", "Nimbus Works Pvt. Ltd. expects every employee to act honestly, fairly and with respect for colleagues, "
          "customers and the law. This Code of Conduct (document POL-HR-006, version 3.0) applies to all employees, "
          "contractors and interns, and describes the standards of behaviour that we expect in every part of our "
          "work. If a situation is not covered here, use good judgement and ask your manager or HR."),
    ("p", "Employees may accept gifts from vendors or clients only if the value does not exceed INR 2,500 per gift "
          "and INR 7,500 in total per calendar year. Gifts above these limits must be politely declined or handed "
          "over to HR. Cash or cash equivalents, such as gift cards, must never be accepted, whatever the amount."),
    ("p", "A conflict of interest arises when a personal interest could influence, or appear to influence, a "
          "business decision. Any such conflict, including a financial interest in a vendor or competitor and a "
          "close relative working for a vendor, must be disclosed in writing to your manager and to HR within 7 days "
          "of becoming aware of it. The manager and HR will decide whether the employee should step away from the "
          "decision concerned."),
    ("p", "Employees must protect confidential company and customer information, both during employment and after "
          "it ends. Confidential information must not be shared on social media, in public forums or with "
          "unauthorised persons. Views posted on personal social media accounts are personal and must not suggest "
          "that they represent the company."),
    ("p", "Anyone who sees or suspects a breach of this Code should report it. Concerns can be raised with the "
          "Ethics Committee through the confidential hotline at 1800-555-0142 or by email to "
          "ethics@nimbusworks.example. Reports can be made anonymously. The company will not tolerate retaliation "
          "against anyone who raises a concern in good faith, and retaliation is itself a breach of this Code."),
    ("p", "The company has zero tolerance for harassment or discrimination of any kind. Complaints of sexual "
          "harassment must be made to the Internal Committee in writing within 3 months of the incident, although "
          "the Committee may extend this period for good reason. All complaints are handled confidentially."),
    ("p", "Violations of this Code may lead to disciplinary action, up to and including termination of employment, "
          "and where the law requires it the company will report the matter to the authorities."),
]

# =============================================================================
# 06 Information Security Policy
# =============================================================================
SECURITY = [
    ("title", "Information Security Policy"),
    ("meta", "Document ID: POL-IT-004  |  Version 2.2  |  Effective from 1 January 2026  |  Owner: IT Security"),
    ("h1", "1. Purpose and Scope"),
    ("p", "This policy protects company and customer data. It applies to all employees, contractors and interns "
          "who use company systems, and to every device used to access them."),
    ("h1", "2. Accounts and Passwords"),
    ("h2", "2.1 Passwords"),
    ("p", "Passwords must be at least 14 characters long. Passwords are not rotated on a fixed schedule, but must "
          "be changed immediately if you suspect they have been compromised. Do not reuse company passwords on "
          "personal accounts."),
    ("h2", "2.2 Multi-Factor Authentication"),
    ("p", "Multi-factor authentication (MFA) is mandatory for company email, the VPN, the code repositories and "
          "the cloud console."),
    ("h2", "2.3 Screen Lock"),
    ("p", "Laptops and desktops must lock automatically after 5 minutes of inactivity. Lock your screen manually "
          "whenever you leave your desk."),
    ("h1", "3. Devices and Media"),
    ("h2", "3.1 Company Laptops"),
    ("p", "All company laptops use full-disk encryption. Employees must not install software that is not on the "
          "approved software list. Requests for new software are raised through the IT service desk."),
    ("h2", "3.2 Removable Media"),
    ("p", "USB storage devices are prohibited on company devices. Exceptions can be requested through an IT "
          "service desk ticket and must be approved by the CISO."),
    ("h2", "3.3 Personal Devices"),
    ("p", "Personal phones and tablets may be used for company email and chat only after they are enrolled in the "
          "company's mobile device management (MDM) system. Personal laptops may not be used to access company "
          "systems."),
    ("h1", "4. Reporting Incidents"),
    ("p", "Report the following events to security@nimbusworks.example immediately:"),
    ("bullets", ["A lost or stolen laptop, phone or access card",
                 "A phishing email that you opened or clicked a link in",
                 "Suspected malware on any device",
                 "Any unauthorised access to systems or data"]),
    ("p", "A lost or stolen device must be reported within 2 hours of discovering the loss. Do not wait until you "
          "have searched for it."),
    ("h1", "5. Consequences"),
    ("p", "Violations of this policy may lead to disciplinary action. Deliberate or repeated violations are "
          "treated as serious misconduct."),
]

# =============================================================================
# 07 Business Travel Policy
# =============================================================================
TRAVEL = [
    ("title", "Business Travel Policy"),
    ("meta", "Document ID: POL-FIN-005  |  Version 1.8  |  Effective from 1 July 2025  |  Owner: Finance"),
    ("h1", "1. Scope"),
    ("p", "This policy applies to all overnight and out-of-city business travel by employees of Nimbus Works."),
    ("h1", "2. Booking and Approval"),
    ("h2", "2.1 Travel Request"),
    ("p", "Submit a travel request on Form TRV-09 and obtain manager approval before booking. Flights and hotels "
          "must be booked through the company travel desk at least 7 days before the travel date, except in "
          "emergencies."),
    ("h2", "2.2 Air Travel"),
    ("p", "Economy class is the standard for all flights. Business class is permitted only for flights longer than "
          "6 hours, for employees in Grade L5 and above, and with Vice President approval."),
    ("h2", "2.3 Rail Travel"),
    ("p", "Employees may travel by AC 2-Tier or Executive Chair Car on rail routes."),
    ("h1", "3. Accommodation"),
    ("p", "Hotel stays must stay within the nightly limits below, which include taxes. The limit depends on the "
          "city tier."),
    ("table", ([["City tier", "Cities", "Limit per night"],
                ["Tier 1", "Mumbai, Delhi, Bengaluru, Chennai, Hyderabad, Kolkata", "INR 7,500"],
                ["Tier 2", "Pune, Ahmedabad, Jaipur, Kochi, Chandigarh", "INR 5,000"]], [25, 95, 40])),
    ("p", "Stays above the limit require advance approval from the Department Head."),
    ("h1", "4. Daily Allowance (Per Diem)"),
    ("p", "On overnight business travel, employees receive a per diem to cover meals and incidental expenses: "
          "INR 1,500 per day for domestic travel and USD 75 per day for international travel. The per diem replaces "
          "the daily meal limits in the Expense Reimbursement Policy (POL-FIN-002) for the days spent travelling. "
          "Local cab fares at the destination remain reimbursable with receipts."),
    ("h1", "5. Advances and Settlement"),
    ("h2", "5.1 Travel Advance"),
    ("p", "Employees may request an advance of up to 80% of the estimated trip cost through the Finance portal."),
    ("h2", "5.2 Settlement"),
    ("p", "Settle the trip within 7 days of returning, by submitting Form EXP-17 with all receipts. Unsettled "
          "advances may be recovered from the next salary."),
]

DOCS = [
    ("01_leave_policy.pdf", "Leave Policy", "POL-HR-001 v3.1", LEAVE, "Leave Policy"),
    ("02_hr_notice_leave_holidays_2026.pdf", "HR Notice: Revised Leave and Holiday Arrangements for 2026",
     "HR-NOT-2025-14", NOTICE, "HR Notice 2025-14"),
    ("03_expense_reimbursement_policy.pdf", "Expense Reimbursement Policy", "POL-FIN-002 v2.0", EXPENSE,
     "Expense Reimbursement Policy"),
    ("04_remote_work_policy.pdf", "Remote and Hybrid Work Policy", "POL-HR-003 v1.4", REMOTE,
     "Remote and Hybrid Work Policy"),
    ("05_code_of_conduct.pdf", "Code of Conduct", "POL-HR-006 v3.0", CONDUCT, "Code of Conduct"),
    ("06_it_security_policy.pdf", "Information Security Policy", "POL-IT-004 v2.2", SECURITY,
     "Information Security Policy"),
    ("07_travel_policy.pdf", "Business Travel Policy", "POL-FIN-005 v1.8", TRAVEL, "Business Travel Policy"),
]

# (id, file, phrase that must appear on the page, section, fact)
FACTS = [
    ("F01", "01_leave_policy.pdf", "12 paid sick days per calendar year", "2.3 Sick Leave", "12 paid sick days per calendar year"),
    ("F02", "01_leave_policy.pdf", "more than 2 consecutive working days", "2.3 Sick Leave", "Medical certificate needed after more than 2 consecutive working days; submit within 3 working days using Form HR-204"),
    ("F03", "01_leave_policy.pdf", "Up to 10 unused days can be carried forward", "2.4 Earned Leave", "Earned Leave: up to 10 days carried forward; accrues 1.5 days/month (18/year)"),
    ("F04", "01_leave_policy.pdf", "8 days per year", "2.1 Annual Entitlement (table)", "Casual Leave is 8 days per year in v3.1 (OUTDATED, see F05)"),
    ("F05", "02_hr_notice_leave_holidays_2026.pdf", "increases from 8 days to 10 days", "2. Casual Leave Increase", "From 1 Jan 2026 Casual Leave is 10 days; notice supersedes Leave Policy 2.1 (CURRENT answer)"),
    ("F06", "02_hr_notice_leave_holidays_2026.pdf", "last working Friday of every quarter", "3. Quarterly Wellness Day", "Wellness Day: last working Friday of each quarter, offices closed"),
    ("F07", "02_hr_notice_leave_holidays_2026.pdf", "10 fixed paid holidays", "4. Company Holidays 2026", "10 fixed paid holidays in 2026 plus 2 optional holidays"),
    ("F08", "02_hr_notice_leave_holidays_2026.pdf", "8 Nov 2026", "4. Company Holidays 2026 (table)", "Diwali is 8 Nov 2026"),
    ("F09", "01_leave_policy.pdf", "26 weeks of paid maternity leave", "3.1 Maternity Leave", "26 weeks paid maternity leave (first two children), 80 days of service, apply 8 weeks before"),
    ("F10", "01_leave_policy.pdf", "5 paid days of Bereavement Leave", "3.2 Bereavement Leave", "5 paid days on death of immediate family; does not reduce Casual Leave"),
    ("F11", "03_expense_reimbursement_policy.pdf", "L3 to L4", "2.1 Meals (table)", "Daily meal limit L3 to L4 is INR 1,200 (L1-L2 800; L5+ 2,000)"),
    ("F12", "03_expense_reimbursement_policy.pdf", "within 30 calendar days", "4.1 Submission Deadline", "Submit Form EXP-17 within 30 calendar days; later needs Finance Controller approval"),
    ("F13", "03_expense_reimbursement_policy.pdf", "above INR 500", "4.1 Submission Deadline", "Receipt required for every expense above INR 500"),
    ("F14", "03_expense_reimbursement_policy.pdf", "INR 10,001 to INR 50,000", "4.2 Approval Limits (table)", "Claims INR 10,001-50,000 approved by Department Head"),
    ("F15", "03_expense_reimbursement_policy.pdf", "within 10 working days of final approval", "4.3 Payment", "Paid within 10 working days of final approval"),
    ("F16", "03_expense_reimbursement_policy.pdf", "Traffic fines", "3. Non-Reimbursable Expenses", "Traffic fines, personal commuting, alcohol (except pre-approved client events) etc. are not reimbursable"),
    ("F17", "04_remote_work_policy.pdf", "at least 3 days per week", "3.1 In-Office Days", "Hybrid employees in office at least 3 days/week; Tue and Thu are anchor days"),
    ("F18", "04_remote_work_policy.pdf", "between 11:00 and 16:00 IST", "3.2 Core Hours", "Core availability 11:00-16:00 IST on remote days"),
    ("F19", "04_remote_work_policy.pdf", "one-time home office stipend of INR 15,000", "4.1 Home Office Stipend", "One-time INR 15,000 stipend, claim once within 12 months using Form EXP-17"),
    ("F20", "04_remote_work_policy.pdf", "internet allowance of INR 1,000", "4.2 Internet Allowance", "INR 1,000 per month internet allowance, no receipts"),
    ("F21", "04_remote_work_policy.pdf", "up to 20 working days in a", "5. Working from Another City", "Up to 20 working days/year in another city; Form RW-02 at least 10 working days ahead; other country needs HR and Legal"),
    ("F22", "05_code_of_conduct.pdf", "INR 2,500 per gift", "(no headings) gifts paragraph", "Gift limit INR 2,500 per gift and INR 7,500 per calendar year; cash equivalents never accepted"),
    ("F23", "05_code_of_conduct.pdf", "within 7 days", "(no headings) conflict of interest paragraph", "Disclose conflicts of interest in writing to manager and HR within 7 days"),
    ("F24", "05_code_of_conduct.pdf", "1800-555-0142", "(no headings) raising concerns paragraph", "Ethics hotline 1800-555-0142 or ethics@nimbusworks.example; anonymous reports allowed"),
    ("F25", "06_it_security_policy.pdf", "at least 14 characters", "2.1 Passwords", "Passwords at least 14 characters; no fixed rotation"),
    ("F26", "06_it_security_policy.pdf", "USB storage devices are prohibited", "3.2 Removable Media", "USB storage prohibited; exceptions via IT ticket approved by CISO"),
    ("F27", "06_it_security_policy.pdf", "within 2 hours", "4. Reporting Incidents", "Report lost or stolen device within 2 hours to security@nimbusworks.example"),
    ("F28", "06_it_security_policy.pdf", "mandatory for company email", "2.2 Multi-Factor Authentication", "MFA mandatory for email, VPN, code repositories, cloud console"),
    ("F29", "06_it_security_policy.pdf", "after 5 minutes of inactivity", "2.3 Screen Lock", "Auto screen lock after 5 minutes of inactivity"),
    ("F30", "07_travel_policy.pdf", "longer than 6 hours", "2.2 Air Travel", "Business class only for flights longer than 6 hours, Grade L5+, with VP approval"),
    ("F31", "07_travel_policy.pdf", "Mumbai, Delhi, Bengaluru", "3. Accommodation (table)", "Tier 1 cities hotel limit INR 7,500/night; Tier 2 (Pune, Ahmedabad, Jaipur, Kochi, Chandigarh) INR 5,000"),
    ("F32", "07_travel_policy.pdf", "INR 1,500 per day for domestic travel", "4. Daily Allowance (Per Diem)", "Per diem INR 1,500/day domestic, USD 75/day international; replaces expense-policy meal limits while travelling"),
    ("F33", "07_travel_policy.pdf", "up to 80% of the estimated trip cost", "5.1 Travel Advance", "Advance up to 80% of estimated trip cost; settle within 7 days of return with Form EXP-17"),
]

# Terms that must NOT appear anywhere in the corpus (they back the not-found test questions).
ABSENT = {
    r"\bpaternity\b": "paternity leave",
    r"\bpets?\b": "pet insurance",
    r"\besops?\b|stock option": "ESOP / stock options",
    r"\bparking allowance\b": "parking allowance",
    r"\btuition\b": "tuition reimbursement",
    r"\bsabbatical\b": "sabbatical",
    r"\bdress code\b": "dress code",
    r"\blucknow\b": "hotel limit for a city not in the tier table",
    r"\bgratuity\b": "gratuity",
    r"\bgym\b": "gym membership",
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    for old in PDF_DIR.glob("*.pdf"):
        old.unlink()
    for filename, title, doc_id, blocks, running in DOCS:
        build(filename, title, doc_id, blocks, running)

    # ---- verify -------------------------------------------------------------
    pages_text: dict[str, list[str]] = {}
    for filename, *_ in DOCS:
        with fitz.open(PDF_DIR / filename) as pdf:
            pages_text[filename] = [norm(p.get_text()) for p in pdf]
    full = " ".join(" ".join(v) for v in pages_text.values()).lower()

    problems = []
    for pattern, label in ABSENT.items():
        if re.search(pattern, full):
            problems.append(f"term for not-found topic '{label}' appears in the corpus")

    rows = []
    for fid, filename, phrase, section, fact in FACTS:
        pages = [i + 1 for i, t in enumerate(pages_text[filename]) if norm(phrase) in t]
        if not pages:
            problems.append(f"{fid}: phrase not found in {filename}: {phrase!r}")
            continue
        rows.append((fid, filename, section, ", ".join(map(str, pages)), fact))

    if problems:
        print("PROBLEMS:\n  " + "\n  ".join(problems))
        sys.exit(1)

    lines = [
        "# Corpus answer key (Nimbus Works, fictional)",
        "",
        "Generated by `scripts/make_sample_pdfs.py`. Page numbers are computed from the real PDFs, so use them "
        "directly as `expected_page` in the eval questions. If you change the PDFs, re-run the script and this "
        "file updates itself.",
        "",
        "## Documents",
        "",
        "| File | Pages | Structure |",
        "|---|---|---|",
    ]
    structure = {
        "01_leave_policy.pdf": "numbered headings, table, bullet list, numbered steps",
        "02_hr_notice_leave_holidays_2026.pdf": "numbered headings, holiday table; supersedes part of 01",
        "03_expense_reimbursement_policy.pdf": "numbered headings, 2 tables, list with colon lead-in",
        "04_remote_work_policy.pdf": "numbered headings, cross-references to 03 and 06",
        "05_code_of_conduct.pdf": "FLAT: no headings, no title, plain paragraphs (fallback chunker test)",
        "06_it_security_policy.pdf": "numbered headings, list with colon lead-in",
        "07_travel_policy.pdf": "numbered headings, table; overrides meal limits in 03 while travelling",
    }
    for filename, *_ in DOCS:
        lines.append(f"| {filename} | {len(pages_text[filename])} | {structure[filename]} |")

    lines += ["", "## Facts (use for answerable questions)", "",
              "| ID | Document | Section | Page(s) | Fact |", "|---|---|---|---|---|"]
    for fid, filename, section, pages, fact in rows:
        lines.append(f"| {fid} | {filename} | {section} | {pages} | {fact} |")

    lines += [
        "",
        "## Suggested question types",
        "",
        "**Conflict / superseded (answer should be 10, cite the notice, may mention the older 8):** "
        "'How many casual leave days do I get?' (F04 vs F05)",
        "",
        "**Multi-document:**",
        "- 'What can I spend on meals on a 2-day work trip to Mumbai as an L3?' -> per diem INR 1,500/day (F32), "
        "not INR 1,200 (F11)",
        "- 'How do I claim the home office stipend?' -> Form EXP-17 within the rules of the expense policy (F19, F12)",
        "- 'Can I use my own laptop for hybrid work?' -> company laptop provided (04 section 4.3) and personal "
        "laptops may not access company systems (06 section 3.3)",
        "",
        "**Exact-term (BM25 should help):** Form HR-204 (F02), Form RW-02 (F21), Form EXP-17 (F12), "
        "Form TRV-09, hotline 1800-555-0142 (F24), 'INR 10,001' (F14).",
        "",
        "**Paraphrased (different words from the policy):** 'How long can I be sick before I need a doctor's "
        "note?' (F02); 'Do I have to change my password every 90 days?' (F25: no fixed rotation); "
        "'Can I plug in a pen drive?' (F26).",
        "",
        "**Partial coverage:**",
        "- 'What is the maximum taxi fare I can claim?' -> taxi fares are reimbursable with receipts but no cap is "
        "stated (03 section 2.2)",
        "- 'What is the per diem and hotel cap for an international trip?' -> international per diem is USD 75 "
        "(F32) but there is no international hotel limit",
        "",
        "**Not found (verified absent from every PDF by the generator):**",
        "",
    ]
    for label in ABSENT.values():
        lines.append(f"- {label}")
    lines += [
        "",
        "Closest-but-not-covered cases are the best traps: paternity leave (maternity is covered, paternity is "
        "not), hotel limit in Lucknow (only Tier 1 and Tier 2 cities are listed), and pet insurance.",
        "",
    ]
    FACTS_MD.parent.mkdir(parents=True, exist_ok=True)
    FACTS_MD.write_text("\n".join(lines), encoding="utf-8")

    for filename, *_ in DOCS:
        print(f"{filename:42s} {len(pages_text[filename])} page(s)")
    print(f"\n{len(rows)} facts located. Answer key: {FACTS_MD.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
