import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State, ctx
from components.core.base_component import BaseComponent

class AIOTable(BaseComponent):
    def __init__(self, id_prefix, page_size=10):
        super().__init__(id_prefix)
        self.page_size = page_size
        
        self.table_id = self._create_component_id("table")
        self.pagination_id = self._create_component_id("pagination")
        self.page_size_id = self._create_component_id("page-size")
        self.current_page_id = self._create_component_id("current-page")
        self.total_pages_id = self._create_component_id("total-pages")
        self.prev_btn_id = self._create_component_id("prev-btn")
        self.next_btn_id = self._create_component_id("next-btn")
        self.current_page_store_id = self._create_component_id("current-page-store")
        self.data_store_id = self._create_component_id("full-data")
        
    def create_layout(self, columnDefs, rowData=None):
        if rowData is None:
            rowData = []
            
        total_pages = max(1, (len(rowData) + self.page_size - 1) // self.page_size)
        
        return html.Div([
            dag.AgGrid(
                id=self.table_id,
                columnDefs=columnDefs,
                rowData=rowData[:self.page_size] if rowData else [],
                dashGridOptions={
                    "pagination": False,
                    "domLayout": "autoHeight",
                },
                className="ag-theme-alpine",
                style={"width": "100%", "height": "auto"}
            ),
            
            html.Div([
                dbc.Row([
                    dbc.Col([
                        dbc.InputGroup([
                            dbc.InputGroupText("Page Size"),
                            dbc.Select(
                                id=self.page_size_id,
                                options=[
                                    {"label": str(size), "value": size} 
                                    for size in [5, 10, 25, 50, 100]
                                ],
                                value=self.page_size,
                                style={"width": "80px"}
                            )
                        ], size="sm"),
                    ], width="auto"),
                    
                    dbc.Col([
                        dbc.ButtonGroup([
                            dbc.Button("Previous", id=f"{self.id_prefix}-prev-btn", 
                                      disabled=True, color="primary", outline=True, size="sm"),
                            dbc.Button("Next", id=f"{self.id_prefix}-next-btn", 
                                      disabled=total_pages <= 1, color="primary", outline=True, size="sm"),
                        ]),
                    ], width="auto"),
                    
                    dbc.Col([
                        html.Div([
                            "Page ",
                            html.Span("1", id=self.current_page_id),
                            " of ",
                            html.Span(str(total_pages), id=self.total_pages_id)
                        ], className="d-flex align-items-center h-100 gap-1", style={"whiteSpace": "nowrap"})
                    ], width="auto"),
                ], className="justify-content-between align-items-center mt-2")
            ]),
            
            dcc.Store(id=f"{self.id_prefix}-full-data", data=rowData),
            dcc.Store(id=f"{self.id_prefix}-current-page-store", data=1),
        ])
    
    def register_callbacks(self, app):
        @app.callback(
            [Output(self.table_id, "rowData"),
             Output(self.current_page_store_id, "data"),
             Output(self.current_page_id, "children"),
             Output(self.total_pages_id, "children"),
             Output(self.prev_btn_id, "disabled"),
             Output(self.next_btn_id, "disabled")],
            [Input(self.prev_btn_id, "n_clicks"),
             Input(self.next_btn_id, "n_clicks"),
             Input(self.page_size_id, "value")],
            [State(self.current_page_store_id, "data"),
             State(self.data_store_id, "data")]
        )
        def update_table_pagination(prev_clicks, next_clicks, page_size, current_page, all_data):
            triggered_id = ctx.triggered_id if ctx.triggered_id else None
            
            try:
                page_size = int(page_size)
            except (TypeError, ValueError):
                page_size = 10
            
            if not all_data:
                all_data = []
            total_pages = max(1, (len(all_data) + page_size - 1) // page_size)
            
            if triggered_id == self.prev_btn_id and current_page > 1:
                current_page -= 1
            elif triggered_id == self.next_btn_id and current_page < total_pages:
                current_page += 1
            elif triggered_id == self.page_size_id:
                current_page = 1
            
            start_idx = (current_page - 1) * page_size
            end_idx = min(start_idx + page_size, len(all_data))
            
            current_data = all_data[start_idx:end_idx] if all_data else []
            
            prev_disabled = current_page <= 1
            next_disabled = current_page >= total_pages
            
            return current_data, current_page, str(current_page), str(total_pages), prev_disabled, next_disabled