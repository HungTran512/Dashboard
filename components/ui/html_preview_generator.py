import re
from datetime import datetime
from dash import html, dcc
import dash_bootstrap_components as dbc

class HTMLPreviewGenerator:
    """
    Class responsible for generating HTML preview content for reports.
    """
    
    @staticmethod
    def create_preview_content(data, report_content):
        """
        Create HTML preview content for the report
        
        Args:
            data (dict): The data used to generate the report
            report_content (dict): The structured content for the report
            
        Returns:
            list: A list of Dash HTML components representing the preview
        """
        preview_elements = []
 
        preview_elements.append(html.H2("Process Analysis Report", className="text-center"))
        preview_elements.append(html.P(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 
                                      className="text-center text-muted"))
        preview_elements.append(html.Hr())
        
        HTMLPreviewGenerator._add_text_section(preview_elements, "Executive Summary", 
                                             report_content.get("executive_summary", ""))
        
        HTMLPreviewGenerator._add_text_section(preview_elements, "Top Variables Analysis", 
                                             report_content.get("top_variables_analysis", ""))

        HTMLPreviewGenerator._add_text_section(preview_elements, "Impact Breakdown", 
                                             report_content.get("impact_breakdown", ""))
        
        HTMLPreviewGenerator._add_recommendations_section(preview_elements, 
                                                       report_content.get("recommendations", ""))
        
        if report_content.get("tables"):
            HTMLPreviewGenerator._add_tables_section(preview_elements, report_content.get("tables", []))
        
        return preview_elements
    
    @staticmethod
    def _add_text_section(preview_elements, title, content):
        """
        Add a text section to the preview
        
        Args:
            preview_elements (list): The list of preview elements
            title (str): The section title
            content (str): The section content
        """
        preview_elements.append(html.H3(title))
        preview_elements.append(html.P(content))
    
    @staticmethod
    def _add_recommendations_section(preview_elements, recommendations_text):
        """
        Add recommendations section to the preview with special formatting
        
        Args:
            preview_elements (list): The list of preview elements
            recommendations_text (str): The recommendations text
        """
        preview_elements.append(html.H3("Recommendations"))
        
        if recommendations_text:
            if re.search(r'\d+\.\s+\*\*.*?\*\*:', recommendations_text) or re.search(r'\d+\.\s+\*\*.*?\*\*', recommendations_text):
                recommendations_items = []
                
                items = re.split(r'(\d+\.\s+)', recommendations_text)
                for i in range(1, len(items), 2):
                    if i+1 < len(items):
                        item_num = items[i]
                        item_content = items[i+1].replace('**', '<b>').replace(':**', '</b>:').replace('**', '</b>')
                        recommendations_items.append(html.Li(
                            html.Span(item_num),
                            dcc.Markdown(item_content, dangerously_allow_html=True)
                        ))
                
                preview_elements.append(html.Ol(recommendations_items,"bullet-list"))
            else:
         
                lines = recommendations_text.split('\n')
                bullet_items = []
                
                for line in lines:
                    if line.strip():
                        html_content = line.replace('**', '<b>').replace(':**', '</b>:').replace('**', '</b>')
                        bullet_items.append(dcc.Markdown(html_content, dangerously_allow_html=True))
                
                if bullet_items:
                    preview_elements.append(html.Ul(bullet_items, className="bullet-list"))
                else:
                    preview_elements.append(dcc.Markdown(recommendations_text.replace('**', '<b>').replace(':**', '</b>:').replace('**', '</b>'), 
                                                       dangerously_allow_html=True))
        else:
            preview_elements.append(html.P("No recommendations available."))
    
    @staticmethod
    def _add_tables_section(preview_elements, tables_data):
        """
        Add tables section to the preview
        
        Args:
            preview_elements (list): The list of preview elements
            tables_data (list): The list of table data
        """
        preview_elements.append(html.H3("Data Tables"))
        
        for table_info in tables_data:
            preview_elements.append(html.H4(table_info.get("title", "")))
            preview_elements.append(html.P(table_info.get("description", "")))
            
            table_data = table_info.get("data", [])
            if table_data:
                header = html.Thead(html.Tr([html.Th(col) for col in table_data[0]]))
                
                rows = []
                for row_data in table_data[1:]:
                    rows.append(html.Tr([html.Td(cell) for cell in row_data]))
                
                body = html.Tbody(rows)
                
                preview_elements.append(
                    dbc.Table([header, body], bordered=True, striped=True, hover=True, responsive=True)
                )