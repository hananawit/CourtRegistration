
import re
import base64
import webbrowser
from typing import Dict, Text, Any, List, Union, Optional
import datetime
from rasa_sdk import Tracker, Action 
from rasa_sdk.executor import CollectingDispatcher 
from rasa_sdk.forms import FormAction,ActiveLoop
from rasa_sdk.events import AllSlotsReset, SlotSet,EventType,FollowupAction
from datetime import date
from rasa_sdk.types import DomainDict
from pyrsistent import v
from rasa_sdk import Tracker,FormValidationAction
from rasa_sdk.events import SlotSet,AllSlotsReset
import requests
import json
from rasa_sdk import Action, Tracker, logger
from rasa_sdk.events import SlotSet, EventType



access_token1 = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbWFpbCI6IiIsInN1YiI6IjUyYTYyYWIwLTExYmEtNDdlYS1hNDI5LWE3ZjQ5MGNjOTYxNyIsInJvbGUiOnsiaWQiOiI1ODkxYzYzOS1kZmI3LTRmMWItYTMwZi02NmEzNDI4ODRjM2MiLCJuYW1lIjoiY2xpZW50IiwiY29kZSI6IkJSQU5DSF9MRVZFTCJ9LCJjb3VydExldmVsSWQiOm51bGwsImJyYW5jaElkIjpudWxsLCJpYXQiOjE3NzAzMDA0NzAsImV4cCI6MTc3MDkwNTI3MH0.BAlRYxKHy47ITW_7Qxpx5oTMtf5lvIVZ4IR7wUecIY4"

# referenceNumber=''
# isCaseNumberAvailable= ''


class GlobalVariables:
    referenceNumber = None
    isCaseNumberAvailable = None
    access_token = None
    data = {"documents": "", "extension": ""}

def send_login_register_buttons(dispatcher, tracker):
    """Helper function to send login and register buttons when user is not authenticated"""
    # Capture the current intent as previous_intent for routing after login
    current_intent = tracker.latest_message.get("intent", {}).get("name")

    buttons = [
        {"title": "📝 ምዝገባ", "payload": "/register"},
        {"title": "🔐 መግባት", "payload": "/login"},
        {"title": "❌ ሰርዝ", "payload": "/cancel"}
    ]
    dispatcher.utter_message(
        text="📋 ቅሬታ ለመግባት መመዝገብ ወይም መግባት ያስፈልግዎታል።",
        buttons=buttons
    )

    # Return SlotSet for previous_intent if current_intent exists
    if current_intent:
        return [SlotSet("previous_intent", current_intent)]
    return []

def connected_to_internet(url='http://10.10.20.211:8080/apis/myfeedback', timeout=120):
    print(url)
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("No connection available. from int")
    return False




class ActionResetAllSlots(Action):
    def name(self) -> Text:
        return "action_reset_all_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
   
        return [AllSlotsReset()]
# =============== REGISTRATION FORM ===============
class RegistrationForm(FormAction):
    def name(self) -> Text:
        return "registration_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["phone", "password"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "phone": [self.from_text()],
            "password": [self.from_text()],
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("Registration form submitted")
        phone = tracker.get_slot("phone")
        password = tracker.get_slot("password")

        # Basic validation
        if not phone or not password:
            dispatcher.utter_message(text="እባክዎ ሁሉንም መረጃ ያስገቡ")
            return [SlotSet("phone", None), SlotSet("password", None), FollowupAction("registration_form")]

        return [FollowupAction("action_register_user")]

# =============== LOGIN FORM ===============
class LoginForm(FormAction):
    def name(self) -> Text:
        return "login_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["phone", "password"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "phone": [self.from_text()],
            "password": [self.from_text()],
        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        print("Login form submitted")
        phone = tracker.get_slot("phone")
        password = tracker.get_slot("password")

        # Basic validation
        if not phone or not password:
            dispatcher.utter_message(text="እባክዎ ሁሉንም መረጃ ያስገቡ")
            return [SlotSet("phone", None), SlotSet("password", None), FollowupAction("login_form")]

        return [FollowupAction("action_login_user")]

# =============== MAIN REGISTRATION ACTION ===============
class ActionRegisterUser(Action):
    def name(self) -> Text:
        return "action_register_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        phone = tracker.get_slot("phone")
        password = tracker.get_slot("password")

        print(f"=== REGISTRATION ===")
        print(f"Phone: {phone}")
        print(f"Password: {password}")

        if not phone or not password:
            dispatcher.utter_message(text="እባክዎ ሁሉንም መረጃ ያስገቡ")
            return [SlotSet("phone", None), SlotSet("password", None), FollowupAction("registration_form")]
        
        # Clean phone
        phone = phone.replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            phone = "+251" + phone[1:]
        elif not phone.startswith("+") and len(phone) == 9:
            phone = "+251" + phone
        elif not phone.startswith("+"):
            phone = "+" + phone
        
        registration_data = {
            "phone": phone,
            "password": password
        }
        
        try:
            response = requests.post(
                "https://court-api.zorcloud.net/auth/client/register",
                json=registration_data,
                headers={"Content-Type": "application/json"},
                timeout=50
            )
            
            print(f"API Status: {response.status_code}")
            
            if response.status_code == 201:
                response_data = response.json()
                access_token = response_data.get("access_token")
                user_id = response_data.get("user", {}).get("id")
                
                dispatcher.utter_message(
                    text="✅ ምዝገባዎ ተጠናቅቋል! አሁን ይግቡ።"
                )
                
                return [
                    SlotSet("access_token", access_token),
                    SlotSet("user_id", user_id),
                    SlotSet("is_registered", True),
                    SlotSet("phone", phone),  # Keep for auto-fill
                    SlotSet("password", None),
                    FollowupAction("login_form")
                ]
                
            elif response.status_code == 400:
                error_data = response.json()
                message = error_data.get("message", "")
                
                if "already registered" in message.lower():
                    dispatcher.utter_message(
                        text="📱 ይህ ስልክ ቁጥር ከዚህ በፊት ተመዝግቧል። እባክዎ ይግቡ።"
                    )
                    return [FollowupAction("login_form")]
                else:
                    dispatcher.utter_message(text=f"❌ {message}")
                    
            else:
                dispatcher.utter_message(text="❌ ምዝገባ አልተሳካም።")
                
        except Exception as e:
            print(f"Error: {e}")
            dispatcher.utter_message(text="❌ አንድ ስህተት ተከስቷል።")
        
        return [SlotSet("phone", None), SlotSet("password", None)]

# =============== MAIN LOGIN ACTION ===============
class ActionPostLoginMenu(Action):
    def name(self) -> Text:
        return "action_post_login_menu"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [
            {"title": "ቅሬታ ማስገባት", "payload": "/start_complaint"},
            {"title": "ቅሬታዎች እኔ", "payload": "/show_my_complaints"},
            {"title": "አቤቱታ አስገባ", "payload": "/appeal_complaint"}
        ]
        dispatcher.utter_message(text="ምን ያስፈልግዎታል?", buttons=buttons, button_type="vertical")
        return []

# class ActionCheckAuth(Action):
#     def name(self) -> Text:
#         return "action_check_auth"

#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any]
#     ) -> List[Dict[Text, Any]]:

#         # 🔐 Always read from slot (Rasa-safe)
#         access_token = tracker.get_slot("access_token")

#         print("====================================")
#         print("DEBUG: ActionCheckAuth")
#         print("DEBUG: access_token from slot:", access_token)
#         print("====================================")

#         # 🧪 STATIC TOKEN FOR TESTING (remove in prod)
#         if not access_token:
#             print("DEBUG: No token in slot → using static test token")
#         access_token = "eyJhbGciOiJIUzI1NiIsSTATIC_TEST_TOKEN"

#         # ❌ Still no token → force login
#         if not access_token:
#             dispatcher.utter_message(
#                 text="📋 ቅሬታ ለመግባት መጀመሪያ መግባት ያስፈልግዎታል።"
#             )
#             return [FollowupAction("login_form")]

#         # ✅ Auth header
#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Accept": "application/json"
#         }

#         case_number = "00/0001/12345"
#         url = f"http://213.55.79.158:8080/api/SearchCase?caseNumber={case_number}"

#         print("DEBUG: Calling API:", url)
#         print("DEBUG: Authorization Header:", headers["Authorization"][:30], "...")

#         try:
#             response = requests.get(url, headers=headers, timeout=30)

#             print("DEBUG: API Status Code:", response.status_code)

#             if response.status_code == 200:
#                 data = response.json()
#                 dispatcher.utter_message(
#                     text="✅ በስርዓቱ ውስጥ መግባት ተሳክቷል። መቀጠል ይችላሉ።"
#                 )

#                 # 🔁 Continue flow
#                 return [FollowupAction("clarification_form_am")]

#             elif response.status_code in [401, 403]:
#                 dispatcher.utter_message(
#                     text="❌ የመግባት ፈቃድ ጊዜው አልፎታል። እባክዎ እንደገና ይግቡ።"
#             )
#             return [FollowupAction("login_form")]

#         else:
#             dispatcher.utter_message(
#                 text="❌ ከሰርቨር ጋር ችግር ተፈጥሯል። እባክዎ ቆይተው ይሞክሩ።"
#             )
#             return []

#         except Exception as e:
#             print("ERROR: API call failed:", e)
#             dispatcher.utter_message(
#                 text="⚠️ ስህተት ተከስቷል። እባክዎ እንደገና ይሞክሩ።"
#             )
#             return []

class ActionLoginUser(Action):
    def name(self) -> Text:
        return "action_login_user"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        phone = tracker.get_slot("phone")
        password = tracker.get_slot("password")

        print(f"=== LOGIN ===")
        print(f"Phone: {phone}")
        print(f"Password: {password}")

        if not phone or not password:
            dispatcher.utter_message(text="እባክዎ ሁሉንም መረጃ ያስገቡ")
            return [SlotSet("phone", None), SlotSet("password", None), FollowupAction("login_form")]

        # Clean phone
        phone = phone.replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            phone = "+251" + phone[1:]
        elif not phone.startswith("+") and len(phone) == 9:
            phone = "+251" + phone
        elif not phone.startswith("+"):
            phone = "+" + phone

        login_data = {
            "phone": phone,
            "password": password
        }

        try:
            response = requests.post(
                "https://court-api.zorcloud.net/auth/client/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=50
            )

            print(f"Login API Status: {response.status_code}")

            if response.status_code in [200, 201]:
                response_data = response.json()
                print(f"DEBUG: Login response_data: {response_data}")
                access_token = response_data.get("access_token")

                user_id = response_data.get("user", {}).get("id")
                print(f"DEBUG: Extracted access_token: {access_token[:20] if access_token else None}")

                if access_token:
                    print(f"DEBUG: Login successful, access_token: {access_token[:20]}...")
                    dispatcher.utter_message(text="✅ በተሳካ ሁኔታ ገብተዋል!")

                    # Route based on previous intent
                    previous_intent = tracker.get_slot("previous_intent")
                    followup_action = "action_post_login_menu"  # default for "login" intent

                    if previous_intent == "start_complaint":
                        followup_action = "check_ref_number_am"
                    elif previous_intent == "show_my_complaints":
                        followup_action = "action_show_my_complaints"
                    elif previous_intent == "appeal_complaint":
                        followup_action = "action_appeal_complaint"
                    # For "login" intent or default, show menu

                    return [
                        SlotSet("access_token", access_token),
                        SlotSet("user_id", user_id),
                        SlotSet("is_logged_in", True),
                        SlotSet("phone", None),
                        SlotSet("password", None),
                        FollowupAction(followup_action)
                    ]
                else:
                    dispatcher.utter_message(text="❌ መግባት አልተሳካም። እባክዎ እንደገና ይሞክሩ።")
                    return [SlotSet("phone", None), SlotSet("password", None), FollowupAction("login_form")]

            elif response.status_code == 401:
                dispatcher.utter_message(text="❌ ስልክ ቁጥር ወይም የይለፍ ቃል የተሳሳተ ነው። እባክዎ እንደገና ያስገቡ።")
                return [SlotSet("phone", None), SlotSet("password", None), FollowupAction("login_form")]

            else:
                dispatcher.utter_message(text="❌ መግባት አልተሳካም። እባክዎ እንደገና ይሞክሩ።")
                return [SlotSet("phone", None), SlotSet("password", None), FollowupAction("login_form")]

        except Exception as e:
            print(f"Login Error: {e}")
            dispatcher.utter_message(text="❌ አንድ ስህተት ተከስቷል። እባክዎ እንደገና ይሞክሩ።")
            return [SlotSet("phone", None), SlotSet("password", None), FollowupAction("login_form")]


