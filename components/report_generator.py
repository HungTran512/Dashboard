import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State
import base64
from dotenv import load_dotenv
from components.utils.utils import FileUtils, UIComponents
from components.core.base_component import BaseComponent
from components.pdf.pdf_generator import PDFGenerator
from components.report.report_content_generator import ReportContentGenerator
from components.ui.html_preview_generator import HTMLPreviewGenerator

load_dotenv()

class ReportGenerator(BaseComponent):
    """
    Report Generator component using Gemini LLM to generate PDF reports from JSON data.
    """
    def __init__(self, id_prefix, api_key=None):
        super().__init__(id_prefix)
        
        self.content_generator = ReportContentGenerator(api_key)
        
        self.upload_id = self._create_component_id("upload")
        self.generate_btn_id = self._create_component_id("generate-btn")
        self.download_id = self._create_component_id("download")
        self.preview_id = self._create_component_id("preview")
        self.store_id = self._create_component_id("store")
        self.status_id = self._create_component_id("status")
        self.loading_id = self._create_component_id("loading")
        
    def create_layout(self):
        """Create the layout for the report generator component"""
        return html.Div([

            dbc.Modal(
                [
                    dbc.ModalHeader("Processing"),
                    dbc.ModalBody([
                        html.Div([
                            dbc.Spinner(size="lg", color="primary"),
                            html.P("Generating report, please wait...", className="mt-3")
                        ], className="text-center")
                    ]),
                ],
                id=self.loading_id,
                is_open=False,
                backdrop="static",
                keyboard=False,
                centered=True,
            ),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Report Generation"),
                    UIComponents.create_upload_area(self.upload_id),
                    dbc.Button("Generate Report", id=self.generate_btn_id, 
                              color="primary", className="mt-2", disabled=True),
                    html.Div(id=self.status_id, className="mt-2"),
                    html.Div([
                        html.A(
                            dbc.Button("Download PDF", color="success", className="mt-2"),
                            id=self.download_id,
                            download="process_report.pdf",
                            href="",
                            target="_blank",
                            style={"display": "none"}
                        )
                    ])
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.H4("Report Preview", className="mt-4"),
                    html.Div(id=self.preview_id, className="border rounded p-3", 
                            style={"minHeight": "500px"})
                ], width=12)
            ]),
            
     
            dcc.Store(id=self.store_id)
        ])
    
    def register_callbacks(self, app):
        """Register the callbacks for the report generator component"""
        
        @app.callback(
            [Output(self.store_id, "data"),
             Output(self.generate_btn_id, "disabled"),
             Output(self.status_id, "children")],
            [Input(self.upload_id, "contents")],
            [State(self.upload_id, "filename")]
        )
        def upload_json(contents, filename):
            if contents is None:
                return None, True, ""
            
            json_data, status_element = FileUtils.parse_uploaded_json(contents, filename)
            return json_data, json_data is None, status_element
        
       
        @app.callback(
            Output(self.loading_id, "is_open"),
            [Input(self.generate_btn_id, "n_clicks")],
            [State(self.store_id, "data")],
            prevent_initial_call=True
        )
        def show_loading_modal(n_clicks, data):
            if n_clicks is None or data is None:
                return False
            return True
        

        @app.callback(
            [Output(self.download_id, "href"),
             Output(self.download_id, "style"),
             Output(self.preview_id, "children"),
             Output(self.status_id, "children", allow_duplicate=True),
             Output(self.loading_id, "is_open", allow_duplicate=True)],
            [Input(self.generate_btn_id, "n_clicks")],
            [State(self.store_id, "data")],
            prevent_initial_call=True
        )
        def generate_report(n_clicks, data):
            if n_clicks is None or data is None:
                return "", {"display": "none"}, "", "", False
            
            try:
     
                report_content = self.generate_report_content(data)  

                pdf_buffer = self.create_pdf(data, report_content)
                
                pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
                href = f"data:application/pdf;base64,{pdf_base64}"
                
                preview_content = self.create_preview_content(data, report_content)
                
                return href, {"display": "block"}, preview_content, html.Div("Report generated successfully", className="text-success"), False
            
            except Exception as e:
                return "", {"display": "none"}, "", html.Div(f"Error generating report: {str(e)}", className="text-danger"), False
    
    def generate_report_content(self, data):
        """Generate report content using the content generator
        
        Args:
            data (dict): The data to generate the report from
            
        Returns:
            dict: The structured report content
        """
        return self.content_generator.generate_report_content(data)
    
    def create_pdf(self, data, report_content):
        """Create a PDF report from the data and report content
        
        Args:
            data (dict): The data used to generate the report
            report_content (dict): The structured content for the report
            
        Returns:
            BytesIO: A buffer containing the generated PDF
        """
        return PDFGenerator.create_pdf(data, report_content)
    
    def create_preview_content(self, data, report_content):
        """Create HTML preview content for the report
        
        Args:
            data (dict): The data used to generate the report
            report_content (dict): The structured content for the report
            
        Returns:
            list: A list of Dash HTML components representing the preview
        """
        return HTMLPreviewGenerator.create_preview_content(data, report_content)