schema = {
    'hangup_call': {
        "type": "function",
        "function": {
            "name": "hangup_call",
            "description": "Thanks callee for their time and ends or hangs up the phone call.",
            "parameters": {
                "type": "object",
                "properties": {
                    "msg": {
                        "type": "string",
                        "description": "A polite message spoken to the callee before hanging up the call. This message should express gratitude and provide a courteous closing."
                    }    
                },
                "additionalProperties": False
            },
            "strict": True
        }
    }
}   