"""
Sampler Module
==============
Collects representative samples from large log files.
Does NOT send entire file to AI - only a sample.
"""

import random
import logging
from typing import List

logger = logging.getLogger(__name__)


class Sampler:
    """
    Collects representative samples from log files.
    
    Instead of taking first 100 lines (which might all be same),
    we take samples from different parts of the file.
    """
    
    def __init__(self, sample_size: int = 300):
        self.sample_size = sample_size
    
    def collect_sample(self, content: str) -> List[str]:
        """
        Collect a representative sample from file content.
        
        Strategy:
        1. First 50 lines (startup patterns)
        2. Random lines from middle (varied patterns)
        3. Last 50 lines (recent activity)
        
        Args:
            content: Full file content as string
            
        Returns:
            List of sample lines
        """
        lines = content.splitlines()
        total_lines = len(lines)
        
        if total_lines == 0:
            raise ValueError("File is empty - no lines to sample")
        
        # If file is small enough, return all lines
        if total_lines <= self.sample_size:
            logger.info(f"File has {total_lines} lines, using all as sample")
            return [l.strip() for l in lines if l.strip()]
        
        samples = []
        
        # 1. First 50 lines (startup patterns, config, etc.)
        first_count = min(50, total_lines // 5)
        samples.extend(lines[:first_count])
        
        # 2. Random lines from middle
        middle_lines = lines[first_count:-first_count] if total_lines > 100 else lines[first_count:]
        random_count = min(self.sample_size - 100, len(middle_lines))
        
        if random_count > 0 and middle_lines:
            # Use seed for reproducibility
            random.seed(42)
            random_samples = random.sample(middle_lines, min(random_count, len(middle_lines)))
            samples.extend(random_samples)
        
        # 3. Last 50 lines (recent activity)
        last_count = min(50, total_lines // 5)
        samples.extend(lines[-last_count:])
        
        # Remove empty lines and duplicates while preserving order
        seen = set()
        unique_samples = []
        for line in samples:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                unique_samples.append(line)
        
        logger.info(
            f"Collected {len(unique_samples)} unique sample lines "
            f"from {total_lines} total lines"
        )
        
        return unique_samples
    
    def collect_diverse_sample(self, content: str) -> List[str]:
        """
        Collect a diverse sample - lines that look DIFFERENT from each other.
        
        This helps format detection because we see different patterns.
        """
        lines = content.splitlines()
        total_lines = len(lines)
        
        if total_lines == 0:
            raise ValueError("File is empty")
        
        if total_lines <= self.sample_size:
            return [l.strip() for l in lines if l.strip()]
        
        # Collect from different sections
        sections = 10
        section_size = total_lines // sections
        samples = []
        
        for i in range(sections):
            start = i * section_size
            end = start + section_size
            section_lines = lines[start:end]
            
            # Take 30 lines from each section
            if section_lines:
                count = min(30, len(section_lines))
                step = max(1, len(section_lines) // count)
                selected = section_lines[::step][:count]
                samples.extend(selected)
        
        # Remove empty and deduplicate
        seen = set()
        unique = []
        for line in samples:
            line = line.strip()
            if line and line not in seen:
                seen.add(line)
                unique.append(line)
        
        logger.info(f"Diverse sample: {len(unique)} unique lines from {total_lines}")
        
        return unique
