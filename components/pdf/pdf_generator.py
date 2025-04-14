from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import re

matplotlib.use('Agg')

class PDFGenerator:
    """
    Utility class for generating PDF reports with consistent styling and structure.
    """
    
    @staticmethod
    def create_pdf(data, report_content):
        """
        Create a PDF report from the data and report content
        
        Args:
            data (dict): The data used to generate the report
            report_content (dict): The structured content for the report
            
        Returns:
            BytesIO: A buffer containing the generated PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=1,
            spaceAfter=12
        )
        elements.append(Paragraph("Process Analysis Report", title_style))
        elements.append(Spacer(1, 12))
        
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,
            spaceAfter=12
        )
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", date_style))
        elements.append(Spacer(1, 24))
        
        PDFGenerator._add_text_section(elements, "Executive Summary", report_content.get("executive_summary", ""), styles)
        PDFGenerator._add_text_section(elements, "Top Variables Analysis", report_content.get("top_variables_analysis", ""), styles)
        PDFGenerator._add_text_section(elements, "Impact Breakdown", report_content.get("impact_breakdown", ""), styles)
        PDFGenerator._add_recommendations_section(elements, "Recommendations", report_content.get("recommendations", ""), styles)
        
        if report_content.get("tables"):
            PDFGenerator._add_tables_section(elements, report_content.get("tables", []), styles)

        if report_content.get("charts"):
            PDFGenerator._add_charts_section(elements, report_content.get("charts", []), styles)

        PDFGenerator._add_kpi_summary(elements, data, styles)
        
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def _add_text_section(elements, title, content, styles):
        """
        Add a text section to the PDF
        
        Args:
            elements (list): The list of PDF elements
            title (str): The section title
            content (str): The section content
            styles (dict): The reportlab styles
        """
        elements.append(Paragraph(title, styles["Heading2"]))
        elements.append(Paragraph(content, styles["Normal"]))
        elements.append(Spacer(1, 12))
        
    @staticmethod
    def _add_recommendations_section(elements, title, recommendations_text, styles):
        """
        Add recommendations section to the PDF with enhanced formatting
        
        Args:
            elements (list): The list of PDF elements
            title (str): The section title
            recommendations_text (str): The recommendations text
            styles (dict): The reportlab styles
        """
        elements.append(Paragraph(title, styles["Heading2"]))
        elements.append(Spacer(1, 6))
        
        recommendation_title_style = ParagraphStyle(
            'RecommendationTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            spaceAfter=2
        )

        recommendation_content_style = ParagraphStyle(
            'RecommendationContent',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            leftIndent=20,
            spaceAfter=10
        )
        
        bullet_style = ParagraphStyle(
            'BulletPoint',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            leftIndent=20,
            bulletIndent=10,
            firstLineIndent=0,
            spaceBefore=2,
            spaceAfter=2
        )
        
        recommendation_number_style = ParagraphStyle(
            'RecommendationNumber',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=14,
            textColor=colors.darkblue
        )
        
        if not recommendations_text:
            elements.append(Paragraph("No recommendations available.", styles["Normal"]))
            elements.append(Spacer(1, 12))
            return
        
        if re.search(r'\d+\.\s+\*\*.*?\*\*:', recommendations_text) or re.search(r'\d+\.\s+\*\*.*?\*\*', recommendations_text):
            items = re.split(r'(\d+\.\s+)', recommendations_text)
            
            if items and not items[0].strip():
                items = items[1:]
            
            list_flowables = []
            
            for i in range(0, len(items), 2):
                if i+1 < len(items):
                    item_num = items[i].strip()  
                    item_content = items[i+1].strip() 

                    title_match = re.match(r'\*\*(.*?)\*\*:?\s*(.*)', item_content, re.DOTALL)
                    
                    if title_match:
                        rec_title = title_match.group(1).strip()
                        rec_content = title_match.group(2).strip()
                        
                        if ':' in item_content:
                            text = f"{item_num} <b>{rec_title}:</b>"
                        else:
                            text = f"{item_num} <b>{rec_title}</b>"
                            
                        list_flowables.append(Paragraph(text, recommendation_title_style))
                        list_flowables.append(Paragraph(rec_content, recommendation_content_style))
                        list_flowables.append(Spacer(1, 6))
                    else:
                        text = f"{item_content}"
                        list_flowables.append(Paragraph(text, bullet_style))
                        list_flowables.append(Spacer(1, 6))
            
            for flowable in list_flowables:
                elements.append(flowable)
        else:
            lines = recommendations_text.split('\n')
            for line in lines:
                if line.strip():
                    elements.append(Paragraph(line.strip(), bullet_style))
                    elements.append(Spacer(1, 4))
            
        elements.append(Spacer(1, 12))
    
    @staticmethod
    def _add_tables_section(elements, tables_data, styles):
        """
        Add tables to the PDF
        
        Args:
            elements (list): The list of PDF elements
            tables_data (list): The list of table data
            styles (dict): The reportlab styles
        """
        elements.append(Paragraph("Data Tables", styles["Heading2"]))
        
        for table_info in tables_data:
            elements.append(Paragraph(table_info.get("title", ""), styles["Heading3"]))
            elements.append(Paragraph(table_info.get("description", ""), styles["Normal"]))
            
            table_data = table_info.get("data", [])
            if table_data:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
            elements.append(Spacer(1, 12))
    
    @staticmethod
    def _add_charts_section(elements, charts_data, styles):
        """
        Add charts to the PDF
        
        Args:
            elements (list): The list of PDF elements
            charts_data (list): The list of chart data
            styles (dict): The reportlab styles
        """
        elements.append(Paragraph("Data Visualizations", styles["Heading2"]))
        
        for chart_info in charts_data:
            elements.append(Paragraph(chart_info.get("title", ""), styles["Heading3"]))
            elements.append(Paragraph(chart_info.get("description", ""), styles["Normal"]))
            
            chart_type = chart_info.get("type", "")
            chart_data = chart_info.get("data", {})
            
            if chart_type and chart_data:
                img_buffer = PDFGenerator._create_chart_image(chart_type, chart_data, chart_info.get("title", ""))
                if img_buffer:
                    img = Image(img_buffer, width=450, height=250)
                    elements.append(img)
            
            elements.append(Spacer(1, 12))
    
    @staticmethod
    def _create_chart_image(chart_type, chart_data, title):
        """
        Create a chart image for the PDF
        
        Args:
            chart_type (str): The type of chart to create
            chart_data (dict): The data for the chart
            title (str): The chart title
            
        Returns:
            BytesIO: A buffer containing the chart image
        """
        img_buffer = BytesIO()
        fig = plt.figure(figsize=(7, 4))
        
        labels, values, x, y = PDFGenerator._extract_chart_data(chart_type, chart_data)
        
        if chart_type == "bar":
            plt.bar(labels, values)
            plt.xlabel(chart_data.get("xlabel", ""))
            plt.ylabel(chart_data.get("ylabel", ""))
            
        elif chart_type == "pie":
            if len(labels) > len(values):
                labels = labels[:len(values)]
            elif len(values) > len(labels):
                values = values[:len(labels)]
                
            plt.pie(values, labels=labels, autopct='%1.1f%%')
            
        elif chart_type == "line":
            plt.plot(x, y)
            plt.xlabel(chart_data.get("xlabel", ""))
            plt.ylabel(chart_data.get("ylabel", ""))
            
            if len(x) > 10:
                plt.xticks(rotation=45, ha='right')
                plt.subplots_adjust(bottom=0.3)
        
        plt.title(title)
        plt.tight_layout()
        
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
    
    @staticmethod
    def _extract_chart_data(chart_type, chart_data):
        """
        Extract data from chart_data in a consistent format
        
        Args:
            chart_type (str): The type of chart
            chart_data (dict): The chart data
            
        Returns:
            tuple: (labels, values, x, y) for the chart
        """
        labels = []
        values = []
        x = []
        y = []
        
        if "labels" in chart_data and "values" in chart_data:
            labels = chart_data.get("labels", [])
            values = chart_data.get("values", [])
            x = labels
            y = values
        elif "labels" in chart_data and "datasets" in chart_data:
            labels = chart_data.get("labels", [])
            values = chart_data.get("datasets", [{}])[0].get("data", [])
            x = labels
            y = values
        elif "x" in chart_data and "y" in chart_data:
            x = chart_data.get("x", [])
            y = chart_data.get("y", [])
            labels = x
            values = y
        
        return labels, values, x, y
    
    @staticmethod
    def _add_kpi_summary(elements, data, styles):
        """
        Add KPI summary section to the PDF
        
        Args:
            elements (list): The list of PDF elements
            data (dict): The data containing KPI information
            styles (dict): The reportlab styles
        """
        elements.append(Paragraph("KPI Summary Across Scenarios", styles["Heading2"]))
        
        simulated_data = data.get('data', {}).get("simulated_summary", {}).get('simulated_data', [])
        if not simulated_data and 'simulated_summary' in data:
            simulated_data = data.get("simulated_summary", {}).get('simulated_data', [])
            
        if simulated_data:

            kpi_values = [scenario.get("kpi_value", 0) for scenario in simulated_data 
                          if scenario.get("kpi_value") is not None]
            
            if kpi_values:
                avg_kpi = sum(kpi_values) / len(kpi_values)
                max_kpi = max(kpi_values)
                min_kpi = min(kpi_values)
                
                kpi_summary = f"""The analysis includes {len(kpi_values)} scenarios with KPI values. 
                The average KPI value across all scenarios is {avg_kpi:.2f}. 
                The maximum KPI value is {max_kpi:.2f} and the minimum is {min_kpi:.2f}."""
                elements.append(Paragraph(kpi_summary, styles["Normal"]))
                elements.append(Spacer(1, 12))
                
                PDFGenerator._add_kpi_table(elements, simulated_data, max_kpi)
                
                if len(kpi_values) > 1:
                    PDFGenerator._add_kpi_histogram(elements, kpi_values, avg_kpi)
    
    @staticmethod
    def _add_kpi_table(elements, simulated_data, max_kpi):
        """
        Add KPI table to the PDF
        
        Args:
            elements (list): The list of PDF elements
            simulated_data (list): The simulated data
            max_kpi (float): The maximum KPI value
        """
        kpi_data = [["Scenario", "KPI Value", "% of Maximum"]]
        
        sorted_scenarios = sorted(simulated_data, key=lambda x: x.get("kpi_value", 0), reverse=True)
        
        for scenario in sorted_scenarios:
            kpi_value = scenario.get("kpi_value", 0)
            percent_of_max = (kpi_value / max_kpi * 100) if max_kpi > 0 else 0
            kpi_data.append([
                scenario.get("scenario", ""),
                f"{kpi_value:.2f}",
                f"{percent_of_max:.1f}%"
            ])
        
        kpi_table = Table(kpi_data)
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 12))
    
    @staticmethod
    def _add_kpi_histogram(elements, kpi_values, avg_kpi):
        """
        Add KPI histogram to the PDF
        
        Args:
            elements (list): The list of PDF elements
            kpi_values (list): The KPI values
            avg_kpi (float): The average KPI value
        """
        img_buffer = BytesIO()
        fig = plt.figure(figsize=(7, 4))
        
        plt.hist(kpi_values, bins=min(10, len(kpi_values)), alpha=0.7, color='skyblue')
        plt.axvline(avg_kpi, color='red', linestyle='dashed', linewidth=1, label=f'Mean: {avg_kpi:.2f}')
        plt.xlabel('KPI Value')
        plt.ylabel('Frequency')
        plt.title('Distribution of KPI Values Across Scenarios')
        plt.legend()
        plt.tight_layout()
        
        plt.savefig(img_buffer, format='png')
        img_buffer.seek(0)
        
        img = Image(img_buffer, width=450, height=250)
        elements.append(img)
        plt.close(fig)