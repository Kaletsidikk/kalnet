"""
Validation utilities for user input validation
"""
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional

class ValidationUtils:
    """Utility class for validating user inputs"""
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """Validate customer name"""
        if not name or len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name.strip()) > 50:
            return False, "Name cannot exceed 50 characters"
        
        # Check for basic characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-']+$", name.strip()):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, name.strip().title()
    
    @staticmethod
    def validate_company_name(company_name: str) -> Tuple[bool, str]:
        """Validate company name (optional field)"""
        if not company_name:
            return True, ""
        
        if len(company_name.strip()) > 100:
            return False, "Company name cannot exceed 100 characters"
        
        # Allow letters, numbers, spaces, and common business symbols
        if not re.match(r"^[a-zA-Z0-9\s\-'&.,()]+$", company_name.strip()):
            return False, "Company name contains invalid characters"
        
        return True, company_name.strip()
    
    @staticmethod
    def validate_quantity(quantity_str: str) -> Tuple[bool, int]:
        """Validate quantity input"""
        try:
            quantity = int(quantity_str.strip())
            
            if quantity <= 0:
                return False, 0
            
            if quantity > 100000:  # Reasonable upper limit
                return False, 0
            
            return True, quantity
            
        except ValueError:
            return False, 0
    
    @staticmethod
    def validate_delivery_date(date_str: str) -> Tuple[bool, str]:
        """Validate delivery date"""
        date_str = date_str.strip()
        
        # Try different date formats
        date_formats = [
            "%d/%m/%Y",      # 25/12/2024
            "%d-%m-%Y",      # 25-12-2024
            "%d.%m.%Y",      # 25.12.2024
            "%Y-%m-%d",      # 2024-12-25
            "%m/%d/%Y"       # 12/25/2024 (US format)
        ]
        
        parsed_date = None
        
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                break
            except ValueError:
                continue
        
        if not parsed_date:
            return False, ""
        
        # Check if date is in the future (at least tomorrow)
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if parsed_date < tomorrow:
            return False, ""
        
        # Check if date is not too far in the future (1 year)
        max_date = datetime.now() + timedelta(days=365)
        if parsed_date > max_date:
            return False, ""
        
        # Return standardized format
        return True, parsed_date.strftime("%d/%m/%Y")
    
    @staticmethod
    def validate_contact_info(contact: str) -> Tuple[bool, str]:
        """Validate contact information (phone or email)"""
        contact = contact.strip()
        
        if not contact:
            return False, ""
        
        # Check if it's an email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, contact):
            return True, contact.lower()
        
        # Check if it's a phone number
        # Remove common formatting characters
        phone = re.sub(r'[\\s\\-\\(\\)\\+]', '', contact)
        
        # Check if it's a valid phone number (6-15 digits, optionally starting with +)
        phone_pattern = r'^\\+?[0-9]{6,15}$'
        if re.match(phone_pattern, phone):
            return True, contact
        
        return False, ""
    
    @staticmethod
    def validate_datetime_preference(datetime_str: str) -> Tuple[bool, str]:
        """Validate preferred datetime for scheduling"""
        datetime_str = datetime_str.strip()
        
        if not datetime_str:
            return False, ""
        
        # For scheduling, we allow more flexible input
        # User can provide natural language like "Next Monday 2 PM" or "25/12/2024 14:00"
        
        # Try to parse structured datetime first
        datetime_formats = [
            "%d/%m/%Y %H:%M",    # 25/12/2024 14:30
            "%d-%m-%Y %H:%M",    # 25-12-2024 14:30
            "%Y-%m-%d %H:%M",    # 2024-12-25 14:30
            "%d/%m/%Y %I:%M %p", # 25/12/2024 2:30 PM
        ]
        
        for date_format in datetime_formats:
            try:
                parsed_datetime = datetime.strptime(datetime_str, date_format)
                
                # Check if datetime is in the future
                if parsed_datetime <= datetime.now():
                    return False, ""
                
                # Check if it's business hours (8 AM - 6 PM, Mon-Fri)
                if parsed_datetime.weekday() >= 5:  # Weekend
                    return True, f"{datetime_str} (Weekend - will confirm availability)"
                
                if parsed_datetime.hour < 8 or parsed_datetime.hour > 18:
                    return True, f"{datetime_str} (Outside business hours - will confirm availability)"
                
                return True, datetime_str
                
            except ValueError:
                continue
        
        # If structured parsing fails, accept natural language but mark for manual processing
        if len(datetime_str) >= 5:  # Reasonable minimum length
            return True, f"{datetime_str} (Will confirm specific time)"
        
        return False, ""
    
    @staticmethod
    def validate_message_text(message: str) -> Tuple[bool, str]:
        """Validate message text"""
        message = message.strip()
        
        if not message:
            return False, ""
        
        if len(message) < 5:
            return False, "Message is too short (minimum 5 characters)"
        
        if len(message) > 1000:
            return False, "Message is too long (maximum 1000 characters)"
        
        return True, message
    
    @staticmethod
    def validate_service_selection(service_input: str, available_services: list) -> Tuple[bool, str]:
        """Validate service selection"""
        if not service_input:
            return False, ""
        
        service_input = service_input.strip()
        
        # Check exact match first
        for service in available_services:
            if service.lower() == service_input.lower():
                return True, service
        
        # Check partial match
        matches = [s for s in available_services if service_input.lower() in s.lower()]
        if len(matches) == 1:
            return True, matches[0]
        
        return False, ""
    
    @staticmethod
    def sanitize_text_for_html(text: str) -> str:
        """Sanitize text for HTML display"""
        # Replace HTML entities
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text
    
    @staticmethod
    def format_contact_display(contact: str) -> str:
        """Format contact information for display"""
        if '@' in contact:
            # It's an email
            return f"📧 {contact}"
        else:
            # It's a phone number
            return f"📞 {contact}"