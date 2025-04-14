import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, State

from components.utils.utils import FileUtils, UIComponents
from components.core.base_component import BaseComponent

class FileUploadHandler(BaseComponent):
    """
    Reusable component for handling file uploads with standardized callbacks.
    This component follows the Single Responsibility Principle by focusing solely on file upload handling.
    """
    def __init__(self, id_prefix, file_types=None, upload_text=None):
        """
        Initialize the file upload handler component.
        
        Args:
            id_prefix (str): Prefix for component IDs
            file_types (list, optional): List of accepted file extensions (e.g., ['.json', '.csv'])
            upload_text (str, optional): Custom text for the upload area
        """
        super().__init__(id_prefix)
        
        self.file_types = file_types or ['.json']
        self.upload_text = upload_text or f"Drag and Drop or Select {', '.join(self.file_types)} File"
        
        self.upload_id = self._create_component_id("upload")
        self.store_id = self._create_component_id("store")
        self.status_id = self._create_component_id("status")
    
    def create_layout(self, show_status=True):
        """
        Create the layout for the file upload component
        
        Args:
            show_status (bool): Whether to show the status message
            
        Returns:
            dash.html.Div: The component layout
        """
        components = [
            UIComponents.create_upload_area(self.upload_id, self.upload_text)
        ]
        
        if show_status:
            components.append(html.Div(id=self.status_id, className="mt-2"))
            
        components.append(dcc.Store(id=self.store_id))
        
        return html.Div(components)
    
    def register_callbacks(self, app):
        """
        Register the callbacks for the file upload component
        
        Args:
            app (dash.Dash): The Dash application instance
        """
        @app.callback(
            [Output(self.store_id, "data"),
             Output(self.status_id, "children")],
            [Input(self.upload_id, "contents")],
            [State(self.upload_id, "filename")]
        )
        def upload_file(contents, filename):
            """
            Parse the uploaded file and update the store and status
            
            Args:
                contents (str): The file contents
                filename (str): The filename
                
            Returns:
                tuple: (data, status_element)
            """
            if contents is None:
                return None, ""
            
            valid_extension = any(filename.endswith(ext) for ext in self.file_types) if filename else False
            
            if not valid_extension:
                return None, html.Div(f"Please upload a {', '.join(self.file_types)} file", className="text-danger")
            
            if filename.endswith('.json'):
                return FileUtils.parse_uploaded_json(contents, filename)
            

            return None, html.Div(f"File type not supported yet: {filename}", className="text-warning")
    
    def get_upload_id(self):
        """
        Get the upload component ID
        
        Returns:
            str: The upload component ID
        """
        return self.upload_id
    
    def get_store_id(self):
        """
        Get the store component ID
        
        Returns:
            str: The store component ID
        """
        return self.store_id
    
    def get_status_id(self):
        """
        Get the status component ID
        
        Returns:
            str: The status component ID
        """
        return self.status_id