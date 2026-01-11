from datetime import datetime, timedelta
from typing import List, Dict, Optional


def plan_smart_schedule(
    issues: List[Dict],
    tickets: List[Dict],
    start_date: datetime,
    work_hours: dict,
    slot_minutes: int,
    work_days: list = None,
    rest_days_per_week: int = 1,
) -> List[tuple]:
    """
    Intelligently schedule issues based on their estimates.
    
    Algorithm:
    - Match issues with tickets from contract by title similarity
    - Sort tickets by estimate (smallest first for quick wins)
    - Space slots based on estimate: estimate_slots = days between tickets
    - One slot per ticket
    - Schedule outside working hours
    - Leave rest days (weekends + personal time)
    
    Args:
        issues: List of GitHub issues (dict with 'title', 'number', etc.)
        tickets: List of tickets from contract (dict with 'name', 'estimate_slots')
        start_date: Starting date for scheduling
        work_hours: Dict with "start" and "end" times
        slot_minutes: Duration of each slot
        work_days: List of work days
        rest_days_per_week: Number of rest days per week (default: 1 for weekends)
    
    Returns:
        List of tuples: (issue, slot_datetime, estimate)
    """

    if work_days is None:
        work_days = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]
    else:
        work_days_set = set(day.upper() for day in work_days)
        if "SA" not in work_days_set:
            work_days.append("SA")
        if "SU" not in work_days_set:
            work_days.append("SU")
    
    day_map = {
        "MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6
    }
    work_day_numbers = {day_map.get(day.upper(), -1) for day in work_days}
    
    def match_issue_to_ticket(issue_title: str, tickets: List[Dict]) -> Optional[Dict]:
        """Match issue title with ticket name (simple substring matching)"""
        issue_lower = issue_title.lower()
        for ticket in tickets:
            ticket_name = ticket.get("name", "").lower()
            if ticket_name in issue_lower or issue_lower in ticket_name:
                return ticket
            issue_words = set(issue_lower.split()[:4])
            ticket_words = set(ticket_name.split()[:4])
            if len(issue_words.intersection(ticket_words)) >= 2:
                return ticket
        return None
    
    issue_ticket_pairs = []
    for issue in issues:
        ticket = match_issue_to_ticket(issue["title"], tickets)
        if ticket:
            estimate = ticket.get("estimate_slots") or 3
            issue_ticket_pairs.append((issue, ticket, estimate))
        else:
            issue_ticket_pairs.append((issue, None, 3))
    
    issue_ticket_pairs.sort(key=lambda x: x[2])
    
    schedule = []
    current_date = start_date.replace(hour=18, minute=0, second=0, microsecond=0)  # Start evening
    if current_date < datetime.now():
        current_date = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    
    start_hour = int(work_hours["start"].split(":")[0])
    start_minute = int(work_hours["start"].split(":")[1]) if ":" in work_hours["start"] and len(work_hours["start"].split(":")[1]) > 0 else 0
    end_hour = int(work_hours["end"].split(":")[0])
    end_minute = int(work_hours["end"].split(":")[1]) if ":" in work_hours["end"] and len(work_hours["end"].split(":")[1]) > 0 else 0
    
    morning_hour = 7
    morning_minute = 0
    
    evening_hour = end_hour
    evening_minute = end_minute
    
    consecutive_work_days = 0
    max_consecutive_days = 7
    
    for issue, ticket, estimate in issue_ticket_pairs:
        slot_found = False
        attempts = 0
        max_attempts = 365
        
        while not slot_found and attempts < max_attempts:
            if current_date.weekday() in work_day_numbers:
                use_morning = len(schedule) % 2 == 0
                
                if use_morning:
                    slot_time = current_date.replace(hour=morning_hour, minute=morning_minute)
                else:
                    slot_time = current_date.replace(hour=evening_hour, minute=evening_minute)
                
                if slot_time > datetime.now():
                    schedule.append((issue, slot_time, estimate))
                    slot_found = True
                    
                    # Calculate spacing based on estimate
                    # Estimate 1-2: 1 day spacing
                    # Estimate 3-5: 2-3 days spacing
                    # Estimate 8+: estimate/2 days spacing
                    if estimate <= 2:
                        days_spacing = 1
                    elif estimate <= 5:
                        days_spacing = 2
                    else:
                        days_spacing = max(3, estimate // 2)
                    
                    current_date += timedelta(days=days_spacing)
                    consecutive_work_days += days_spacing
                    
                    if consecutive_work_days >= max_consecutive_days:
                        current_date += timedelta(days=rest_days_per_week)
                        consecutive_work_days = 0
                    
                    break
            
            current_date += timedelta(days=1)
            attempts += 1
        
        if not slot_found:
            print(f"⚠️ Could not schedule issue #{issue['number']}: {issue['title']}")
    
    return schedule
