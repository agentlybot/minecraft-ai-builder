"""
Style Reference Module

Extracts patterns from NBT example builds and injects them
into AI prompts as style references.
"""

from .extractor import StyleExtractor, extract_style_from_nbt
from .aggregator import StyleAggregator, aggregate_styles
from .prompt_enhancer import PromptEnhancer

__all__ = [
    'StyleExtractor',
    'extract_style_from_nbt',
    'StyleAggregator',
    'aggregate_styles',
    'PromptEnhancer'
]
