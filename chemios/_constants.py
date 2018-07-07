class StatusCodes:
    '''Class for protocol status codes'''

    @staticmethod
    def _compose_message(code: int, status: str, message: str = None):  
        text = "{} {}".format(code, status)
        if message:
            text = "{} - {}".format(text, message)
        return text

    @classmethod
    def idle(cls, status_text=None):
        '''Status of a protocol that is idle

        Args:
            status_text (str): Custom status text to add to message.
                               (Default: None)

        '''
        return cls._compose_message(100, "Idle", status_text)

    @classmethod
    def running(cls, status_text=None):
        '''Status of a protocol that is runnning

        Args:
            status_text (str): Custom status text to add to message.
                               (Default: None)

        '''
        return cls._compose_message(200, "Running", status_text)

    @classmethod
    def stopped(cls, status_text=None):
        '''Status of a protocol that was stopped before completion

        Args:
            status_text: Custom status text to add to message

        '''
        return cls._compose_message(300, "Stopped", status_text)
