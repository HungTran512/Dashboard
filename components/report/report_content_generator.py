import json
import re
from google import genai
import os

class ReportContentGenerator:
    """
    Class responsible for generating report content using LLM or fallback methods.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the report content generator
        
        Args:
            api_key (str, optional): The API key for the LLM service
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
    
    def generate_report_content(self, data):
        """
        Generate report content using Gemini LLM or fallback to simple report
        
        Args:
            data (dict): The data to generate the report from
            
        Returns:
            dict: The structured report content
        """
        if not self.api_key:
            return self.generate_simple_report(data)
        
        try:
            client = genai.Client(api_key=self.api_key)
            
            prompt = self._create_llm_prompt(data)
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            
            content = response.text
            
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*$', '', content)
            
            try:
                report_content = json.loads(content)
                if not isinstance(report_content, dict):
                    raise ValueError("Generated content is not a valid JSON object")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error parsing JSON content: {str(e)}")
                print(f"Raw content: {content}")
                report_content = {
                    "executive_summary": "Could not generate structured report. Here's the raw output:",
                    "top_variables_analysis": content,
                    "impact_breakdown": "",
                    "recommendations": "",
                    "tables": [],
                    "charts": []
                }
            
            return report_content
            
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return self.generate_simple_report(data)
    
    def _create_llm_prompt(self, data):
        """
        Create a prompt for the LLM
        
        Args:
            data (dict): The data to include in the prompt
            
        Returns:
            str: The formatted prompt
        """
        return f"""
        Generate a detailed report based on the following JSON data about process equipment variables and KPI results.
        
        The report should include:
        1. An executive summary of the findings
        2. Analysis of the top variables that impact the KPI
        3. Detailed breakdown of setpoint and condition impacts
        4. Recommendations for optimizing the process
        
        Here's the data:
        {json.dumps(data, indent=2)}
        
        Format the response as a JSON with the following structure:
        {{
            "executive_summary": "text...",
            "top_variables_analysis": "text...",
            "impact_breakdown": "text...",
            "recommendations": "text...",
            "tables": [
                {{
                    "title": "table title",
                    "description": "table description",
                    "data": [["header1", "header2"], ["row1col1", "row1col2"], ...]
                }}
            ],
            "charts": [
                {{
                    "title": "chart title",
                    "description": "chart description",
                    "type": "bar/pie/line",
                    "data": {{...chart data structure...}}
                }}
            ]
        }}
        
        Return ONLY the valid JSON object without any markdown formatting or code blocks.
        """
    
    def generate_simple_report(self, data):
        """
        Generate a simple report without using LLM
        
        Args:
            data (dict): The data to generate the report from
            
        Returns:
            dict: The structured report content
        """

        processed_data = data.get('data', data)

        main_summary = processed_data.get("main_summary_text", "Process Analysis Report")
        top_summary = processed_data.get("top_summary_text", "Top Variables Impact Analysis")
        
        top_impact = processed_data.get("top_impact", {})
        top_variables = processed_data.get("top_variables", [])
        
        simulated_data = processed_data.get("simulated_summary", {}).get("simulated_data", [])
        if not simulated_data and "simulated_summary" in data:
            simulated_data = data.get("simulated_summary", {}).get("simulated_data", [])

        exec_summary = f"""
        This report analyzes the impact of various process variables on the key performance indicator (KPI).
        The analysis is based on {len(simulated_data)} simulated scenarios.
        """
        
        top_vars_analysis = f"""
        The analysis identified {len(top_impact)} variables with significant impact on the KPI.
        The most influential variable is {list(top_impact.keys())[0] if top_impact else 'not available'} 
        with a weightage of {list(top_impact.values())[0] if top_impact else 'not available'}.
        """
        
        impact_breakdown = f"""
        The setpoint variables that impact the KPI include:
        {', '.join([item.get('setpoint', '') for item in processed_data.get('setpoint_impact_summary', [])])}
        
        The condition variables that impact the KPI include:
        {', '.join([item.get('condition', '') for item in processed_data.get('condition_impact_summary', [])])}
        """
        
        recommendations = """
        Based on the analysis, we recommend:
        1. Focus on optimizing the top impact variables
        2. Monitor the KPI closely when adjusting these variables
        3. Consider further experiments to validate the findings
        """
 
        tables = [
            {
                "title": "Top Impact Variables",
                "description": "Variables with the highest impact on the KPI",
                "data": [
                    ["Variable", "Impact Weightage"],
                    *[[k, str(v)] for k, v in top_impact.items()]
                ]
            }
        ]

        return {
            "executive_summary": exec_summary,
            "top_variables_analysis": top_vars_analysis,
            "impact_breakdown": impact_breakdown,
            "recommendations": recommendations,
            "tables": tables,
        }