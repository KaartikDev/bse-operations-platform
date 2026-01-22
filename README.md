# How To Develop With This and Background on Google's API
```
This should help you get up to speed on the very very basics of working with Google's API and the structure of a Google Cloud Project.
```
Note: This is from my understanding at the moment. I'm not fully clear on the specific workflow. 

Another Note: This readme was mostly AI Generated. I just organized it a little.

## Google Oauth:

When using the Google Sheets API to access your own or others' data, it requires the security framework, OAuth 2.0. 
OAuth 2.0 is designed to let an application perform actions on your behalf without you ever having to give that application your actual Google password. 

## The Structure of the Project
Note: I made a Google Cloud Project using my personal UCLA gmail. It would be best if we create a Google Cloud Project using the BSE email and have us act as collaborators. 

### The Google Cloud Project (The "Container")
A Project acts as the top-level container for all your technical settings. 
It is where you: 
1. Manage APIs: You must explicitly turn on the specific APIs (ex. Google Sheets API) within the project so Google knows which specific services your code is allowed to use.
2. Manage Quotas: It tracks how many requests your app makes to prevent abuse of Google’s servers. 

### The Brand & Consent Screen (The "ID Card")
The Brand (configured on the OAuth Consent Screen) is what a user sees when they log in. 
Identity: It tells the user exactly which "app" is asking for their data (e.g., your app's name and logo).
Transparency: It lists the "Scopes" (permissions) being requested, such as "View and manage your spreadsheets".
Trust: By showing this screen, Google ensures you are making an informed choice to let this specific app touch your files. 

### The OAuth Client (The "Key")
The Client ID and Client Secret are the "username and password" for the application itself. 
Platform-Specific Rules: When you create a client, you specify if it's a web app, a desktop app, or a mobile app. Each has different security requirements (e.g., a web app needs a "Redirect URI").
Identification: These credentials prove to Google that the request is coming from your specific, registered project and not an impostor. 

### The Login & Token (The "Access Pass")
The reason you must log in and generate a token is that Google doesn't want your code to store your password. 
Access Token: When you log in, Google issues a short-lived "access pass" (the token). This token is sent with every API request to prove you gave permission.
Limited Power: If someone steals this token, they only have access to your Sheets for a short time, and they still don't have your password to change your account settings.
Refresh Token: Most setups also give you a "refresh token." This allows your app to get a new access token automatically in the background so you don't have to manually log in every hour. 

## When You Make API Calls
The email address being used is the individual Google account you use to log in when the "Consent Screen" appears.
Even though you created the project and "Brand" in a Google Cloud account (which might be the same email), the API technically acts as the specific user who successfully completes the login prompt and generates the token. 

The API can only see and edit spreadsheets that the authenticated email has permission to access. If you log in with personal@gmail.com but the sheet is owned by work@company.com, the API will fail unless the sheet has been shared with your personal email. 

## How This Connects with the Client ID 
The Client ID creates a credentials.json you download and move into the project folder that is essentially the ID card for your application. It contains the client_id and client_secret that prove to Google that the code running on your machine is the specific project you registered in the Cloud Console. 
1. Identification: When your code starts, it reads credentials.json to tell Google, "I am App X from Project Y".
2. Authorization Trigger: Google sees this ID and then triggers the login screen for the user to sign in.
3. Token Generation: Once the user logs in, Google uses the information in credentials.json to issue a token.json. This second file is the actual "key" that lets your app edit spreadsheets. 

### Do multiple people use the same credentials.json?
Yes, but only if they are using the same application. 

The Developers/Users: If you give your script to a coworker, they must have a copy of credentials.json so the script can identify itself to Google. Without it, the script won't know which Google Cloud project it belongs to.

The Login is Different: Even if 10 people use the same credentials.json, they will each be prompted to log into their own Google accounts. This generates 10 unique token.json files, one for each person. Each person's actions in the spreadsheet will be tied to their individual email. 

### Critical Security Warnings
Never Share Publicly: Do not upload credentials.json to GitHub or public repositories. If someone steals it, they can "impersonate" your app to trick other users into giving up their data.

Treat it like a Password: While multiple users of your tool might need it, it should only be shared with people you trust.

Don't Share the Token: Never share the token.json file. That file is tied to your specific email account and gives anyone who has it direct access to your spreadsheets. 