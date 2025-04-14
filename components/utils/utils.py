import base64
import json
from dash import html

class FileUtils:
    """
    Utility class for file operations used across components.
    """
    @staticmethod
    def parse_uploaded_json(contents, filename):
        """
        Parse uploaded JSON file contents.
        
        Args:
            contents (str): The file contents as a base64 encoded string
            filename (str): The name of the uploaded file
            
        Returns:
            tuple: (json_data, status_element) where json_data is the parsed JSON data
                  and status_element is a Dash HTML component with status message
        """
        if contents is None:
            return None, ""
        
        if not filename.endswith('.json'):
            return None, html.Div("Please upload a JSON file", className="text-danger")
        
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        try:
            json_data = json.loads(decoded.decode('utf-8'))
            return json_data, html.Div("JSON file uploaded successfully", className="text-success")
        except Exception as e:
            return None, html.Div(f"Error parsing JSON: {str(e)}", className="text-danger")


class UIComponents:
    @staticmethod
    def create_upload_area(upload_id, text="Drag and Drop or Select JSON File"):
        from dash import dcc
        
        return dcc.Upload(
            id=upload_id,
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select JSON File')
            ]),
            style={
                'width': '100%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '10px 0'
            },
            multiple=False
        )


class DataProcessor:
    @staticmethod
    def extract_nested_data(data):
        
        if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
            return data["data"]
        return data


class ErrorHandler:
    @staticmethod
    def create_error_message(error, include_traceback=False):
        """
        Create a standardized error message component.
        
        Args:
            error (Exception): The exception that occurred
            include_traceback (bool): Whether to include the full traceback
            
        Returns:
            list: A list of Dash components representing the error
        """
        error_components = [html.Div(f"Error: {str(error)}", className="text-danger")]
        
        if include_traceback:
            import traceback
            error_details = traceback.format_exc()
            error_components.append(
                html.Pre(error_details, 
                         style={"background": "#f8f9fa", "padding": "15px", "border-radius": "5px"})
            )
            
        return error_components