class BaseComponent:
    """
    Base component class that provides common functionality for all components.
    All components should inherit from this class to ensure consistent structure.
    """
    def __init__(self, id_prefix):
        """
        Initialize the base component with an ID prefix.
        
        Args:
            id_prefix (str): Prefix to use for all component IDs
        """
        self.id_prefix = id_prefix
        
    def _create_component_id(self, id_suffix):
        """
        Create a component ID using the prefix and suffix.
        
        Args:
            id_suffix (str): Suffix to append to the ID prefix
            
        Returns:
            str: The complete component ID
        """
        return f"{self.id_prefix}-{id_suffix}"
    
    def create_layout(self):
        """
        Create the layout for the component.
        This method should be implemented by all subclasses.
        
        Returns:
            dash.html.Div: The component layout
        """
        raise NotImplementedError("Subclasses must implement create_layout()")
    
    def register_callbacks(self, app):
        """
        Register callbacks for the component.
        This method should be implemented by all subclasses.
        
        Args:
            app (dash.Dash): The Dash application instance
        """
        raise NotImplementedError("Subclasses must implement register_callbacks()")