import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
import dash_bootstrap_components as dbc
from components.utils.utils import DataProcessor, ErrorHandler

class ChartDataProcessor:
    """
    Class for processing chart data.
    """
    @staticmethod
    def process_chart_data(data):
        if data is None:
            return []
        
        charts = []
        charts.append(html.H3("Data Visualization Dashboard", className="mt-4"))
        charts.append(html.P("Interactive charts and analytics based on the uploaded JSON data."))
        
        try:

            data = DataProcessor.extract_nested_data(data)
            

            if "charts" in data and isinstance(data["charts"], list):
                charts.extend(ChartDataProcessor._process_llm_charts(data["charts"]))
            

            if "tables" in data and isinstance(data["tables"], list):
                charts.extend(ChartDataProcessor._process_llm_tables(data["tables"]))
            else:

                charts.extend(ChartDataProcessor._process_traditional_format(data))
            

            charts.extend(ChartDataProcessor._process_text_sections(data))
            
        except Exception as e:
            error_components = ErrorHandler.create_error_message(e, include_traceback=True)
            charts.extend(error_components)
        

        chart_count = sum(1 for item in charts if isinstance(item, dcc.Graph) or isinstance(item, dbc.Table))
        if chart_count == 0:
            charts.append(html.Div(
                "No charts could be generated from the provided data. Please check the JSON format.",
                className="alert alert-warning mt-4"
            ))
            
        return charts
    
    @staticmethod
    def _process_llm_charts(charts_data):
        """
        Process charts data in LLM-generated format.

        Args:
            charts_data (list): List of chart data objects

        Returns:
            list: List of chart components
        """
        components = []
        
        for chart_info in charts_data:
            chart_type = chart_info.get("type", "")
            chart_data = chart_info.get("data", {})
            title = chart_info.get("title", "")
            description = chart_info.get("description", "")
            
            components.append(html.H4(title, className="mt-4"))
            components.append(html.P(description))
            
            if chart_type == "bar":
                components.append(ChartDataProcessor._create_bar_chart(chart_data, title))
            elif chart_type == "pie":
                components.append(ChartDataProcessor._create_pie_chart(chart_data, title))
            elif chart_type == "line":
                components.append(ChartDataProcessor._create_line_chart(chart_data, title))
            elif chart_type == "scatter":
                components.append(ChartDataProcessor._create_scatter_chart(chart_data, title))
        
        return components
    
    @staticmethod
    def _create_bar_chart(chart_data, title):
        """
        Create a bar chart from the provided data.
        
        Args:
            chart_data (dict): The chart data
            title (str): The chart title
            
        Returns:
            dcc.Graph: The bar chart component
        """
        if "labels" in chart_data and "datasets" in chart_data:
            labels = chart_data.get("labels", [])
            values = chart_data.get("datasets", [{}])[0].get("data", [])
            fig = px.bar(
                x=labels,
                y=values,
                labels={"x": "Variable", "y": "Value"},
                title=title
            )
            fig.update_layout(
                xaxis_title="Variable",
                yaxis_title="Value",
                plot_bgcolor="white",
                height=400
            )
            return dcc.Graph(figure=fig)
        return html.Div("Insufficient data for bar chart", className="text-warning")
    
    @staticmethod
    def _create_pie_chart(chart_data, title):
        """
        Create a pie chart from the provided data.
        
        Args:
            chart_data (dict): The chart data
            title (str): The chart title
            
        Returns:
            dcc.Graph: The pie chart component
        """
        if "labels" in chart_data and "datasets" in chart_data:
            labels = chart_data.get("labels", [])
            values = chart_data.get("datasets", [{}])[0].get("data", [])
            
            if len(labels) > len(values):
                labels = labels[:len(values)]
            elif len(values) > len(labels):
                values = values[:len(labels)]
                
            fig = px.pie(
                names=labels,
                values=values,
                title=title,
                hole=0.4
            )
            fig.update_layout(
                legend_title="Variables",
                height=500
            )
            return dcc.Graph(figure=fig)
        return html.Div("Insufficient data for pie chart", className="text-warning")
    
    @staticmethod
    def _create_line_chart(chart_data, title):
        """
        Create a line chart from the provided data.
        
        Args:
            chart_data (dict): The chart data
            title (str): The chart title
            
        Returns:
            dcc.Graph: The line chart component
        """
        if "labels" in chart_data and "datasets" in chart_data:
            labels = chart_data.get("labels", [])
            values = chart_data.get("datasets", [{}])[0].get("data", [])
            fig = px.line(
                x=labels,
                y=values,
                markers=True,
                labels={"x": "Scenario", "y": chart_data.get("datasets", [{}])[0].get("label", "Value")},
                title=title
            )
            fig.update_layout(
                xaxis_title="Scenario",
                yaxis_title="Value",
                plot_bgcolor="white",
                height=400
            )
            return dcc.Graph(figure=fig)
        return html.Div("Insufficient data for line chart", className="text-warning")
    
    @staticmethod
    def _create_scatter_chart(chart_data, title):
        """
        Create a scatter chart from the provided data.
        
        Args:
            chart_data (dict): The chart data
            title (str): The chart title
            
        Returns:
            dcc.Graph: The scatter chart component
        """
        if "datasets" in chart_data:
            dataset = chart_data.get("datasets", [{}])[0]
            scatter_data = dataset.get("data", [])
            
            if scatter_data:
                x_values = [point.get("x", 0) for point in scatter_data]
                y_values = [point.get("y", 0) for point in scatter_data]
                
                fig = px.scatter(
                    x=x_values,
                    y=y_values,
                    labels={
                        "x": chart_data.get("xlabel", "X Value"),
                        "y": chart_data.get("ylabel", "Y Value")
                    },
                    title=title
                )
                fig.update_layout(
                    xaxis_title=chart_data.get("xlabel", "X Value"),
                    yaxis_title=chart_data.get("ylabel", "Y Value"),
                    plot_bgcolor="white",
                    height=500
                )
                
                if len(x_values) > 1:
                    fig.update_traces(marker=dict(size=10))
                    fig = px.scatter(
                        x=x_values,
                        y=y_values,
                        trendline="ols",
                        labels={
                            "x": chart_data.get("xlabel", "X Value"),
                            "y": chart_data.get("ylabel", "Y Value")
                        },
                        title=title
                    )
                
                return dcc.Graph(figure=fig)
        return html.Div("Insufficient data for scatter chart", className="text-warning")
    
    @staticmethod
    def _process_llm_tables(tables_data):
        """
        Process tables data in LLM-generated format.
        
        Args:
            tables_data (list): List of table data objects
            
        Returns:
            list: List of table components
        """
        components = []
        
        for table_info in tables_data:
            title = table_info.get("title", "")
            description = table_info.get("description", "")
            table_data = table_info.get("data", [])
            
            if table_data:
                components.append(html.H4(title, className="mt-4"))
                components.append(html.P(description))
                
                header = table_data[0] if table_data else []
                rows = table_data[1:] if len(table_data) > 1 else []
                
                table = dbc.Table(
                    [
                        html.Thead(html.Tr([html.Th(col) for col in header])),
                        html.Tbody([
                            html.Tr([html.Td(cell) for cell in row])
                            for row in rows
                        ])
                    ],
                    bordered=True,
                    hover=True,
                    striped=True,
                    className="mt-3"
                )
                components.append(table)
        
        return components
    
    @staticmethod
    def _process_traditional_format(data):
        """
        Process data in traditional format (like mock_results.json).
        
        Args:
            data (dict): The data to process
            
        Returns:
            list: List of chart components
        """
        components = []
        
        top_impact = data.get("top_impact", {})
        if top_impact:
            components.append(html.H4("Top Impact Variables", className="mt-4"))
            components.append(html.P("Variables with the highest impact on the KPI."))
            
            fig = px.bar(
                x=list(top_impact.keys()),
                y=list(top_impact.values()),
                labels={"x": "Variable", "y": "Impact Weightage"},
                title="Top Impact Variables"
            )
            fig.update_layout(
                xaxis_title="Variable",
                yaxis_title="Impact Weightage",
                plot_bgcolor="white",
                height=400
            )
            components.append(dcc.Graph(figure=fig))
        
        setpoint_impact = data.get("setpoint_impact_summary", [])
        if setpoint_impact:
            components.append(html.H4("Setpoint Impact Distribution", className="mt-4"))
            components.append(html.P("Distribution of impact across different setpoint variables."))
            
            labels = [item.get("setpoint", "") for item in setpoint_impact]
            values = [item.get("weightage", 0) for item in setpoint_impact]
            
            fig = px.pie(
                names=labels,
                values=values,
                title="Setpoint Impact Distribution",
                hole=0.4
            )
            fig.update_layout(
                legend_title="Setpoint Variables",
                height=500
            )
            components.append(dcc.Graph(figure=fig))
        
        simulated_data = data.get("simulated_summary", {}).get("simulated_data", [])
        if simulated_data:
            components.append(html.H4("KPI Values Across Scenarios", className="mt-4"))
            components.append(html.P("Comparison of KPI values for different scenarios."))
            
            sorted_data = sorted(simulated_data, key=lambda x: x.get("kpi_value", 0), reverse=True)
            scenarios = [item.get("scenario", "") for item in sorted_data]
            kpi_values = [item.get("kpi_value", 0) for item in sorted_data]
            
            fig = px.line(
                x=scenarios,
                y=kpi_values,
                markers=True,
                labels={"x": "Scenario", "y": "KPI Value"},
                title="KPI Values Across Scenarios"
            )
            fig.update_layout(
                xaxis_title="Scenario",
                yaxis_title="KPI Value",
                plot_bgcolor="white",
                height=400
            )
            components.append(dcc.Graph(figure=fig))
        
        return components
    
    @staticmethod
    def _process_text_sections(data):
        """
        Process text sections from the data.
        
        Args:
            data (dict): The data containing text sections
            
        Returns:
            list: List of text section components
        """
        components = []
        
        for section in ["executive_summary", "top_variables_analysis", "impact_breakdown", "recommendations"]:
            if section in data and data[section]:
                section_title = section.replace("_", " ").title()
                components.append(html.H4(section_title, className="mt-4"))
                paragraphs = data[section].split("\n")
                for paragraph in paragraphs:
                    if paragraph.strip():
                        components.append(html.P(paragraph))
        
        return components