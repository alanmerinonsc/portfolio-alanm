  Salesforce JWT Authentication Utility (C)

  Overview:
  This program is a C console-based utility designed to simplify the process of
  configuring and testing Salesforce JWT (JSON Web Token) authentication. It allows
  developers or administrators to generate RSA key pairs and self-signed X.509
  certificates, create signed JWT assertions using the RS256 algorithm, and optionally
  exchange those assertions for Salesforce OAuth access tokens.
 
  The tool streamlines the setup required for Salesforce’s OAuth 2.0 JWT Bearer
  Token Flow by automating certificate generation, JWT creation, and token
  request operations that are commonly performed manually during integration
  development.

  Usage:
  When executed, the program presents a console menu with three main options:
 
  1) Generate RSA key pair + self-signed certificate
     - Creates a new RSA private key and a corresponding self-signed X.509 certificate.
     - Allows configuration of key size, certificate subject, validity period, and
       optional password-protected PFX export.
     - Outputs files in PEM format, including:
          • Public certificate (.crt) to upload to a Salesforce Connected App
          • Private key (.key) used to sign JWT tokens
          • Optional .pfx bundle containing both certificate and private key
 
  2) Create signed JWT (RS256)
     - Loads a private key from either a PKCS8 PEM file or a PFX certificate.
     - Prompts the user for Salesforce authentication parameters:
          • Consumer Key (Connected App client ID)
          • Salesforce username
          • Target environment (Production or Sandbox)
          • Token expiration time
     - Generates and signs a JWT assertion using the RS256 algorithm and outputs
       the resulting token, which can be used with the Salesforce OAuth JWT
       bearer grant type.
 
  3) Exchange JWT for an OAuth access token
     - Sends an HTTP POST request to the Salesforce OAuth token endpoint.
     - Submits the JWT assertion using the JWT Bearer Token Flow grant type.
     - If successful, returns the Salesforce access token that can be used to
       authenticate API requests.
 
  Key Features:
  - Automated generation of RSA key pairs and X.509 certificates
  - Support for PEM and PFX private key formats
  - Secure JWT signing using RS256
  - Built-in Salesforce OAuth token exchange
  - Interactive console prompts with input validation and error handling
  - Compatible with both Salesforce Production and Sandbox environments
 
  Dependencies:
  - System.Security.Cryptography (RSA key generation and certificate creation)
  - System.IdentityModel.Tokens.Jwt (JWT generation and signing)
  - Microsoft.IdentityModel.Tokens (cryptographic signing support)
  - System.Net.Http (OAuth token request)
 
  Typical Workflow:
  1. Generate a certificate and private key using option 1.
  2. Upload the generated certificate (.crt) to a Salesforce Connected App.
  3. Use option 2 to create a signed JWT assertion.
  4. Use option 3 to exchange the JWT for an OAuth access token.
 
  The resulting access token can then be used to authenticate Salesforce API
  requests using the "Authorization: Bearer <token>" header.