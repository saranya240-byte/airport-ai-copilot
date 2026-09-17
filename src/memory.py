class ConversationMemory:
    """
    Short-term conversational memory for the Airport Operations Copilot.
    Keeps recent user requests, responses, and the active airport.
    """

    def __init__(self, max_turns=10):
        self.max_turns = max_turns
        self.history = []
        self.active_airport = None

    def set_airport(self, airport_code):
        if airport_code:
            self.active_airport = airport_code.upper().strip()

    def get_airport(self):
        return self.active_airport

    def add_turn(self, user_message, assistant_message):
        self.history.append(
            {
                "user": user_message,
                "assistant": assistant_message,
            }
        )

        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]

    def get_context(self):
        return self.history[-self.max_turns:]

    def clear(self):
        self.history = []
        self.active_airport = None
