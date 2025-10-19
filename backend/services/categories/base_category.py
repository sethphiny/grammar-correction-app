"""
Base category class for grammar checking.

All category classes inherit from this base class for consistent structure.
"""

from typing import List, Tuple, Callable, Optional
import re


class BaseCategory:
    """
    Base class for all grammar checking categories.
    
    Each category defines its own patterns and checking logic.
    """
    
    def __init__(self):
        """Initialize the category with its name and patterns."""
        self.category_name = self.get_category_name()
        self.display_name = self.get_display_name()
        self.patterns = self.get_patterns()
    
    def get_category_name(self) -> str:
        """
        Return the internal category name (e.g., 'redundancy', 'grammar').
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_category_name()")
    
    def get_display_name(self) -> str:
        """
        Return the human-readable display name (e.g., 'Redundant Phrases').
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_display_name()")
    
    def get_patterns(self) -> List[Tuple]:
        """
        Return the list of patterns for this category.
        
        Each pattern is a tuple of:
        - (pattern: str, description: str, fix_function: Callable or None)
        
        For dictionary-based categories (like redundancy), return empty list
        and override get_dictionary() instead.
        
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement get_patterns()")
    
    def get_dictionary(self) -> Optional[dict]:
        """
        Return the dictionary for dictionary-based categories.
        
        For categories that use a dictionary of replacements
        (e.g., redundancy: {'phrase': 'replacement'}).
        
        Returns None by default (for pattern-based categories).
        """
        return None
    
    def has_custom_checker(self) -> bool:
        """
        Return True if this category has custom checking logic.
        
        If True, the check() method will be called instead of
        using standard pattern matching.
        """
        return False
    
    def check(self, line_content: str, line_number: int, **kwargs) -> List:
        """
        Custom checking logic for categories that need it.
        
        Override this method for categories with complex checking logic
        (e.g., passive voice detection with spaCy).
        
        Args:
            line_content: The line text to check
            line_number: The line number in the document
            **kwargs: Additional context (e.g., nlp model, full document)
        
        Returns:
            List of GrammarIssue objects
        """
        return []
    
    def get_confidence(self, pattern_index: int = 0) -> float:
        """
        Return the confidence level for a pattern.
        
        Can be overridden by subclasses to provide pattern-specific confidence.
        
        Args:
            pattern_index: Index of the pattern in the patterns list
        
        Returns:
            Confidence value between 0.0 and 1.0
        """
        return 0.85  # Default confidence
    
    def get_description(self) -> str:
        """
        Return a description of what this category checks for.
        
        Used for documentation and help text.
        """
        return f"Checks for {self.display_name.lower()} issues"
    
    def is_experimental(self) -> bool:
        """
        Return True if this category is experimental.
        
        Experimental categories may produce false positives
        and are marked accordingly in the UI.
        """
        return False