# =============== SHOW MY COMPLAINTS ACTION ===============
class ActionShowMyComplaints(Action):
    def name(self) -> Text:
        return "action_show_my_complaints"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        access_token = access_token1

        if not access_token:
            send_login_register_buttons(dispatcher, tracker)
            return []

        try:
            api_url = "https://court-api.zorcloud.net/complaints/my-complaints"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code != 200:
                dispatcher.utter_message(text="ቅሬታዎችን ለማሳየት አልተሳካም።")
                return []

            complaints_data = response.json()

            if not complaints_data.get("data"):
                dispatcher.utter_message(text="ምንም ቅሬታ አልተገኘም።")
                return []

            complaints = complaints_data["data"]

            # Store complaints data for later use (to get IDs)
            user_complaints = []
            for complaint in complaints:
                user_complaints.append({
                    "id": complaint.get("id"),
                    "reference_no": complaint.get("reference_no", "N/A")
                })

            # Instead of buttons, use quick_replies
            quick_replies = []
            for complaint in complaints:
                ref_no = complaint.get("reference_no", "N/A")
                payload = f'/select_complaint{{"reference_no": "{ref_no}"}}'
                quick_replies.append({"title": ref_no, "payload": payload})

            dispatcher.utter_message(
                text="እባክዎ ቅሬታ ይምረጡ:",
                quick_replies=quick_replies
            )

        except Exception as e:
            print(f"Error fetching complaints: {e}")
            dispatcher.utter_message(text="ስህተት ተፈጥሯል።")

        return [SlotSet("user_complaints", user_complaints)]

# =============== SELECT COMPLAINT ACTION ===============
class ActionSelectComplaint(Action):
    def name(self) -> Text:
        return "action_select_complaint"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_text = tracker.latest_message.get("text", "")
        intent_name = tracker.latest_message.get("intent", {}).get("name")

        # If a view/appeal payload was routed here by mistake, redirect safely.
        if intent_name == "view_complaint_detail" or "/view_complaint_detail" in user_text or user_text.startswith("view_"):
            reference_no = tracker.get_slot("selected_complaint_ref")
            if not reference_no and "reference_no" in user_text:
                match = re.search(r'reference_no\"\s*:\s*\"([^\"]+)\"', user_text)
                if match:
                    reference_no = match.group(1)
            if not reference_no and user_text.startswith("view_"):
                reference_no = user_text.replace("view_", "", 1).strip()

            events: List[EventType] = []
            if reference_no:
                events.append(SlotSet("selected_complaint_ref", reference_no))
            events.append(FollowupAction("action_view_complaint_detail"))
            return events

        if intent_name == "appeal_complaint" or "/appeal_complaint" in user_text or user_text.startswith("appeal_"):
            reference_no = tracker.get_slot("selected_complaint_ref")
            if not reference_no and "reference_no" in user_text:
                match = re.search(r'reference_no\"\s*:\s*\"([^\"]+)\"', user_text)
                if match:
                    reference_no = match.group(1)
            if not reference_no and user_text.startswith("appeal_"):
                reference_no = user_text.replace("appeal_", "", 1).strip()

            events = []
            if reference_no:
                events.append(SlotSet("selected_complaint_ref", reference_no))
            events.append(FollowupAction("action_appeal_complaint"))
            return events

        # Extract reference_no from payload
        reference_no = None

        # Method 1: Entity parsed from intent payload (/select_complaint{"reference_no": "REF-..."})
        for entity in tracker.latest_message.get("entities", []):
            if entity.get("entity") == "reference_no":
                reference_no = entity.get("value")
                if reference_no:
                    print(f"DEBUG: Extracted reference_no from entity: {reference_no}")
                break

        # Method 2: Regex extract from JSON in text (handles optional space after intent)
        if not reference_no and "reference_no" in user_text:
            match = re.search(r'reference_no\"\s*:\s*\"([^\"]+)\"', user_text)
            if match:
                reference_no = match.group(1)
                print(f"DEBUG: Extracted reference_no from JSON text: {reference_no}")

        # Method 3: Parse JSON part after /select_complaint (handles optional leading space)
        if not reference_no and "/select_complaint" in user_text:
            json_start = user_text.find("/select_complaint") + len("/select_complaint")
            json_str = user_text[json_start:].strip()
            if json_str.startswith("{") and json_str.endswith("}"):
                try:
                    data = json.loads(json_str)
                    reference_no = data.get("reference_no")
                    if reference_no:
                        print(f"DEBUG: Extracted reference_no from select_complaint JSON: {reference_no}")
                except json.JSONDecodeError:
                    pass

        # Method 4: Text payload like "/select_complaint REF-..." (space separated)
        if not reference_no and user_text.startswith("/select_complaint "):
            reference_no = user_text.replace("/select_complaint ", "", 1).strip()
            print(f"DEBUG: Extracted reference_no from intent payload: {reference_no}")

        # Method 5: Direct text fallback (button title may be the reference number)
        if not reference_no and user_text and user_text.strip():
            reference_no = user_text.strip()
            print(f"DEBUG: Extracted reference_no from direct payload: {reference_no}")

        if reference_no:
            # Clean the reference number
            reference_no = reference_no.strip()

            dispatcher.utter_message(text=f"ቅሬታ {reference_no} ተመርጧል።")

            # Telegram callback_data is length-limited, so keep payloads short.
            buttons = [
                {"title": "ዝርዝር አሳይ", "payload": "/view_complaint_detail"},
                {"title": "አቤቱታ አስገባ", "payload": "/appeal_complaint"},
                {"title": "ተመለስ", "payload": "/show_my_complaints"}
            ]

            dispatcher.utter_message(
                text="ምን ያስፈልግዎታል?",
                buttons=buttons,
                button_type="vertical"
            )

            return [SlotSet("selected_complaint_ref", reference_no)]

        dispatcher.utter_message(text="እባክዎ ትክክለኛ ቅሬታ ይምረጡ።")
        return []

# =============== VIEW COMPLAINT DETAIL ACTION ===============
class ActionViewComplaintDetail(Action):
    def name(self) -> Text:
        return "action_view_complaint_detail"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # First try to get reference_no from the selected_complaint_ref slot
        reference_no = tracker.get_slot("selected_complaint_ref")

        # If not available, extract from payload as fallback
        if not reference_no:
            user_text = tracker.latest_message.get("text", "")
            intent_name = tracker.latest_message.get("intent", {}).get("name")

            # Method 1: If intent is view_complaint_detail, text is the reference_no
            if intent_name == "view_complaint_detail":
                reference_no = user_text.strip()
                print(f"DEBUG: Extracted reference_no from view_complaint_detail intent: {reference_no}")

            # Method 2: Extract from intent payload "/view_complaint_detail {reference_no}"
            elif user_text.startswith("/view_complaint_detail "):
                reference_no = user_text.replace("/view_complaint_detail ", "", 1).strip()
                print(f"DEBUG: Extracted reference_no from intent payload: {reference_no}")

            # Method 3: Extract from JSON payload (primary)
            elif "reference_no" in user_text:
                import re
                match = re.search(r'reference_no\":\s*\"([^\"]+)\"', user_text)
                if match:
                    reference_no = match.group(1)
                    print(f"DEBUG: Extracted reference_no from JSON: {reference_no}")

            # Method 4: Extract from "view_" prefix (fallback)
            elif user_text.startswith("view_"):
                reference_no = user_text.replace("view_", "", 1)
                print(f"DEBUG: Extracted reference_no from view_ prefix: {reference_no}")

        if not reference_no:
            dispatcher.utter_message(text="እባክዎ ትክክለኛ ቅሬታ ይምረጡ።")
            return []

        # Find the complaint ID from stored user_complaints data
        user_complaints = tracker.get_slot("user_complaints") or []
        complaint_id = None
        for complaint in user_complaints:
            if isinstance(complaint, dict) and complaint.get("reference_no") == reference_no:
                complaint_id = complaint.get("id")
                break

        if not complaint_id:
            dispatcher.utter_message(text="ቅሬታ ዝርዝሮችን ለማሳየት አልተሳካም።")
            return []

        access_token = access_token1

        if not access_token:
            send_login_register_buttons(dispatcher, tracker)
            return []

        try:
            api_url = f"https://court-api.zorcloud.net/complaints/{complaint_id}"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code != 200:
                dispatcher.utter_message(text="ቅሬታ ዝርዝሮችን ለማሳየት አልተሳካም።")
                return []

            complaint_data = response.json()

            def first_value(*values):
                for value in values:
                    if value not in (None, "", []):
                        return value
                return "N/A"

            def format_date(value: Optional[Text]) -> Text:
                if not value:
                    return "N/A"
                if isinstance(value, str) and "T" in value:
                    return value.split("T", 1)[0]
                return str(value)

            reference_display = first_value(
                complaint_data.get("reference_no"),
                complaint_data.get("referenceNo"),
                reference_no
            )
            case_number = first_value(
                complaint_data.get("case_no"),
                complaint_data.get("case_number"),
                complaint_data.get("caseNumber")
            )
            content = first_value(
                complaint_data.get("content"),
                complaint_data.get("complaint"),
                complaint_data.get("description")
            )
            branch_name = first_value(
                (complaint_data.get("branch") or {}).get("name"),
                complaint_data.get("branch_name"),
                complaint_data.get("branchName")
            )
            organization_name = first_value(
                (complaint_data.get("organization") or {}).get("name"),
                complaint_data.get("organization_name"),
                complaint_data.get("organizationName"),
                (complaint_data.get("department") or {}).get("name")
            )
            current_status = first_value(
                (complaint_data.get("currentStatus") or {}).get("name"),
                (complaint_data.get("status") or {}).get("name"),
                complaint_data.get("status")
            )
            created_at = format_date(first_value(
                complaint_data.get("createdAt"),
                complaint_data.get("created_at")
            ))
            updated_at = format_date(first_value(
                complaint_data.get("updatedAt"),
                complaint_data.get("updated_at")
            ))

            details_text = (
                f"🔢 ማጣቀሻ ቁጥር: {reference_display}\n"
                f"📝 የጉዳይ ቁጥር: {case_number}\n"
                f"📄 የቅሬታ ፍሬ: {content}\n"
                f"🏛️ ቅርንጫፍ: {branch_name}\n"
                f"🏢 ክፍል: {organization_name}\n"
                f"📊 ሁኔታ: {current_status}\n"
                f"📅 የተፈጠረበት ቀን: {created_at}\n"
                f"🔄 የተሻሻለበት ቀን: {updated_at}"
            )
            dispatcher.utter_message(text=details_text)

            # Show buttons for appeal and back (Telegram-friendly payloads)
            buttons = [
                {"title": "አቤቱታ አስገባ", "payload": "/appeal_complaint"},
                {"title": "ተመለስ", "payload": "/show_my_complaints"}
            ]
            dispatcher.utter_message(
                text="ምን ያስፈልግዎታል?",
                buttons=buttons,
                button_type="vertical"
            )

        except Exception as e:
            print(f"Error fetching complaint details: {e}")
            dispatcher.utter_message(text="ስህተት ተፈጥሯል።")

        return []

