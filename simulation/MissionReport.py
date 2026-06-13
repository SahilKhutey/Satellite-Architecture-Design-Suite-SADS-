from typing import Dict

class MissionReport:
    @staticmethod
    def generate_html_report(satellite_name: str, metrics: Dict[str, float]) -> str:
        rows = ""
        for k, v in metrics.items():
            rows += f"<tr><td>{k}</td><td>{v:.2f}</td></tr>"
        
        return f"""
        <html>
        <head><title>SADS Mission Report - {satellite_name}</title></head>
        <body>
            <h1>Mission Summary for {satellite_name}</h1>
            <table border="1">
                <tr><th>Metric</th><th>Value</th></tr>
                {rows}
            </table>
        </body>
        </html>
        """
