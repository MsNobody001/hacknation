import logging
from celery import shared_task, chain
from celery.exceptions import MaxRetriesExceededError

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name='clerk_assistant.tasks.detect_discrepancies_task',
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def detect_discrepancies_task(self, analysis_id: str) -> dict:
    from clerk_assistant.services.discrepancy_service import detect_discrepancies
    from clerk_assistant.models import Analysis
    
    logger.info(f"Starting discrepancy detection task for analysis {analysis_id}")
    
    try:
        result = detect_discrepancies(analysis_id)
        logger.info(f"Discrepancy detection completed for {analysis_id}: "
                   f"{result.get('discrepancies_count', 0)} discrepancies found")
        return result
        
    except Exception as e:
        logger.error(f"Discrepancy detection failed for {analysis_id}: {e}")
        
        # Update analysis status on final failure
        try:
            if self.request.retries >= self.max_retries:
                analysis = Analysis.objects.get(id=analysis_id)
                analysis.status = 'failed'
                analysis.error_message = f"Discrepancy detection failed: {str(e)}"
                analysis.save()
        except Exception:
            pass
        
        raise


@shared_task(
    bind=True,
    name='clerk_assistant.tasks.perform_formal_analysis_task',
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def perform_formal_analysis_task(self, analysis_id: str) -> dict:
    from clerk_assistant.services.formal_analysis_service import perform_formal_analysis
    from clerk_assistant.models import Analysis
    
    logger.info(f"Starting formal analysis task for analysis {analysis_id}")
    
    try:
        result = perform_formal_analysis(analysis_id)
        logger.info(f"Formal analysis completed for {analysis_id}: "
                   f"qualifies={result.get('qualifies_as_work_accident')}")
        return result
        
    except Exception as e:
        logger.error(f"Formal analysis failed for {analysis_id}: {e}")
        
        # Update analysis status on final failure
        try:
            if self.request.retries >= self.max_retries:
                analysis = Analysis.objects.get(id=analysis_id)
                analysis.status = 'failed'
                analysis.error_message = f"Formal analysis failed: {str(e)}"
                analysis.save()
        except Exception:
            pass
        
        raise


@shared_task(
    bind=True,
    name='clerk_assistant.tasks.complete_analysis_task',
)
def complete_analysis_task(self, results: list, analysis_id: str) -> dict:
    from clerk_assistant.models import Analysis
    
    logger.info(f"Completing analysis {analysis_id}")
    
    try:
        analysis = Analysis.objects.get(id=analysis_id)
        analysis.status = 'completed'
        analysis.error_message = None
        analysis.save()
        
        logger.info(f"Analysis {analysis_id} marked as completed")
        
        return {
            "status": "completed",
            "analysis_id": analysis_id,
            "task_results": results,
        }
        
    except Analysis.DoesNotExist:
        logger.error(f"Analysis {analysis_id} not found during completion")
        raise ValueError(f"Analysis {analysis_id} not found")


def run_analysis_pipeline(analysis_id: str) -> str:
    from clerk_assistant.models import Analysis
    try:
        analysis = Analysis.objects.get(id=analysis_id)
        analysis.status = 'processing'
        analysis.save()
    except Analysis.DoesNotExist:
        raise ValueError(f"Analysis {analysis_id} not found")
    
    pipeline = chain(
        detect_discrepancies_task.s(analysis_id),
        perform_formal_analysis_task.s(analysis_id),
        complete_analysis_task.s(analysis_id),
    )
    
    # Execute the chain
    result = pipeline.apply_async()
    
    logger.info(f"Started analysis pipeline for {analysis_id}, task_id={result.id}")
    
    return result.id


# Individual task runners for manual execution
def run_discrepancy_detection(analysis_id: str) -> str:
    result = detect_discrepancies_task.delay(analysis_id)
    logger.info(f"Started discrepancy detection for {analysis_id}, task_id={result.id}")
    return result.id


def run_formal_analysis(analysis_id: str) -> str:
    result = perform_formal_analysis_task.delay(analysis_id)
    logger.info(f"Started formal analysis for {analysis_id}, task_id={result.id}")
    return result.id