# =============== APPEAL COMPLAINT ACTION ===============
class ActionAppealComplaint(Action):
    def name(self) -> Text:
        return "action_appeal_complaint"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Extract reference_no from payload or slot
        user_text = tracker.latest_message.get("text", "")
        reference_no = tracker.get_slot("selected_complaint_ref")

        # Method 1: Extract from "appeal_" prefix (legacy)
        if not reference_no and user_text.startswith("appeal_"):
            reference_no = user_text.replace("appeal_", "", 1)
            print(f"DEBUG: Extracted reference_no from appeal_ prefix: {reference_no}")

        # Method 2: Extract from JSON payload (fallback)
        if not reference_no and "reference_no" in user_text:
            import re
            match = re.search(r'reference_no\":\s*\"([^\"]+)\"', user_text)
            if match:
                reference_no = match.group(1)

        if reference_no:
            # Find the complaint ID from stored user_complaints data
            user_complaints = tracker.get_slot("user_complaints") or []
            complaint_id = None
            for complaint in user_complaints:
                if isinstance(complaint, dict) and complaint.get("reference_no") == reference_no:
                    complaint_id = complaint.get("id")
                    break

            if not complaint_id:
                dispatcher.utter_message(text="ቅሬታ አልተገኘም።")
                return []

            access_token = access_token1

            if not access_token:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ።")
                return []

            try:
                api_url = f"https://court-api.zorcloud.net/complaints/{complaint_id}"
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }

                response = requests.get(api_url, headers=headers, timeout=10)

                if response.status_code != 200:
                    dispatcher.utter_message(text="ቅሬታ ዝርዝሮችን ለማሳየት አልተሳካም።")
                    return []

                complaint_data = response.json()
                status_code = (complaint_data.get("currentStatus") or {}).get("code", "") or ""
                status_name = (complaint_data.get("currentStatus") or {}).get("name", "") or ""
                normalized_status = status_code.lower() or status_name.lower()

                # Only allow appeals for final decision statuses
                allowed_statuses = {"rejected", "closed", "resolved"}
                if normalized_status and normalized_status not in allowed_statuses:
                    dispatcher.utter_message(
                        text="አቤቱታ ለመስጠት ቅሬታው በመጨረሻ ውሳኔ ሁኔታ መሆን አለበት (ተቀባይነት አልተሰጠም/ተዘግቷል/ተጠናቅቋል)।"
                    )
                    return []

                # Ask for appeal reason
                dispatcher.utter_message(text="እባክዎ የአቤቱታዎን ምክንያት በአጭር ያስገቡ።")
                return [
                    SlotSet("appeal_complaint_id", complaint_id),
                    SlotSet("appeal_reference_no", reference_no),
                    SlotSet("is_appeal", True)
                ]

            except Exception as e:
                print(f"Error fetching complaint details for appeal: {e}")
                dispatcher.utter_message(text="ስህተት ተፈጥሯል።")
                return []

        else:
            # No reference_no provided, show complaints for selection
            dispatcher.utter_message(text="አቤቱታ ለመስጠት ቅሬታዎን ይምረጡ።")

            # Set a slot to indicate this is an appeal
            return [
                SlotSet("is_appeal", True),
                FollowupAction("action_show_my_complaints")
            ]

# =============== SUBMIT APPEAL ACTION ===============
class ActionSubmitAppeal(Action):
    def name(self) -> Text:
        return "action_submit_appeal"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        appeal_reason = tracker.latest_message.get("text", "").strip()
        complaint_id = tracker.get_slot("appeal_complaint_id")
        reference_no = tracker.get_slot("appeal_reference_no")

        if not complaint_id:
            dispatcher.utter_message(text="እባክዎ መጀመሪያ ቅሬታዎን ይምረጡ።")
            return [FollowupAction("action_show_my_complaints")]

        if not appeal_reason:
            dispatcher.utter_message(text="እባክዎ የአቤቱታዎን ምክንያት ያስገቡ።")
            return []

        access_token = access_token1
        if not access_token:
            dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ።")
            return []

        try:
            api_url = f"https://court-api.zorcloud.net/complaints/{complaint_id}/appeal"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            payload = {"reason": appeal_reason}

            response = requests.post(api_url, json=payload, headers=headers, timeout=10)

            if response.status_code not in (200, 201):
                try:
                    error_data = response.json()
                    message = error_data.get("message", "አቤቱታ ማስገባት አልተሳካም።")
                except Exception:
                    message = "አቤቱታ ማስገባት አልተሳካም።"
                dispatcher.utter_message(text=message)
                return []

            appeal_data = response.json()
            status = appeal_data.get("status", "PENDING")
            created_at = appeal_data.get("created_at", "")
            created_at = created_at.split("T", 1)[0] if "T" in created_at else created_at

            dispatcher.utter_message(
                text=(
                    f"✅ አቤቱታዎ ተመዝግቧል።\n"
                    f"🔢 ማጣቀሻ ቁጥር: {reference_no}\n"
                    f"📊 ሁኔታ: {status}\n"
                    f"📅 የተፈጠረበት ቀን: {created_at}"
                )
            )

            return [
                SlotSet("appeal_complaint_id", None),
                SlotSet("appeal_reference_no", None),
                SlotSet("is_appeal", False)
            ]

        except Exception as e:
            print(f"Error submitting appeal: {e}")
            dispatcher.utter_message(text="ስህተት ተፈጥሯል።")
            return []
# class ActionCheckAuth(Action):
#     def name(self) -> Text:
#         return "action_check_auth"

#     def run(self, dispatcher, tracker, domain):

#         # ✅ ALWAYS read from slot
#         access_token = tracker.get_slot("access_token")
#         print(f"DEBUG: ActionCheckAuth - access_token: {access_token[:20] if access_token else None}")

#         if access_token:
#             # dispatcher.utter_message(
#             #     text="✅ አስቀድመው ገብተዋል። ቅሬታ ማስገባት ይችላሉ።")
            
#             return [FollowupAction("clarification_form_am")]

#         buttons = [
#             {"title": "📝 ምዝገባ", "payload": "/register"},
#             {"title": "🔐 መግባት", "payload": "/login"},
#             # {"title": "❌ ሰርዝ", "payload": "/cancel"}
#         ]

#         dispatcher.utter_message(
#             text="📋 የቅሬታ አገልግሎት ለማግኘት መመዝገብ ወይም መግባት ያስፈልግዎታል።",
#             buttons=buttons
#         )
#         return []


class Actioncheck_ref_numberAm(Action):
    def name(self) -> Text:
        return "check_ref_number_am"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        

        case_number = tracker.get_slot("case_number")
        session = requests.Session()
        hostname = f"http://213.55.79.158:8080/api/SearchCase?caseNumber=00/0001/{case_number}"
        
        try:
            if connected_to_internet(url=hostname):
                response = session.get(hostname, headers={'Content-type': 'application/json', 'Accept': 'application/json'})
                response_json = response.json()
                GlobalVariables.isCaseNumberAvailable = response_json.get("CaseNumber")
                
                if GlobalVariables.isCaseNumberAvailable is None:
                    message = "በዚህ ማጣቀሻ ቁጥር የተመዘገበ ፋይል የለም ሰለዚህ"
                    dispatcher.utter_message(text=message)
                    return [SlotSet("case_number", None), FollowupAction("clarification_form_am")]
                
                # Show case info
                case_info = self.format_case_info(response_json)
                dispatcher.utter_message(text=case_info)
                
                # Ask for confirmation
                buttons = [
                    {"title": "✓ ትክክል ነው - ቀጥል", "payload": "/confirm_case_correct"},
                    {"title": "✗ ትክክል አይደለም - እንደገና አስገባ", "payload": "/confirm_case_wrong"}
                ]
                dispatcher.utter_message(
                text="ይህ የእርሶ ጉዳይ ነው?",
                buttons=buttons,
                button_type="vertical")
            else:
                message = "ለጊዜው, ይህን ሂደት ማከናወን አልችልም"
                dispatcher.utter_message(text=message)
                return [SlotSet("case_number", None)]
                
        except Exception as e:
            print(f"Error: {e}")
            dispatcher.utter_message("no connection available casenumber ")
            return [SlotSet("case_number", None)]
    
    def format_case_info(self, case_data: Dict) -> str:
        # Same format function as above
        info = []
        if case_data.get("CaseNumber"): info.append(f"ጉዳይ ቁጥር: {case_data['CaseNumber']}")
        if case_data.get("Plaintiff"): info.append(f"ከሳሽ: {case_data['Plaintiff']}")
        if case_data.get("Defendant"): info.append(f"ተከሳሽ: {case_data['Defendant']}")
        if case_data.get("Bench"): info.append(f"ችሎት: {case_data['Bench']}")
        if case_data.get("WhoWon"): info.append(f"ያሸነፈው: {case_data['WhoWon']}")
        if case_data.get("DateResolved"): info.append(f"የተፈታበት ቀን: {case_data['DateResolved']}")
        return "\n".join(info)

    


class CaseDisplayAm(Action):
    def name(self) -> Text:
        return "case_display_am"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        case_number = tracker.get_slot("case_number")
        session = requests.Session()
        hostname = f"http://213.55.79.158:8080/api/SearchCase?caseNumber=00/0001/{case_number}"
        
        try:
            if connected_to_internet(url=hostname):
                response = session.get(hostname, headers={'Content-type': 'application/json', 'Accept': 'application/json'})
                response_json = response.json()
                GlobalVariables.isCaseNumberAvailable = response_json.get("CaseNumber")
                
                if GlobalVariables.isCaseNumberAvailable is None:
                    message = "በዚህ ማጣቀሻ ቁጥር የተመዘገበ ፋይል የለም ሰለዚህ"
                    dispatcher.utter_message(text=message)
                    return [SlotSet("case_number", None), FollowupAction("clarification_form_am")]
                
                # Show case info
                case_info = self.format_case_info(response_json)
                dispatcher.utter_message(text=case_info)
                
                # Ask for confirmation
                buttons = [
                    {"title": "✓ ትክክል ነው - ቀጥል", "payload": "/case_correct"},
                    {"title": "✗ ትክክል አይደለም - እንደገና አስገባ", "payload": "/case_wrong"}
                ]
                dispatcher.utter_message(
                text="ይህ ትክክለኛው ጉዳይ ነው?",
                buttons=buttons,
                button_type="vertical")
            else:
                message = "ለጊዜው, ይህን ሂደት ማከናወን አልችልም"
                dispatcher.utter_message(text=message)
                return [SlotSet("case_number", None)]
                
        except Exception as e:
            print(f"Error: {e}")
            dispatcher.utter_message("no connection available case display")
            return [SlotSet("case_number", None)]


