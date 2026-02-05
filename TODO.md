## Tasks
- [x] Implement missing `action_save_subunit_one` in actions.py
- [x] Fix duplicate rule names in rules.yml and ensure proper sequencing
- [x] Update domain.yml to include all actions from actions.py
- [x] Verify the complete complaint flow: start_complaint → check_auth → register/login → case verification → court level → branch → main service → subunit selection
- [x] Update organization fetching actions to filter by branch_id in API calls
- [x] Clear organization slots when branch changes to prevent "Organization does not belong to the specified branch" error
=======
# TODO: Fix Rules and Actions Communication

## Tasks
- [x] Implement missing `action_save_subunit_one` in actions.py
- [x] Fix duplicate rule names in rules.yml and ensure proper sequencing
- [x] Update domain.yml to include all actions from actions.py
- [x] Verify the complete complaint flow: start_complaint → check_auth → register/login → case verification → court level → branch → main service → subunit selection
- [x] Update organization fetching actions to filter by branch_id in API calls
- [x] Clear organization slots when branch changes to prevent "Organization does not belong to the specified branch" error
- [x] Implement view_complaint_detail functionality
  - [x] Add view_complaint_detail intent in data/nlu.yml
  - [x] Add action_view_complaint_detail to actions in domain.yml
  - [x] Add view_complaint_detail to intents in domain.yml
  - [x] Create ActionViewComplaintDetail class in actions/actions.py
  - [x] Add rule in data/rules.yml to map intent to action
- [x] Implement appeal_complaint functionality
  - [x] Add appeal_complaint intent in data/nlu.yml
  - [x] Add action_appeal_complaint to actions in domain.yml
  - [x] Add appeal_complaint to intents in domain.yml
  - [x] Create ActionAppealComplaint class in actions/actions.py
  - [x] Add rule in data/rules.yml to map intent to action
