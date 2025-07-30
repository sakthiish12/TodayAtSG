"""
Comprehensive scrapers package for TodayAtSG.

This package contains production-ready web scrapers for various Singapore event sources.
All scrapers inherit from BaseScraper and implement standardized data extraction.
"""

from .base import BaseScraper, ScrapedEvent, ScrapingResult, ScrapingError
from .visitsingapore import VisitSingaporeScraper
from .eventbrite import EventbriteScraper  
from .marinabaysands import MarinaBayScandsScraper
from .sunteccity import SuntecCityScraper
from .community_centers import CommunityCenter
from .data_processor import EventDataProcessor

__all__ = [
    'BaseScraper',
    'ScrapedEvent', 
    'ScrapingResult',
    'ScrapingError',
    'VisitSingaporeScraper',
    'EventbriteScraper',
    'MarinaBayScandsScraper', 
    'SuntecCityScraper',
    'CommunityCenter',
    'EventDataProcessor'
]