class clarificationformAm(FormAction):
    """Example of a custom form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "clarification_form_am"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["case_number",]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""
        return [{
            "case_number": [
                self.from_text(),
            ],},FollowupAction()]

# class ActionFetchcourt_leveles(Action):
#     def name(self):
#         return "action_fetch_court_leveles"
    
#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict]:
#         """Fetch court_leveles from API using access token and display as buttons"""
        
#         try:
#             # Get access token from slot
#             access_token = tracker.get_slot("access_token")
#             access_token=access_token1
#             print(f"Access Token court_leveles: {access_token1}")
            
#             if not access_token:
#                 dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ")
#                 return []  # Just return empty, don't force login
            
#             # API endpoint
#             api_url = "https://court-api.zorcloud.net/court-levels" 
            
#             # Prepare headers with authorization
#             headers = {
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/json"
#             }
            
#             # Make authenticated API call
#             response = requests.get(api_url, headers=headers, timeout=10)
            
#             # Check for authentication errors
#             if response.status_code == 401 or response.status_code == 403:
#                 dispatcher.utter_message(text="መግባትዎ ጊዜው አልቋል፣ እባክዎ እንደገና ይግቡ")
#                 return []
            
#             # if response.status_code != 200 or response.status_code != 201:
#             #     dispatcher.utter_message(text=f"ስህተት: ኮድ {response.status_code}")
#             #     return []
            
#             court_leveles = response.json()
            
#             if not court_leveles:
#                 dispatcher.utter_message(text="ምንም ቅርንጫፍ የለም")
#                 return []
            
#             buttons = []

#             # Handle response format
#             if isinstance(court_leveles, dict) and "data" in court_leveles:
#                 court_leveles_list = court_leveles["data"]
#             else:
#                 court_leveles_list = court_leveles
            
#             for court_level in court_leveles_list:
#                 bname = court_level.get("name", "Unknown court_level")
#                 bid = court_level.get("id")

#                 if bid:
#                     # payload = "/select_court_level{\"court_level_id\": \"" + bid + "\"}"
#                     payload = f"/select_court_level{{\"court_level_id\": \"{bid}\"}}"
#                     buttons.append({"title": bname, "payload": payload})
            
#             if not buttons:
#                 dispatcher.utter_message(text="ምንም ቅርንጫፍ አልተገኘም")
#                 return []
            
#             # Display message with buttons
#             message = "እባክዎን ቅርንጫፍ ይምረጡ:"
#             dispatcher.utter_message(text=message, buttons=buttons, button_type="vertical")
            
#             # Store court_leveles data
#             court_level_data = []
#             for court_level in court_leveles_list:
#                 if court_level.get("id"):
#                     court_level_data.append({
#                         "id": court_level.get("id"),
#                         "name": court_level.get("name", ""),
#                         "description": court_level.get("description", ""),
#                         "court_level": court_level.get("court_level", {}).get("name", "") if isinstance(court_level.get("court_level"), dict) else ""
#                     })
            
#             # CRITICAL: Just return the slot, NO FollowupAction!
#             return []
            
#         except requests.exceptions.Timeout:
#             dispatcher.utter_message(text="ጊዜ አልቋል")
#             return []
#         except Exception as e:
#             print(f"Error: {e}")
#             dispatcher.utter_message(text="ስህተት ተፈጥሯል")
#             return []
#         except requests.exceptions.ConnectionError:
#             dispatcher.utter_message(text="መስመሩ ዝግ ነው!")
#             return []
#         except requests.exceptions.Timeout:
#             dispatcher.utter_message(text="ጥያቄው ጊዜው አልቋል፣ እባክዎ እንደገና ይሞክሩ")
#             return []
#         except json.JSONDecodeError:
#             dispatcher.utter_message(text="መልሱ ስህተት አለበት")
#             return []
#         except Exception as e:
#             print(f"Error: {str(e)}")  # Log for debugging
#             dispatcher.utter_message(text="ስህተት ተፈጥሯል")
#             return []
class ActionSavecourt_level(Action):
    def name(self) -> Text:
        return "action_save_court_level"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Save the selected court_level ID"""

        user_text = tracker.latest_message.get("text", "")
        print(f"DEBUG: Saving court level, user input: {user_text}")

        court_level_id = None

        # Method 1: Extract from pattern "court_level_id{id}"
        if user_text.startswith("court_level_id"):
            # Extract everything after "court_level_id"
            court_level_id = user_text.replace("court_level_id", "", 1)
            print(f"DEBUG: Extracted ID from prefix: {court_level_id}")
        
        # Method 2: Extract from any position in text
        if not court_level_id and "court_level_id" in user_text:
            # If pattern is somewhere in the middle: "some text court_level_id{id} more text"
            parts = user_text.split("court_level_id")
            if len(parts) > 1:
                # The ID is everything after "court_level_id" until next space or end
                court_level_id = parts[1].strip()
                # Remove any trailing characters that might be part of other text
                if " " in court_level_id:
                    court_level_id = court_level_id.split(" ")[0]
                print(f"DEBUG: Extracted ID from middle: {court_level_id}")

        if court_level_id:
            # Clean up - remove any non-alphanumeric characters (except hyphens for UUID)
            import re
            # Keep only UUID format characters: a-f, 0-9, and hyphens
            court_level_id = re.sub(r'[^a-f0-9\-]', '', court_level_id.lower())
            
            # Validate it looks like a UUID
            if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', court_level_id):
                print(f"DEBUG: Valid court_level_id found: {court_level_id}")
                dispatcher.utter_message(text="✅ የፍ/ቤት ደረጃ ተመርጧል")
                
                # Save court level ID for fetching branches
                return [
                    SlotSet("court_level_id", court_level_id),
                    FollowupAction("action_fetch_branches_by_court_level")
                ]
            else:
                print(f"DEBUG: Invalid UUID format: {court_level_id}")

        dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን የፍ/ቤት ደረጃዎች ይምረጡ")
        return []
# class ActionSavecourt_level(Action):
#     def name(self) -> Text:
#         return "action_save_court_level"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         """Save the selected court_level ID"""

#         user_text = tracker.latest_message.get("text", "")
#         print(f"DEBUG: Saving court level, user input: {user_text}")

#         # Extract court_level_id from entity
#         # court_level_id = None

#         # Method 1: Check entities from intent
#         for entity in tracker.latest_message.get("entities", []):
#             if entity["entity"] == "court_level_id":
#                 court_level_id = entity["value"]
#                 break

#         # Method 2: Extract from button payload
#         if not court_level_id and "court_level_id" in user_text:
#             import re
#             match = re.search(r'court_level_id\":\s*\"([^\"]+)\"', user_text)
#             if match:
#                 court_level_id = match.group(1)

#         if court_level_id:
#             # Find court level name for confirmation
#             dispatcher.utter_message(text="✅ የፍ/ቤት ደረጃ ተመርጧል")

#             # Save court level ID for fetching branches
#             return [
#                 SlotSet("court_level_id", court_level_id),
#                 FollowupAction("action_fetch_branches_by_court_level")
#             ]

#         dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን የፍ/ቤት ደረጃዎች ይምረጡ")
#         return []
class ActionFetchcourt_leveles(Action):
    def name(self):
        return "action_fetch_court_leveles"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Fetch court_leveles from API using access token and display as buttons"""
        
        try:
            # Get access token from slot
            access_token = tracker.get_slot("access_token")
            access_token=access_token1
            print(f"Access Token court_leveles: {access_token1}")
            
            if not access_token:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ")
                return []
            
            # API endpoint
            api_url = "https://court-api.zorcloud.net/court-levels" 
            
            # Prepare headers with authorization
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Make authenticated API call
            response = requests.get(api_url, headers=headers, timeout=10)
            
            # Check for authentication errors
            if response.status_code == 401 or response.status_code == 403:
                dispatcher.utter_message(text="መግባትዎ ጊዜው አልቋል፣ እባክዎ እንደገና ይግቡ")
                return []
            
            court_leveles = response.json()
            
            if not court_leveles:
                dispatcher.utter_message(text="ምንም ቅርንጫፍ የለም")
                return []
            
            buttons = []

            # Handle response format
            if isinstance(court_leveles, dict) and "data" in court_leveles:
                court_leveles_list = court_leveles["data"]
            else:
                court_leveles_list = court_leveles
            
            for court_level in court_leveles_list:
                bname = court_level.get("name", "Unknown court_level")
                bid = court_level.get("id")

                if bid:
                    # USE THE WORKING PATTERN from your other action
                    # Format: "court_level_id" + bid (simple concatenation)
                    payload = "court_level_id" + bid
                    buttons.append({"title": bname, "payload": payload})
            
            if not buttons:
                dispatcher.utter_message(text="ምንም ቅርንጫፍ አልተገኘም")
                return []
            
            # Display message with buttons - SAME FORMAT as working action
            message = "እባክዎን ቅርንጫፍ ይምረጡ:"
            dispatcher.utter_message(text=message, buttons=buttons, button_type="vertical")
            
            return []
            
        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="ጊዜ አልቋል")
            return []
        except requests.exceptions.ConnectionError:
            dispatcher.utter_message(text="መስመሩ ዝግ ነው!")
            return []
        except json.JSONDecodeError:
            dispatcher.utter_message(text="መልሱ ስህተት አለበት")
            return []
        except Exception as e:
            print(f"Error: {str(e)}")
            dispatcher.utter_message(text="ስህተት ተፈጥሯል")
            return []

class ActionFetchBranchesBycourt_level_id(Action):
    def name(self):
        return "action_fetch_branches_by_court_level"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Fetch branches filtered by selected court level"""
        
        try:
            # Get access token and court level ID
            # access_token = tracker.get_slot("access_token")
            court_level_id = tracker.get_slot("court_level_id")
            access_token= access_token1
            print(f"DEBUG: Court Level ID: {court_level_id}")
            print(f"DEBUG: Access Token: {access_token[:50] if access_token else 'None'}...")
            
            if not access_token:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ")
                return []
            
            if not court_level_id:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ የፍ/ቤት ደረጃ ይምረጡ")
                return []
            
            # OPTION 1: If API supports filtering by court_level_id
            api_url = f"https://court-api.zorcloud.net/branches/by-court-level/{court_level_id}"
            
  
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code != 200:
                dispatcher.utter_message(text=f"ስህተት: ኮድ {response.status_code}")
                return []

            branches = response.json()

            if branches is None:
                dispatcher.utter_message(text="ለዚህ የፍ/ቤት ደረጃ ቅርንጫፍ የለም")
                return []

            # Handle response format
            if isinstance(branches, dict) and "data" in branches:
                branches = branches["data"]

            if branches is None:
                dispatcher.utter_message(text="ለዚህ የፍ/ቤት ደረጃ ቅርንጫፍ የለም")
                return []

            # Check for API error responses
            if isinstance(branches, dict) and "success" in branches and not branches.get("success", True):
                error_message = branches.get("message", "API error occurred")
                print(f"DEBUG: API Error: {error_message}")
                dispatcher.utter_message(text=f"ስህተት: {error_message}")
                return []

            # Check if response is a list
            if not isinstance(branches, list):
                print(f"DEBUG: Unexpected response type: {type(branches)}, content: {branches}")
                dispatcher.utter_message(text="ስህተት ተፈጥሯል")
                return []

            if not branches:
                dispatcher.utter_message(text="ለዚህ የፍ/ቤት ደረጃ ቅርንጫፍ የለም")
                return []

            # Create buttons
            buttons = []
            for branch in branches:
                bname = branch.get("name", "ቅርንጫፍ")
                bid = branch.get("id")

                if bid:
                    # payload = "/select_branch{\"branch_id\": \"" + bid + "\"}"
                    payload = "select_branch" + bid

                    buttons.append({"title": bname, "payload": payload})
            
            if not buttons:
                dispatcher.utter_message(text="ምንም ቅርንጫፍ አልተገኘም")
                return []
            
            # Show buttons
            dispatcher.utter_message(
                text="እባክዎን ቅርንጫፍ ይምረጡ:", 
                buttons=buttons, 
                button_type="vertical"
            )
            
            # Store branches for reference if needed
            branch_data = []
            for branch in branches:
                branch_data.append({
                    "id": branch.get("id"),
                    "name": branch.get("name"),
                    "court_level_id": branch.get("court_level_id")
                })
            
            return []
            
        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="ጊዜ አልቋል")
            return []
        except Exception as e:
            print(f"Error fetching branches: {e}")
            dispatcher.utter_message(text="ስህተት ተፈጥሯል")
            return []

