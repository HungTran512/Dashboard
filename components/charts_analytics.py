import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
from components.utils.utils import FileUtils, UIComponents
from components.core.base_component import BaseComponent
from components.data.chart_data_processor import ChartDataProcessor

class ChartsAnalytics(BaseComponent):
    """
    Charts and Analytics component for visualizing data from JSON.
    """
    def __init__(self, id_prefix):
        super().__init__(id_prefix)
        
        self.upload_id = self._create_component_id("upload")
        self.store_id = self._create_component_id("store")
        self.charts_container_id = self._create_component_id("charts-container")
        self.status_id = self._create_component_id("status")
        self.loading_id = self._create_component_id("loading")
        
    def create_layout(self):
        """Create the layout for the charts and analytics component"""
        return html.Div([
            dbc.Modal(
                [
                    dbc.ModalHeader("Processing"),
                    dbc.ModalBody([
                        html.Div([
                            dbc.Spinner(size="lg", color="primary"),
                            html.P("Loading charts, please wait...", className="mt-3")
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
                    html.H4("Charts and Analytics"),
                    UIComponents.create_upload_area(self.upload_id),
                    html.Div(id=self.status_id, className="mt-2"),
                ], width=12)
            ]),
            
            dbc.Row([
                dbc.Col([
                    html.Div(id=self.charts_container_id)
                ], width=12)
            ]),
            
            dcc.Store(id=self.store_id)
        ])
    
    def register_callbacks(self, app):
        """Register the callbacks for the charts and analytics component"""
        
        @app.callback(
            [Output(self.store_id, "data"),
             Output(self.status_id, "children"),
             Output(self.loading_id, "is_open")],
            [Input(self.upload_id, "contents")],
            [State(self.upload_id, "filename")]
        )
        def upload_json(contents, filename):
            if contents is None:
                return None, "", False
            
            json_data, status_element = FileUtils.parse_uploaded_json(contents, filename)
            return json_data, status_element, True
        

        @app.callback(
            [Output(self.charts_container_id, "children"),
             Output(self.loading_id, "is_open", allow_duplicate=True)],
            [Input(self.store_id, "data"),
             Input("report-gen-store", "data")],
            prevent_initial_call=True
        )
        def generate_charts(data, report_data):
            """Generate charts based on the uploaded JSON data"""
            if data is None and report_data is None:
                return [], False
                
            if report_data is not None:
                data = report_data
            
            charts = ChartDataProcessor.process_chart_data(data)
            
            return charts, False
