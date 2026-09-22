import json
from django.shortcuts import render
from .services import (
    get_all_table_stats, 
    get_table_data, 
    get_executive_summary_metrics, 
    get_state_distribution_stats, 
    get_monthly_trend_stats,
    get_master_projects,
    get_single_project_detail
)

def data_overview_view(request):
    """Renders the executive dashboard with metrics, explorer table, search, analytics charts, and master projects."""
    table_stats = get_all_table_stats()
    metrics = get_executive_summary_metrics()
    
    current_table = request.GET.get('table', 'allocated_limits')
    search_query = request.GET.get('q', '').strip()
    
    allowed_tables = [s['table_name'] for s in table_stats]
    if current_table not in allowed_tables:
        current_table = 'allocated_limits'
        
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0
    limit = 51

    columns, records, total_matching = get_table_data(current_table, limit=limit, offset=offset, search_query=search_query)
    records_json = json.dumps(records, default=str)

    # Fetch chart analytics data based on active table or default to recommendations
    chart_table = current_table if current_table in ['works_recommended', 'works_sanctioned', 'works_completed', 'allocated_limits'] else 'works_recommended'
    state_stats = get_state_distribution_stats(chart_table)
    
    state_labels = [item['state'] for item in state_stats]
    state_counts = [item['count'] for item in state_stats]

    trend_stats = get_monthly_trend_stats()
    master_projects = get_master_projects(limit=15)

    # Merged single context dictionary containing all variables
    context = {
        'table_stats': table_stats,
        'metrics': metrics,
        'current_table': current_table,
        'columns': columns,
        'records': records,
        'records_json': records_json,
        'search_query': search_query,
        'state_labels_json': json.dumps(state_labels),
        'state_counts_json': json.dumps(state_counts),
        'trend_labels_json': json.dumps(trend_stats['labels']),
        'trend_exp_json': json.dumps(trend_stats['expenditure']),
        'trend_app_json': json.dumps(trend_stats['approvals']),
        'master_projects': master_projects,
        'offset': offset,
        'limit': limit,
        'total_records': total_matching,
        'has_prev': offset > 0,
        'has_next': (offset + limit) < total_matching,
        'prev_offset': max(0, offset - limit),
        'next_offset': offset + limit,
    }
    return render(request, 'projects/data_overview.html', context)

def table_detail_view(request, table_name):
    """Renders the paginated rows and columns for the selected table."""
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0
    limit = 50

    columns, records, _ = get_table_data(table_name, limit=limit, offset=offset)

    context = {
        'current_table': table_name,
        'columns': columns,
        'records': records,
        'records_json': json.dumps(records, default=str),  # Passes records to JS for the popup
        'current_offset': offset,
        'next_offset': offset + limit,
        'prev_offset': max(0, offset - limit),
        'has_prev': offset > 0,
    }
    return render(request, 'projects/table_detail.html', context)

def project_detail_view(request, project_id):
    """Renders the dedicated deep-dive diagnostics page for a specific master project."""
    project = get_single_project_detail(project_id)
    context = {
        'project': project,
    }
    return render(request, 'projects/project_detail.html', context)