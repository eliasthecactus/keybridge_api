from models import Logs
from sqlalchemy import or_, cast, String
from datetime import datetime
from services.response_service import make_response

def get_logs_service(params):
    """Retrieve logs with filtering, sorting, and pagination."""
    try:
        # Extract parameters
        level = params.get('level')
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        page = int(params.get('page', 1))
        per_page = int(params.get('per_page', 10))
        sort_field = params.get('sort_field', 'timestamp')
        sort_order = params.get('sort_order', 'asc')
        search_string = params.get('search_string', '')

        # Validate pagination
        if page < 1 or per_page < 1:
            return {"code": 40, "message": "Invalid page or per_page value", "status_code": 400}

        # Start building query
        query = Logs.query

        # Apply filters
        if level:
            query = query.filter(Logs.level.ilike(f"%{level}%"))  # Case-insensitive partial match

        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(Logs.timestamp >= start_date_obj)
            except ValueError:
                return {"code": 40, "message": "Invalid start_date format. Use YYYY-MM-DD.", "status_code": 400}

        if end_date:
            try:
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(Logs.timestamp <= end_date_obj)
            except ValueError:
                return {"code": 40, "message": "Invalid end_date format. Use YYYY-MM-DD.", "status_code": 400}
            
        if search_string:
            query = query.filter(
                or_(
                    Logs.level.ilike(f"%{search_string}%"),
                    Logs.message.ilike(f"%{search_string}%"),
                    cast(Logs.data, String).ilike(f"%{search_string}%")
                )
            )

        # Apply sorting
        sort_column = getattr(Logs, sort_field, Logs.timestamp)  # Fallback to `timestamp`
        query = query.order_by(sort_column.asc() if sort_order.lower() == 'asc' else sort_column.desc())

        # Paginate results
        paginated_logs = query.paginate(page=page, per_page=per_page)

        # Format logs for response
        logs = [
            {
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "level": log.level,
                "message": log.message,
                "data": log.data
            }
            for log in paginated_logs.items
        ]

        return {
            "code": 0,
            "message": "Logs retrieved successfully",
            "status_code": 200,
            "data": {
                "logs": logs,
                "total": paginated_logs.total,
                "pages": paginated_logs.pages,
                "current_page": paginated_logs.page
            }
        }

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {"code": 70, "message": "An unexpected error occurred", "status_code": 500}