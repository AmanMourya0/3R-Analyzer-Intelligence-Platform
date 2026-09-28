# Reporting & Exports

## API Endpoints
All exports respect the current active AST filter from the UI.
* `GET /api/export/tickets/csv`: Dumps raw tickets.
* `GET /api/export/clusters/csv`: Dumps cluster summaries.
* `GET /api/export/summary/csv`: Dumps high-level 3R KPIs.
* `GET /api/export/executive-report/pdf`: Generates a fully formatted, leadership-ready PDF using `reportlab`.

## Implementation Details
The backend streams these exports with correct `Content-Disposition` attachment headers and `text/csv` or `application/pdf` media types.
