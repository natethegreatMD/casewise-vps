"""
Output writer for grading results in CaseWise v2.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..core.logger import get_logger
from ..config import settings
from ..models.grading import GradingSession, GradingResult

logger = get_logger(__name__)


class OutputWriter:
    """Writer for grading results and outputs."""
    
    def __init__(self):
        """Initialize the output writer."""
        self.output_dir = settings.output_dir
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "json").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        (self.output_dir / "summaries").mkdir(exist_ok=True)
        
        logger.info("Output writer initialized", output_dir=str(self.output_dir))
    
    async def write_grading_result(self, session: GradingSession) -> None:
        """Write grading result to output files."""
        if not session.result:
            logger.warning("No result to write")
            return
        
        try:
            # Write JSON output
            await self._write_json_output(session)
            
            # Write human-readable report
            await self._write_report(session)
            
            # Write summary
            await self._write_summary(session)
            
            logger.info("Grading output written successfully")
            
        except Exception as e:
            logger.error("Failed to write grading output", error=str(e))
            raise
    
    async def _write_json_output(self, session: GradingSession) -> None:
        """Write detailed JSON output."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"grading_{session.id}_{timestamp}.json"
        filepath = self.output_dir / "json" / filename
        
        # Prepare output data
        output_data = {
            "session": {
                "id": session.id,
                "status": session.status.value,
                "rubric_id": session.rubric_id,
                "case_id": session.case_id,
                "user_id": session.user_id,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None,
                "error_message": session.error_message
            },
            "result": session.result.dict() if session.result else None,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "2.0.0"
            }
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.debug("JSON output written", filepath=str(filepath))
    
    async def _write_report(self, session: GradingSession) -> None:
        """Write human-readable report."""
        if not session.result:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"report_{session.id}_{timestamp}.txt"
        filepath = self.output_dir / "reports" / filename
        
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("CASEWISE GRADING REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Session ID: {session.id}")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Rubric ID: {session.rubric_id}")
        report_lines.append(f"Case ID: {session.case_id}")
        report_lines.append("")
        
        # Overall results
        result = session.result
        report_lines.append("OVERALL RESULTS")
        report_lines.append("-" * 40)
        report_lines.append(f"Total Score: {result.total_score:.1f} / {result.max_score:.1f}")
        report_lines.append(f"Percentage: {result.percentage:.1f}%")
        report_lines.append(f"Passed: {'Yes' if result.passed else 'No'}")
        report_lines.append(f"Confidence: {result.confidence:.2f}")
        report_lines.append(f"Grading Time: {result.grading_time_seconds:.1f} seconds")
        report_lines.append("")
        
        # Category results
        report_lines.append("CATEGORY RESULTS")
        report_lines.append("-" * 40)
        for category in result.category_results:
            report_lines.append(f"Category: {category.name}")
            report_lines.append(f"  Score: {category.score:.1f} / {category.max_score:.1f}")
            report_lines.append(f"  Percentage: {category.get_percentage():.1f}%")
            report_lines.append(f"  Weight: {category.weight}")
            report_lines.append(f"  Feedback: {category.feedback}")
            report_lines.append("")
            
            # Criterion results
            for criterion in category.criteria_results:
                report_lines.append(f"  Criterion: {criterion.criterion_id}")
                report_lines.append(f"    Score: {criterion.score:.1f} / {criterion.max_score:.1f}")
                report_lines.append(f"    Percentage: {criterion.get_percentage():.1f}%")
                report_lines.append(f"    Weight: {criterion.weight}")
                report_lines.append(f"    Feedback: {criterion.feedback}")
                if criterion.keywords_found:
                    report_lines.append(f"    Keywords Found: {', '.join(criterion.keywords_found)}")
                if criterion.keywords_missing:
                    report_lines.append(f"    Keywords Missing: {', '.join(criterion.keywords_missing)}")
                report_lines.append("")
        
        # Overall feedback
        report_lines.append("OVERALL FEEDBACK")
        report_lines.append("-" * 40)
        report_lines.append(result.overall_feedback)
        report_lines.append("")
        
        # Strengths and areas for improvement
        if result.strengths:
            report_lines.append("STRENGTHS")
            report_lines.append("-" * 40)
            for strength in result.strengths:
                report_lines.append(f"• {strength}")
            report_lines.append("")
        
        if result.areas_for_improvement:
            report_lines.append("AREAS FOR IMPROVEMENT")
            report_lines.append("-" * 40)
            for area in result.areas_for_improvement:
                report_lines.append(f"• {area}")
            report_lines.append("")
        
        # QA flags
        if result.qa_flags:
            report_lines.append("QUALITY ASSURANCE FLAGS")
            report_lines.append("-" * 40)
            for flag in result.qa_flags:
                report_lines.append(f"[{flag.level.value.upper()}] {flag.type.value}: {flag.message}")
            report_lines.append("")
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.debug("Report written", filepath=str(filepath))
    
    async def _write_summary(self, session: GradingSession) -> None:
        """Write summary output."""
        if not session.result:
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{session.id}_{timestamp}.json"
        filepath = self.output_dir / "summaries" / filename
        
        result = session.result
        
        summary_data = {
            "session_id": session.id,
            "rubric_id": session.rubric_id,
            "case_id": session.case_id,
            "user_id": session.user_id,
            "timestamp": datetime.now().isoformat(),
            "overall_score": result.total_score,
            "max_score": result.max_score,
            "percentage": result.percentage,
            "passed": result.passed,
            "confidence": result.confidence,
            "grading_time_seconds": result.grading_time_seconds,
            "category_summary": [
                {
                    "category_id": cat.category_id,
                    "name": cat.name,
                    "score": cat.score,
                    "max_score": cat.max_score,
                    "percentage": cat.get_percentage(),
                    "weight": cat.weight
                }
                for cat in result.category_results
            ],
            "qa_flags_count": len(result.qa_flags),
            "qa_flags_summary": {
                "critical": len([f for f in result.qa_flags if f.level.value == "critical"]),
                "high": len([f for f in result.qa_flags if f.level.value == "high"]),
                "medium": len([f for f in result.qa_flags if f.level.value == "medium"]),
                "low": len([f for f in result.qa_flags if f.level.value == "low"])
            }
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        logger.debug("Summary written", filepath=str(filepath))
    
    async def write_batch_summary(self, batch_id: str, results: List[GradingSession]) -> None:
        """Write batch grading summary."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"batch_{batch_id}_{timestamp}.json"
        filepath = self.output_dir / "summaries" / filename
        
        # Calculate batch statistics
        completed_results = [r for r in results if r.status.value == "completed"]
        failed_results = [r for r in results if r.status.value == "failed"]
        
        if completed_results:
            avg_score = sum(r.result.total_score for r in completed_results) / len(completed_results)
            avg_percentage = sum(r.result.percentage for r in completed_results) / len(completed_results)
            pass_rate = sum(1 for r in completed_results if r.result.passed) / len(completed_results) * 100
        else:
            avg_score = 0
            avg_percentage = 0
            pass_rate = 0
        
        batch_summary = {
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "total_submissions": len(results),
            "completed": len(completed_results),
            "failed": len(failed_results),
            "average_score": avg_score,
            "average_percentage": avg_percentage,
            "pass_rate": pass_rate,
            "results": [
                {
                    "session_id": r.id,
                    "status": r.status.value,
                    "score": r.result.total_score if r.result else None,
                    "percentage": r.result.percentage if r.result else None,
                    "passed": r.result.passed if r.result else None,
                    "error": r.error_message
                }
                for r in results
            ]
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(batch_summary, f, indent=2, ensure_ascii=False)
        
        logger.info("Batch summary written", 
                   batch_id=batch_id,
                   filepath=str(filepath),
                   total=len(results),
                   completed=len(completed_results))
    
    def get_output_files(self, session_id: str) -> Dict[str, str]:
        """Get output file paths for a session."""
        files = {}
        
        # Find JSON file
        json_files = list((self.output_dir / "json").glob(f"grading_{session_id}_*.json"))
        if json_files:
            files["json"] = str(json_files[-1])  # Most recent
        
        # Find report file
        report_files = list((self.output_dir / "reports").glob(f"report_{session_id}_*.txt"))
        if report_files:
            files["report"] = str(report_files[-1])  # Most recent
        
        # Find summary file
        summary_files = list((self.output_dir / "summaries").glob(f"summary_{session_id}_*.json"))
        if summary_files:
            files["summary"] = str(summary_files[-1])  # Most recent
        
        return files
    
    def cleanup_old_files(self, max_age_days: int = 30) -> int:
        """Clean up old output files."""
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 3600)
        deleted_count = 0
        
        for subdir in ["json", "reports", "summaries"]:
            subdir_path = self.output_dir / subdir
            if not subdir_path.exists():
                continue
            
            for file_path in subdir_path.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                    except Exception as e:
                        logger.warning("Failed to delete old file", 
                                     filepath=str(file_path), 
                                     error=str(e))
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old output files")
        
        return deleted_count 