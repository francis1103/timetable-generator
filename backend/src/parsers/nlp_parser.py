"""Natural Language Processing parser for scheduling rules."""

from typing import Dict, Any, List
import re


class NLPParser:
    """
    NLP parser for converting natural language rules to constraints.
    Uses pattern matching and NLP techniques.
    """
    
    def __init__(self):
        """Initialize NLP parser."""
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, Any]:
        """Compile regex patterns for rule matching."""
        return {
            'no_classes_after': re.compile(
                r'no classes? (?:for )?(.*?) after (\d+)\s*(am|pm) on (\w+)',
                re.IGNORECASE
            ),
            'prefer_time': re.compile(
                r'(.*?) prefers? (morning|evening|afternoon) (?:slots|classes)',
                re.IGNORECASE
            ),
            'max_consecutive': re.compile(
                r'max (\d+) consecutive classes? (?:for )?(.*?)',
                re.IGNORECASE
            ),
            'no_day': re.compile(
                r'no classes? on (\w+)',
                re.IGNORECASE
            ),
        }
    
    def parse_rule(self, rule: str) -> Dict[str, Any]:
        """
        Parse a natural language rule into a constraint specification.
        
        Args:
            rule: Natural language rule string
            
        Returns:
            Constraint specification dictionary
        """
        rule = rule.strip()
        
        # Try matching against known patterns
        for pattern_name, pattern in self.patterns.items():
            match = pattern.search(rule)
            
            if match:
                return self._process_match(pattern_name, match)
        
        # If no pattern matched, use simple keyword extraction
        return self._fallback_parse(rule)
    
    def _process_match(self, pattern_name: str, match) -> Dict[str, Any]:
        """Process a regex match into a constraint."""
        if pattern_name == 'no_classes_after':
            entity = match.group(1).strip()
            hour = int(match.group(2))
            meridiem = match.group(3).lower()
            day = match.group(4).lower()
            
            if meridiem == 'pm' and hour != 12:
                hour += 12
            elif meridiem == 'am' and hour == 12:
                hour = 0
            
            return {
                'type': 'time_restriction',
                'entity': entity,
                'day': day,
                'after_hour': hour,
                'description': f"No classes for {entity} after {hour}:00 on {day}"
            }
        
        elif pattern_name == 'prefer_time':
            entity = match.group(1).strip()
            time_preference = match.group(2).lower()
            
            return {
                'type': 'time_preference',
                'entity': entity,
                'preference': time_preference,
                'description': f"{entity} prefers {time_preference} slots"
            }
        
        elif pattern_name == 'max_consecutive':
            max_count = int(match.group(1))
            entity = match.group(2).strip()
            
            return {
                'type': 'consecutive_limit',
                'entity': entity,
                'max_consecutive': max_count,
                'description': f"Max {max_count} consecutive classes for {entity}"
            }
        
        elif pattern_name == 'no_day':
            day = match.group(1).lower()
            
            return {
                'type': 'day_restriction',
                'day': day,
                'description': f"No classes on {day}"
            }
        
        return {}
    
    def _fallback_parse(self, rule: str) -> Dict[str, Any]:
        """Fallback parsing using keyword extraction."""
        rule_lower = rule.lower()
        
        constraint = {
            'type': 'general',
            'description': rule,
            'keywords': []
        }
        
        # Extract time-related keywords
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        for day in days:
            if day in rule_lower:
                constraint['keywords'].append(('day', day))
        
        # Extract preference keywords
        if 'prefer' in rule_lower or 'like' in rule_lower:
            constraint['type'] = 'preference'
        elif 'no' in rule_lower or 'not' in rule_lower or 'avoid' in rule_lower:
            constraint['type'] = 'restriction'
        
        return constraint
    
    def parse_batch(self, rules: List[str]) -> List[Dict[str, Any]]:
        """
        Parse multiple rules at once.
        
        Args:
            rules: List of natural language rules
            
        Returns:
            List of constraint specifications
        """
        return [self.parse_rule(rule) for rule in rules]
    
    def validate_rule(self, rule: str) -> bool:
        """
        Check if a rule can be parsed.
        
        Args:
            rule: Natural language rule
            
        Returns:
            True if parseable
        """
        parsed = self.parse_rule(rule)
        return 'type' in parsed


# Example usage
if __name__ == '__main__':
    parser = NLPParser()
    
    # Test examples
    examples = [
        "No classes for Computer Science students after 3 PM on Fridays",
        "Faculty X prefers morning slots",
        "Max 2 consecutive classes for Dr. Smith",
        "No classes on Saturday",
    ]
    
    for example in examples:
        result = parser.parse_rule(example)
        print(f"\nRule: {example}")
        print(f"Parsed: {result}")
