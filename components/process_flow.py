import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
from dash import html, dcc, Input, Output, State
import uuid
from components.core.base_component import BaseComponent
from components.utils.graph_style_service import GraphStyleService
from components.data.data_sharing_service import DataSharingService

cyto.load_extra_layouts()

class ProcessFlow(BaseComponent):
    """
    Process Flow Visualization component with node and edge tables.
    """
    def __init__(self, id_prefix):
        super().__init__(id_prefix)
        
        self.node_table_id = self._create_component_id("node-table")
        self.edge_table_id = self._create_component_id("edge-table")
        self.graph_id = self._create_component_id("graph")
        self.store_id = self._create_component_id("store")
        
        self.node_types = GraphStyleService.get_node_types()
        self.default_stylesheet = GraphStyleService.get_default_stylesheet()
        
    def _create_node_table(self):
        """Create the node table component"""
        return html.Div([
            html.H4("Nodes"),
            dag.AgGrid(
                id=self.node_table_id,
                columnDefs=[
                    {"headerName": "Name", "field": "name", "editable": True},
                    {"headerName": "Type", "field": "type", "editable": True, 
                     "cellEditor": "agSelectCellEditor",
                     "cellEditorParams": {
                         "values": self.node_types
                     }}
                ],
                rowData=[],
                dashGridOptions={
                    "rowSelection": "multiple",
                    "editType": "fullRow",
                    "domLayout": "autoHeight",
                },
                className="ag-theme-alpine",
                style={"width": "100%", "height": "300px"}
            ),
            dbc.Button("Add Node", id=f"{self.id_prefix}-add-node", 
                      color="primary", className="mt-2 me-2"),
            dbc.Button("Delete Selected", id=f"{self.id_prefix}-delete-node", 
                      color="danger", className="mt-2")
        ])
    
    def _create_edge_table(self):
        """Create the edge table component"""
        return html.Div([
            html.H4("Edges"),
            dag.AgGrid(
                id=self.edge_table_id,
                columnDefs=[
                    {"headerName": "Upstream Node", "field": "source", "editable": True,
                     "cellEditor": "agSelectCellEditor"},
                    {"headerName": "Downstream Node", "field": "target", "editable": True,
                     "cellEditor": "agSelectCellEditor"}
                ],
                rowData=[],
                dashGridOptions={
                    "rowSelection": "multiple",
                    "editType": "fullRow",
                    "domLayout": "autoHeight",
                },
                className="ag-theme-alpine",
                style={"width": "100%", "height": "300px"}
            ),
            dbc.Button("Add Edge", id=f"{self.id_prefix}-add-edge", 
                      color="primary", className="mt-2 me-2"),
            dbc.Button("Delete Selected", id=f"{self.id_prefix}-delete-edge", 
                      color="danger", className="mt-2")
        ])
    
    def _create_graph_visualization(self):
        """Create the graph visualization component"""
        return html.Div([
            html.H4("Process Flow Visualization", className="mt-4"),
            html.Div([
                cyto.Cytoscape(
                    id=self.graph_id,
                    layout={'name': 'dagre'},
                    style={'width': '100%', 'height': '500px'},
                    elements=[],
                    stylesheet=self.default_stylesheet
                )
            ], className="border rounded p-3")
        ])
    
    def create_layout(self):
        """Create the layout for the process flow component"""
        return html.Div([
            dbc.Row([
                dbc.Col(self._create_node_table(), width=6),
                dbc.Col(self._create_edge_table(), width=6)
            ]),
            
            dbc.Row([
                dbc.Col(self._create_graph_visualization())
            ]),
            
            dcc.Store(id=self.store_id, data={"nodes": [], "edges": []})
        ])
    
    def _update_store_data(self, store_data, key, value):
        """Helper method to update store data"""
        updated_data = store_data.copy()
        updated_data[key] = value
        return updated_data
    
    def _generate_unique_id(self):
        """Generate a unique ID for nodes and edges"""
        return str(uuid.uuid4())[:8]
    
    def _create_node_elements(self, nodes):
        """Create node elements for cytoscape graph"""
        return GraphStyleService.create_node_elements(nodes)
    
    def _create_edge_elements(self, edges, nodes):
        """Create edge elements for cytoscape graph"""
        return GraphStyleService.create_edge_elements(edges, nodes)
    
    def register_callbacks(self, app):
        """Register the callbacks for the process flow component"""
        
        DataSharingService.register_data_sharing_callback(
            app, 
            self.store_id, 
            "charts-store", 
            DataSharingService.transform_process_flow_to_chart_data
        )
        
        @app.callback(
            [Output(self.node_table_id, "rowData"),
             Output(self.store_id, "data", allow_duplicate=True)],
            [Input(f"{self.id_prefix}-add-node", "n_clicks")],
            [State(self.node_table_id, "rowData"),
             State(self.store_id, "data")],
            prevent_initial_call=True
        )
        def add_node(n_clicks, current_rows, store_data):
            if n_clicks is None:
                return current_rows, store_data
            
            new_id = self._generate_unique_id()
            new_node = {"id": new_id, "name": f"Node {len(current_rows) + 1}", "type": "type1"}
            
            updated_rows = current_rows + [new_node] if current_rows else [new_node]

            updated_store = self._update_store_data(store_data, "nodes", updated_rows)
            
            return updated_rows, updated_store
        
        @app.callback(
            [Output(self.node_table_id, "rowData", allow_duplicate=True),
             Output(self.edge_table_id, "rowData"),
             Output(self.store_id, "data", allow_duplicate=True)],
            [Input(f"{self.id_prefix}-delete-node", "n_clicks")],
            [State(self.node_table_id, "rowData"),
             State(self.node_table_id, "selectedRows"),
             State(self.edge_table_id, "rowData"),
             State(self.store_id, "data")],
            prevent_initial_call=True
        )
        def delete_node(n_clicks, current_nodes, selected_nodes, current_edges, store_data):
            if n_clicks is None or not selected_nodes:
                return current_nodes, current_edges, store_data
            
            selected_ids = [node["id"] for node in selected_nodes]
            selected_names = [node["name"] for node in selected_nodes]
            
            updated_nodes = [node for node in current_nodes if node["id"] not in selected_ids]
            
            updated_edges = [edge for edge in current_edges 
                            if edge["source"] not in selected_names and edge["target"] not in selected_names]

            updated_store = store_data.copy()
            updated_store["nodes"] = updated_nodes
            updated_store["edges"] = updated_edges
            
            return updated_nodes, updated_edges, updated_store
        
        @app.callback(
            [Output(self.edge_table_id, "rowData", allow_duplicate=True),
             Output(self.store_id, "data", allow_duplicate=True)],
            [Input(f"{self.id_prefix}-add-edge", "n_clicks")],
            [State(self.edge_table_id, "rowData"),
             State(self.node_table_id, "rowData"),
             State(self.node_table_id, "selectedRows"),
             State(self.store_id, "data")],
            prevent_initial_call=True
        )
        def add_edge(n_clicks, current_edges, nodes, selected_nodes, store_data):
            if n_clicks is None or not nodes or len(nodes) < 1:
                return current_edges, store_data
            
            source, target = self._determine_source_target(nodes, selected_nodes)
            
            new_edge = {"id": self._generate_unique_id(), "source": source, "target": target}
            
            updated_edges = current_edges + [new_edge] if current_edges else [new_edge]

            updated_store = self._update_store_data(store_data, "edges", updated_edges)
            
            return updated_edges, updated_store
        


        
        @app.callback(
            [Output(self.edge_table_id, "rowData", allow_duplicate=True),
             Output(self.store_id, "data", allow_duplicate=True)],
            [Input(f"{self.id_prefix}-delete-edge", "n_clicks")],
            [State(self.edge_table_id, "rowData"),
             State(self.edge_table_id, "selectedRows"),
             State(self.store_id, "data")],
            prevent_initial_call=True
        )
        def delete_edge(n_clicks, current_edges, selected_edges, store_data):
            if n_clicks is None or not selected_edges:
                return current_edges, store_data
            
            selected_ids = [edge["id"] for edge in selected_edges]
            
            updated_edges = [edge for edge in current_edges if edge["id"] not in selected_ids]
            
            updated_store = self._update_store_data(store_data, "edges", updated_edges)
            
            return updated_edges, updated_store
        
        @app.callback(
            Output(self.edge_table_id, "columnDefs"),
            [Input(self.node_table_id, "rowData")]
        )
        def update_edge_options(nodes):
            node_names = [node["name"] for node in nodes] if nodes else []
            
            return [
                {"headerName": "Upstream Node", "field": "source", "editable": True,
                 "cellEditor": "agSelectCellEditor",
                 "cellEditorParams": {"values": node_names}},
                {"headerName": "Downstream Node", "field": "target", "editable": True,
                 "cellEditor": "agSelectCellEditor",
                 "cellEditorParams": {"values": node_names}}
            ]
        
        @app.callback(
            [Output(self.edge_table_id, "rowData", allow_duplicate=True),
             Output(self.store_id, "data", allow_duplicate=True)],
            [Input(self.node_table_id, "cellValueChanged")],
            [State(self.node_table_id, "rowData"),
             State(self.edge_table_id, "rowData"),
             State(self.store_id, "data")],
            prevent_initial_call=True
        )
        def update_edge_node_names(cell_changed, nodes, edges, store_data):
            if cell_changed is None or not edges or cell_changed["colId"] != "name":
                return edges, store_data
            
            old_name = cell_changed["oldValue"]
            new_name = cell_changed["value"]

            updated_edges = self._update_edge_references(edges, old_name, new_name)
            
            updated_store = self._update_store_data(store_data, "edges", updated_edges)
            
            return updated_edges, updated_store
        
        @app.callback(
            Output(self.graph_id, "elements"),
            [Input(self.node_table_id, "rowData"),
             Input(self.edge_table_id, "rowData"),
             Input(self.edge_table_id, "cellValueChanged")]
        )
        def update_graph(nodes, edges, cell_changed):
            if not nodes:
                return []
            
            node_elements = self._create_node_elements(nodes)
            edge_elements = self._create_edge_elements(edges, nodes)
            
            return node_elements + edge_elements
            

    
    def _determine_source_target(self, nodes, selected_nodes):
        """Helper method to determine source and target nodes for a new edge"""
        if selected_nodes and len(selected_nodes) >= 2:
            source = selected_nodes[0]["name"]
            target = selected_nodes[1]["name"]
        elif selected_nodes and len(selected_nodes) == 1:

            source = selected_nodes[0]["name"]

            for node in nodes:
                if node["name"] != source:
                    target = node["name"]
                    break
            else:
                target = source
        else:

            if len(nodes) == 1:
                source = target = nodes[0]["name"]
            else:
                source = nodes[0]["name"]
                target = nodes[1]["name"]
        
        return source, target
    
    def _update_edge_references(self, edges, old_name, new_name):
        """Helper method to update edge references when a node name changes"""
        updated_edges = []
        for edge in edges:
            updated_edge = edge.copy()
            if updated_edge["source"] == old_name:
                updated_edge["source"] = new_name
            if updated_edge["target"] == old_name:
                updated_edge["target"] = new_name
            updated_edges.append(updated_edge)
        
        return updated_edges