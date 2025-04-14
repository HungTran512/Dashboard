import dash_cytoscape as cyto

class GraphStyleService:
    """
    Service class for standardizing graph styling across components.
    This follows the Single Responsibility Principle by focusing solely on graph styling.
    """
    
    @staticmethod
    def get_default_stylesheet():
        """
        Get the default stylesheet for Cytoscape graphs
        
        Returns:
            list: The default stylesheet
        """
        return [
            {
                'selector': 'node',
                'style': {
                    'label': 'data(label)',
                    'background-color': '#11479e',
                    'color': 'white',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'width': '80px',
                    'height': '80px'
                }
            },
            {
                'selector': 'node[type="type1"]',
                'style': {
                    'background-color': '#11479e'
                }
            },
            {
                'selector': 'node[type="type2"]',
                'style': {
                    'background-color': '#7c4dff'
                }
            },
            {
                'selector': 'node[type="type3"]',
                'style': {
                    'background-color': '#00bcd4'
                }
            },
            {
                'selector': 'edge',
                'style': {
                    'width': 3,
                    'line-color': '#ccc',
                    'target-arrow-color': '#ccc',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            }
        ]
    
    @staticmethod
    def get_node_types():
        """
        Get the standard node types
        
        Returns:
            list: The standard node types
        """
        return ["type1", "type2", "type3"]
    
    @staticmethod
    def create_node_elements(nodes):
        """
        Create node elements for cytoscape graph
        
        Args:
            nodes (list): The list of node data
            
        Returns:
            list: The node elements
        """
        return [
            {
                "data": {
                    "id": node["id"],
                    "label": node["name"],
                    "type": node["type"]
                }
            }
            for node in nodes
        ]
    
    @staticmethod
    def create_edge_elements(edges, nodes):
        """
        Create edge elements for cytoscape graph
        
        Args:
            edges (list): The list of edge data
            nodes (list): The list of node data
            
        Returns:
            list: The edge elements
        """
        if not edges:
            return []
            
        name_to_id = {node["name"]: node["id"] for node in nodes}
        
        edge_elements = []
        for edge in edges:
            if edge["source"] in name_to_id and edge["target"] in name_to_id:
                edge_elements.append({
                    "data": {
                        "id": edge["id"],
                        "source": name_to_id[edge["source"]],
                        "target": name_to_id[edge["target"]]
                    }
                })
                
        return edge_elements