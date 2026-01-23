import requests
from flask import current_app

class WebOperatingLayerClient:
    """
    Acts as the bridge between HR UI (Module 1) and Web Operating Layer (Module 2).
    """
    
    @staticmethod
    def send_action(candidate_id, action_type):
        """
        Sends a request to Module 2 to initiate Screening, Shortlisting, etc.
        """
        url = f"{current_app.config['MODULE_2_API_URL']}/execute_action"
        payload = {
            "candidate_id": candidate_id,
            "action": action_type,
            "initiated_by": "HR_Admin" # In real app, use current_user.id
        }
        
        try:
            # We mock the response for now until Module 2 is built
            # response = requests.post(url, json=payload)
            # return response.json()
            
            # MOCK RETURN to allow UI testing:
            return {
                "status": "success", 
                "ethical_decision": "Allow", 
                "message": f"{action_type} initiated successfully. Ethics checks passed."
            }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": str(e)}