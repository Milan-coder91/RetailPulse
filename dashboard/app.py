    ],
    "Value": [
        total_sales_latest, total_units_latest, total_orders_latest, low_stock_items,
        average_daily_sales, f"{sales_difference_pct:+.2f}%", sales_alert_status,
        inventory_alert_status, reorder_alert_status, high_priority_items,
        medium_priority_items, low_priority_items, total_reorder_items,
        float(daily_sales.tail(7).mean()) if not daily_sales.empty else 0,
        f"{(((total_sales_latest - daily_sales.tail(7).mean()) / daily_sales.tail(7).mean()) * 100):+.2f}%" if not daily_sales.tail(7).empty and daily_sales.tail(7).mean() else "N/A",
        critical_alerts, strong_alerts, normal_alerts
    ]
})
alert_csv = alert_summary.to_csv(index=False).encode("utf-8")
st.download_button(
    label="🚨 Download Alert Summary (CSV)",
    data=alert_csv,
    file_name="retailpulse_alert_summary.csv",
    mime="text/csv"
)

# PDF export remains an option inside the dashboard; this deliverable itself is a Python .py file.
def create_pdf_report():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        return None

    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    styles["Title"].alignment = TA_CENTER
    story = [
        Paragraph("RetailPulse AI Analytics Platform", styles["Title"]),
        Paragraph("Metrics & Alert Report", styles["Heading2"]),
        Spacer(1, 12),
        Paragraph("Key Metrics", styles["Heading2"]),
    ]
    metrics_data = [
        ["Metric", "Value"],
        ["Latest Sales", f"INR {total_sales_latest:,.0f}"],
        ["Units Sold", f"{total_units_latest:,.0f}"],
        ["Orders", f"{total_orders_latest:,}"],
        ["Low Stock Alerts", f"{low_stock_items:,}"],
        ["Latest Sales Date", latest_date.strftime("%d %b %Y")],
    ]
    metrics_table = Table(metrics_data, colWidths=[250, 180])
    metrics_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([metrics_table, Spacer(1, 15), Paragraph("Sales Performance Alert", styles["Heading2"])])
    story.extend([
        Paragraph(f"Average Daily Sales: INR {average_daily_sales:,.0f}", styles["Normal"]),
        Paragraph(f"Sales Difference: {sales_difference_pct:+.2f}%", styles["Normal"]),
        Paragraph(f"Sales Alert Status: {sales_alert_status}", styles["Normal"]),
        Spacer(1, 15), Paragraph("Inventory & Reorder Alerts", styles["Heading2"]),
    ])
    alert_table_data = [
        ["Alert Metric", "Value"],
        ["Low Stock Items", f"{low_stock_items:,}"],
        ["High Priority", f"{high_priority_items:,}"],
        ["Medium Priority", f"{medium_priority_items:,}"],
        ["Low Priority", f"{low_priority_items:,}"],
        ["Total Replenishment Items", f"{total_reorder_items:,}"],
    ]
    alert_table = Table(alert_table_data, colWidths=[250, 180])
    alert_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([alert_table, Spacer(1, 15), Paragraph("Final Alert Status", styles["Heading2"])])
    story.extend([
        Paragraph(f"Sales Status: {sales_alert_status}", styles["Normal"]),
        Paragraph(f"Inventory Status: {inventory_alert_status}", styles["Normal"]),
        Paragraph(f"Reorder Status: {reorder_alert_status}", styles["Normal"]),
        Spacer(1, 10),
        Paragraph("Report generated from the RetailPulse dashboard.", styles["Normal"]),
    ])
    document.build(story)
    buffer.seek(0)
    return buffer.getvalue()

pdf_report = create_pdf_report()
if pdf_report:
    st.download_button(
        label="📑 Download Business Report (PDF)",
        data=pdf_report,
        file_name="retailpulse_business_report.pdf",
        mime="application/pdf"
    )
else:
    st.info("PDF export needs ReportLab. Add 'reportlab' to requirements.txt to enable it.")

st.subheader("📊 Export Summary")
export_summary = pd.DataFrame({
    "Report": ["Sales Data", "Inventory & Reorder Data", "Alert Summary", "Business Report"],
    "Format": ["CSV", "CSV", "CSV", "PDF"],
    "Status": ["Available", "Available", "Available", "Available" if pdf_report else "Needs reportlab"],
})
st.dataframe(export_summary, use_container_width=True, hide_index=True)

export_validation = {
    "Sales CSV Export": len(sales_csv) > 0,
    "Inventory CSV Export": len(inventory_csv) > 0,
    "Alert Summary CSV Export": len(alert_csv) > 0,
    "PDF Report Export": bool(pdf_report),
    "Export Summary": len(export_summary) == 4,
}
passed_exports = sum(export_validation.values())
total_exports = len(export_validation)
st.subheader("✅ Export Functionality Validation")
with st.expander("View export validation checks", expanded=False):
    st.dataframe(pd.DataFrame({"Check": list(export_validation.keys()), "Passed": list(export_validation.values())}), use_container_width=True, hide_index=True)
if passed_exports == total_exports:
    st.success("All CSV and PDF export functions are ready.")
else:
    st.warning(f"{passed_exports}/{total_exports} export checks passed. If PDF is unavailable, install ReportLab to enable it.")
st.success("RetailPulse export center is ready. Download sales, inventory, and alert CSVs from the buttons above.")
