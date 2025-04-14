import dash
from dash import dcc, Input, Output

class DataSharingService:
    """
    Service class for standardizing data sharing between components.
    This follows the Single Responsibility Principle by focusing solely on data sharing.
    """
    
    @staticmethod
    def create_store(id_prefix, store_type="memory", initial_data=None):
        """
        Create a dcc.Store component with standardized configuration
        
        Args:
            id_prefix (str): The ID prefix for the store
            store_type (str): The type of store ('memory', 'local', or 'session')
            initial_data (dict, optional): Initial data for the store
            
        Returns:
            dcc.Store: The configured store component
        """
        return dcc.Store(
            id=id_prefix,
            storage_type=store_type,
            data=initial_data
        )
    
    @staticmethod
    def register_data_sharing_callback(app, source_store_id, target_store_id, transform_func=None):
        """
        Register a callback to share data between two stores
        
        Args:
            app (dash.Dash): The Dash application instance
            source_store_id (str): The ID of the source store
            target_store_id (str): The ID of the target store
            transform_func (callable, optional): Function to transform data before sharing
        """
        @app.callback(
            Output(target_store_id, "data", allow_duplicate=True),
            [Input(source_store_id, "data")],
            prevent_initial_call=True
        )
        def share_data(source_data):
            if source_data is None:
                return dash.no_update
            
            if transform_func is not None:
                return transform_func(source_data)
            
            return source_data
    
    @staticmethod
    def transform_process_flow_to_chart_data(process_flow_data):
        """
        Transform process flow data to chart-compatible format
        
        Args:
            process_flow_data (dict): The process flow data
            
        Returns:
            dict: Chart-compatible data
        """
        if not process_flow_data or not isinstance(process_flow_data, dict):
            return None
            
        nodes = process_flow_data.get("nodes", [])
        edges = process_flow_data.get("edges", [])
        
        if not nodes:
            return None
            
        node_types = {}
        for node in nodes:
            node_type = node.get("type", "unknown")
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        connection_counts = {}
        for node in nodes:
            node_name = node.get("name", "")
            outgoing = sum(1 for edge in edges if edge.get("source") == node_name)
            incoming = sum(1 for edge in edges if edge.get("target") == node_name)
            connection_counts[node_name] = {"outgoing": outgoing, "incoming": incoming}
        
        chart_data = {
            "charts": [
                {
                    "title": "Node Type Distribution",
                    "description": "Distribution of node types in the process flow",
                    "type": "pie",
                    "data": {
                        "labels": list(node_types.keys()),
                        "datasets": [{
                            "data": list(node_types.values())
                        }]
                    }
                },
                {
                    "title": "Node Connections",
                    "description": "Number of incoming and outgoing connections per node",
                    "type": "bar",
                    "data": {
                        "labels": list(connection_counts.keys()),
                        "datasets": [
                            {
                                "label": "Outgoing Connections",
                                "data": [data["outgoing"] for data in connection_counts.values()]
                            },
                            {
                                "label": "Incoming Connections",
                                "data": [data["incoming"] for data in connection_counts.values()]
                            }
                        ]
                    }
                }
            ],
            "process_flow_summary": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "node_types": node_types
            }
        }
        
        return chart_data