# class ActionSaveBranch(Action):
#     def name(self) -> Text:
#         return "action_save_branch"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         user_text = tracker.latest_message.get("text", "")
#         print(f"DEBUG: Saving branch, user input: {user_text}")

#         # Extract branch_id from entity
#         branch_id = None

#         # Method 1: Check entities from intent
#         for entity in tracker.latest_message.get("entities", []):
#             if entity["entity"] == "branch_id":
#                 branch_id = entity["value"]
#                 break

#         # Method 2: Extract from button payload
#         if not branch_id and "branch_id" in user_text:
#             import re
#             match = re.search(r'branch_id\":\s*\"([^\"]+)\"', user_text)
#             if match:
#                 branch_id = match.group(1)

#         # Method 3: Fallback to simple extraction
#         if not branch_id and "inform" in user_text:
#             parts = user_text.split("inform")
#             if len(parts) > 1:
#                 branch_id = parts[1]

#         if branch_id:
#             # Find branch name for confirmation
#             dispatcher.utter_message(text="✅ ቅርንጫፍ ተመርጧል")

#             # Save branch ID for fetching court main services
#             # Clear any previously selected organization slots to ensure they are re-selected for the new branch
#             return [
#                 SlotSet("branch_id", branch_id),
#                 SlotSet("court_main_service_id", None),
#                 SlotSet("subunit_one_id", None),
#                 SlotSet("subunit_two_id", None),
#                 SlotSet("subunit_three_id", None),
#                 SlotSet("available_court_main_services", None),
#                 SlotSet("available_subunits", None),
#                 SlotSet("available_subunit_twos", None),
#                 SlotSet("available_subunit_threes", None),
#                 FollowupAction("action_fetch_court_main_services")
#             ]

#         dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን ቅርንጫፎች ይምረጡ")
#         return []
class ActionSaveBranch(Action):
    def name(self) -> Text:
        return "action_save_branch"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_text = tracker.latest_message.get("text", "")
        print(f"DEBUG: Saving branch, user input: {user_text}")

        # Extract branch_id from entity
        branch_id = None

        # Method 1: Check entities from intent
        for entity in tracker.latest_message.get("entities", []):
            if entity["entity"] == "branch_id":
                branch_id = entity["value"]
                break

        # Method 2: Extract from button payload with JSON format
        if not branch_id and "branch_id" in user_text:
            import re
            match = re.search(r'branch_id\":\s*\"([^\"]+)\"', user_text)
            if match:
                branch_id = match.group(1)

        # Method 3: Extract from "select_branch" prefix (NEW - for your pattern)
        if not branch_id and user_text.startswith("select_branch"):
            # Extract everything after "select_branch"
            branch_id = user_text.replace("select_branch", "", 1)
            print(f"DEBUG: Extracted from select_branch prefix: {branch_id}")

        # Method 4: Fallback to old "inform" pattern
        if not branch_id and "inform" in user_text:
            parts = user_text.split("inform")
            if len(parts) > 1:
                branch_id = parts[1]

        # Clean and validate the branch_id
        if branch_id:
            import re
            # Clean up - remove any non-UUID characters
            branch_id = re.sub(r'[^a-f0-9\-]', '', branch_id.lower())
            
            # Validate UUID format
            if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', branch_id):
                print(f"DEBUG: Valid branch_id found: {branch_id}")
                
                # Find branch name for confirmation
                dispatcher.utter_message(text="✅ ቅርንጫፍ ተመርጧል")

                # Save branch ID for fetching court main services
                # Clear any previously selected organization slots to ensure they are re-selected for the new branch
                return [
                    SlotSet("branch_id", branch_id),
                    SlotSet("court_main_service_id", None),
                    SlotSet("subunit_one_id", None),
                    SlotSet("subunit_two_id", None),
                    SlotSet("subunit_three_id", None),
                    SlotSet("available_court_main_services", None),
                    SlotSet("available_subunits", None),
                    SlotSet("available_subunit_twos", None),
                    SlotSet("available_subunit_threes", None),
                    FollowupAction("action_fetch_court_main_services")
                ]
            else:
                print(f"DEBUG: Invalid UUID format: {branch_id}")

        dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን ቅርንጫፎች ይምረጡ")
        return []
# class ActionFetchCourtMainServices(Action):
#     def name(self):
#         return "action_fetch_court_main_services"
    
#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict]:
#         """Fetch top-level organizations (where parentId is null) as Court Main Services"""

#         try:
#             access_token = GlobalVariables.access_token
#             branch_id = tracker.get_slot("branch_id")

#             print(f"DEBUG: Fetching court main services for branch: {branch_id}")
#             print(f"DEBUG: Access Token: {access_token[:50]}...")

#             if not access_token:
#                 dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ")
#                 return []

#             if not branch_id:
#                 dispatcher.utter_message(text="እባክዎ በመጀመሪያ ቅርንጫፍ ይምረጡ")
#                 return []

#             # API endpoint for organizations filtered by branch_id
#             api_url = f"https://court-api.zorcloud.net/organizations/branch/{branch_id}"

#             headers = {
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/json"
#             }
            
#             # Fetch all organizations
#             response = requests.get(api_url, headers=headers, timeout=10)

#             if response.status_code not in [200, 201]:
#                 print(f"DEBUG: API Error - Status: {response.status_code}")
#                 try:
#                     error_response = response.json()
#                     print(f"DEBUG: Error response: {error_response}")
#                     error_message = error_response.get("message", f"ስህተት: ኮድ {response.status_code}")
#                     dispatcher.utter_message(text=error_message)
#                 except json.JSONDecodeError:
#                     print(f"DEBUG: Non-JSON error response: {response.text}")
#                     dispatcher.utter_message(text=f"ስህተት: ኮድ {response.status_code}")
#                 return []
            
#             organizations = response.json()

#             print(f"DEBUG: Raw API response: {organizations}")
#             print(f"DEBUG: Response type: {type(organizations)}")

#             if not organizations:
#                 dispatcher.utter_message(text="ምንም የፍ/ቤት አገልግሎት የለም")
#                 return []

#             # Check if response is a flat list of organizations
#             if isinstance(organizations, list) and organizations and isinstance(organizations[0], dict) and "parentId" in organizations[0]:
#                 # Direct list of organizations
#                 print("DEBUG: Detected flat list of organizations")
#                 all_organizations = organizations
#             else:
#                 # Extract actual organizations from the "organizations" arrays within categories
#                 print("DEBUG: Detected categories with organizations")
#                 all_organizations = []
#                 for category in organizations:
#                     category_orgs = category.get("organizations", [])
#                     for org in category_orgs:
#                         # Add category info to each organization
#                         org["_category_name"] = category.get("name", "")
#                         org["_category_id"] = category.get("id", "")
#                         all_organizations.append(org)

#             # Filter organizations where parentId is null (top-level)
#             top_level_organizations = []
#             for org in all_organizations:
#                 if org.get("parentId") is None:
#                     top_level_organizations.append(org)

#             print(f"DEBUG: Found {len(top_level_organizations)} top-level organizations")
#             print(f"DEBUG: Total organizations returned: {len(all_organizations)}")

#             # If no top-level organizations found, show all organizations as fallback
#             if not top_level_organizations and all_organizations:
#                 print("DEBUG: No top-level organizations found, showing all organizations")
#                 top_level_organizations = all_organizations

#             if not top_level_organizations:
#                 dispatcher.utter_message(text="የፍ/ቤት ዋና አገልግሎቶች የሉም")
#                 return []

#             # Create buttons for each top-level organization
#             buttons = []
#             seen_ids = set()

#             for org in top_level_organizations:
#                 org_id = org.get("id")
#                 org_name = org.get("name", "የፍ/ቤት አገልግሎት")

#                 if not org_id or org_id in seen_ids:
#                     continue

#                 seen_ids.add(org_id)

#                 # Create payload with organization ID
#                 payload = "/select_court_main_service{\"court_main_service_id\": \"" + org_id + "\"}"
#                 buttons.append({"title": org_name, "payload": payload})

#             if not buttons:
#                 dispatcher.utter_message(text="ምንም የፍ/ቤት አገልግሎት አልተገኘም")
#                 return []

#             # Display organizations as buttons
#             message = "እባክዎን የፍ/ቤት ዋና አገልግሎት ይምረጡ:"
#             dispatcher.utter_message(text=message, buttons=buttons, button_type="vertical")

#             # Store organizations data for reference
#             org_data = []
#             for org in top_level_organizations:
#                 org_data.append({
#                     "id": org.get("id"),
#                     "name": org.get("name"),
#                     "code": org.get("code"),
#                     "description": org.get("description"),
#                     "parentId": org.get("parentId"),
#                     "category": org.get("_category_name", ""),
#                     "accepts_complaints": org.get("accepts_complaints", False)
#                 })

#             return [SlotSet("available_court_main_services", org_data)]
            
