class StatusCodes:
    '''Class for protocol status codes'''

    def _compose_message(self, code: int, status: str, message: str = None):
        text = "{} {}".format(code, status)
        if message:
            text = "{} - {}".format(text, message)
        return message

    def idle(self, status_text=None):
        '''Status of a protocol that is runnning

        Args:
            status_text (str): Custom status text to add to message.
                               (Default: None)

        '''
        return self._compose_message(0, "Idle", status_text)

    def running(self, status_text=None):
        '''Status of a protocol that is runnning

        Args:
            status_text (str): Custom status text to add to message.
                               (Default: None)

        '''
        return self._compose_message(1, "Running", status_text)

    def stopped(self, status_text: str):
        '''Status of a protocol that was stopped before completion

        Args:
            status_text: Custom status text to add to message

        '''
        return self._compose_message(2, "Stopped", status_text)
