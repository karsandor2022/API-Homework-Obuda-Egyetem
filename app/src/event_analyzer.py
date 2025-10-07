class EventAnalyzer:
    def __init__(self, events):
        self.events = events

    def get_joiners_multiple_meetings(self):
        joiners = {}
        for event in self.events:
            for joiner in event['joiners']:
                if joiner['email'] in joiners:
                    joiners[joiner['email']]['meetings_attended'] += 1
                else:
                    joiners[joiner['email']] = {
                        'full_name': joiner['name'],
                        'email': joiner['email'],
                        'meetings_attended': 1
                    }

        # Filter joiners who attended at least 2 meetings
        filtered_joiners = [joiner for joiner in joiners.values() if joiner['meetings_attended'] >= 2]

        return filtered_joiners