#         except requests.exceptions.Timeout:
#             dispatcher.utter_message(text="ጊዜ አልቋል")
#             return []
#         except Exception as e:
#             print(f"Error fetching court main services: {e}")
#             dispatcher.utter_message(text="ስህተት ተፈጥሯል")
#             return []
class ActionFetchCourtMainServices(Action):
    def name(self):
        return "action_fetch_court_main_services"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Fetch top-level organizations (where parentId is null) as Court Main Services"""

        try:
            access_token = access_token1
            branch_id = tracker.get_slot("branch_id")

            print(f"DEBUG: Fetching court main services by branch: {branch_id}")
            print(f"DEBUG: Access Token: {access_token[:50]}...")

            if not access_token:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ")
                return []

            if not branch_id:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ቅርንጫፍ ይምረጡ")
                return []

            # API endpoint for organizations filtered by branch_id
            api_url = f"https://court-api.zorcloud.net/organizations/branch/{branch_id}"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Fetch all organizations
            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code not in [200, 201]:
                print(f"DEBUG: API Error - Status: {response.status_code}")
                try:
                    error_response = response.json()
                    print(f"DEBUG: Error response: {error_response}")
                    error_message = error_response.get("message", f"ስህተት: ኮድ {response.status_code}")
                    dispatcher.utter_message(text=error_message)
                except json.JSONDecodeError:
                    print(f"DEBUG: Non-JSON error response: {response.text}")
                    dispatcher.utter_message(text=f"ስህተት: ኮድ {response.status_code}")
                return []
            
            organizations = response.json()

            # Check if organizations is None or empty
            if not organizations:
                print("DEBUG: No organizations returned from API")
                dispatcher.utter_message(text="ምንም የፍ/ቤት አገልግሎት የለም")
                return []

            # Based on your API response, it's a list of organizations
            all_organizations = organizations if isinstance(organizations, list) else []

            # Filter organizations where parentId is null (top-level)
            top_level_organizations = []
            for org in all_organizations:
                if isinstance(org, dict) and org.get("parentId") is None:
                    top_level_organizations.append(org)

            print(f"DEBUG: Found {len(top_level_organizations)} top-level organizations")

            # If no top-level organizations found, show all organizations as fallback
            if not top_level_organizations and all_organizations:
                print("DEBUG: No top-level organizations found, showing all organizations")
                top_level_organizations = all_organizations

            if not top_level_organizations:
                dispatcher.utter_message(text="የፍ/ቤት ዋና አገልግሎቶች የሉም")
                return []

            # Create buttons for each top-level organization
            buttons = []
            seen_ids = set()

            for org in top_level_organizations:
                org_id = org.get("id")
                org_name = org.get("name", "የፍ/ቤት አገልግሎት")

                if not org_id or org_id in seen_ids:
                    continue

                seen_ids.add(org_id)

                # FIX: Telegram-friendly button payload
                # Keep it short and simple - just the ID
                # payload = org_id  # Just use the UUID
                
                # Or if you need a prefix, keep it very short:
                payload = "cms_" + org_id  # 3-4 char prefix
                
                buttons.append({"title": org_name, "payload": payload})

            if not buttons:
                dispatcher.utter_message(text="ምንም የፍ/ቤት አገልግሎት አልተገኘም")
                return []

            # Display organizations as buttons
            message = "እባክዎን የፍ/ቤት ዋና አገልግሎት ይምረጡ:"
            dispatcher.utter_message(text=message, buttons=buttons, button_type="vertical")

            return [SlotSet("available_court_main_services", top_level_organizations)]
            
        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="ጊዜ አልቋል")
            return []
        except Exception as e:
            print(f"Error fetching court main services: {e}")
            import traceback
            traceback.print_exc()
            dispatcher.utter_message(text="ስህተት ተፈጥሯል")
            return []
# class ActionSaveCourtMainService(Action):
#     def name(self) -> Text:
#         return "action_save_court_main_service"
    
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         """Save the selected court main service ID"""
        
#         user_text = tracker.latest_message.get("text", "")
#         print(f"DEBUG: Saving court main service, user input: {user_text}")
        
#         # Extract court_main_service_id from entity
#         court_main_service_id = None
        
#         # Method 1: Check entities from intent
#         for entity in tracker.latest_message.get("entities", []):
#             if entity["entity"] == "court_main_service_id":
#                 court_main_service_id = entity["value"]
#                 break
        
#         # Method 2: Extract from button payload
#         if not court_main_service_id and "court_main_service_id" in user_text:
#             import re
#             match = re.search(r'"court_main_service_id":\s*"([^"]+)"', user_text)
#             if match:
#                 court_main_service_id = match.group(1)

#         if court_main_service_id:
#             # Save service ID for fetching subunits
#             return [
#                 SlotSet("court_main_service_id", court_main_service_id),
#                 FollowupAction("action_fetch_subunit_one")  # Next step to fetch children
#             ]

#         dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን አገልግሎቶች ይምረጡ")
#         return []
class ActionSaveCourtMainService(Action):
    def name(self) -> Text:
        return "action_save_court_main_service"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Save the selected court main service ID from button click"""

        user_text = tracker.latest_message.get("text", "")
        print(f"DEBUG: Saving court main service, user input: {user_text}")

        court_main_service_id = None
        
        # Extract from "cms_" prefix pattern
        if user_text.startswith("cms_"):
            # Remove "cms_" prefix to get the UUID
            court_main_service_id = user_text.replace("cms_", "", 1)
            print(f"DEBUG: Extracted from cms_ prefix: {court_main_service_id}")
        else:
            # Try direct UUID (without prefix)
            court_main_service_id = user_text.strip()
        
        # Validate it's a UUID
        import re
        uuid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        
        if court_main_service_id and re.match(uuid_pattern, court_main_service_id):
            print(f"DEBUG: Valid court_main_service_id: {court_main_service_id}")
            dispatcher.utter_message(text="✅ የፍ/ቤት ዋና አገልግሎት ተመርጧል")
            
            # Find the organization name from stored data
            available_services = tracker.get_slot("available_court_main_services") or []
            service_name = "የፍ/ቤት አገልግሎት"
            
            for service in available_services:
                if isinstance(service, dict) and service.get("id") == court_main_service_id:
                    service_name = service.get("name", service_name)
                    break
            
            return [
                SlotSet("court_main_service_id", court_main_service_id),
                FollowupAction("action_fetch_subunit_one")  # Next step to fetch children
            ]
        
        print(f"DEBUG: Invalid court_main_service_id format: {court_main_service_id}")
        dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን የፍ/ቤት አገልግሎቶች ይምረጡ")
        return []
# class ActionSaveCourtMainService(Action):
#     def name(self) -> Text:
#         return "action_save_court_main_service"
    
#     def run(self, dispatcher, tracker, domain):
#         user_text = tracker.latest_message.get("text", "")
#         print(f"DEBUG: Saving court main service, user input: {user_text}")
        
#         court_main_service_id = None
        
#         # Extract from "court_main_service" prefix
#         if user_text.startswith("court_main_service"):
#             court_main_service_id = user_text.replace("court_main_service", "", 1)
#             print(f"DEBUG: Extracted court_main_service_id: {court_main_service_id}")
        
#         if court_main_service_id:
#             dispatcher.utter_message(text="✅ የፍ/ቤት ዋና አገልግሎት ተመርጧል")
#             return [SlotSet("court_main_service_id", court_main_service_id)]
        
#         dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን የፍ/ቤት አገልግሎቶች ይምረጡ")
#         return []

class ActionFetchSubUnitOne(Action):
    def name(self):
        return "action_fetch_subunit_one"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Fetch child organizations (subunits) of selected court main service"""

        try:
            # Get access token, branch ID and parent service ID
            access_token = access_token1
            branch_id = tracker.get_slot("branch_id")
            parent_service_id = tracker.get_slot("court_main_service_id")

            print(f"DEBUG: Fetching subunits for parent ID: {parent_service_id}, branch: {branch_id}")

            if not access_token:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ")
                return []

            if not branch_id:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ቅርንጫፍ ይምረጡ")
                return []

            if not parent_service_id:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ዋና አገልግሎት ይምረጡ")
                return [FollowupAction("action_fetch_court_main_services")]

            # API endpoint for organizations filtered by branch_id
            api_url = f"https://court-api.zorcloud.net/organization-categories?branch_id={branch_id}"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # Fetch all organizations
            response = requests.get(api_url, headers=headers, timeout=120)

            if response.status_code not in [200, 201]:
                dispatcher.utter_message(text=f"ስህተት: ኮድ {response.status_code}")
                return []

            organizations = response.json()

            if not organizations:
                dispatcher.utter_message(text="ምንም ንዑስ ክፍል የለም")
                return []

            # Handle different response formats
            if isinstance(organizations, dict):
                if "data" in organizations:
                    organizations = organizations["data"]
                elif "organizations" in organizations:
                    organizations = organizations["organizations"]

            # Extract actual organizations from the "organizations" arrays within categories
            all_organizations = []
            if isinstance(organizations, list):
                if organizations and isinstance(organizations[0], dict) and "organizations" in organizations[0]:
                    # It's list of categories
                    for category in organizations:
                        if isinstance(category, dict):
                            category_orgs = category.get("organizations", [])
                            for org in category_orgs:
                                if isinstance(org, dict):
                                    # Add category info to each organization
                                    org["_category_name"] = category.get("name", "")
                                    org["_category_id"] = category.get("id", "")
                                    all_organizations.append(org)
                else:
                    # It's flat list of orgs
                    for org in organizations:
                        if isinstance(org, dict):
                            all_organizations.append(org)
            else:
                dispatcher.utter_message(text="መልሱ ስህተት አለበት")
                return []

            # Filter organizations where parentId = selected service ID
            child_organizations = []

            for org in all_organizations:
                # Check if organization is a child of selected service
                if org.get("parentId") == parent_service_id:
                    child_organizations.append(org)

            print(f"DEBUG: Found {len(child_organizations)} child organizations")

            if not child_organizations:
                # No subunits available, go to content
                dispatcher.utter_message(text="ለዚህ አገልግሎት ንዑስ ክፍሎች የሉም፣ ወደ ቀጣይ ደረጃ እንሸጋገራለን")
                return [FollowupAction("content_compliant_form")]

            # Create buttons for each child organization
            buttons = []

            for org in child_organizations:
                org_id = org.get("id")
                org_name = org.get("name", "ንዑስ ክፍል")

                if org_id:
                    payload = "select_subunit_one" + org_id  # 3-4 char prefix

                    buttons.append({"title": org_name, "payload": payload})

            # Display subunits as buttons
            message = "እባክዎን ንዑስ ክፍል ይምረጡ:"
            dispatcher.utter_message(text=message, buttons=buttons, button_type="vertical")

            # Store child organizations for reference
            child_data = []
            for org in child_organizations:
                child_data.append({
                    "id": org.get("id"),
                    "name": org.get("name"),
                    "parentId": org.get("parentId"),
                    "accepts_complaints": org.get("accepts_complaints", False)
                })

            return [SlotSet("available_subunits", child_data)]

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="ጊዜ አልቋል")
            return []
        except Exception as e:
            print(f"Error fetching subunits: {e}")
            dispatcher.utter_message(text="ስህተት ተፈጥሯል")
            return []

# class ActionSaveSubUnitOne(Action):
#     def name(self) -> Text:
#         return "action_save_subunit_one"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#         """Save the selected subunit one ID"""

#         user_text = tracker.latest_message.get("text", "")
#         print(f"DEBUG: Saving subunit one, user input: {user_text}")

#         # Extract subunit_one_id from entity
#         subunit_one_id = None

#         # Method 1: Check entities from intent
#         for entity in tracker.latest_message.get("entities", []):
#             if entity["entity"] == "subunit_one_id":
#                 subunit_one_id = entity["value"]
#                 break

#         # Method 2: Extract from button payload
#         if not subunit_one_id and "subunit_one_id" in user_text:
#             import re
#             match = re.search(r'subunit_one_id\":\s*\"([^\"]+)\"', user_text)
#             if match:
#                 subunit_one_id = match.group(1)

#         # Method 3: Fallback to simple extraction
#         if not subunit_one_id and "subone" in user_text:
#             parts = user_text.split("subone")
#             if len(parts) > 1:
#                 subunit_one_id = parts[1]

#         if subunit_one_id:
#         # Find subunit name for confirmation
#             available_subunits = tracker.get_slot("available_subunits") or []
#             if isinstance(available_subunits, str):
#                 import json
#                 available_subunits = json.loads(available_subunits)
#             subunit_name = "ንዑስ ክፍል"

#             for subunit in available_subunits:
#                 if isinstance(subunit, dict) and subunit.get("id") == subunit_one_id:
#                     subunit_name = subunit.get("name", "ንዑስ ክፍል")
#                     break

#             dispatcher.utter_message(text=f"✅ {subunit_name} ተመርጧል")

#             # Save subunit ID and fetch subunit two
#             return [
#                 SlotSet("subunit_one_id", subunit_one_id),
#                 FollowupAction("action_fetch_subunit_two")  # Next step - fetch subunit two
#             ]

#         dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን ንዑስ ክፍሎች ይምረጡ")
#         return []
class ActionSaveSubUnitOne(Action):
    def name(self) -> Text:
        return "action_save_subunit_one"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Save the selected subunit one ID"""

        user_text = tracker.latest_message.get("text", "")
        print(f"DEBUG: Saving subunit one, user input: {user_text}")

        # Extract subunit_one_id from entity
        subunit_one_id = None

        # Method 1: Extract from "select_subunit_one" prefix (NEW)
        if user_text.startswith("select_subunit_one"):
            # Remove "select_subunit_one" prefix to get the UUID
            subunit_one_id = user_text.replace("select_subunit_one", "", 1)
            print(f"DEBUG: Extracted from select_subunit_one prefix: {subunit_one_id}")
        
        # Method 2: Check entities from intent
        if not subunit_one_id:
            for entity in tracker.latest_message.get("entities", []):
                if entity["entity"] == "subunit_one_id":
                    subunit_one_id = entity["value"]
                    break

        # Method 3: Extract from button payload (JSON format)
        if not subunit_one_id and "subunit_one_id" in user_text:
            import re
            match = re.search(r'subunit_one_id\":\s*\"([^\"]+)\"', user_text)
            if match:
                subunit_one_id = match.group(1)

        # Method 4: Fallback to old "subone" pattern
        if not subunit_one_id and "subone" in user_text:
            parts = user_text.split("subone")
            if len(parts) > 1:
                subunit_one_id = parts[1]

        # Clean and validate the subunit_one_id
        if subunit_one_id:
            import re
            # Clean up - remove any non-UUID characters
            subunit_one_id = re.sub(r'[^a-f0-9\-]', '', subunit_one_id.lower())
            
            # Validate UUID format
            if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', subunit_one_id):
                print(f"DEBUG: Valid subunit_one_id found: {subunit_one_id}")
                
                # Find subunit name for confirmation
                available_subunits = tracker.get_slot("available_subunits") or []
                if isinstance(available_subunits, str):
                    import json
                    available_subunits = json.loads(available_subunits)
                subunit_name = "ንዑስ ክፍል"

                for subunit in available_subunits:
                    if isinstance(subunit, dict) and subunit.get("id") == subunit_one_id:
                        subunit_name = subunit.get("name", "ንዑስ ክፍል")
                        break

                dispatcher.utter_message(text=f"✅ {subunit_name} ተመርጧል")

                # Save subunit ID and fetch subunit two
                return [
                    SlotSet("subunit_one_id", subunit_one_id),
                    FollowupAction("action_fetch_subunit_two")  # Next step - fetch subunit two
                ]
            else:
                print(f"DEBUG: Invalid UUID format: {subunit_one_id}")

        dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን ንዑስ ክፍሎች ይምረጡ")
        return []

