from django.urls import path
from . import views

urlpatterns = [
    path('sample/', views.SampleView.as_view(), name="sample"),
    path('sequential-events-agent/', views.SequentialEventsAgentView.as_view(), name="sequential_events_agent"),
    path('accident-data-collector/', views.AccidentDataCollectorView.as_view(), name="accident_data_collector"),
    
    path('accident-statement-collector/', views.AccidentStatementCollectorView.as_view(), name="accident_statement_collector"),
    path('accident-report-collector/', views.AccidentReportCollectorView.as_view(), name="accident_report_collector"),
]