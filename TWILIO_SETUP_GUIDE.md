# 📞 Step-by-Step Twilio Phone Number Setup Guide

Yes! **Twilio is the industry standard** for connecting a real phone number to your AI receptionist.

When you sign up for Twilio, they give you **$15.00 in free trial credits** (which is 100% free with no credit card required to start testing).

---

## Step 1: Create a Free Twilio Account
1. Go to [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up with your email and verify your mobile number.
3. In the setup questionnaire:
   * **"What product are you here to use?"** -> Select **Voice**
   * **"What do you plan to build?"** -> Select **Customer Care / IVR / Voice AI**
   * **"Preferred language?"** -> Select **Python**

---

## Step 2: Get a Free Twilio Phone Number
1. On your Twilio Console dashboard, click **"Get a Trial Phone Number"**.
2. Twilio will instantly assign you a virtual phone number (e.g. `+1 (555) ...` or select country).
3. Save this phone number — this will be the number your client/customers call!

---

## Step 3: Connect Twilio to Your Local Laptop Using a Free Tunnel
Because your AI server is running locally on your laptop (`http://localhost:8000`), Twilio on the internet needs a secure URL to reach it.

You can use **Cloudflare Tunnel (cloudflared)** or **ngrok** (both are 100% free).

### Using Free Cloudflare Quick Tunnel (Zero signup needed):
1. Download `cloudflared.exe` from [https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/) and put it in `I:\jewellery_voice_receptionist\`.
2. Run this command:
   ```cmd
   cloudflared.exe tunnel --url http://localhost:8000
   ```
3. Cloudflare gives you a free HTTPS link, like: `https://sparkling-jewel-abc.trycloudflare.com`

---

## Step 4: Configure the Webhook in Twilio
1. Go to **Twilio Console** -> **Phone Numbers** -> **Manage** -> **Active Numbers**.
2. Click on your active phone number.
3. Scroll down to the **Voice Configuration** section:
   * **"A CALL COMES IN"** -> Set to **Webhook**
   * **URL** -> Enter your tunnel URL + `/twilio/voice`:
     ```
     https://sparkling-jewel-abc.trycloudflare.com/twilio/voice
     ```
   * **HTTP Method** -> Select **HTTP POST**
4. Click **Save Configuration** at the bottom.

---

## Step 5: Test the Call!
1. Start your server by double-clicking `run_receptionist.bat` on Drive `I:`.
2. Pick up your mobile phone and dial the Twilio phone number.
3. The AI receptionist will pick up the call, welcome you, listen to your query, check the jewellery database, and speak the reply directly into your phone!