class ActionFetchSubUnitTwo(Action):
    def name(self):
        return "action_fetch_subunit_two"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Fetch child organizations (subunit two) of selected subunit one"""

        try:
            # Get access token, branch ID and parent subunit one ID
            access_token = access_token1

            branch_id = tracker.get_slot("branch_id")
            parent_subunit_one_id = tracker.get_slot("subunit_one_id")

            print(f"DEBUG: Fetching subunit two for parent ID: {parent_subunit_one_id}, branch: {branch_id}")

            if not access_token:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ")
                return []

            if not branch_id:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ቅርንጫፍ ይምረጡ")
                return []

            if not parent_subunit_one_id:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ንዑስ ክፍል አንድ ይምረጡ")
                return [FollowupAction("action_fetch_subunit_one")]

            # API endpoint for organizations filtered by branch_id
            api_url = f"https://court-api.zorcloud.net/organization-categories?branch_id={branch_id}"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # Fetch all organizations
            response = requests.get(api_url, headers=headers, timeout=120)

            if response.status_code not in [200, 201]:
                dispatcher.utter_message(text=f"ስህተት: ኮድ {response.status_code}")
                return []

            organizations = response.json()

            if not organizations:
                dispatcher.utter_message(text="ምንም ንዑስ ክፍል ሁለት የለም")
                return []

            # Extract actual organizations from the "organizations" arrays within categories
            all_organizations = []
            for category in organizations:
                category_orgs = category.get("organizations", [])
                for org in category_orgs:
                    # Add category info to each organization
                    org["_category_name"] = category.get("name", "")
                    org["_category_id"] = category.get("id", "")
                    all_organizations.append(org)

            # Filter organizations where parentId = selected subunit one ID
            subunit_two_organizations = []

            for org in all_organizations:
                # Check if organization is a child of selected subunit one
                if org.get("parentId") == parent_subunit_one_id:
                    subunit_two_organizations.append(org)

            print(f"DEBUG: Found {len(subunit_two_organizations)} subunit two organizations")

            if not subunit_two_organizations:
                # No subunit two available, go to content
                dispatcher.utter_message(text="ለዚህ ንዑስ ክፍል ንዑስ ክፍሎች ሁለት የሉም፣ ወደ ቀጣይ ደረጃ እንሸጋገራለን")
                return [FollowupAction("content_compliant_form")]

            # Create buttons for each subunit two organization
            buttons = []

            for org in subunit_two_organizations:
                org_id = org.get("id")
                org_name = org.get("name", "ንዑስ ክፍል ሁለት")

                if org_id:
                    # payload = "/select_subunit_two{\"subunit_two_id\": \"" + org_id + "\"}"
                    payload = "select_subunit_two" + org_id  # 3-4 char prefix

                    buttons.append({"title": org_name, "payload": payload})

            # Display subunit two as buttons
            message = "እባክዎን ንዑስ ክፍል ሁለት ይምረጡ:"
            dispatcher.utter_message(text=message, buttons=buttons, button_type="vertical")

            # Store subunit two organizations for reference
            subunit_two_data = []
            for org in subunit_two_organizations:
                subunit_two_data.append({
                    "id": org.get("id"),
                    "name": org.get("name"),
                    "parentId": org.get("parentId"),
                    "accepts_complaints": org.get("accepts_complaints", False)
                })

            import json
            return [SlotSet("available_subunit_twos", json.dumps(subunit_two_data))]

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="ጊዜ አልቋል")
            return []
        except Exception as e:
            print(f"Error fetching subunit two: {e}")
            dispatcher.utter_message(text="ስህተት ተፈጥሯል")
            return []

class ActionSaveSubUnitTwo(Action):
    def name(self) -> Text:
        return "action_save_subunit_two"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Save the selected subunit two ID"""

        user_text = tracker.latest_message.get("text", "")
        print(f"DEBUG: Saving subunit two, user input: {user_text}")

        # Extract subunit_two_id from entity
        subunit_two_id = None

        # Method 1: Extract from "select_subunit_two" prefix (NEW)
        if user_text.startswith("select_subunit_two"):
            # Remove "select_subunit_two" prefix to get the UUID
            subunit_two_id = user_text.replace("select_subunit_two", "", 1)
            print(f"DEBUG: Extracted from select_subunit_two prefix: {subunit_two_id}")
        
        # Method 2: Check entities from intent
        if not subunit_two_id:
            for entity in tracker.latest_message.get("entities", []):
                if entity["entity"] == "subunit_two_id":
                    subunit_two_id = entity["value"]
                    break

        # Method 3: Extract from button payload (JSON format)
        if not subunit_two_id and "subunit_two_id" in user_text:
            import re
            match = re.search(r'subunit_two_id\":\s*\"([^\"]+)\"', user_text)
            if match:
                subunit_two_id = match.group(1)

        # Clean and validate the subunit_two_id
        if subunit_two_id:
            import re
            # Clean up - remove any non-UUID characters
            subunit_two_id = re.sub(r'[^a-f0-9\-]', '', subunit_two_id.lower())
            
            # Validate UUID format
            if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', subunit_two_id):
                print(f"DEBUG: Valid subunit_two_id found: {subunit_two_id}")
                
                # Find subunit two name for confirmation
                available_subunit_twos = tracker.get_slot("available_subunit_twos") or []
                if isinstance(available_subunit_twos, str):
                    import json
                    available_subunit_twos = json.loads(available_subunit_twos)
                subunit_two_name = "ንዑስ ክፍል ሁለት"

                for subunit in available_subunit_twos:
                    if isinstance(subunit, dict) and subunit.get("id") == subunit_two_id:
                        subunit_two_name = subunit.get("name", "ንዑስ ክፍል ሁለት")
                        break

                dispatcher.utter_message(text=f"✅ {subunit_two_name} ተመርጧል")

                # Save subunit two ID and fetch subunit three
                return [
                    SlotSet("subunit_two_id", subunit_two_id),
                    FollowupAction("action_fetch_subunit_three")  # Next step - fetch subunit three
                ]
            else:
                print(f"DEBUG: Invalid UUID format: {subunit_two_id}")

        dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን ንዑስ ክፍሎች ሁለት ይምረጡ")
        return []

