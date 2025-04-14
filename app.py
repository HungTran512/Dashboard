import dash
from dash import html, Input, Output
import dash_bootstrap_components as dbc
from components.table_component import AIOTable
from components.process_flow import ProcessFlow
from components.report_generator import ReportGenerator
from components.charts_analytics import ChartsAnalytics


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server 

aio_table = AIOTable(id_prefix="demo-table")
process_flow = ProcessFlow(id_prefix="process-flow")
report_generator = ReportGenerator(id_prefix="report-gen")
charts_analytics = ChartsAnalytics(id_prefix="charts")

app.layout = dbc.Container([
    html.H1("Process First LLC Dashboard", className="my-4"),
    
    dbc.Tabs([
        dbc.Tab([
            html.Div([
                html.H3("Reusable Paginated Table Demo", className="my-3"),
                html.P("This is a demonstration of the reusable All-in-One paginated table component."),
                
                aio_table.create_layout(
                    columnDefs=[
                        {"headerName": "ID", "field": "id"},
                        {"headerName": "Name", "field": "name"},
                        {"headerName": "Value", "field": "value"},
                        {"headerName": "Type", "field": "type"}
                    ],
                    rowData=[
                        {"id": i, "name": f"Item {i}", "value": i * 10, "type": "Type A" if i % 2 == 0 else "Type B"}
                        for i in range(1, 100)
                    ]
                )
            ], className="p-3")
        ], label="Paginated Table"),
        
        dbc.Tab([
            html.Div([
                process_flow.create_layout()
            ], className="p-3")
        ], label="Process Flow Visualization"),
        
        dbc.Tab([
            html.Div([
                report_generator.create_layout()
            ], className="p-3")
        ], label="Report Generation"),
        
        dbc.Tab([
            html.Div([
                charts_analytics.create_layout()
            ], className="p-3")
        ], label="Charts & Analytics")
    ], className="mt-4")
], fluid=True)

aio_table.register_callbacks(app)
process_flow.register_callbacks(app)
report_generator.register_callbacks(app)
charts_analytics.register_callbacks(app)


@app.callback(
    Output("charts-store", "data", allow_duplicate=True),
    [Input("report-gen-store", "data")],
    prevent_initial_call=True
)
def pass_report_data_to_charts(report_data):
    if report_data is None:
        return dash.no_update
    return report_data

if __name__ == "__main__":
    app.run_server(debug=True)