# Upload Image/File Form Flow Study - IN PROGRESS

## Summary

The task was to study the flow for uploading an image/file form to successfully attach the document when "affirm" is selected without sending the data.

## Changes Made

### 1. Added new rule in data/rules.yml
```
yaml
- rule: Handle affirm for attachment
  steps:
  - intent: affirm
  - action: action_save_attachment
```
 
## Issue: Flow Still Not Working

The user reports that when clicking "affirm" (አዎ አለኝ), the complaint is submitted immediately without asking for image upload.

## Root Cause Analysis

The most likely cause is that **the Rasa model needs to be retrained** for the new rules to take effect. In Rasa:

1. Rules are part of the Training Data
2. The model must be retrained with `rasa train` to include new rules
3. After retraining, the new model must be deployed to the Rasa server

## Required Steps to Fix

### Step 1: Retrain the Rasa Model
Run the following command to retrain the model with the new rules:
```
bash
rasa train
```

### Step 2: Deploy the New Model
After training, copy the new model to the models directory:
```
bash
cp models/<new_model.tar.gz> models/20260217-105749.tar.gz
```

### Step 3: Restart Rasa Server
Restart the Rasa server to load the new model:
```
bash
rasa run -m models/20260217-105749.tar.gz
```

## Alternative: Check if Rules Are Working

You can verify if the rules are being loaded by checking the Rasa logs. Look for any errors related to rule parsing.

## Current Flow (After Fix Should Work):

1. **action_ask_attachment** - Asks "አባር ለቅረታዎ ያለው ማብራሪያ አለዎት?" (Do you have an attachment?)
2. **User responds with "affirm" (አዎ)** - Intent is detected as "affirm"
3. **Rule "Handle affirm for attachment"** - Matches and triggers action_save_attachment
4. **action_save_attachment** - Sets has_attachment=True, asks for file upload, and triggers form_upload_image
5. **form_upload_image** - Form is activated to collect upload_image slot
6. **User uploads image/file** - The image is processed
7. **Form submission** - After form is complete, action_upload_image is called, then submit_compliant_en

## Status: Awaiting Model Retraining
