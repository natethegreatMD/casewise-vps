"""
Quality assurance flags manager for CaseWise v2.
"""

import time
from typing import Dict, List, Optional, Any

from ..core.logger import get_logger
from ..config import settings
from ..models.grading import QAFlag, QAFlagLevel, QAFlagType, GradingResult
from ..models.rubric import Rubric

logger = get_logger(__name__)


class QAFlagsManager:
    """Manager for quality assurance flags and analysis."""
    
    def __init__(self):
        """Initialize the QA flags manager."""
        self.threshold = settings.qa_threshold
        logger.info("QA Flags Manager initialized", threshold=self.threshold)
    
    async def analyze_grading_result(self, 
                                   grading_result: GradingResult, 
                                   rubric: Rubric) -> List[QAFlag]:
        """Analyze grading result for potential QA issues."""
        qa_flags = []
        
        # Check for score consistency
        consistency_flags = self._check_score_consistency(grading_result, rubric)
        qa_flags.extend(consistency_flags)
        
        # Check for feedback quality
        feedback_flags = self._check_feedback_quality(grading_result)
        qa_flags.extend(feedback_flags)
        
        # Check for keyword coverage
        keyword_flags = self._check_keyword_coverage(grading_result, rubric)
        qa_flags.extend(keyword_flags)
        
        # Check for confidence issues
        confidence_flags = self._check_confidence_issues(grading_result)
        qa_flags.extend(confidence_flags)
        
        # Check for completeness
        completeness_flags = self._check_completeness(grading_result, rubric)
        qa_flags.extend(completeness_flags)
        
        # Filter by threshold
        filtered_flags = [flag for flag in qa_flags if flag.confidence >= self.threshold]
        
        logger.info("QA analysis completed", 
                   total_flags=len(qa_flags),
                   filtered_flags=len(filtered_flags),
                   threshold=self.threshold)
        
        return filtered_flags
    
    def _check_score_consistency(self, grading_result: GradingResult, rubric: Rubric) -> List[QAFlag]:
        """Check for score consistency issues."""
        flags = []
        
        # Check if total score matches sum of category scores
        calculated_total = sum(cat.get_weighted_score() for cat in grading_result.category_results)
        if abs(calculated_total - grading_result.total_score) > 0.1:
            flags.append(QAFlag(
                id=f"qa_{int(time.time())}_consistency_1",
                type=QAFlagType.INCONSISTENT_SCORING,
                level=QAFlagLevel.HIGH,
                message=f"Total score ({grading_result.total_score}) doesn't match calculated sum ({calculated_total})",
                confidence=0.9
            ))
        
        # Check for negative scores
        for category in grading_result.category_results:
            if category.score < 0:
                flags.append(QAFlag(
                    id=f"qa_{int(time.time())}_consistency_2",
                    type=QAFlagType.INCONSISTENT_SCORING,
                    level=QAFlagLevel.CRITICAL,
                    message=f"Negative score detected in category {category.name}",
                    category_id=category.category_id,
                    confidence=1.0
                ))
            
            for criterion in category.criteria_results:
                if criterion.score < 0:
                    flags.append(QAFlag(
                        id=f"qa_{int(time.time())}_consistency_3",
                        type=QAFlagType.INCONSISTENT_SCORING,
                        level=QAFlagLevel.CRITICAL,
                        message=f"Negative score detected in criterion {criterion.criterion_id}",
                        category_id=category.category_id,
                        criterion_id=criterion.criterion_id,
                        confidence=1.0
                    ))
        
        return flags
    
    def _check_feedback_quality(self, grading_result: GradingResult) -> List[QAFlag]:
        """Check for feedback quality issues."""
        flags = []
        
        # Check for empty or very short feedback
        if len(grading_result.overall_feedback.strip()) < 10:
            flags.append(QAFlag(
                id=f"qa_{int(time.time())}_feedback_1",
                type=QAFlagType.MISSING_CONTENT,
                level=QAFlagLevel.MEDIUM,
                message="Overall feedback is too short or missing",
                confidence=0.8
            ))
        
        # Check category feedback
        for category in grading_result.category_results:
            if len(category.feedback.strip()) < 5:
                flags.append(QAFlag(
                    id=f"qa_{int(time.time())}_feedback_2",
                    type=QAFlagType.MISSING_CONTENT,
                    level=QAFlagLevel.LOW,
                    message=f"Category feedback is too short for {category.name}",
                    category_id=category.category_id,
                    confidence=0.7
                ))
            
            # Check criterion feedback
            for criterion in category.criteria_results:
                if len(criterion.feedback.strip()) < 5:
                    flags.append(QAFlag(
                        id=f"qa_{int(time.time())}_feedback_3",
                        type=QAFlagType.MISSING_CONTENT,
                        level=QAFlagLevel.LOW,
                        message=f"Criterion feedback is too short",
                        category_id=category.category_id,
                        criterion_id=criterion.criterion_id,
                        confidence=0.6
                    ))
        
        return flags
    
    def _check_keyword_coverage(self, grading_result: GradingResult, rubric: Rubric) -> List[QAFlag]:
        """Check for keyword coverage issues."""
        flags = []
        
        for category in grading_result.category_results:
            for criterion in category.criteria_results:
                # Find corresponding rubric criterion
                rubric_criterion = rubric.get_criterion_by_id(criterion.criterion_id)
                if not rubric_criterion:
                    continue
                
                expected_keywords = rubric_criterion.expected_keywords
                if not expected_keywords:
                    continue
                
                # Check if keywords were evaluated
                if not criterion.keywords_found and not criterion.keywords_missing:
                    flags.append(QAFlag(
                        id=f"qa_{int(time.time())}_keywords_1",
                        type=QAFlagType.MISSING_CONTENT,
                        level=QAFlagLevel.MEDIUM,
                        message=f"Keyword evaluation missing for criterion {criterion.criterion_id}",
                        category_id=category.category_id,
                        criterion_id=criterion.criterion_id,
                        confidence=0.7
                    ))
                
                # Check for unusual keyword patterns
                found_count = len(criterion.keywords_found)
                missing_count = len(criterion.keywords_missing)
                total_expected = len(expected_keywords)
                
                if found_count + missing_count != total_expected:
                    flags.append(QAFlag(
                        id=f"qa_{int(time.time())}_keywords_2",
                        type=QAFlagType.INCONSISTENT_SCORING,
                        level=QAFlagLevel.MEDIUM,
                        message=f"Keyword count mismatch: found {found_count}, missing {missing_count}, expected {total_expected}",
                        category_id=category.category_id,
                        criterion_id=criterion.criterion_id,
                        confidence=0.8
                    ))
        
        return flags
    
    def _check_confidence_issues(self, grading_result: GradingResult) -> List[QAFlag]:
        """Check for confidence-related issues."""
        flags = []
        
        # Check overall confidence
        if grading_result.confidence < 0.5:
            flags.append(QAFlag(
                id=f"qa_{int(time.time())}_confidence_1",
                type=QAFlagType.UNCLEAR_RESPONSE,
                level=QAFlagLevel.MEDIUM,
                message=f"Low overall confidence in grading ({grading_result.confidence:.2f})",
                confidence=0.8
            ))
        
        # Check criterion confidence
        low_confidence_criteria = []
        for category in grading_result.category_results:
            for criterion in category.criteria_results:
                if criterion.confidence < 0.3:
                    low_confidence_criteria.append(criterion.criterion_id)
        
        if low_confidence_criteria:
            flags.append(QAFlag(
                id=f"qa_{int(time.time())}_confidence_2",
                type=QAFlagType.UNCLEAR_RESPONSE,
                level=QAFlagLevel.MEDIUM,
                message=f"Low confidence in criteria: {', '.join(low_confidence_criteria[:3])}",
                confidence=0.7
            ))
        
        return flags
    
    def _check_completeness(self, grading_result: GradingResult, rubric: Rubric) -> List[QAFlag]:
        """Check for completeness issues."""
        flags = []
        
        # Check if all rubric categories are covered
        rubric_category_ids = {cat.id for cat in rubric.categories}
        result_category_ids = {cat.category_id for cat in grading_result.category_results}
        
        missing_categories = rubric_category_ids - result_category_ids
        if missing_categories:
            flags.append(QAFlag(
                id=f"qa_{int(time.time())}_completeness_1",
                type=QAFlagType.MISSING_CONTENT,
                level=QAFlagLevel.HIGH,
                message=f"Missing categories in grading: {', '.join(missing_categories)}",
                confidence=0.9
            ))
        
        # Check if all criteria are covered
        for category in grading_result.category_results:
            rubric_category = rubric.get_category_by_id(category.category_id)
            if not rubric_category:
                continue
            
            rubric_criterion_ids = {crit.id for crit in rubric_category.criteria}
            result_criterion_ids = {crit.criterion_id for crit in category.criteria_results}
            
            missing_criteria = rubric_criterion_ids - result_criterion_ids
            if missing_criteria:
                flags.append(QAFlag(
                    id=f"qa_{int(time.time())}_completeness_2",
                    type=QAFlagType.MISSING_CONTENT,
                    level=QAFlagLevel.MEDIUM,
                    message=f"Missing criteria in category {category.name}: {', '.join(missing_criteria)}",
                    category_id=category.category_id,
                    confidence=0.8
                ))
        
        return flags
    
    def get_qa_summary(self, qa_flags: List[QAFlag]) -> Dict[str, Any]:
        """Get a summary of QA flags."""
        if not qa_flags:
            return {"total_flags": 0, "by_level": {}, "by_type": {}}
        
        by_level = {}
        by_type = {}
        
        for flag in qa_flags:
            # Count by level
            level = flag.level.value
            by_level[level] = by_level.get(level, 0) + 1
            
            # Count by type
            flag_type = flag.type.value
            by_type[flag_type] = by_type.get(flag_type, 0) + 1
        
        return {
            "total_flags": len(qa_flags),
            "by_level": by_level,
            "by_type": by_type,
            "critical_count": by_level.get("critical", 0),
            "high_count": by_level.get("high", 0),
            "medium_count": by_level.get("medium", 0),
            "low_count": by_level.get("low", 0)
        }
    
    def should_require_review(self, qa_flags: List[QAFlag]) -> bool:
        """Determine if grading result requires manual review."""
        critical_flags = [flag for flag in qa_flags if flag.level == QAFlagLevel.CRITICAL]
        high_flags = [flag for flag in qa_flags if flag.level == QAFlagLevel.HIGH]
        
        # Require review if there are critical flags or too many high flags
        return len(critical_flags) > 0 or len(high_flags) >= 3 