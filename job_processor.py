from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
import traceback

class JobProcessor:
    def __init__(self, db_connection):
        """
        Initialize JobProcessor with database connection
        
        Args:
            db_connection: MongoDB database connection
        """
        self.db = db_connection
        self.jobs = self.db.jobs
        self.raw_data = self.db.your_raw_collection  # Original data collection
        
    def create_jobs_from_pipeline(self, pipeline, job_type="data_processing"):
        """
        Create jobs from existing pipeline results
        
        Args:
            pipeline: MongoDB aggregation pipeline
            job_type: Type of job to create
            
        Returns:
            List of created job IDs
        """
        
        # Execute existing pipeline to get documents to process
        documents = list(self.raw_data.aggregate(pipeline))
        
        # Create jobs for each document (prevent duplicates)
        created_jobs = []
        for doc in documents:
            try:
                job_doc = {
                    "data_id": doc["_id"],
                    "job_type": job_type,
                    "status": "pending",
                    "is_completed": False,
                    "priority": 3,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "retry_count": 0,
                    "max_retries": 3,
                    "metadata": {}
                }
                
                # Use upsert to prevent duplicates
                result = self.jobs.update_one(
                    {"data_id": doc["_id"]},
                    {"$setOnInsert": job_doc},
                    upsert=True
                )
                
                if result.upserted_id:
                    created_jobs.append(result.upserted_id)
                    
            except Exception as e:
                print(f"Failed to create job for {doc['_id']}: {e}")
        
        print(f"Created {len(created_jobs)} jobs")
        return created_jobs
    
    def process_pending_jobs(self, worker_id="default-worker", batch_size=100):
        """
        Process pending jobs in batches
        
        Args:
            worker_id: Identifier for the worker processing jobs
            batch_size: Number of jobs to process in each batch
            
        Returns:
            Total number of processed jobs
        """
        
        processed_count = 0
        
        while True:
            # Get pending jobs to process
            pending_jobs = list(self.jobs.find({
                "is_completed": False,
                "status": "pending"
            }).sort([("priority", 1), ("created_at", 1)]).limit(batch_size))
            
            if not pending_jobs:
                break
                
            print(f"Processing {len(pending_jobs)} jobs...")
            
            # Process each job individually
            for job in pending_jobs:
                success = self._process_single_job(job, worker_id)
                if success:
                    processed_count += 1
        
        print(f"Total processed: {processed_count} jobs")
        return processed_count
    
    def _process_single_job(self, job, worker_id):
        """
        Process a single job
        
        Args:
            job: Job document to process
            worker_id: Identifier for the worker
            
        Returns:
            True if successful, False if failed
        """
        job_id = job["_id"]
        
        try:
            # Mark job as processing
            self._mark_job_processing(job_id, worker_id)
            
            # Get original data
            raw_document = self.raw_data.find_one({"_id": job["data_id"]})
            if not raw_document:
                self._complete_job(job_id, False, error_msg="Data not found", error_code="DATA_NOT_FOUND")
                return False
            
            # Execute actual processing logic (original for loop content)
            result = self._process_document(raw_document)
            
            # Mark as successful
            self._complete_job(job_id, True, result_data=result)
            return True
            
        except Exception as e:
            # Handle failure
            error_msg = str(e)
            error_code = "PROCESSING_ERROR"
            self._complete_job(job_id, False, error_msg=error_msg, error_code=error_code)
            print(f"Job {job_id} failed: {error_msg}")
            return False
    
    def _mark_job_processing(self, job_id, worker_id):
        """
        Mark job as currently being processed
        
        Args:
            job_id: Job ID to mark
            worker_id: Worker processing the job
        """
        self.jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "processing",
                    "processor_id": worker_id,
                    "started_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )
    
    def _complete_job(self, job_id, success, result_data=None, error_msg=None, error_code=None):
        """
        Mark job as completed (success or failure)
        
        Args:
            job_id: Job ID to complete
            success: Whether the job succeeded
            result_data: Result data if successful
            error_msg: Error message if failed
            error_code: Error code if failed
            
        Returns:
            True if update was successful
        """
        current_time = datetime.now()
        
        # Get existing job info to calculate processing duration
        job = self.jobs.find_one({"_id": job_id})
        if not job:
            return False
        
        duration = None
        if job.get("started_at"):
            duration = int((current_time - job["started_at"]).total_seconds() * 1000)
        
        update_data = {
            "status": "success" if success else "failed",
            "is_completed": success,  # Only mark as completed if successful
            "processed_at": current_time,
            "updated_at": current_time,
            "processing_duration": duration
        }
        
        if result_data:
            update_data["result"] = result_data
        
        if not success:
            update_data["error_message"] = error_msg
            update_data["error_code"] = error_code
        
        result = self.jobs.update_one(
            {"_id": job_id},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
    
    def _process_document(self, document):
        """
        Actual document processing logic (replace with your existing for loop content)
        
        Args:
            document: Document to process
            
        Returns:
            Processing result data
        """
        # TODO: Replace this with your existing processing logic
        # This is where your original for loop content goes
        
        # Example processing logic
        processed_data = {
            "original_id": document["_id"],
            "processed_at": datetime.now(),
            "field_count": len(document),
            # Add your specific processing results here
        }
        
        # Save processed results to another collection if needed
        # self.db.processed_collection.insert_one(processed_data)
        
        return {
            "status": "completed",
            "processed_fields": len(document),
            "result": "success"
        }

    def retry_failed_jobs(self):
        """
        Reset failed jobs for retry
        
        Returns:
            Number of jobs reset for retry
        """
        result = self.jobs.update_many(
            {
                "status": "failed",
                "retry_count": {"$lt": 3}
            },
            {
                "$set": {
                    "status": "pending",
                    "updated_at": datetime.now()
                },
                "$inc": {"retry_count": 1}
            }
        )
        
        print(f"Reset {result.modified_count} failed jobs for retry")
        return result.modified_count

    def handle_timeout_jobs(self, timeout_minutes=30):
        """
        Handle jobs that have been processing too long
        
        Args:
            timeout_minutes: Minutes after which to consider a job timed out
            
        Returns:
            Number of jobs marked as failed due to timeout
        """
        timeout_time = datetime.now() - timedelta(minutes=timeout_minutes)
        
        result = self.jobs.update_many(
            {
                "status": "processing",
                "started_at": {"$lt": timeout_time}
            },
            {
                "$set": {
                    "status": "failed",
                    "error_message": "Processing timeout",
                    "error_code": "TIMEOUT",
                    "updated_at": datetime.now()
                }
            }
        )
        
        print(f"Marked {result.modified_count} jobs as failed due to timeout")
        return result.modified_count

    def get_job_summary(self):
        """
        Get summary of job statuses
        
        Returns:
            Dictionary with status counts
        """
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        
        result = list(self.jobs.aggregate(pipeline))
        summary = {item["_id"]: item["count"] for item in result}
        return summary

# Usage example
def main():
    """
    Main function demonstrating how to use JobProcessor
    """
    client = MongoClient('mongodb://localhost:27017/')
    db = client.your_database
    
    processor = JobProcessor(db)
    
    # 1. Create jobs from existing pipeline
    your_pipeline = [
        {"$match": {"status": "need_processing"}},
        {"$sort": {"created_at": 1}},
        # Add your existing pipeline conditions here
    ]
    
    processor.create_jobs_from_pipeline(your_pipeline)
    
    # 2. Process jobs
    processor.process_pending_jobs(worker_id="worker-001")
    
    # 3. Check status
    summary = processor.get_job_summary()
    print(f"Processing summary: {summary}")
    
    # 4. Handle timeouts and retries
    processor.handle_timeout_jobs()
    processor.retry_failed_jobs()

if __name__ == "__main__":
    main()
