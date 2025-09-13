"""
URL Content Extractor Module.
This module provides functionality for extracting content from URLs.
"""
from typing import Optional, Dict, Any, List, Set
import logging
import re
import urllib.parse

# Import libraries for URL content extraction
try:
    import aiohttp
    from bs4 import BeautifulSoup
    import trafilatura
except ImportError:
    aiohttp = None
    BeautifulSoup = None
    trafilatura = None

logger = logging.getLogger(__name__)

class URLContentExtractor:
    """Extract content from URLs"""
    
    def __init__(self):
        if aiohttp is None or BeautifulSoup is None:
            logger.warning("aiohttp or BeautifulSoup is not installed. URL extraction will not be available.")
    
    async def extract(self, url: str, follow_links: bool = False, max_depth: int = 1, 
                    same_domain_only: bool = True) -> Dict[str, Any]:
        """Extract and return text content from URL with optional link following
        
        Args:
            url: The URL to extract content from
            follow_links: Whether to follow links in the page
            max_depth: Maximum depth for link following
            same_domain_only: Only follow links to the same domain
            
        Returns:
            Dict containing main content and optionally linked content
        """
        if aiohttp is None or BeautifulSoup is None:
            raise ImportError("aiohttp and BeautifulSoup are required for URL extraction")
            
        try:
            # Extract content from the main URL
            main_content = await self._extract_from_url(url)
            
            result = {
                "url": url,
                "content": main_content["content"],
                "title": main_content.get("title", ""),
                "metadata": main_content.get("metadata", {})
            }
            
            # Follow links if requested
            if follow_links and max_depth > 0:
                linked_content = await self._follow_links(
                    url, 
                    main_content.get("links", []), 
                    max_depth, 
                    same_domain_only
                )
                result["linked_content"] = linked_content
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            raise ValueError(f"Failed to extract content from URL: {str(e)}")
    
    async def _extract_from_url(self, url: str) -> Dict[str, Any]:
        """Extract content from a single URL"""
        # First try trafilatura for high-quality extraction if available
        if trafilatura is not None:
            content = await self._extract_with_trafilatura(url)
            if content:
                return content
        
        # Fall back to BeautifulSoup
        return await self._extract_with_bs4(url)
    
    async def _extract_with_trafilatura(self, url: str) -> Optional[Dict[str, Any]]:
        """Extract content using trafilatura library"""
        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded:
                content = trafilatura.extract(downloaded, include_comments=False, 
                                           include_tables=True, output_format='markdown')
                
                # Extract metadata
                metadata = trafilatura.extract_metadata(downloaded)
                metadata_dict = {}
                
                if metadata:
                    if metadata.title:
                        metadata_dict["title"] = metadata.title
                    if metadata.author:
                        metadata_dict["author"] = metadata.author
                    if metadata.date:
                        metadata_dict["date"] = metadata.date
                    if metadata.sitename:
                        metadata_dict["site_name"] = metadata.sitename
                    if metadata.description:
                        metadata_dict["description"] = metadata.description
                
                # Extract links for potential following
                links = []
                soup = BeautifulSoup(downloaded, 'html.parser')
                for a_tag in soup.find_all('a', href=True):
                    links.append(a_tag['href'])
                
                if content:
                    return {
                        "content": content,
                        "title": metadata_dict.get("title", ""),
                        "metadata": metadata_dict,
                        "links": links
                    }
            return None
        except Exception as e:
            logger.warning(f"Trafilatura extraction failed for {url}: {str(e)}")
            return None
    
    async def _extract_with_bs4(self, url: str) -> Dict[str, Any]:
        """Extract content using BeautifulSoup"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                html = await response.text()
                
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = ""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.string
        
        # Extract metadata
        metadata = {}
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                metadata[meta.get('name')] = meta.get('content')
            elif meta.get('property'):
                metadata[meta.get('property')] = meta.get('content')
        
        # Extract links
        links = []
        for a_tag in soup.find_all('a', href=True):
            links.append(a_tag['href'])
        
        # Remove script and style elements for content extraction
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.decompose()
        
        # Try to find the main content
        main_content = None
        
        # Look for common content containers
        content_elements = soup.select('article, [role="main"], .content, #content, .post, .entry, .post-content, .article-content, main')
        
        if content_elements:
            # Use the first content element found
            main_content = content_elements[0]
        else:
            # If no content container found, use the body
            main_content = soup.body
        
        # Get text from the main content
        if main_content:
            text = main_content.get_text(separator='\n')
        else:
            text = soup.get_text(separator='\n')
        
        # Clean text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return {
            "content": text,
            "title": title,
            "metadata": metadata,
            "links": links
        }
    
    async def _follow_links(self, base_url: str, links: List[str], max_depth: int, 
                          same_domain_only: bool) -> List[Dict[str, Any]]:
        """Follow links from the base URL up to max_depth"""
        if max_depth <= 0:
            return []
            
        # Parse base URL to get domain
        parsed_base = urllib.parse.urlparse(base_url)
        base_domain = parsed_base.netloc
        
        # Normalize and filter links
        normalized_links = []
        for link in links:
            # Skip empty links, anchors, javascript, etc.
            if not link or link.startswith('#') or link.startswith('javascript:') or link.startswith('mailto:'):
                continue
                
            # Normalize relative URLs
            if link.startswith('/'):
                link = f"{parsed_base.scheme}://{base_domain}{link}"
            elif not link.startswith('http'):
                # Handle relative URLs without leading slash
                link = urllib.parse.urljoin(base_url, link)
                
            # Filter by domain if requested
            if same_domain_only:
                parsed_link = urllib.parse.urlparse(link)
                if parsed_link.netloc != base_domain:
                    continue
                    
            normalized_links.append(link)
            
        # Remove duplicates while preserving order
        unique_links = []
        seen = set()
        for link in normalized_links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
                
        # Limit number of links to follow (prevent too many requests)
        links_to_follow = unique_links[:min(len(unique_links), 5)]
        
        # Follow links
        results = []
        for link in links_to_follow:
            try:
                content = await self._extract_from_url(link)
                
                # Add to results
                results.append({
                    "url": link,
                    "content": content["content"],
                    "title": content.get("title", ""),
                    "metadata": content.get("metadata", {})
                })
                
                # Recursively follow links from this page
                if max_depth > 1:
                    sub_links = await self._follow_links(
                        link, 
                        content.get("links", []), 
                        max_depth - 1, 
                        same_domain_only
                    )
                    for sub_link in sub_links:
                        results.append(sub_link)
                        
            except Exception as e:
                logger.warning(f"Error following link {link}: {str(e)}")
                continue
                
        return results