class ActionFetchSubUnitThree(Action):
    def name(self):
        return "action_fetch_subunit_three"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Fetch child organizations (subunit three) of selected subunit two"""

        try:
            # Get access token, branch ID and parent subunit two ID
            access_token = access_token1
            branch_id = tracker.get_slot("branch_id")
            parent_subunit_two_id = tracker.get_slot("subunit_two_id")

            print(f"DEBUG: Fetching subunit three for parent ID: {parent_subunit_two_id}, branch: {branch_id}")

            if not access_token:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ")
                return []

            if not branch_id:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ቅርንጫፍ ይምረጡ")
                return []

            if not parent_subunit_two_id:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ንዑስ ክፍል ሁለት ይምረጡ")
                return [FollowupAction("action_fetch_subunit_two")]

            # API endpoint for organizations filtered by branch_id
            api_url = f"https://court-api.zorcloud.net/organization-categories?branch_id={branch_id}"

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # Fetch all organizations
            response = requests.get(api_url, headers=headers, timeout=120)

            if response.status_code not in [200, 201]:
                dispatcher.utter_message(text=f"ስህተት: ኮድ {response.status_code}")
                return []

            organizations = response.json()

            if not organizations:
                dispatcher.utter_message(text="ምንም ንዑስ ክፍል ሶስት የለም")
                return []

            # Handle different response formats
            if isinstance(organizations, dict):
                if "data" in organizations:
                    organizations = organizations["data"]
                elif "organizations" in organizations:
                    organizations = organizations["organizations"]

            # Extract actual organizations from the "organizations" arrays within categories
            all_organizations = []
            if isinstance(organizations, list):
                if organizations and isinstance(organizations[0], dict) and "organizations" in organizations[0]:
                    # It's list of categories
                    for category in organizations:
                        if isinstance(category, dict):
                            category_orgs = category.get("organizations", [])
                            for org in category_orgs:
                                if isinstance(org, dict):
                                    # Add category info to each organization
                                    org["_category_name"] = category.get("name", "")
                                    org["_category_id"] = category.get("id", "")
                                    all_organizations.append(org)
                else:
                    # It's flat list of orgs
                    for org in organizations:
                        if isinstance(org, dict):
                            all_organizations.append(org)
            else:
                dispatcher.utter_message(text="መልሱ ስህተት አለበት")
                return []

            # Filter organizations where parentId = selected subunit two ID
            subunit_three_organizations = []

            for org in all_organizations:
                # Check if organization is a child of selected subunit two
                if org.get("parentId") == parent_subunit_two_id:
                    subunit_three_organizations.append(org)

            print(f"DEBUG: Found {len(subunit_three_organizations)} subunit three organizations")

            if not subunit_three_organizations:
                # No subunit three available, go to content
                dispatcher.utter_message(text="ለዚህ ንዑስ ክፍል ንዑስ ክፍሎች ሶስት የሉም፣ ወደ ቀጣይ ደረጃ እንሸጋገራለን")
                return [FollowupAction("content_compliant_form")]

            # Create buttons for each subunit three organization
            buttons = []

            for org in subunit_three_organizations:
                org_id = org.get("id")
                org_name = org.get("name", "ንዑስ ክፍል ሶስት")

                if org_id:
                    # payload = "/select_subunit_three{\"subunit_three_id\": \"" + org_id + "\"}"
                    payload = "select_subunit_three" + org_id  # 3-4 char prefix

                    buttons.append({"title": org_name, "payload": payload})

            # Display subunit three as buttons
            message = "እባክዎን ንዑስ ክፍል ሶስት ይምረጡ:"
            dispatcher.utter_message(text=message, buttons=buttons, button_type="vertical")

            # Store subunit three organizations for reference
            subunit_three_data = []
            for org in subunit_three_organizations:
                subunit_three_data.append({
                    "id": org.get("id"),
                    "name": org.get("name"),
                    "parentId": org.get("parentId"),
                    "accepts_complaints": org.get("accepts_complaints", False)
                })

            return [SlotSet("available_subunit_threes", subunit_three_data)]

        except requests.exceptions.Timeout:
            dispatcher.utter_message(text="ጊዜ አልቋል")
            return []
        except Exception as e:
            print(f"Error fetching subunit three: {e}")
            dispatcher.utter_message(text="ስህተት ተፈጥሯል")
            return []

class ActionSaveSubUnitThree(Action):
    def name(self) -> Text:
        return "action_save_subunit_three"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        """Save the selected subunit three ID"""

        user_text = tracker.latest_message.get("text", "")
        print(f"DEBUG: Saving subunit three, user input: {user_text}")

        # Extract subunit_three_id from entity
        subunit_three_id = None

        # Method 1: Extract from "select_subunit_three" prefix (NEW)
        if user_text.startswith("select_subunit_three"):
            # Remove "select_subunit_three" prefix to get the UUID
            subunit_three_id = user_text.replace("select_subunit_three", "", 1)
            print(f"DEBUG: Extracted from select_subunit_three prefix: {subunit_three_id}")
        
        # Method 2: Check entities from intent
        if not subunit_three_id:
            for entity in tracker.latest_message.get("entities", []):
                if entity["entity"] == "subunit_three_id":
                    subunit_three_id = entity["value"]
                    break

        # Method 3: Extract from button payload (JSON format)
        if not subunit_three_id and "subunit_three_id" in user_text:
            import re
            match = re.search(r'subunit_three_id\":\s*\"([^\"]+)\"', user_text)
            if match:
                subunit_three_id = match.group(1)

        # Clean and validate the subunit_three_id
        if subunit_three_id:
            import re
            # Clean up - remove any non-UUID characters
            subunit_three_id = re.sub(r'[^a-f0-9\-]', '', subunit_three_id.lower())
            
            # Validate UUID format
            if re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', subunit_three_id):
                print(f"DEBUG: Valid subunit_three_id found: {subunit_three_id}")
                
                # Find subunit three name for confirmation
                available_subunit_threes = tracker.get_slot("available_subunit_threes") or []
                if isinstance(available_subunit_threes, str):
                    import json
                    available_subunit_threes = json.loads(available_subunit_threes)
                subunit_three_name = "ንዑስ ክፍል ሶስት"

                for subunit in available_subunit_threes:
                    if isinstance(subunit, dict) and subunit.get("id") == subunit_three_id:
                        subunit_three_name = subunit.get("name", "ንዑስ ክፍል ሶስት")
                        break

                dispatcher.utter_message(text=f"✅ {subunit_three_name} ተመርጧል")

                # Save subunit three ID and go to ask attachment
                return [
                    SlotSet("subunit_three_id", subunit_three_id),
                    FollowupAction("content_compliant_form") ]
            else:
                print(f"DEBUG: Invalid UUID format: {subunit_three_id}")

        dispatcher.utter_message(text="እባክዎ ከላይ ያሉትን ንዑስ ክፍሎች ሶስት ይምረጡ")
        return []


# class ActionAskAttachment(Action):
#     def name(self) -> Text:
#         return "action_ask_attachment"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         buttons = [
#             {"title": "አዎ", "payload": "/affirm"},
#             {"title": "አይ", "payload": "/deny"}
#         ]
#         dispatcher.utter_message(text="አባር ለቅሬታዎ ያለው ማብራሪያ አለዎት?", buttons=buttons, button_type="vertical")
#         return []


class ActionSaveAttachment(Action):
    def name(self) -> Text:
        return "action_save_attachment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        last_intent = tracker.latest_message.get("intent", {}).get("name")

        if last_intent == "affirm":
            return [SlotSet("has_attachment", True), FollowupAction("form_upload_image")]
        elif last_intent == "deny":
            return [SlotSet("has_attachment", False), FollowupAction("content_compliant_form")]

        return []


class ActionAskContent(Action):
    def name(self) -> Text:
        return "action_ask_content"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="እባክዎ ቅሬታዎን በአጭር ያስተያዩ")
        return []





# class ActionSaveContent(Action):
#     def name(self) -> Text:
#         return "action_save_content"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         content = tracker.latest_message.get("text", "")
#         return [SlotSet("complaint_content", content)]





class othernew_complaintm(FormAction):
    def name(self) -> Text:
        return "content_compliant_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["content","new_slot"]
    def slot_mappings(self) -> Dict[Text, Union[Dict,List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""
        return {

            "content": [
                self.from_text(),
            ],
            
            "new_slot": [
                self.from_text(),
            ]

        }

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # Process the filled slots and perform necessary actions
        new_slot = tracker.get_slot("new_slot")
        if new_slot == "accept":
            return [FollowupAction("form_upload_image")]
        else:
            return [FollowupAction("submit_compliant_en")]

        return []

class Actionchoosenewslot(Action):
    def name(self) -> Text:
        return "action_new_slot"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        new_slot = tracker.latest_message.get("text")
        if new_slot == "accept":
            return [SlotSet("new_slot", new_slot), FollowupAction("form_upload_image")]
        else:
            return [SlotSet("new_slot", new_slot), FollowupAction("submit_compliant_en")]

        return []






class ImageUpload(FormAction):
    def name(self) -> Text:
        return "form_upload_image"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        return ["upload_image"]
    def slot_mappings(self) -> Dict[Text, Union[Dict,List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""
        return {

            "upload_image": [
                self.from_text(),
            ]
            

        }

        return []

class ActionUPLOADPICTURE(Action):
    def name(self) -> Text:
        return "action_upload_image"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
         after all required slots are filled"""

        session = requests.Session()
        image_id = ""   
        urlimg = "https://api.telegram.org/bot6344667146:AAHNf0PpA8DLx9CdXbItH4TI-ndApEnu3tA"
        r2 = requests.get(urlimg)
        img = base64.b64encode(r2.content)
        

        if tracker.get_slot("upload_image"):
            image_id = tracker.get_slot("upload_image")
            print("image id", image_id)
            url2 = "https://api.telegram.org/bot6344667146:AAHNf0PpA8DLx9CdXbItH4TI-ndApEnu3tA/getFile?file_id=" + image_id
            r = requests.get(url2)
            img = base64.b64encode(r.content)

            resp = json.loads(r.text)
            file_path = resp["result"]["file_path"]

            print("this is " + file_path)
            url3 = "https://api.telegram.org/file/bot6344667146:AAHNf0PpA8DLx9CdXbItH4TI-ndApEnu3tA/" + file_path
            r2 = requests.get(url3)
            img = base64.b64encode(r2.content)
            # Get the file extension from the filename
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1]

            # Call the convertToBase64 method to get the Base64 string
            img_base64 = img

            GlobalVariables.data["documents"] = img_base64.decode('utf-8')
            GlobalVariables.data["extension"] = file_extension  # Set the file extension
        
        # print("This  is image iddd",image_id)
        # if image_id!= "":
        #     data["documents"]=img.decode('utf-8')
        #     print("data is .....",data)
               
        
        # try:
            
        #     if connected_to_internet(url=hostname):
                
        #         response_text = session.post(url, json=data)
        #         # response_json = json.loads(response_text.text)
        #         print("respnse jason nw ....   ",response_text)
        #         dispatcher.utter_message("ur document is sent sucessfully")
               
        #     else:
        #          message = "For the time being, I can not perform this process"
        #          dispatcher.utter_message(text=message)


        # except ValueError as e:
        #     message = "no available"
        #     dispatcher.utter_message(text=message)
        return [SlotSet("upload_image", img)]
    



class ActionSubmitcompliant(Action):
    def name(self) -> Text:
        return "submit_compliant_en"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
         after all required slots are filled"""
        session = requests.Session()

        hostname ="https://court-api.zorcloud.net/complaints"

        url = hostname
        buttons = []
        
        compliant = tracker.get_slot("compliant")
        if compliant == "ቅ/ጽ/ቤት":
           buttons.append({"title": "sdf", "payload": "‘payload_value’"})
           dispatcher.utter_message(buttons=buttons)
            
            
            # "fileName": tracker.get_slot("upload_image"),

        # Get the last selected organization ID (subunit_three_id takes precedence, then subunit_two_id, etc.)
        organization_id = (
            tracker.get_slot("subunit_three_id") or
            tracker.get_slot("subunit_two_id") or
            tracker.get_slot("subunit_one_id") or
            tracker.get_slot("court_main_service_id")
        )

        # Prepare form data for multipart/form-data
        data = {
            "content": tracker.get_slot("content"),
            "case_number": tracker.get_slot("case_number"),
            "organization_id": organization_id,
            "branch_id": tracker.get_slot("branch_id"),
            # "current_status_id": "5942d6eb-4fc0-41de-9b05-5359a3c49814",  # Default status
            # "priority": "HIGH",  # Default priority
            # "sender_phone": "+251911234567",  # This should be from user data, but using default for now
            # "sender_email": "john.doe@example.com",  # Should be from user data
            # "sender_name": "John Doe",  # Should be from user data
            # "is_anonymous": "false"
        }

        files = {}
        if GlobalVariables.data.get("documents"):
            # For multipart, we need to handle the file properly
            # Assuming the file is base64 encoded string, we need to decode it
            import base64
            try:
                file_data = base64.b64decode(GlobalVariables.data["documents"])
                files["file"] = ("attachment", file_data, "application/octet-stream")
            except Exception as e:
                print(f"Error decoding file: {e}")

        print("data is", data)
        try:
            # Get access token from slot
            # access_token = tracker.get_slot("access_token")
            access_token=access_token1
            print(f"Access Token court_leveles: {access_token}")
            
            if not access_token:
                dispatcher.utter_message(text="እባክዎ በመጀመሪያ ይግቡ")
                return []
            
            # API endpoint
            api_url = "https://court-api.zorcloud.net/court-levels" 
            
            # Prepare headers with authorization
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Make authenticated API call
            # response = requests.get(api_url, headers=headers, timeout=10)
            
            if connected_to_internet(url=url):
                print("checking")
                response_text = requests.post(url, json=data, headers=headers, timeout=50)
                # access_token=access_token1
                if response_text.status_code == 201:
                    response_json = json.loads(response_text.text)
                    dispatcher.utter_message("ከእኛ ጋር ስላደረጉት ቆይታ እናመሰግናለን.")
                    reference_number = response_json.get('reference_no', 'N/A')
                    compalint_id = response_json.get('id', 'N/A')
                    print(reference_number)
                    dispatcher.utter_message(" ቅሬታህን ተቀብለናል ,ለሚመለከተው ክፍል እናደርሳለን" +"\n"+ str(reference_number) +"\n"+ "በዚህ ቁጥር የአቤቱታ ሁኔታዎን መከታተል ይችላሉ.")
                
                else:
                    # Try to extract the error message from the response
                    try:
                        error_response = response_text.json()
                        print(f"DEBUG: API Error Response: {error_response}")
                        
                        # Extract the message - it could be a string or list
                        error_message = error_response.get('message', 'Unknown error')
                        
                        # If message is a list, join it
                        if isinstance(error_message, list):
                            error_message = ', '.join(error_message)
                        
                        # Also check other possible error fields
                        if not error_message or error_message == 'Unknown error':
                            error_message = error_response.get('error', str(response_text.status_code))
                            
                        print(f"DEBUG: Extracted error message: {error_message}")
                        dispatcher.utter_message(f"ቅሬታ ማስገባት አልተሳካም። ስህተት: {error_message}")
                        
                    except json.JSONDecodeError:
                        # If response is not JSON, show the raw text
                        print(f"DEBUG: Non-JSON error response: {response_text.text}")
                        dispatcher.utter_message(f"ቅሬታ ማስገባት አልተሳካም። ኮድ: {response_text.status_code}")
            else:
                message = "አስተያየቶች አልተላኩም። እባክዎ ቆየት ብለው ይሞክሩ"
                dispatcher.utter_message(text=message)
            dispatcher.utter_message(response="action_reset_slots_value")
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            message = "ስህተት ተፈጥሯል።"
            dispatcher.utter_message(text=message)
            # print("submited")
          
        return [AllSlotsReset()]
    
